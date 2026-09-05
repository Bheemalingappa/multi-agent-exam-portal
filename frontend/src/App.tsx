import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './auth/AuthProvider';
import { ProtectedRoute } from './auth/ProtectedRoute';

import { AuthLayout } from './layouts/AuthLayout';
import { CandidateLayout } from './layouts/CandidateLayout';
import { RecruiterLayout } from './layouts/RecruiterLayout';

import { LandingPage } from './pages/public/LandingPage';
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';

import { CandidateDashboard } from './pages/candidate/CandidateDashboard';
import { ExamDetailPage } from './pages/candidate/ExamDetailPage';
import { CandidateIDEPage } from './pages/candidate/CandidateIDEPage';
import { SubmissionResultPage } from './pages/candidate/SubmissionResultPage';
import { CandidateResultsHistoryPage } from './pages/candidate/CandidateResultsHistoryPage';

import { StudentResultPage } from './pages/candidate/StudentResultPage';

import { RecruiterDashboard } from './pages/recruiter/RecruiterDashboard';
import { RecruiterExamsPage } from './pages/recruiter/RecruiterExamsPage';
import { CreateExamPage } from './pages/recruiter/CreateExamPage';
import { ManageQuestionsPage } from './pages/recruiter/ManageQuestionsPage';
import { LiveMonitorPage } from './pages/recruiter/LiveMonitorPage';
import { RecruiterAnalyticsPage } from './pages/recruiter/RecruiterAnalyticsPage';
import { QuestionPaperGeneratorPage } from './pages/recruiter/QuestionPaperGeneratorPage';
import { TeacherQuestionPapersPage } from './pages/recruiter/TeacherQuestionPapersPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Home & Landing */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/home" element={<LandingPage />} />

            {/* Public Auth Routes */}
            <Route element={<AuthLayout />}>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
            </Route>

            {/* Candidate Protected Routes */}
            <Route element={<ProtectedRoute allowedRoles={['candidate']} />}>
              <Route element={<CandidateLayout />}>
                <Route path="/candidate" element={<CandidateDashboard />} />
                <Route path="/candidate/exams/:examId" element={<ExamDetailPage />} />
                <Route path="/candidate/attempts/:attemptId" element={<CandidateIDEPage />} />
                <Route path="/candidate/attempts/:attemptId/result" element={<StudentResultPage />} />
                <Route path="/candidate/submissions/:submissionId" element={<SubmissionResultPage />} />
                <Route path="/candidate/results" element={<CandidateResultsHistoryPage />} />
              </Route>
            </Route>

            {/* Recruiter Protected Routes */}
            <Route element={<ProtectedRoute allowedRoles={['recruiter', 'admin']} />}>
              <Route element={<RecruiterLayout />}>
                <Route path="/recruiter" element={<RecruiterDashboard />} />
                <Route path="/recruiter/exams" element={<RecruiterExamsPage />} />
                <Route path="/recruiter/exams/create" element={<CreateExamPage />} />
                <Route path="/recruiter/exams/:examId/questions" element={<ManageQuestionsPage />} />
                <Route path="/recruiter/exams/:examId/live" element={<LiveMonitorPage />} />
                <Route path="/recruiter/analytics" element={<RecruiterAnalyticsPage />} />
                <Route path="/recruiter/question-papers" element={<TeacherQuestionPapersPage />} />
                <Route path="/recruiter/question-papers/generate" element={<QuestionPaperGeneratorPage />} />
              </Route>
            </Route>


            {/* Catch-all Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
};
