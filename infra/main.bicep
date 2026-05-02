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
var staticWebAppName = '${namePrefix}-${uniqueSuffix}-web'
var fileShareName = 'qlearning-data'
var envStorageName = 'qlearningdata'
var dataVolumeName = 'data'
var acrPullRoleDefinitionId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
var frontendOrigin = 'https://${staticWebApp.properties.defaultHostname}'

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

resource containerEnv 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: containerEnvName
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
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

resource acrPullAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, containerApp.id, acrPullRoleDefinitionId)
  scope: acr
  properties: {
    roleDefinitionId: acrPullRoleDefinitionId
    principalId: containerApp.identity.principalId
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
output logAnalyticsWorkspaceName string = logAnalytics.name
output staticWebAppName string = staticWebApp.name
output storageAccountName string = storage.name
