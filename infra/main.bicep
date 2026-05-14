@description('Azure region for all resources.')
param location string = resourceGroup().location

@description('Short lowercase prefix used in resource names.')
param namePrefix string = 'qlearning'

@description('Container image used for the initial Container App revision. CI/CD will update this value after pushing to ACR.')
param containerImage string = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

@description('Runtime data root inside the backend container. Azure Files is mounted here.')
param dataRoot string = '/app/data'

@description('Initial placeholder container port. The backend workflow switches ingress to 8000 for the FastAPI image.')
param containerPort int = 80

@description('CPU assigned to the backend container.')
param containerCpu string = '1.0'

@description('Memory assigned to the backend container.')
param containerMemory string = '2.0Gi'

@description('Enable the optional internal Ollama/Gemma Container App used by the AI analyst.')
param enableLlm bool = false

@description('Container image for the optional Ollama/Gemma service. CI/CD can replace this with an ACR image.')
param llmImage string = 'ollama/ollama:latest'

@description('Ollama model tag used by the AI analyst.')
param llmModel string = 'gemma4:26b'

@description('CPU assigned to the optional LLM container.')
param llmCpu string = '8.0'

@description('Memory assigned to the optional LLM container.')
param llmMemory string = '56.0Gi'

@description('Workload profile used by the optional LLM container. Use a GPU profile for 26B-class models.')
param llmWorkloadProfileName string = 'Consumption-GPU-NC24-A100'

@description('Azure Files share quota in GiB for the Ollama model cache.')
param llmFileShareQuota int = 100

@description('Azure Files share quota in GiB.')
param fileShareQuota int = 20

@description('SKU for Azure Static Web Apps.')
@allowed([
  'Free'
  'Standard'
])
param staticWebAppSku string = 'Free'

@description('Common tags for all resources.')
param tags object = {
  project: 'q-learning-lab'
  workload: 'academic-demo'
}

var compactPrefix = take(replace(toLower(namePrefix), '-', ''), 12)
var uniqueSuffix = take(uniqueString(resourceGroup().id, namePrefix), 8)
var acrName = take('${compactPrefix}${uniqueSuffix}acr', 50)
var storageName = take('${compactPrefix}${uniqueSuffix}st', 24)
var logAnalyticsName = '${namePrefix}-${uniqueSuffix}-logs'
var appInsightsName = '${namePrefix}-${uniqueSuffix}-appi'
var containerEnvName = '${namePrefix}-${uniqueSuffix}-cae'
var containerAppName = '${namePrefix}-${uniqueSuffix}-api'
var llmContainerAppName = '${namePrefix}-${uniqueSuffix}-llm'
var staticWebAppName = '${namePrefix}-${uniqueSuffix}-web'
var fileShareName = 'qlearning-data'
var llmFileShareName = 'ollama-models'
var envStorageName = 'qlearningdata'
var llmEnvStorageName = 'ollamamodels'
var dataVolumeName = 'data'
var llmVolumeName = 'ollama-models'
var acrPullRoleDefinitionId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
var frontendOrigin = 'https://${staticWebApp.properties.defaultHostname}'
var containerEnvProperties = union({
  appLogsConfiguration: {
    destination: 'log-analytics'
    logAnalyticsConfiguration: {
      customerId: logAnalytics.properties.customerId
      sharedKey: logAnalytics.listKeys().primarySharedKey
    }
  }
}, enableLlm ? {
  workloadProfiles: [
    {
      name: 'Consumption'
      workloadProfileType: 'Consumption'
    }
    {
      name: llmWorkloadProfileName
      workloadProfileType: llmWorkloadProfileName
      minimumCount: 0
      maximumCount: 1
    }
  ]
} : {})
var llmBaseUrl = enableLlm ? 'https://${llmContainerApp!.properties.configuration.ingress.fqdn}/v1' : 'http://127.0.0.1:11434/v1'

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  tags: tags
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
  }
}

resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageName
  location: location
  tags: tags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

resource fileService 'Microsoft.Storage/storageAccounts/fileServices@2023-01-01' = {
  parent: storage
  name: 'default'
}

resource fileShare 'Microsoft.Storage/storageAccounts/fileServices/shares@2023-01-01' = {
  parent: fileService
  name: fileShareName
  properties: {
    shareQuota: fileShareQuota
  }
}

resource llmFileShare 'Microsoft.Storage/storageAccounts/fileServices/shares@2023-01-01' = if (enableLlm) {
  parent: fileService
  name: llmFileShareName
  properties: {
    shareQuota: llmFileShareQuota
  }
}

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

resource staticWebApp 'Microsoft.Web/staticSites@2022-09-01' = {
  name: staticWebAppName
  location: location
  tags: tags
  sku: {
    name: staticWebAppSku
    tier: staticWebAppSku
  }
  properties: {
    allowConfigFileUpdates: true
    stagingEnvironmentPolicy: 'Enabled'
  }
}

