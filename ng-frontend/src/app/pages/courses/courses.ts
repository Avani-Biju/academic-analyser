import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../shared/services/api.service';
import { Course } from '../../shared/models/types';

export interface CourseViewModel extends Course {
  progressPercentage: number;
  questionPapersCount: number;
  analysisStatus: 'Completed' | 'Pending' | 'Not Started';
  lastActivity: string;
}

@Component({
  selector: 'app-courses',
  imports: [CommonModule, RouterLink, FormsModule],
  templateUrl: './courses.html',
  styleUrl: './courses.css'
})
export class Courses implements OnInit {
  courses: CourseViewModel[] = [];
  loading = true;
  searchQuery = '';

  skeletonItems = [1, 2, 3, 4];

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.api.getCourses().subscribe({
      next: (data) => {
        try {
          if (Array.isArray(data)) {
            this.courses = data.map(course => this.enrichWithMockData(course));
          } else {
            console.warn('API /courses returned non-array:', data);
            this.courses = [];
          }
        } catch (e) {
          console.error('Error parsing courses data:', e);
          this.courses = [];
        }
        this.loading = false;
      },
      error: (err) => {
        console.error('API /courses error:', err);
        this.loading = false;
      }
    });
  }

  get filteredCourses(): CourseViewModel[] {
    if (!this.searchQuery.trim()) {
      return this.courses;
    }
    const query = this.searchQuery.toLowerCase();
    return this.courses.filter(c => 
      (c.course_name && c.course_name.toLowerCase().includes(query)) ||
      (c.course_code && c.course_code.toLowerCase().includes(query))
    );
  }

  // Deterministic mock data generation based on course ID so it remains stable
  private enrichWithMockData(course: Course): CourseViewModel {
    const id = course.id;
    
    // Pseudo-random progress based on ID
    const progress = (id * 37) % 100;
    
    // Pseudo-random question paper count
    const qpCount = (id * 5) % 8;
    
    // Analysis status
    let status: 'Completed' | 'Pending' | 'Not Started' = 'Not Started';
    if (progress > 80) status = 'Completed';
    else if (progress > 30) status = 'Pending';

    // Last activity
    const activities = ['Today', 'Yesterday', '2 days ago', 'Last week', 'A month ago'];
    const activity = activities[id % activities.length];

    return {
      ...course,
      progressPercentage: progress,
      questionPapersCount: qpCount,
      analysisStatus: status,
      lastActivity: activity
    };
  }
}
