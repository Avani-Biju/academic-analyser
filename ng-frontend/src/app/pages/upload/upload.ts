import { ChangeDetectorRef, Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { finalize } from 'rxjs';
import { ApiService } from '../../shared/services/api.service';

@Component({
  selector: 'app-upload',
  imports: [CommonModule],
  templateUrl: './upload.html',
  styleUrl: './upload.css'
})
export class Upload {
  syllabusFile: File | null = null;
  questionFile: File | null = null;

  syllabusStatus: 'idle' | 'uploading' | 'success' | 'error' = 'idle';
  questionStatus: 'idle' | 'uploading' | 'success' | 'error' = 'idle';

  syllabusResult: any = null;
  questionResult: any = null;

  syllabusError = '';
  questionError = '';

  constructor(
    private api: ApiService,
    private cdr: ChangeDetectorRef
  ) {}

  onSyllabusSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.syllabusFile = input.files[0];
      this.syllabusStatus = 'idle';
      this.syllabusResult = null;
      this.syllabusError = '';
    }
  }

  onQuestionSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.questionFile = input.files[0];
      this.questionStatus = 'idle';
      this.questionResult = null;
      this.questionError = '';
    }
  }

  uploadSyllabus() {
    if (!this.syllabusFile) return;
    this.syllabusStatus = 'uploading';
    this.syllabusError = '';

    this.api.uploadDocument(this.syllabusFile, 'syllabus')
      .pipe(finalize(() => this.cdr.detectChanges()))
      .subscribe({
        next: (res) => {
          console.log('Syllabus upload response:', res);
          this.syllabusStatus = 'success';
          this.syllabusResult = res;
        },
        error: (err) => {
          console.error('Syllabus upload error:', err);
          this.syllabusStatus = 'error';
          this.syllabusError = err.error?.detail || 'Upload failed';
        }
      });
  }

  uploadQuestion() {
    if (!this.questionFile) return;
    this.questionStatus = 'uploading';
    this.questionError = '';

    this.api.uploadDocument(this.questionFile, 'question_paper')
      .pipe(finalize(() => this.cdr.detectChanges()))
      .subscribe({
        next: (res) => {
          console.log('Question paper upload response:', res);
          this.questionStatus = 'success';
          this.questionResult = res;
        },
        error: (err) => {
          console.error('Question paper upload error:', err);
          this.questionStatus = 'error';
          this.questionError = err.error?.detail || 'Upload failed';
        }
      });
  }
}
