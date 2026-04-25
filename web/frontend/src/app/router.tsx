import { lazy, Suspense } from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
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
const LegacyApp = lazy(() => import('../App').then((m) => ({ default: m.App })));

function PageFallback() {
  return (
    <div className="flex items-center justify-center py-20 text-sm text-ink-muted">
      Se încarcă…
    </div>
  );
}

const router = createBrowserRouter([
  {
    element: <AppShell />,
    children: [
      { path: '/', element: <Suspense fallback={<PageFallback />}><HomePage /></Suspense> },
      { path: '/antrenare', element: <Suspense fallback={<PageFallback />}><TrainPage /></Suspense> },
      { path: '/rulari', element: <Suspense fallback={<PageFallback />}><RunsPage /></Suspense> },
      { path: '/rulari/:runId', element: <Suspense fallback={<PageFallback />}><RunDetailPage /></Suspense> },
      { path: '/evaluare', element: <Suspense fallback={<PageFallback />}><EvaluatePage /></Suspense> },
      { path: '/editor-mediu', element: <Suspense fallback={<PageFallback />}><BuilderPage /></Suspense> },
      { path: '/comparatie', element: <Suspense fallback={<PageFallback />}><ComparePage /></Suspense> },
    ],
  },
  {
    path: '/legacy',
    element: <Suspense fallback={<PageFallback />}><LegacyApp /></Suspense>,
  },
]);

export function AppRouter() {
  return (
    <TooltipProvider delayDuration={150}>
      <RouterProvider router={router} />
    </TooltipProvider>
  );
}
