import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ApiService } from '../../shared/services/api.service';
import { Course, Syllabus, QuestionPaper } from '../../shared/models/types';

@Component({
  selector: 'app-course-details',
  imports: [CommonModule, RouterLink],
  templateUrl: './course-details.html',
  styleUrl: './course-details.css'
})
export class CourseDetails implements OnInit {
  course: Course | null = null;
  syllabus: Syllabus | null = null;
  questionPapers: QuestionPaper[] = [];
  loading = true;
  syllabusModules: any[] = [];

  constructor(private api: ApiService, private route: ActivatedRoute) {}

  ngOnInit() {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.loadCourse(id);
  }

  loadCourse(id: number) {
    this.api.getCourse(id).subscribe({
      next: (course) => {
        this.course = course;
        this.loading = false;
      },
      error: () => this.loading = false
    });

    this.api.getCourseSyllabus(id).subscribe({
      next: (syl) => {
        this.syllabus = syl;
        this.syllabusModules = syl.json_data?.modules || [];
      },
      error: () => {}
    });

    this.api.getCourseQuestionPapers(id).subscribe({
      next: (papers) => this.questionPapers = papers,
      error: () => {}
    });
  }

  runMatching(qpId: number) {
    if (!this.syllabus) return;
    this.api.runMatching(this.syllabus.id, qpId).subscribe({
      next: (result) => {
        alert('Matching complete! Navigate to the Matching page to see results.');
      },
      error: (err) => {
        alert('Matching failed: ' + (err.error?.detail || 'Unknown error'));
      }
    });
  }
}
