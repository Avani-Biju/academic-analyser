import { Routes } from '@angular/router';

export const routes: Routes = [
  // ── Primary Routes ──────────────────────────────────────────────
  {
    path: '',
    loadComponent: () =>
      import('./pages/dashboard/dashboard').then(m => m.Dashboard),
    title: 'Dashboard – Academic Analyzer'
  },
  {
    path: 'courses',
    loadComponent: () =>
      import('./pages/courses/courses').then(m => m.Courses),
    title: 'My Courses – Academic Analyzer'
  },
  {
    path: 'courses/new',
    loadComponent: () =>
      import('./pages/create-course/create-course').then(m => m.CreateCourse),
    title: 'Create Course – Academic Analyzer'
  },

  // ── Course Workspace ─────────────────────────────────────────────
  {
    path: 'courses/:id',
    loadComponent: () =>
      import('./pages/course-workspace/course-workspace').then(m => m.CourseWorkspace),
    children: [
      {
        path: '',
        redirectTo: 'overview',
        pathMatch: 'full'
      },
      {
        path: 'overview',
        loadComponent: () =>
          import('./pages/course-workspace/tabs/overview/overview').then(m => m.OverviewTab),
        title: 'Overview – Academic Analyzer'
      },
      {
        path: 'syllabus',
        loadComponent: () =>
          import('./pages/course-workspace/tabs/syllabus/syllabus').then(m => m.SyllabusTab),
        title: 'Syllabus – Academic Analyzer'
      },
      {
        path: 'question-papers',
        loadComponent: () =>
          import('./pages/course-workspace/tabs/question-papers/question-papers').then(m => m.QuestionPapersTab),
        title: 'Question Papers – Academic Analyzer'
      },
      {
        path: 'question-papers/:qpId',
        loadComponent: () =>
          import('./pages/course-workspace/tabs/question-papers/qp-detail/qp-detail').then(m => m.QpDetail),
        title: 'Question Paper – Academic Analyzer'
      },
      {
        path: 'analysis',
        loadComponent: () =>
          import('./pages/course-workspace/tabs/analysis/analysis').then(m => m.AnalysisTab),
        title: 'Analysis – Academic Analyzer'
      },
      {
        path: 'coach',
        loadComponent: () =>
          import('./pages/course-workspace/tabs/coach/coach').then(m => m.CoachTab),
        title: 'AI Study Coach – Academic Analyzer'
      }
    ]
  },

  // ── Settings ─────────────────────────────────────────────────────
  {
    path: 'settings',
    loadComponent: () =>
      import('./pages/settings/settings').then(m => m.Settings),
    title: 'Settings – Academic Analyzer'
  },

  // ── Fallback ─────────────────────────────────────────────────────
  { path: '**', redirectTo: '' }
];
