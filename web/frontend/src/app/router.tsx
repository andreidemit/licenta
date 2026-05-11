import { lazy, Suspense } from 'react';
import { createBrowserRouter, isRouteErrorResponse, Link, RouterProvider, useRouteError } from 'react-router-dom';
import { TooltipProvider } from '../components/ui/tooltip';
import { AppShell } from './layout/AppShell';

const HomePage = lazy(() => import('../pages/HomePage').then((m) => ({ default: m.HomePage })));
const TrainPage = lazy(() => import('../pages/TrainPage').then((m) => ({ default: m.TrainPage })));
const RunsPage = lazy(() => import('../pages/RunsPage').then((m) => ({ default: m.RunsPage })));
const RunDetailPage = lazy(() =>
  import('../pages/RunDetailPage').then((m) => ({ default: m.RunDetailPage })),
);
const EvaluatePage = lazy(() =>
  import('../pages/EvaluatePage').then((m) => ({ default: m.EvaluatePage })),
);
const BuilderPage = lazy(() => import('../pages/BuilderPage').then((m) => ({ default: m.BuilderPage })));
const ComparePage = lazy(() => import('../pages/ComparePage').then((m) => ({ default: m.ComparePage })));
const SafeNavigationApp = lazy(() => import('../App').then((m) => ({ default: m.App })));
const MonteCarloAnalysisPage = lazy(() =>
  import('../features/safe-navigation/analysis/MonteCarloAnalysisPage').then((m) => ({
    default: m.MonteCarloAnalysisPage,
  })),
);

function PageFallback() {
  return (
    <div className="flex items-center justify-center py-20 text-sm text-ink-muted">
      Se încarcă…
    </div>
  );
}

function RouteError() {
  const error = useRouteError();
  const message = isRouteErrorResponse(error)
    ? `${error.status} ${error.statusText}`
    : error instanceof Error
      ? error.message
      : 'A apărut o eroare neașteptată.';

  return (
    <main className="min-h-screen bg-canvas px-6 py-16 text-ink">
      <div className="mx-auto max-w-2xl rounded-3xl border border-danger/30 bg-danger/10 p-8 shadow-card">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-danger">Eroare interfață</p>
        <h1 className="mt-3 font-serif text-3xl">Ceva nu a funcționat corect.</h1>
        <p className="mt-3 text-sm text-ink-muted">
          Interfața a prins eroarea înainte să blocheze complet aplicația. Reîncarcă pagina sau revino la panoul principal.
        </p>
        <pre className="mt-5 overflow-x-auto rounded-2xl border border-border/60 bg-black/30 p-4 text-xs text-ink-muted">
          {message}
        </pre>
        <Link
          to="/"
          className="mt-6 inline-flex rounded-full bg-accent px-5 py-2 text-sm font-semibold text-white shadow-glow"
        >
          Înapoi la panou
        </Link>
      </div>
    </main>
  );
}

const router = createBrowserRouter([
  {
    path: '/',
    element: <Suspense fallback={<PageFallback />}><SafeNavigationApp /></Suspense>,
    errorElement: <RouteError />,
  },
  {
    path: '/lab',
    element: <AppShell />,
    errorElement: <RouteError />,
    children: [
      { index: true, element: <Suspense fallback={<PageFallback />}><HomePage /></Suspense> },
      { path: 'antrenare', element: <Suspense fallback={<PageFallback />}><TrainPage /></Suspense> },
      { path: 'rulari', element: <Suspense fallback={<PageFallback />}><RunsPage /></Suspense> },
      { path: 'rulari/:runId', element: <Suspense fallback={<PageFallback />}><RunDetailPage /></Suspense> },
      { path: 'evaluare', element: <Suspense fallback={<PageFallback />}><EvaluatePage /></Suspense> },
      { path: 'editor-mediu', element: <Suspense fallback={<PageFallback />}><BuilderPage /></Suspense> },
      { path: 'comparatie', element: <Suspense fallback={<PageFallback />}><ComparePage /></Suspense> },
    ],
  },
  {
    path: '/safe-navigation',
    element: <Suspense fallback={<PageFallback />}><SafeNavigationApp /></Suspense>,
    errorElement: <RouteError />,
  },
  {
    path: '/safe-navigation/monte-carlo',
    element: <Suspense fallback={<PageFallback />}><MonteCarloAnalysisPage /></Suspense>,
    errorElement: <RouteError />,
  },
]);

export function AppRouter() {
  return (
    <TooltipProvider delayDuration={150}>
      <RouterProvider router={router} />
    </TooltipProvider>
  );
}
