import { Component, OnInit } from '@angular/core';
import { CommonModule, NgClass } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../shared/services/api.service';
import { Course, MatchResult } from '../../shared/models/types';

@Component({
  selector: 'app-matching',
  imports: [CommonModule, NgClass, RouterLink],
  templateUrl: './matching.html',
  styleUrl: './matching.css'
})
export class Matching implements OnInit {
  courses: Course[] = [];
  selectedCourseId: number | null = null;
  matchResults: any[] = [];
  loading = true;
  matchLoading = false;

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.api.getCourses().subscribe({
      next: (data) => {
        this.courses = data;
        this.loading = false;
        if (data.length > 0) {
          this.selectCourse(data[0].id);
        }
      },
      error: () => this.loading = false
    });
  }

  selectCourse(courseId: number) {
    this.selectedCourseId = courseId;
    this.matchLoading = true;
    this.matchResults = [];

    this.api.getCourseMatches(courseId).subscribe({
      next: (matches) => {
        // Flatten all result_json.results into one array for display
        this.matchResults = [];
        for (const m of matches) {
          const results = m.result_json?.results || [];
          this.matchResults.push(...results);
        }
        this.matchLoading = false;
      },
      error: () => this.matchLoading = false
    });
  }

  getConfidenceClass(confidence: number): string {
    if (confidence >= 0.85) return 'text-bg-success';
    if (confidence >= 0.5) return 'text-bg-warning';
    if (confidence > 0) return 'text-bg-danger';
    return 'text-bg-secondary';
  }
}
