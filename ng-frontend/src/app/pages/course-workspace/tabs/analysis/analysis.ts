import { Component } from '@angular/core';

@Component({
  selector: 'app-analysis-tab',
  template: `
    <div class="page-content">
      <div class="tab-placeholder">
        <span class="tab-placeholder__phase">Phase 9.8</span>
        <h2 class="tab-placeholder__title">Analysis</h2>
        <p class="tab-placeholder__desc">Performance timeline, module-wise results, Bloom's taxonomy breakdown, and question performance table.</p>
      </div>
    </div>
  `,
  styles: [`
    .tab-placeholder { display:flex; flex-direction:column; gap:var(--space-3); padding:var(--space-8) 0; }
    .tab-placeholder__phase { display:inline-flex; padding:3px 10px; border-radius:var(--radius-full); background:var(--color-primary-light); color:var(--color-primary); font-size:var(--font-size-xs); font-weight:600; width:fit-content; }
    .tab-placeholder__title { font-size:var(--font-size-2xl); font-weight:700; letter-spacing:-0.02em; }
    .tab-placeholder__desc  { font-size:var(--font-size-base); color:var(--color-text-secondary); max-width:420px; line-height:1.6; }
  `]
})
export class AnalysisTab {}
