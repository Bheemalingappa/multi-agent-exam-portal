import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  generateQuestionPaperApi,
  saveQuestionPaperApi,
  publishQuestionPaperApi,
  analyzeTopicApi,
  analyzePdfApi,
  GeneratedQuestionPaper,
  QuestionItem,
  SectionConfig,
  AnalyzeTopicResult,
  AnalyzePdfResult,
  GeneratedSection
} from '../../api/questionPapers';
import { assignExamApi } from '../../api/exams';
import { MathRenderer } from '../../components/common/MathRenderer';
import {
  Sparkles,
  Plus,
  Trash2,
  Edit3,
  CheckCircle2,
  Download,
  AlertCircle,
  ArrowLeft,
  ArrowUp,
  ArrowDown,
  Layers,
  Loader2,
  BookOpen,
  Send,
  BookMarked,
  X
} from 'lucide-react';

const CLASS_OPTIONS = Array.from({ length: 12 }, (_, i) => i + 1);
const SUBJECT_OPTIONS = ['Kannada', 'Mathematics', 'Science', 'English', 'Social Studies', 'Physics', 'Chemistry', 'Biology'];
const LANGUAGE_OPTIONS = ['Kannada', 'English'];
const DIFFICULTY_OPTIONS = ['easy', 'medium', 'hard', 'mixed'];
const QUESTION_TYPES = ['MCQ', 'Short Answer', 'Long Answer', 'Numerical Problem'];

const KANNADA_TOPIC_SUGGESTIONS = [
  { name: 'ಸಂಧಿಗಳು', class: 7, desc: 'ಕನ್ನಡ ಸವರ್ಣದೀರ್ಘ, ಗುಣ ಮತ್ತು ಯಣ್ ಸಂಧಿಗಳು' },
  { name: 'ಕನ್ನಡ ವರ್ಣಮಾಲೆ', class: 1, desc: 'ಸ್ವರಗಳು, ವ್ಯಂಜನಗಳು ಮತ್ತು ಯೋಗವಾಹಗಳು' },
  { name: 'ಪದಗಳು ಮತ್ತು ವಾಕ್ಯಗಳು', class: 5, desc: 'ನಾಮಪದ, ಕ್ರಿಯಾಪದ ಮತ್ತು ವಾಕ್ಯ ರಚನೆ' },
  { name: 'ಕುವೆಂಪು ಅವರ ಸಾಹಿತ್ಯ', class: 8, desc: 'ರಾಷ್ಟ್ರಕವಿ ಕುವೆಂಪು ಅವರ ಬದುಕು-ಬರಹ' },
  { name: 'ಕನ್ನಡ ಸಾಹಿತ್ಯ', class: 10, desc: 'ಪಂಪ, ರನ್ನ, ಜನ್ನ ಮತ್ತು ಹಳೆಯಗನ್ನಡ ಕಾವ್ಯಗಳು' },
  { name: 'ಕರ್ನಾಟಕ ಇತಿಹಾಸ', class: 12, desc: 'ಕರ್ನಾಟಕದ ಇತಿಹಾಸ ಮತ್ತು ಸ್ವಾತಂತ್ರ್ಯ ಚಳುವಳಿಗಳು' }
];