resource containerEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: containerEnvName
  location: location
  tags: tags
  properties: containerEnvProperties
}

resource envStorage 'Microsoft.App/managedEnvironments/storages@2023-05-01' = {
  parent: containerEnv
  name: envStorageName
  properties: {
    azureFile: {
      accountName: storage.name
      accountKey: storage.listKeys().keys[0].value
      shareName: fileShare.name
      accessMode: 'ReadWrite'
    }
  }
}

resource llmEnvStorage 'Microsoft.App/managedEnvironments/storages@2023-05-01' = if (enableLlm) {
  parent: containerEnv
  name: llmEnvStorageName
  properties: {
    azureFile: {
      accountName: storage.name
      accountKey: storage.listKeys().keys[0].value
      shareName: llmFileShare.name
      accessMode: 'ReadWrite'
    }
  }
}

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: containerAppName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: containerEnv.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: containerPort
        transport: 'auto'
        allowInsecure: false
      }
    }
    template: {
      scale: {
        minReplicas: 0
        maxReplicas: 1
      }
      containers: [
        {
          name: 'api'
          image: containerImage
          resources: {
            cpu: json(containerCpu)
            memory: containerMemory
          }
          env: [
            {
              name: 'APP_ENV'
              value: 'production'
            }
            {
              name: 'HOST'
              value: '0.0.0.0'
            }
            {
              name: 'PORT'
              value: string(containerPort)
            }
            {
              name: 'DATA_ROOT'
              value: dataRoot
            }
            {
              name: 'CORS_ORIGINS'
              value: frontendOrigin
            }
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              value: appInsights.properties.ConnectionString
            }
            {
              name: 'LLM_ENABLED'
              value: enableLlm ? 'true' : 'false'
            }
            {
              name: 'LLM_PROVIDER'
              value: 'ollama'
            }
            {
              name: 'LLM_BASE_URL'
              value: llmBaseUrl
            }
            {
              name: 'LLM_MODEL'
              value: llmModel
            }
            {
              name: 'LLM_TIMEOUT_SECONDS'
              value: '120'
            }
            {
              name: 'LLM_MAX_OUTPUT_TOKENS'
              value: '700'
            }
          ]
          volumeMounts: [
            {
              volumeName: dataVolumeName
              mountPath: dataRoot
            }
          ]
        }
      ]
      volumes: [
        {
          name: dataVolumeName
          storageType: 'AzureFile'
          storageName: envStorage.name
        }
      ]
    }
  }
}

resource llmContainerApp 'Microsoft.App/containerApps@2024-03-01' = if (enableLlm) {
  name: llmContainerAppName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: containerEnv.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: false
        targetPort: 11434
        transport: 'auto'
        allowInsecure: false
      }
    }
    workloadProfileName: llmWorkloadProfileName
    template: {
      scale: {
        minReplicas: 0
        maxReplicas: 1
      }
      containers: [
        {
          name: 'llm'
          image: llmImage
          resources: {
            cpu: json(llmCpu)
            memory: llmMemory
          }
          env: [
            {
              name: 'LLM_MODEL'
              value: llmModel
            }
            {
              name: 'OLLAMA_HOST'
              value: '0.0.0.0:11434'
            }
            {
              name: 'OLLAMA_MODELS'
              value: '/root/.ollama'
            }
          ]
          volumeMounts: [
            {
              volumeName: llmVolumeName
              mountPath: '/root/.ollama'
            }
          ]
        }
      ]
      volumes: [
        {
          name: llmVolumeName
          storageType: 'AzureFile'
          storageName: llmEnvStorage.name
        }
      ]
    }
  }
}

resource acrPullAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, containerApp.id, acrPullRoleDefinitionId)
  scope: acr
  properties: {
    roleDefinitionId: acrPullRoleDefinitionId
    principalId: containerApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource llmAcrPullAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (enableLlm) {
  name: guid(acr.id, llmContainerApp!.id, acrPullRoleDefinitionId)
  scope: acr
  properties: {
    roleDefinitionId: acrPullRoleDefinitionId
    principalId: llmContainerApp!.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

output acrLoginServer string = acr.properties.loginServer
output acrName string = acr.name
output appInsightsName string = appInsights.name
output backendUrl string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
output containerAppName string = containerApp.name
output containerAppsEnvironmentName string = containerEnv.name
output fileShareName string = fileShare.name
output frontendUrl string = frontendOrigin
output llmContainerAppName string = enableLlm ? llmContainerApp!.name : ''
output llmInternalUrl string = enableLlm ? 'https://${llmContainerApp!.properties.configuration.ingress.fqdn}' : ''
output llmModelName string = llmModel
output logAnalyticsWorkspaceName string = logAnalytics.name
output staticWebAppName string = staticWebApp.name
output storageAccountName string = storage.name
