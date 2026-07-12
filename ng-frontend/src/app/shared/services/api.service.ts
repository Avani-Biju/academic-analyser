import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Course, Syllabus, QuestionPaper, MatchResult } from '../models/types';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  // Call FastAPI directly - CORS is enabled on the backend.
  // We tried the Angular proxy but the new esbuild dev server doesn't
  // reliably forward multipart/form-data uploads; direct calls with CORS work.
  private baseUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) { }

  // Courses
  getCourses(): Observable<Course[]> {
    return this.http.get<Course[]>(`${this.baseUrl}/courses`);
  }

  getCourse(id: number): Observable<Course> {
    return this.http.get<Course>(`${this.baseUrl}/courses/${id}`);
  }

  updateCourse(id: number, payload: Partial<Course>): Observable<Course> {
    return this.http.patch<Course>(`${this.baseUrl}/courses/${id}`, payload);
  }

  getCourseSyllabus(courseId: number): Observable<Syllabus> {
    return this.http.get<Syllabus>(`${this.baseUrl}/courses/${courseId}/syllabus`);
  }

  updateCourseSyllabus(courseId: number, payload: Partial<Syllabus>): Observable<Syllabus> {
    return this.http.patch<Syllabus>(`${this.baseUrl}/courses/${courseId}/syllabus`, payload);
  }

  getCourseQuestionPapers(courseId: number): Observable<QuestionPaper[]> {
    return this.http.get<QuestionPaper[]>(`${this.baseUrl}/courses/${courseId}/question-papers`);
  }

  getCourseMatches(courseId: number): Observable<MatchResult[]> {
    return this.http.get<MatchResult[]>(`${this.baseUrl}/courses/${courseId}/matches`);
  }

  // Uploads
  uploadDocument(file: File, type: 'syllabus' | 'question_paper'): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('doc_type', type);
    return this.http.post<any>(`${this.baseUrl}/upload`, formData);
  }

  // Matching
  runMatching(syllabusId: number, questionPaperId: number): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/match`, {
      syllabus_id: syllabusId,
      question_paper_id: questionPaperId
    });
  }
}
