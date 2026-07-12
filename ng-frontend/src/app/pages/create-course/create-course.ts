import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import {
  AbstractControl,
  FormArray,
  FormBuilder,
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';
import { finalize, switchMap } from 'rxjs';
import { ApiService } from '../../shared/services/api.service';

interface UploadResponse {
  filename: string;
  message: string;
  course_code: string;
  course_id: number | null;
  syllabus_id: number | null;
  parsed_data: Record<string, any>;
}

@Component({
  selector: 'app-create-course',
  imports: [CommonModule, RouterLink, ReactiveFormsModule],
  templateUrl: './create-course.html',
  styleUrl: './create-course.css'
})
export class CreateCourse implements OnInit {
  readonly maxSteps = 4;
  readonly steps = [
    { number: 1, label: 'Course Details' },
    { number: 2, label: 'Upload Syllabus' },
    { number: 3, label: 'Extract & Review' },
    { number: 4, label: 'Save Course' }
  ];
  currentStep = 1;

  detailsForm!: FormGroup;
  syllabusForm!: FormGroup;

  selectedFile: File | null = null;
  isDragging = false;
  uploading = false;
  saving = false;
  uploadProgress = 0;

  uploadError = '';
  reviewError = '';
  saveError = '';

  parserConfirmed = false;
  uploadedFilename = '';
  uploadedCourseId: number | null = null;
  uploadedSyllabusId: number | null = null;

  constructor(
    private readonly fb: FormBuilder,
    private readonly api: ApiService,
    private readonly router: Router,
    private readonly cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.detailsForm = this.fb.group({
      courseName: ['', Validators.required],
      courseCode: ['', Validators.required],
      semester: ['', Validators.required],
      credits: ['', [Validators.required, Validators.min(1)]],
      department: ['']
    });

    this.initSyllabusForm();
  }

  private initSyllabusForm(): void {
    this.syllabusForm = this.fb.group({
      course_name: ['', Validators.required],
      course_code: ['', Validators.required],
      semester: ['', Validators.required],
      credits: ['', [Validators.required, Validators.min(1)]],
      department: [''],
      course_outcomes: this.fb.array([]),
      modules: this.fb.array([])
    });
  }

  get stepTitle(): string {
    return `Step ${this.currentStep} of ${this.maxSteps}`;
  }

  get courseOutcomes(): FormArray<FormControl<string | null>> {
    return this.syllabusForm.get('course_outcomes') as FormArray<FormControl<string | null>>;
  }

  get modules(): FormArray<FormGroup> {
    return this.syllabusForm.get('modules') as FormArray<FormGroup>;
  }

  getTopics(moduleIndex: number): FormArray<FormControl<string | null>> {
    return this.modules.at(moduleIndex).get('topics') as FormArray<FormControl<string | null>>;
  }

  nextStep(): void {
    if (this.currentStep === 1) {
      if (this.detailsForm.invalid) {
        this.detailsForm.markAllAsTouched();
        return;
      }

      this.seedReviewFormFromDetails();
    }

    if (this.currentStep === 3) {
      if (!this.parserConfirmed) {
        this.reviewError = 'Upload and parser confirmation are required before you can continue.';
        return;
      }

      if (this.syllabusForm.invalid) {
        this.reviewError = 'Please finish the required syllabus details before reviewing the summary.';
        this.syllabusForm.markAllAsTouched();
        return;
      }

      this.reviewError = '';
    }

    if (this.currentStep < this.maxSteps) {
      this.currentStep += 1;
    }
  }

  prevStep(): void {
    if (this.currentStep > 1) {
      this.currentStep -= 1;
    }
  }

  cancel(): void {
    this.router.navigate(['/courses']);
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] ?? null;
    this.handleFile(file);
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.isDragging = true;
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    this.isDragging = false;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.isDragging = false;
    const file = event.dataTransfer?.files?.[0] ?? null;
    this.handleFile(file);
  }

  handleFile(file: File | null): void {
    this.uploadError = '';
    this.saveError = '';

    if (!file) {
      return;
    }

    const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
    if (!isPdf) {
      this.selectedFile = null;
      this.parserConfirmed = false;
      this.uploadedFilename = '';
      this.uploadError = 'Please choose a PDF syllabus file to continue.';
      return;
    }

    this.uploadProgress = 0;
    this.selectedFile = file;
    this.parserConfirmed = false;
    this.uploadedFilename = file.name;
    this.uploadedCourseId = null;
    this.uploadedSyllabusId = null;
    this.uploadSyllabus();
  }

  clearSelectedFile(event?: Event): void {
    event?.stopPropagation();
    this.selectedFile = null;
    this.uploadedFilename = '';
    this.uploadProgress = 0;
    this.uploadError = '';
    this.parserConfirmed = false;
    this.uploadedCourseId = null;
    this.uploadedSyllabusId = null;
  }

  uploadSyllabus(): void {
    if (!this.selectedFile || this.uploading) {
      return;
    }

    this.uploading = true;
    this.uploadError = '';
    this.reviewError = '';
    this.saveError = '';
    this.uploadProgress = 15;

    const progressInterval = setInterval(() => {
      if (this.uploadProgress < 90) {
        this.uploadProgress += 5;
      }
    }, 180);

    this.api.uploadDocument(this.selectedFile, 'syllabus')
      .pipe(finalize(() => {
        clearInterval(progressInterval);
        this.cdr.detectChanges();
      }))
      .subscribe({
        next: (response: UploadResponse) => {
          try {
            this.uploadProgress = 100;
            this.parserConfirmed = true;
            this.uploadedFilename = response.filename;
            this.uploadedCourseId = response.course_id;
            this.uploadedSyllabusId = response.syllabus_id;
            this.populateSyllabusForm(response.parsed_data ?? {});
            this.cdr.detectChanges();

            setTimeout(() => {
              this.uploading = false;
              this.currentStep = 3;
              this.cdr.detectChanges();
            }, 350);
          } catch (error) {
            this.uploading = false;
            this.parserConfirmed = false;
            this.uploadProgress = 0;
            this.uploadError = 'We parsed the PDF response but could not prepare the review screen. Please try again.';
            console.error('Create course upload processing error:', error);
            this.cdr.detectChanges();
          }
        },
        error: (error) => {
          this.uploading = false;
          this.parserConfirmed = false;
          this.uploadProgress = 0;
          this.uploadError = error?.error?.detail || 'We could not parse that PDF. Please try another syllabus file.';
          this.cdr.detectChanges();
        }
      });
  }

  addOutcome(value = ''): void {
    this.courseOutcomes.push(this.fb.control(value, Validators.required));
  }

  removeOutcome(index: number): void {
    this.courseOutcomes.removeAt(index);
  }

  addModule(moduleName = ''): void {
    this.modules.push(
      this.fb.group({
        module_name: [moduleName, Validators.required],
        topics: this.fb.array([])
      })
    );
  }

  removeModule(index: number): void {
    this.modules.removeAt(index);
  }

  addTopic(moduleIndex: number, value = ''): void {
    this.getTopics(moduleIndex).push(this.fb.control(value, Validators.required));
  }

  removeTopic(moduleIndex: number, topicIndex: number): void {
    this.getTopics(moduleIndex).removeAt(topicIndex);
  }

  goToStep(step: number): void {
    if (step >= 1 && step <= this.maxSteps && step < this.currentStep) {
      this.currentStep = step;
    }
  }

  private populateSyllabusForm(parsedData: Record<string, any>): void {
    this.initSyllabusForm();

    this.syllabusForm.patchValue({
      course_name: parsedData['course_name'] || this.detailsForm.value.courseName,
      course_code: parsedData['course_code'] || this.detailsForm.value.courseCode,
      semester: String(parsedData['semester'] || this.detailsForm.value.semester || ''),
      credits: String(parsedData['credits'] || this.detailsForm.value.credits || ''),
      department: parsedData['department'] || this.detailsForm.value.department || ''
    });

    const outcomes = Array.isArray(parsedData['course_outcomes']) ? parsedData['course_outcomes'] : [];
    if (outcomes.length > 0) {
      outcomes.forEach((outcome: string) => this.addOutcome(outcome));
    } else {
      this.addOutcome();
    }

    const modules = Array.isArray(parsedData['modules']) ? parsedData['modules'] : [];
    if (modules.length > 0) {
      modules.forEach((moduleData: Record<string, any>, index: number) => {
        this.addModule(moduleData['module_name'] || moduleData['module_title'] || `Module ${index + 1}`);

        const topics = Array.isArray(moduleData['topics']) ? moduleData['topics'] : [];
        if (topics.length > 0) {
          topics.forEach((topic: string) => this.addTopic(index, topic));
        } else {
          this.addTopic(index);
        }
      });
    } else {
      this.addModule('Module 1');
      this.addTopic(0);
    }
  }

  private seedReviewFormFromDetails(): void {
    this.syllabusForm.patchValue({
      course_name: this.detailsForm.value.courseName,
      course_code: this.detailsForm.value.courseCode,
      semester: this.detailsForm.value.semester,
      credits: this.detailsForm.value.credits,
      department: this.detailsForm.value.department
    });
  }

  saveCourse(): void {
    if (!this.parserConfirmed || !this.uploadedCourseId) {
      this.saveError = 'Please complete syllabus extraction before saving the course.';
      return;
    }

    if (this.syllabusForm.invalid) {
      this.saveError = 'Please review the extracted syllabus and complete the required fields before saving.';
      this.currentStep = 3;
      this.syllabusForm.markAllAsTouched();
      return;
    }

    this.saving = true;
    this.saveError = '';

    const courseId = this.uploadedCourseId;
    const coursePayload = {
      course_name: this.asString(this.syllabusForm.value.course_name),
      course_code: this.asString(this.syllabusForm.value.course_code),
      semester: this.asString(this.syllabusForm.value.semester),
      credits: this.asString(this.syllabusForm.value.credits)
    };

    const syllabusPayload = {
      source_file: this.uploadedFilename || this.selectedFile?.name || 'syllabus.pdf',
      json_data: this.buildSyllabusJson()
    };

    this.api.updateCourse(courseId, coursePayload).pipe(
      switchMap(() => this.api.updateCourseSyllabus(courseId, syllabusPayload)),
      finalize(() => {
        this.saving = false;
      })
    ).subscribe({
      next: () => {
        this.router.navigate(['/courses', courseId]);
      },
      error: (error) => {
        this.saveError = error?.error?.detail || 'We could not save the reviewed course right now. Please try again.';
      }
    });
  }

  buildSyllabusJson(): Record<string, any> {
    const formValue = this.syllabusForm.getRawValue();
    return {
      course_name: this.asString(formValue.course_name),
      course_code: this.asString(formValue.course_code),
      semester: this.asString(formValue.semester),
      credits: this.asString(formValue.credits),
      department: this.asString(formValue.department),
      course_outcomes: (formValue.course_outcomes || []).map((outcome: string) => this.asString(outcome)),
      modules: (formValue.modules || []).map((moduleData: Record<string, any>) => ({
        module_name: this.asString(moduleData['module_name']),
        topics: (moduleData['topics'] || []).map((topic: string) => this.asString(topic))
      }))
    };
  }

  get totalModules(): number {
    return this.modules.length;
  }

  get totalTopics(): number {
    return this.modules.controls.reduce((count, _, index) => count + this.getTopics(index).length, 0);
  }

  get summaryCourseName(): string {
    return this.asString(this.syllabusForm.value.course_name);
  }

  get summaryCourseCode(): string {
    return this.asString(this.syllabusForm.value.course_code);
  }

  controlInvalid(control: AbstractControl | null): boolean {
    return !!control && control.invalid && (control.touched || control.dirty);
  }

  private asString(value: unknown): string {
    return typeof value === 'string' ? value.trim() : String(value ?? '').trim();
  }
}
