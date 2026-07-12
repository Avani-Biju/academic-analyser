import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../shared/services/api.service';
import { Course } from '../../shared/models/types';

@Component({
  selector: 'app-course-workspace',
  imports: [CommonModule, RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './course-workspace.html',
  styleUrl: './course-workspace.css'
})
export class CourseWorkspace implements OnInit {
  courseId!: number;
  course: Course | null = null;
  loading = true;

  tabs = [
    { label: 'Overview',         path: 'overview'         },
    { label: 'Syllabus',         path: 'syllabus'         },
    { label: 'Question Papers',  path: 'question-papers'  },
    { label: 'Analysis',         path: 'analysis'         },
    { label: 'AI Study Coach',   path: 'coach'            },
  ];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private api: ApiService
  ) {}

  ngOnInit() {
    this.courseId = Number(this.route.snapshot.paramMap.get('id'));
    this.api.getCourse(this.courseId).subscribe({
      next: (data) => {
        this.course = data;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  tabRoute(path: string): string {
    return `/courses/${this.courseId}/${path}`;
  }
}
