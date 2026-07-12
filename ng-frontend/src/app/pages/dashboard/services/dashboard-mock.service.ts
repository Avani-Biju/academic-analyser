import { Injectable } from '@angular/core';
import { Observable, of, delay } from 'rxjs';

export interface DashboardData {
  studentName: string;
  semester: string;
  continueWorking: {
    courseName: string;
    courseCode: string;
    progressPercentage: number;
    pendingTask: string;
    courseId: number;
  };
  overallProgress: {
    totalCourses: number;
    papersUploaded: number;
    analysesCompleted: number;
    averageScore: number;
  };
  recentActivity: {
    id: number;
    action: string;
    timeAgo: string;
    icon: string;
    iconClass: string;
  }[];
  aiSummary: {
    strongestCourse: string;
    needsAttention: string;
    recommendedTopic: string;
  };
}

@Injectable({
  providedIn: 'root'
})
export class DashboardMockService {
  getDashboardData(): Observable<DashboardData> {
    const mockData: DashboardData = {
      studentName: 'Alex',
      semester: 'Semester 5',
      continueWorking: {
        courseName: 'Data Structures and Algorithms',
        courseCode: 'CS301',
        progressPercentage: 82,
        pendingTask: 'Upload CIE-2 Question Paper',
        courseId: 1
      },
      overallProgress: {
        totalCourses: 6,
        papersUploaded: 14,
        analysesCompleted: 12,
        averageScore: 78
      },
      recentActivity: [
        {
          id: 1,
          action: 'Analysis completed for Database Management',
          timeAgo: '2 hours ago',
          icon: 'activity',
          iconClass: 'text-success'
        },
        {
          id: 2,
          action: 'Added CIE-1 Question Paper for Operating Systems',
          timeAgo: 'Yesterday',
          icon: 'file-text',
          iconClass: 'text-primary'
        },
        {
          id: 3,
          action: 'Uploaded Computer Networks syllabus',
          timeAgo: '2 days ago',
          icon: 'upload',
          iconClass: 'text-secondary'
        },
        {
          id: 4,
          action: 'AI recommendation updated',
          timeAgo: '3 days ago',
          icon: 'zap',
          iconClass: 'text-warning'
        }
      ],
      aiSummary: {
        strongestCourse: 'Mathematics',
        needsAttention: 'Operating Systems',
        recommendedTopic: 'Process Scheduling Algorithms'
      }
    };

    // Simulate network delay
    return of(mockData).pipe(delay(600));
  }
}