export const QuestionPaperGeneratorPage: React.FC = () => {
  const navigate = useNavigate();

  // Source Selection State
  const [sourceType, setSourceType] = useState<'TOPIC_ONLY' | 'PDF_ONLY' | 'PDF_AND_TOPIC'>('TOPIC_ONLY');

  // Form Configuration State
  const [classLevel, setClassLevel] = useState<number>(7);
  const [subject, setSubject] = useState<string>('Kannada');
  const [language, setLanguage] = useState<string>('Kannada');
  const [topic, setTopic] = useState<string>('ಸಂಧಿಗಳು');
  const [exactTopic, setExactTopic] = useState<string>('ಸಂಧಿಗಳು');
  const [difficulty, setDifficulty] = useState<string>('medium');
  const [durationMinutes, setDurationMinutes] = useState<number>(60);
  const [maximumMarks, setMaximumMarks] = useState<number>(50);

  // PDF Document & Analysis State
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [pdfAnalyzing, setPdfAnalyzing] = useState<boolean>(false);
  const [pdfAnalysisResult, setPdfAnalysisResult] = useState<AnalyzePdfResult | null>(null);

  // Topic Analysis State
  const [analyzing, setAnalyzing] = useState<boolean>(false);
  const [analysisResult, setAnalysisResult] = useState<AnalyzeTopicResult | null>(null);

  // Section Builder State
  const [sectionsConfig, setSectionsConfig] = useState<SectionConfig[]>([
    { name: 'Section A — Multiple Choice Questions (MCQ)', question_type: 'MCQ', num_questions: 10, marks_per_question: 5 }
  ]);

  // Generation & Active Paper State
  const [generating, setGenerating] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [activePaper, setActivePaper] = useState<GeneratedQuestionPaper | null>(null);
  const [activeTab, setActiveTab] = useState<'paper' | 'answers'>('paper');

  // Question Editing & Modal State
  const [editingQuestion, setEditingQuestion] = useState<{ secIdx: number; qIdx: number; q: QuestionItem } | null>(null);
  const [showAssignModal, setShowAssignModal] = useState<boolean>(false);
  const [saving, setSaving] = useState<boolean>(false);
  const [publishing, setPublishing] = useState<boolean>(false);
  const [assigning, setAssigning] = useState<boolean>(false);
  const [successMsg, setSuccessMsg] = useState<string>('');

  // Assignment Modal Inputs
  const [assignTargetClass, setAssignTargetClass] = useState<number>(7);
  const [assignStartAt, setAssignStartAt] = useState<string>('');
  const [assignEndAt, setAssignEndAt] = useState<string>('');

  // Marks Validation Calculation
  const totalCalculatedMarks = sectionsConfig.reduce((acc, s) => acc + (s.num_questions * s.marks_per_question), 0);

  // Automatically sync maximumMarks with section configuration calculation
  React.useEffect(() => {
    setMaximumMarks(totalCalculatedMarks);
  }, [totalCalculatedMarks]);

  const isMarksValid = Math.abs(totalCalculatedMarks - maximumMarks) < 0.01;

  // Total Requested Questions Calculation
  const totalRequestedQuestions = sectionsConfig.reduce((acc, s) => acc + (s.num_questions || 0), 0);
  const actualTotalQuestions = activePaper ? activePaper.sections.reduce((acc, s) => acc + (s.questions?.length || 0), 0) : 0;
  const isQuestionCountMatching = activePaper ? actualTotalQuestions === totalRequestedQuestions : true;

  const handleAnalyzeTopic = async () => {
    const targetTopic = exactTopic.trim() || topic.trim();
    if (!targetTopic) {
      setError('Please enter a topic before analyzing.');
      return;
    }
    setError('');
    setAnalyzing(true);
    try {
      const res = await analyzeTopicApi({
        class_level: classLevel,
        subject,
        topic: targetTopic,
        language
      });
      setAnalysisResult(res);
    } catch (err: any) {
      setError(err.message || 'Failed analyzing topic.');
    } finally {
      setAnalyzing(false);
    }
  };

  const handlePdfFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        setError('Please select a valid PDF file.');
        return;
      }
      setPdfFile(file);
      setError('');
      await handleAnalyzePdf(file);
    }
  };

  const handleAnalyzePdf = async (fileToUpload?: File) => {
    const targetFile = fileToUpload || pdfFile;
    if (!targetFile) {
      setError('Please select a PDF document to upload.');
      return;
    }
    setError('');
    setPdfAnalyzing(true);
    try {
      const res = await analyzePdfApi(targetFile);
      setPdfAnalysisResult(res);
      if (res.suggested_topics && res.suggested_topics.length > 0) {
        if (!exactTopic || exactTopic === 'ಸಂಧಿಗಳು') {
          setExactTopic(res.suggested_topics[0]);
          setTopic(res.suggested_topics[0]);
        }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to parse and analyze PDF document.');
    } finally {
      setPdfAnalyzing(false);
    }
  };

  const handleAddSectionConfig = () => {
    setSectionsConfig([
      ...sectionsConfig,
      { name: `ವಿಭಾಗ ${sectionsConfig.length + 1}`, question_type: 'MCQ', num_questions: 2, marks_per_question: 5 }
    ]);
  };

  const handleRemoveSectionConfig = (idx: number) => {
    setSectionsConfig(sectionsConfig.filter((_, i) => i !== idx));
  };

  const handleGenerate = async () => {
    const effectiveExactTopic = exactTopic.trim() || topic.trim();

    if (sourceType === 'TOPIC_ONLY' && !effectiveExactTopic) {
      setError('Validation Error: Please enter an exact topic to test.');
      return;
    }
    if ((sourceType === 'PDF_ONLY' || sourceType === 'PDF_AND_TOPIC') && !pdfAnalysisResult) {
      setError('Validation Error: Please upload and analyze a PDF document first.');
      return;
    }
    if (sourceType === 'PDF_AND_TOPIC' && !effectiveExactTopic) {
      setError('Validation Error: Please enter an exact topic to test from the PDF content.');
      return;
    }
    if (totalRequestedQuestions < 1) {
      setError('Validation Error: Question count must be at least 1 question.');
      return;
    }
    if (totalRequestedQuestions > 100) {
      setError('Validation Error: Maximum 100 questions allowed per question paper.');
      return;
    }
    if (!isMarksValid) {
      setError(`Validation Error: Total section marks (${totalCalculatedMarks} pts) does not equal Maximum Marks (${maximumMarks} pts). Please adjust section question count or marks.`);
      return;
    }

    setError('');
    setGenerating(true);
    setSuccessMsg('');

    try {
      const generated = await generateQuestionPaperApi({
        class_level: classLevel,
        subject,
        topic: effectiveExactTopic,
        exact_topic: effectiveExactTopic,
        source_type: sourceType,
        source_document_id: pdfAnalysisResult?.document_id,
        source_context: pdfAnalysisResult?.source_context,
        language,
        difficulty,
        duration_minutes: durationMinutes,
        maximum_marks: maximumMarks,
        sections: sectionsConfig
      });

      const totalGeneratedQuestions = generated.sections.reduce((acc, s) => acc + (s.questions?.length || 0), 0);
      if (totalGeneratedQuestions !== totalRequestedQuestions) {
        setError(`Question generation returned ${totalGeneratedQuestions} of ${totalRequestedQuestions} requested questions. Please try again.`);
        return;
      }

      setActivePaper(generated);
      setAssignTargetClass(generated.class_level);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed generating question paper.');
    } finally {
      setGenerating(false);
    }
  };

  const handleSaveDraft = async () => {
    if (!activePaper) return;
    setSaving(true);
    setError('');
    try {
      const saved = await saveQuestionPaperApi({
        ...activePaper,
        status: 'DRAFT'
      });
      setSuccessMsg('Question paper draft saved successfully!');
      if (saved.id) {
        setActivePaper({ ...activePaper, id: saved.id, status: 'DRAFT' });
      }
    } catch (err: any) {
      setError(err.message || 'Failed to save question paper draft.');
    } finally {
      setSaving(false);
    }
  };

  const handlePublishOnly = async () => {
    if (!activePaper) return;
    if (!isQuestionCountMatching) {
      setError(`Question Count Mismatch: Current paper contains ${actualTotalQuestions} questions, but requested count is ${totalRequestedQuestions}. Please add or delete questions to match before publishing.`);
      return;
    }
    setPublishing(true);
    setError('');
    try {
      let paperId = activePaper.id;
      if (!paperId) {
        const saved = await saveQuestionPaperApi({ ...activePaper, status: 'DRAFT' });
        paperId = saved.id;
      }

      const published = await publishQuestionPaperApi(paperId!, activePaper.class_level);
      setSuccessMsg('✨ Question paper published successfully! Click "Assign Exam" to schedule it for students.');
      if (published.published_exam_id) {
        setActivePaper({
          ...activePaper,
          id: paperId,
          status: 'PUBLISHED',
          published_exam_id: published.published_exam_id
        });
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to publish question paper.');
    } finally {
      setPublishing(false);
    }
  };

  const handleConfirmAssign = async () => {
    if (!activePaper) return;
    setAssigning(true);
    setError('');
    try {
      let examId = activePaper.published_exam_id;
      let paperId = activePaper.id;

      if (!paperId) {
        const saved = await saveQuestionPaperApi({ ...activePaper, status: 'DRAFT' });
        paperId = saved.id;
      }

      if (!examId) {
        const published = await publishQuestionPaperApi(paperId!, assignTargetClass);
        examId = published.published_exam_id;
      }

      if (examId) {
        await assignExamApi(examId, assignTargetClass, assignStartAt || undefined, assignEndAt || undefined);
        setSuccessMsg(`✨ Exam assigned successfully to Class ${assignTargetClass}! Students of Class ${assignTargetClass} can now view & attempt the exam.`);
        setShowAssignModal(false);
        setActivePaper({
          ...activePaper,
          id: paperId,
          status: 'ASSIGNED',
          published_exam_id: examId
        });
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed assigning exam to class.');
    } finally {
      setAssigning(false);
    }
  };

  const reindexQuestions = (sections: GeneratedSection[]): GeneratedSection[] => {
    let counter = 1;
    return sections.map(sec => ({
      ...sec,
      num_questions: sec.questions.length,
      section_total_marks: sec.questions.length * sec.marks_per_question,
      questions: sec.questions.map(q => ({
        ...q,
        number: counter++
      }))
    }));
  };

  const handleDeleteQuestion = (secIdx: number, qIdx: number) => {
    if (!activePaper) return;
    const newSections = activePaper.sections.map((sec, sI) => {
      if (sI !== secIdx) return sec;
      const updatedQs = sec.questions.filter((_, qI) => qI !== qIdx);
      return { ...sec, questions: updatedQs };
    });
    const reindexed = reindexQuestions(newSections);
    setActivePaper({ ...activePaper, sections: reindexed });
  };

  const handleMoveQuestion = (secIdx: number, qIdx: number, direction: 'up' | 'down') => {
    if (!activePaper) return;
    const targetIdx = direction === 'up' ? qIdx - 1 : qIdx + 1;
    const secQuestions = activePaper.sections[secIdx].questions;
    if (targetIdx < 0 || targetIdx >= secQuestions.length) return;

    const newSections = activePaper.sections.map((sec, sI) => {
      if (sI !== secIdx) return sec;
      const qs = [...sec.questions];
      const temp = qs[qIdx];
      qs[qIdx] = qs[targetIdx];
      qs[targetIdx] = temp;
      return { ...sec, questions: qs };
    });
    const reindexed = reindexQuestions(newSections);
    setActivePaper({ ...activePaper, sections: reindexed });
  };

  const handleAddQuestion = (secIdx: number) => {
    if (!activePaper) return;
    const sec = activePaper.sections[secIdx];
    const isMcq = sec.question_type === 'MCQ';
    const newQ: QuestionItem = {
      number: 0,
      question: 'New question text...',
      options: isMcq ? ['Option A', 'Option B', 'Option C', 'Option D'] : [],
      correct_answer: isMcq ? 'Option A' : 'Expected answer text',
      marks: sec.marks_per_question || 5,
      explanation: 'Explanation for correct answer',
      step_by_step_solution: 'Step 1: ...\nStep 2: ...'
    };
    const newSections = activePaper.sections.map((s, sI) => {
      if (sI !== secIdx) return s;
      return { ...s, questions: [...s.questions, newQ] };
    });
    const reindexed = reindexQuestions(newSections);
    setActivePaper({ ...activePaper, sections: reindexed });
  };

  const handleUpdateQuestion = () => {
    if (!editingQuestion || !activePaper) return;
    const { secIdx, qIdx, q } = editingQuestion;
    const newSections = activePaper.sections.map((sec, sI) => {
      if (sI !== secIdx) return sec;
      const updatedQs = sec.questions.map((oldQ, qI) => qI === qIdx ? q : oldQ);
      return { ...sec, questions: updatedQs };
    });
    setActivePaper({ ...activePaper, sections: newSections });
    setEditingQuestion(null);
  };

  const handleDownloadPaperPDF = () => {
    if (!activePaper) return;
    window.print();
  };

  const handleDownloadAnswerKeyPDF = () => {
    if (!activePaper) return;
    setActiveTab('answers');
    setTimeout(() => window.print(), 200);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-3 sm:p-8 space-y-6 sm:space-y-8">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <button
            onClick={() => navigate('/recruiter')}
            className="text-xs font-semibold text-slate-400 hover:text-amber-400 flex items-center gap-1.5 mb-2 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Educator Portal
          </button>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-white flex items-center gap-3">
            <Sparkles className="w-8 h-8 text-amber-400 animate-pulse" />
            AI Question Paper Generator
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Classes 1–12 Examination Creator with Kannada Medium Support & Multi-Source Intelligence
          </p>
        </div>

        {activePaper && (
          <div className="flex items-center gap-3">
            <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
              activePaper.status === 'ASSIGNED'
                ? 'bg-teal-500/20 text-teal-300 border border-teal-500/30'
                : activePaper.status === 'PUBLISHED'
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
            }`}>
              {activePaper.status || 'DRAFT'}
            </span>
          </div>
        )}
      </div>

      {/* Error & Success Banners */}
      {error && (
        <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-semibold flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={() => setError('')} className="text-rose-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {successMsg && (
        <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>{successMsg}</span>
          </div>
          <button onClick={() => setSuccessMsg('')} className="text-emerald-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Main Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Form & Configuration */}
        <div className="lg:col-span-5 space-y-6">

          {/* SOURCE MODE SELECTION TABS */}
          <div className="bg-slate-900/90 p-5 rounded-3xl border border-slate-800 space-y-3 shadow-xl">
            <label className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Layers className="w-4 h-4 text-amber-400" /> Question Generation Source Mode
            </label>
            <div className="grid grid-cols-3 gap-2 p-1.5 rounded-2xl bg-slate-950 border border-slate-800">
              <button
                type="button"
                onClick={() => setSourceType('TOPIC_ONLY')}
                className={`py-2.5 px-2 rounded-xl text-[11px] font-bold transition-all flex flex-col sm:flex-row items-center justify-center gap-1.5 ${
                  sourceType === 'TOPIC_ONLY'
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-md'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <BookOpen className="w-4 h-4 text-amber-400" />
                <span>Exact Topic</span>
              </button>
              <button
                type="button"
                onClick={() => setSourceType('PDF_ONLY')}
                className={`py-2.5 px-2 rounded-xl text-[11px] font-bold transition-all flex flex-col sm:flex-row items-center justify-center gap-1.5 ${
                  sourceType === 'PDF_ONLY'
                    ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40 shadow-md'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <BookMarked className="w-4 h-4 text-sky-400" />
                <span>PDF Document</span>
              </button>
              <button
                type="button"
                onClick={() => setSourceType('PDF_AND_TOPIC')}
                className={`py-2.5 px-2 rounded-xl text-[11px] font-bold transition-all flex flex-col sm:flex-row items-center justify-center gap-1.5 ${
                  sourceType === 'PDF_AND_TOPIC'
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-md'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <Layers className="w-4 h-4 text-emerald-400" />
                <span>PDF + Topic</span>
              </button>
            </div>
          </div>

          {/* Form Inputs */}
          <div className="bg-slate-900/90 p-4 sm:p-6 rounded-3xl border border-slate-800 space-y-4 shadow-xl">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Class Level</label>
                <select
                  value={classLevel}
                  onChange={(e) => setClassLevel(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-white font-bold"
                >
                  {CLASS_OPTIONS.map((c) => (
                    <option key={c} value={c}>Class {c}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Subject</label>
                <select
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-white font-bold"
                >
                  {SUBJECT_OPTIONS.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Medium / Language</label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-amber-300 font-bold"
                >
                  {LANGUAGE_OPTIONS.map((l) => (
                    <option key={l} value={l}>{l}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Difficulty</label>
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-white capitalize font-bold"
                >
                  {DIFFICULTY_OPTIONS.map((d) => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Exact Topic Input */}
            {(sourceType === 'TOPIC_ONLY' || sourceType === 'PDF_AND_TOPIC') && (
              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-xs font-semibold text-slate-300">Exact Topic to Test</label>
                  <button
                    type="button"
                    onClick={handleAnalyzeTopic}
                    disabled={analyzing}
                    className="text-[10px] text-amber-400 hover:text-amber-300 flex items-center gap-1 font-bold"
                  >
                    {analyzing ? <Loader2 className="w-3 h-3 animate-spin" /> : <><Sparkles className="w-3 h-3" /> Analyze Topic</>}
                  </button>
                </div>
                <input
                  type="text"
                  value={exactTopic}
                  onChange={(e) => {
                    setExactTopic(e.target.value);
                    setTopic(e.target.value);
                  }}
                  placeholder="e.g. Photosynthesis, Quadratic Equations, ಕನ್ನಡ ಸಂಧಿಗಳು"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white font-medium"
                />

                {/* Kannada Suggestions */}
                {language.toLowerCase() === 'kannada' && (
                  <div className="mt-2.5 space-y-1">
                    <span className="text-[10px] font-bold text-slate-400">Popular Kannada Topics:</span>
                    <div className="flex flex-wrap gap-1.5">
                      {KANNADA_TOPIC_SUGGESTIONS.map((sug, i) => (
                        <button
                          key={i}
                          type="button"
                          onClick={() => {
                            setExactTopic(sug.name);
                            setTopic(sug.name);
                          }}
                          className="px-2 py-1 rounded-lg bg-slate-950 border border-slate-800 hover:border-amber-500/40 text-[10px] text-amber-300 transition-colors"
                        >
                          {sug.name}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* PDF Upload Component */}
            {(sourceType === 'PDF_ONLY' || sourceType === 'PDF_AND_TOPIC') && (
              <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                <label className="block text-xs font-bold text-slate-300">Upload PDF Context Document</label>
                <input
                  type="file"
                  accept="application/pdf"
                  onChange={handlePdfFileSelect}
                  className="w-full text-xs text-slate-400 file:mr-3 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-sky-500/20 file:text-sky-300 hover:file:bg-sky-500/30 cursor-pointer"
                />
                {pdfAnalyzing && (
                  <div className="flex items-center gap-2 text-xs text-sky-400">
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Analyzing PDF context...</span>
                  </div>
                )}
                {pdfAnalysisResult && (
                  <div className="p-2.5 rounded-xl bg-sky-950/40 border border-sky-500/20 text-[11px] text-sky-300 space-y-1">
                    <div><strong>PDF Document:</strong> {pdfAnalysisResult.filename} ({pdfAnalysisResult.page_count} Pages)</div>
                    <div className="text-slate-400">{pdfAnalysisResult.summary}</div>
                  </div>
                )}
              </div>
            )}

            {/* Duration & Maximum Marks */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Duration (Minutes)</label>
                <input
                  type="number"
                  value={durationMinutes}
                  onChange={(e) => setDurationMinutes(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-white font-bold"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Maximum Marks</label>
                <input
                  type="number"
                  value={maximumMarks}
                  readOnly
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-emerald-400 font-bold bg-slate-950/50"
                />
              </div>
            </div>
          </div>

          {/* Section Builder */}
          <div className="bg-slate-900/90 p-4 sm:p-6 rounded-3xl border border-slate-800 space-y-4 shadow-xl">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <Layers className="w-4 h-4 text-indigo-400" /> Section Configuration
              </label>
              <button
                type="button"
                onClick={handleAddSectionConfig}
                className="text-[11px] font-bold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" /> Add Section
              </button>
            </div>

            {sectionsConfig.map((sec, idx) => (
              <div key={idx} className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-3 relative">
                <div className="flex justify-between items-center">
                  <input
                    type="text"
                    value={sec.name}
                    onChange={(e) => {
                      const updated = [...sectionsConfig];
                      updated[idx].name = e.target.value;
                      setSectionsConfig(updated);
                    }}
                    className="bg-transparent text-xs font-bold text-white border-b border-slate-800 focus:border-indigo-500 pb-1"
                  />
                  {sectionsConfig.length > 1 && (
                    <button
                      type="button"
                      onClick={() => handleRemoveSectionConfig(idx)}
                      className="text-slate-500 hover:text-rose-400"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>

                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div>
                    <label className="block text-[10px] text-slate-400">Type</label>
                    <select
                      value={sec.question_type}
                      onChange={(e) => {
                        const updated = [...sectionsConfig];
                        updated[idx].question_type = e.target.value;
                        setSectionsConfig(updated);
                      }}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-slate-200 text-[11px]"
                    >
                      {QUESTION_TYPES.map((t) => (
                        <option key={t} value={t}>{t}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-[10px] text-slate-400">Questions</label>
                    <input
                      type="number"
                      min={1}
                      max={100}
                      value={sec.num_questions}
                      onChange={(e) => {
                        const updated = [...sectionsConfig];
                        updated[idx].num_questions = Number(e.target.value);
                        setSectionsConfig(updated);
                      }}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-white font-bold text-[11px]"
                    />
                  </div>

                  <div>
                    <label className="block text-[10px] text-slate-400">Marks/Q</label>
                    <input
                      type="number"
                      step={0.5}
                      value={sec.marks_per_question}
                      onChange={(e) => {
                        const updated = [...sectionsConfig];
                        updated[idx].marks_per_question = Number(e.target.value);
                        setSectionsConfig(updated);
                      }}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-emerald-400 font-bold text-[11px]"
                    />
                  </div>
                </div>
              </div>
            ))}

            <div className="pt-2 flex justify-between items-center text-xs font-bold text-slate-400 border-t border-slate-800">
              <span>Total Questions: <strong className="text-white">{totalRequestedQuestions}</strong></span>
              <span>Total Calculated: <strong className="text-emerald-400">{totalCalculatedMarks} Marks</strong></span>
            </div>
          </div>

          {/* Submit / Generate Button */}
          <button
            type="button"
            disabled={generating}
            onClick={handleGenerate}
            className="w-full py-4 rounded-2xl bg-gradient-to-r from-amber-500 via-indigo-600 to-emerald-600 hover:from-amber-400 hover:to-emerald-500 text-slate-950 font-black text-sm tracking-wide shadow-xl shadow-indigo-600/25 flex items-center justify-center gap-2 disabled:opacity-50 transition-all"
          >
            {generating ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin text-slate-950" />
                <span>Synthesizing Exam Paper...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5 text-slate-950" />
                <span>Generate Exam Paper</span>
              </>
            )}
          </button>
        </div>

        {/* Right Column: Question Paper Preview & Interactive Editor */}
        <div className="lg:col-span-7 space-y-6">
          {/* Topic Analysis Results Card */}
          {analysisResult && (
            <div className="bg-slate-900/90 rounded-3xl border border-slate-800 p-5 space-y-3 shadow-xl">
              <h3 className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-2">
                <Sparkles className="w-4 h-4" /> Educational Topic Intelligence: {analysisResult.topic}
              </h3>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3 rounded-2xl bg-slate-950 border border-slate-800">
                  <strong className="text-slate-300 block mb-1">Key Concepts:</strong>
                  <ul className="list-disc list-inside text-slate-400 space-y-1">
                    {analysisResult.key_concepts.map((kc, i) => (
                      <li key={i}>{kc}</li>
                    ))}
                  </ul>
                </div>
                <div className="p-3 rounded-2xl bg-slate-950 border border-slate-800">
                  <strong className="text-slate-300 block mb-1">Question Areas:</strong>
                  <ul className="list-disc list-inside text-slate-400 space-y-1">
                    {analysisResult.question_areas.map((qa, i) => (
                      <li key={i}>{qa}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {activePaper ? (
            <div className="bg-slate-900/90 rounded-3xl border border-slate-800 p-6 space-y-6 shadow-xl">
              {/* Paper Header Bar */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
                <div>
                  <span className="text-[10px] font-bold px-2.5 py-1 rounded-md bg-amber-500/20 text-amber-300 border border-amber-500/30 uppercase tracking-wider">
                    Class {activePaper.class_level} • {activePaper.subject} ({activePaper.language || language})
                  </span>
                  <h2 className="text-xl font-black text-white mt-1.5">{activePaper.title}</h2>
                  <p className="text-xs text-slate-400">
                    Exact Topic: {activePaper.exact_topic || activePaper.topic} | Time: {activePaper.duration_minutes} Mins | Max Marks: {activePaper.maximum_marks}
                  </p>
                  <div className="mt-1.5 flex items-center gap-2">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                      activePaper.generation_provider === 'GEMINI' || activePaper.generation_provider === 'AWS_BEDROCK'
                        ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
                        : 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                    }`}>
                      {activePaper.generation_provider === 'GEMINI'
                        ? '✨ AI Provider: Google Gemini'
                        : activePaper.generation_provider === 'AWS_BEDROCK'
                        ? '⚡ AI Provider: AWS Bedrock'
                        : '⚙️ Provider: Deterministic Fallback Engine'}
                    </span>
                    {activePaper.source_type && (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/30">
                        Mode: {activePaper.source_type}
                      </span>
                    )}
                  </div>
                </div>

                {/* PDF & Publish Actions */}
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={handleDownloadPaperPDF}
                    className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold flex items-center gap-1.5 border border-slate-700"
                  >
                    <Download className="w-3.5 h-3.5 text-emerald-400" /> Paper PDF
                  </button>
                  <button
                    onClick={handleDownloadAnswerKeyPDF}
                    className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold flex items-center gap-1.5 border border-slate-700"
                  >
                    <Download className="w-3.5 h-3.5 text-sky-400" /> Solutions PDF
                  </button>
                  <button
                    onClick={handleSaveDraft}
                    disabled={saving}
                    className="px-3 py-2 rounded-xl bg-indigo-600/30 hover:bg-indigo-600/40 text-indigo-300 text-xs font-semibold flex items-center gap-1.5 border border-indigo-500/40"
                  >
                    {saving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Save Draft'}
                  </button>
                  <button
                    onClick={handlePublishOnly}
                    disabled={publishing}
                    className="px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold flex items-center gap-1.5 shadow-md shadow-indigo-600/20"
                  >
                    {publishing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <><CheckCircle2 className="w-3.5 h-3.5" /> Publish Paper</>}
                  </button>
                  <button
                    onClick={() => setShowAssignModal(true)}
                    className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white text-xs font-bold shadow-lg shadow-emerald-500/20 flex items-center gap-1.5"
                  >
                    <Send className="w-3.5 h-3.5" /> Assign Exam
                  </button>
                </div>
              </div>

              {/* Question Count Mismatch Warning Banner */}
              {!isQuestionCountMatching && (
                <div className="p-3.5 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-semibold flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    <span>
                      Question Count Mismatch: Current paper has <strong>{actualTotalQuestions}</strong> questions, but exact requested count is <strong>{totalRequestedQuestions}</strong>. Please add or delete questions to match before publishing.
                    </span>
                  </div>
                </div>
              )}

              {/* Tabs: Question Paper vs Answer Key */}
              <div className="flex border-b border-slate-800 gap-4">
                <button
                  onClick={() => setActiveTab('paper')}
                  className={`pb-3 text-xs font-bold border-b-2 transition-colors flex items-center gap-2 ${
                    activeTab === 'paper' ? 'border-amber-400 text-amber-400' : 'border-transparent text-slate-400 hover:text-white'
                  }`}
                >
                  <BookOpen className="w-4 h-4" /> QUESTION PAPER REVIEW ({actualTotalQuestions} Questions)
                </button>
                <button
                  onClick={() => setActiveTab('answers')}
                  className={`pb-3 text-xs font-bold border-b-2 transition-colors flex items-center gap-2 ${
                    activeTab === 'answers' ? 'border-sky-400 text-sky-400' : 'border-transparent text-slate-400 hover:text-white'
                  }`}
                >
                  <CheckCircle2 className="w-4 h-4" /> ANSWER KEY & SOLUTIONS
                </button>
              </div>

              {/* Tab 1: Question Paper View */}
              {activeTab === 'paper' && (
                <div className="space-y-6 font-sans text-slate-200">
                  <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 text-xs space-y-1">
                    <strong className="text-slate-300">General Instructions:</strong>
                    <div className="text-slate-400 whitespace-pre-line">{activePaper.instructions}</div>
                  </div>

                  {activePaper.sections.map((sec, secIdx) => (
                    <div key={secIdx} className="space-y-4">
                      <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                        <h3 className="text-sm font-bold text-amber-300 uppercase tracking-wider">
                          {sec.name} ({sec.questions.length} Questions × {sec.marks_per_question} Marks = {sec.questions.length * sec.marks_per_question} Marks)
                        </h3>
                        <button
                          type="button"
                          onClick={() => handleAddQuestion(secIdx)}
                          className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-amber-400 text-xs font-semibold flex items-center gap-1 border border-slate-700"
                        >
                          <Plus className="w-3.5 h-3.5" /> Add Question
                        </button>
                      </div>

                      <div className="space-y-4">
                        {sec.questions.map((q, qIdx) => (
                          <div key={qIdx} className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-3 relative group">
                            <div className="flex items-start justify-between gap-4">
                              <div className="flex items-start gap-3">
                                <span className="w-6 h-6 rounded-lg bg-amber-500/10 text-amber-400 text-xs font-bold flex items-center justify-center shrink-0 border border-amber-500/20">
                                  Q{q.number}
                                </span>
                                <div>
                                  <MathRenderer content={q.question} className="text-xs font-bold text-white" />
                                  <span className="text-[10px] text-slate-400">[{q.marks} Marks]</span>
                                </div>
                              </div>

                              <div className="flex items-center gap-1 opacity-90 group-hover:opacity-100 transition-opacity">
                                <button
                                  type="button"
                                  onClick={() => handleMoveQuestion(secIdx, qIdx, 'up')}
                                  disabled={qIdx === 0}
                                  className="p-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30"
                                  title="Move Up"
                                >
                                  <ArrowUp className="w-3.5 h-3.5" />
                                </button>
                                <button
                                  type="button"
                                  onClick={() => handleMoveQuestion(secIdx, qIdx, 'down')}
                                  disabled={qIdx === sec.questions.length - 1}
                                  className="p-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30"
                                  title="Move Down"
                                >
                                  <ArrowDown className="w-3.5 h-3.5" />
                                </button>
                                <button
                                  type="button"
                                  onClick={() => setEditingQuestion({ secIdx, qIdx, q: { ...q } })}
                                  className="p-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white"
                                  title="Edit Question"
                                >
                                  <Edit3 className="w-3.5 h-3.5" />
                                </button>
                                <button
                                  type="button"
                                  onClick={() => handleDeleteQuestion(secIdx, qIdx)}
                                  className="p-1 rounded-lg bg-slate-800 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400"
                                  title="Delete Question"
                                >
                                  <Trash2 className="w-3.5 h-3.5" />
                                </button>
                              </div>
                            </div>

                            {/* Options for MCQ */}
                            {q.options && q.options.length > 0 && (
                              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pl-9">
                                {q.options.map((opt, oIdx) => (
                                  <div key={oIdx} className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-xs flex items-center gap-2">
                                    <span className="w-5 h-5 rounded-md bg-slate-800 text-slate-400 text-[10px] font-bold flex items-center justify-center shrink-0">
                                      {String.fromCharCode(65 + oIdx)}
                                    </span>
                                    <MathRenderer content={opt} className="text-slate-300" />
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Tab 2: Answer Key & Solutions View */}
              {activeTab === 'answers' && (
                <div className="space-y-6 font-sans text-slate-200">
                  {activePaper.sections.map((sec, secIdx) => (
                    <div key={secIdx} className="space-y-4">
                      <h3 className="text-sm font-bold text-sky-300 uppercase tracking-wider border-b border-slate-800 pb-2">
                        {sec.name} — Answer Key & Detailed Solutions
                      </h3>

                      <div className="space-y-4">
                        {sec.questions.map((q, qIdx) => (
                          <div key={qIdx} className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                            <div className="flex items-center gap-2">
                              <span className="w-6 h-6 rounded-lg bg-sky-500/10 text-sky-400 text-xs font-bold flex items-center justify-center shrink-0 border border-sky-500/20">
                                Q{q.number}
                              </span>
                              <MathRenderer content={q.question} className="text-xs font-bold text-white" />
                            </div>

                            <div className="p-3 rounded-xl bg-sky-950/40 border border-sky-500/20 text-xs space-y-1.5 pl-4">
                              <div className="text-sky-300 font-bold">
                                Correct Answer: <span className="text-emerald-400">{q.correct_answer}</span>
                              </div>
                              {q.explanation && (
                                <div className="text-slate-300">
                                  <strong>Explanation:</strong> <MathRenderer content={q.explanation} />
                                </div>
                              )}
                              {q.step_by_step_solution && (
                                <div className="text-slate-400 whitespace-pre-line text-[11px] pt-1 border-t border-sky-500/20">
                                  <strong>Step-by-Step Solution:</strong>
                                  <MathRenderer content={q.step_by_step_solution} />
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="bg-slate-900/90 rounded-3xl border border-slate-800 p-12 text-center space-y-4 shadow-xl">
              <BookMarked className="w-16 h-16 text-slate-700 mx-auto" />
              <h3 className="text-lg font-bold text-white">No Exam Paper Generated Yet</h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                Select your preferred source mode (Exact Topic, PDF Document, or PDF + Topic), configure sections, and click "Generate Exam Paper" to synthesize question paper with solutions.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Edit Question Modal */}
      {editingQuestion && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 rounded-3xl border border-slate-800 p-6 max-w-lg w-[calc(100vw-24px)] max-h-[90vh] overflow-y-auto space-y-4 shadow-2xl">
            <h3 className="text-sm font-bold text-white">Edit Question #{editingQuestion.q.number}</h3>

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Question Text</label>
              <textarea
                rows={3}
                value={editingQuestion.q.question}
                onChange={(e) => setEditingQuestion({
                  ...editingQuestion,
                  q: { ...editingQuestion.q, question: e.target.value }
                })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white"
              />
            </div>

            {/* MCQ Options Editing */}
            {editingQuestion.q.options && editingQuestion.q.options.length > 0 && (
              <div className="space-y-2">
                <label className="block text-xs font-semibold text-slate-400">MCQ Options</label>
                {editingQuestion.q.options.map((opt, oI) => (
                  <div key={oI} className="flex items-center gap-2">
                    <span className="w-6 text-xs font-bold text-amber-400">{String.fromCharCode(65 + oI)}:</span>
                    <input
                      type="text"
                      value={opt}
                      onChange={(e) => {
                        const newOpts = [...(editingQuestion.q.options || [])];
                        newOpts[oI] = e.target.value;
                        setEditingQuestion({
                          ...editingQuestion,
                          q: { ...editingQuestion.q, options: newOpts }
                        });
                      }}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-xs text-white"
                    />
                  </div>
                ))}
              </div>
            )}

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Correct Answer</label>
                <input
                  type="text"
                  value={editingQuestion.q.correct_answer}
                  onChange={(e) => setEditingQuestion({
                    ...editingQuestion,
                    q: { ...editingQuestion.q, correct_answer: e.target.value }
                  })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Marks</label>
                <input
                  type="number"
                  value={editingQuestion.q.marks}
                  onChange={(e) => setEditingQuestion({
                    ...editingQuestion,
                    q: { ...editingQuestion.q, marks: Number(e.target.value) }
                  })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-emerald-400 font-bold"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Explanation</label>
              <textarea
                rows={2}
                value={editingQuestion.q.explanation || ''}
                onChange={(e) => setEditingQuestion({
                  ...editingQuestion,
                  q: { ...editingQuestion.q, explanation: e.target.value }
                })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Step-by-Step Solution</label>
              <textarea
                rows={3}
                value={editingQuestion.q.step_by_step_solution || ''}
                onChange={(e) => setEditingQuestion({
                  ...editingQuestion,
                  q: { ...editingQuestion.q, step_by_step_solution: e.target.value }
                })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setEditingQuestion(null)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={handleUpdateQuestion}
                className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-bold"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Assign Exam Modal */}
      {showAssignModal && activePaper && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 rounded-3xl border border-slate-800 p-6 max-w-md w-[calc(100vw-24px)] max-h-[90vh] overflow-y-auto space-y-4 shadow-2xl">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Send className="w-4 h-4 text-emerald-400" /> Assign Exam to Student Class
            </h3>

            <p className="text-xs text-slate-400">
              Assigning this exam will make it active for students of the selected class. Students will see this exam on their portal dashboard and can start attempts.
            </p>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Target Class Level</label>
                <select
                  value={assignTargetClass}
                  onChange={(e) => setAssignTargetClass(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white font-bold"
                >
                  {CLASS_OPTIONS.map((c) => (
                    <option key={c} value={c}>Class {c}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Start Date/Time (Optional)</label>
                  <input
                    type="datetime-local"
                    value={assignStartAt}
                    onChange={(e) => setAssignStartAt(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-white"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">End Date/Time (Optional)</label>
                  <input
                    type="datetime-local"
                    value={assignEndAt}
                    onChange={(e) => setAssignEndAt(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-white"
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setShowAssignModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                disabled={assigning}
                onClick={handleConfirmAssign}
                className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white text-xs font-bold flex items-center gap-1.5"
              >
                {assigning ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Confirm Assignment'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
