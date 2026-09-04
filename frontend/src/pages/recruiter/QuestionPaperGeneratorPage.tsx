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
  AnalyzePdfResult
} from '../../api/questionPapers';
import { MathRenderer } from '../../components/common/MathRenderer';
import {
  Sparkles,
  Plus,
  Trash2,
  Edit3,
  CheckCircle2,
  Download,
  RefreshCw,
  AlertCircle,
  Eye,
  ArrowLeft,
  Layers,
  Settings,
  Loader2,
  Globe,
  BookOpen,
  Send,
  Search,
  BookMarked,
  CheckSquare,
  X,
  FileText,
  UploadCloud,
  FileCheck
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
  const [successMsg, setSuccessMsg] = useState<string>('');

  // Marks Validation Calculation
  const totalCalculatedMarks = sectionsConfig.reduce((acc, s) => acc + (s.num_questions * s.marks_per_question), 0);

  // Automatically sync maximumMarks with section configuration calculation
  React.useEffect(() => {
    setMaximumMarks(totalCalculatedMarks);
  }, [totalCalculatedMarks]);

  const isMarksValid = Math.abs(totalCalculatedMarks - maximumMarks) < 0.01;

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

  // Total Requested Questions Calculation
  const totalRequestedQuestions = sectionsConfig.reduce((acc, s) => acc + (s.num_questions || 0), 0);

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
        setActivePaper({ ...activePaper, id: saved.id });
      }
    } catch (err: any) {
      setError(err.message || 'Failed to save question paper draft.');
    } finally {
      setSaving(false);
    }
  };

  const handlePublishAndAssign = async (targetClass: number) => {
    if (!activePaper) return;
    setPublishing(true);
    setError('');
    try {
      let paperId = activePaper.id;
      if (!paperId) {
        const saved = await saveQuestionPaperApi({ ...activePaper, status: 'DRAFT' });
        paperId = saved.id;
      }

      const published = await publishQuestionPaperApi(paperId!, targetClass);
      setSuccessMsg(`Exam published & assigned to Class ${targetClass} successfully!`);
      setShowAssignModal(false);
      if (published.published_exam_id) {
        setActivePaper({
          ...activePaper,
          id: paperId,
          status: 'PUBLISHED',
          published_exam_id: published.published_exam_id
        });
      }
    } catch (err: any) {
      setError(err.message || 'Failed to publish and assign exam.');
    } finally {
      setPublishing(false);
    }
  };

  const handleUpdateQuestion = () => {
    if (!editingQuestion || !activePaper) return;
    const { secIdx, qIdx, q } = editingQuestion;
    const updatedSections = [...activePaper.sections];
    updatedSections[secIdx].questions[qIdx] = q;
    setActivePaper({ ...activePaper, sections: updatedSections });
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
    <div className="min-h-screen bg-slate-950 text-slate-100 p-4 sm:p-8 space-y-8">
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
              activePaper.status === 'PUBLISHED' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
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
                <FileText className="w-4 h-4 text-sky-400" />
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
                <Sparkles className="w-4 h-4 text-emerald-400" />
                <span>PDF + Topic</span>
              </button>
            </div>

            <p className="text-[11px] text-slate-400 italic">
              {sourceType === 'TOPIC_ONLY' && '• Generates new exam questions strictly based on the exact topic entered below.'}
              {sourceType === 'PDF_ONLY' && '• Upload a PDF document; AI analyzes the text content to generate educational questions.'}
              {sourceType === 'PDF_AND_TOPIC' && '• The exact topic defines WHAT is tested; the uploaded PDF provides the context & depth.'}
            </p>
          </div>

          {/* Form Parameters Box */}
          <div className="bg-slate-900/90 p-6 rounded-3xl border border-slate-800 space-y-5 shadow-xl">
            <h2 className="text-lg font-bold text-white border-b border-slate-800 pb-3 flex items-center gap-2">
              <Settings className="w-5 h-5 text-amber-400" /> Paper Parameters
            </h2>

            {/* Language Selector */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">
                Question Paper Language
              </label>
              <div className="grid grid-cols-2 gap-3">
                {LANGUAGE_OPTIONS.map((lang) => (
                  <button
                    key={lang}
                    type="button"
                    onClick={() => {
                      setLanguage(lang);
                      if (lang === 'Kannada') {
                        setSubject('Kannada');
                        setTopic('ಸಂಧಿಗಳು');
                        setExactTopic('ಸಂಧಿಗಳು');
                      }
                    }}
                    className={`py-2.5 px-4 rounded-xl border text-xs font-bold transition-all flex items-center justify-center gap-2 ${
                      language === lang
                        ? 'bg-amber-500/20 text-amber-300 border-amber-500/50 shadow-lg shadow-amber-500/10'
                        : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-white'
                    }`}
                  >
                    <span>{lang === 'Kannada' ? 'ಕನ್ನಡ (Kannada)' : 'English'}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Class & Subject Selectors */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">Class Level</label>
                <select
                  value={classLevel}
                  onChange={(e) => setClassLevel(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 transition-colors font-bold"
                >
                  {CLASS_OPTIONS.map((c) => (
                    <option key={c} value={c}>Class {c}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">Subject</label>
                <select
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 transition-colors"
                >
                  {SUBJECT_OPTIONS.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* PDF UPLOAD SECTION (For PDF_ONLY and PDF_AND_TOPIC) */}
            {(sourceType === 'PDF_ONLY' || sourceType === 'PDF_AND_TOPIC') && (
              <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold text-sky-400 uppercase tracking-wider flex items-center gap-1.5">
                    <FileText className="w-4 h-4" /> Upload Source PDF Document
                  </label>
                  {pdfAnalysisResult && (
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                      <FileCheck className="w-3 h-3" /> Analyzed ({pdfAnalysisResult.page_count} Pages)
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-3">
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handlePdfFileSelect}
                    className="block w-full text-xs text-slate-400 file:mr-3 file:py-2 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-sky-500/20 file:text-sky-300 hover:file:bg-sky-500/30 cursor-pointer"
                  />
                  {pdfFile && !pdfAnalysisResult && (
                    <button
                      type="button"
                      disabled={pdfAnalyzing}
                      onClick={() => handleAnalyzePdf()}
                      className="px-3 py-2 rounded-xl bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold shrink-0 flex items-center gap-1.5"
                    >
                      {pdfAnalyzing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <UploadCloud className="w-3.5 h-3.5" />}
                      <span>Analyze PDF</span>
                    </button>
                  )}
                </div>

                {pdfAnalysisResult && (
                  <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs space-y-1.5">
                    <div className="text-slate-300 font-bold flex items-center justify-between">
                      <span>📄 {pdfAnalysisResult.filename}</span>
                      <span className="text-[10px] text-slate-400">{pdfAnalysisResult.page_count} Pages</span>
                    </div>
                    <p className="text-[11px] text-slate-400">{pdfAnalysisResult.summary}</p>
                    {pdfAnalysisResult.suggested_topics?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        <span className="text-[10px] text-slate-500 font-semibold">Extracted Topics:</span>
                        {pdfAnalysisResult.suggested_topics.map((t) => (
                          <button
                            key={t}
                            type="button"
                            onClick={() => {
                              setExactTopic(t);
                              setTopic(t);
                            }}
                            className="text-[10px] font-semibold px-2 py-0.5 rounded bg-sky-500/20 hover:bg-sky-500/30 text-sky-300 border border-sky-500/30"
                          >
                            {t}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* EXACT TOPIC INPUT (For TOPIC_ONLY and PDF_AND_TOPIC) */}
            {(sourceType === 'TOPIC_ONLY' || sourceType === 'PDF_AND_TOPIC') && (
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
                    {sourceType === 'PDF_AND_TOPIC' ? 'Exact Topic to Test from PDF' : 'Enter Exact Topic'}
                  </label>
                  <button
                    type="button"
                    disabled={analyzing || !exactTopic.trim()}
                    onClick={handleAnalyzeTopic}
                    className="text-xs font-bold text-amber-400 hover:text-amber-300 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 px-3 py-1 rounded-lg transition-all flex items-center gap-1.5"
                  >
                    {analyzing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                    <span>✨ Analyze Topic</span>
                  </button>
                </div>
                <input
                  type="text"
                  value={exactTopic}
                  onChange={(e) => {
                    setExactTopic(e.target.value);
                    setTopic(e.target.value);
                  }}
                  placeholder="e.g. ಸಂಧಿಗಳು, ಕನ್ನಡ ವರ್ಣಮಾಲೆ, Photosynthesis"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-xs text-white focus:outline-none focus:border-indigo-500 transition-colors font-semibold"
                />
                
                {/* Quick Pickers */}
                {sourceType === 'TOPIC_ONLY' && (
                  <div className="mt-3 space-y-1.5">
                    <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Quick Pick Topics:</span>
                    <div className="flex flex-wrap gap-1.5">
                      {KANNADA_TOPIC_SUGGESTIONS.map((t) => (
                        <button
                          key={t.name}
                          type="button"
                          onClick={() => {
                            setExactTopic(t.name);
                            setTopic(t.name);
                            setClassLevel(t.class);
                            setLanguage('Kannada');
                            setSubject('Kannada');
                          }}
                          className="text-[11px] font-medium px-2.5 py-1 rounded-lg bg-slate-950 hover:bg-amber-500/20 text-slate-300 hover:text-amber-300 border border-slate-800 transition-all"
                        >
                          {t.name} (Class {t.class})
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Difficulty, Duration & Marks */}
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block text-[10px] font-semibold text-slate-400 mb-1 uppercase tracking-wider">Difficulty</label>
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-2 text-xs text-white capitalize"
                >
                  {DIFFICULTY_OPTIONS.map((d) => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-[10px] font-semibold text-slate-400 mb-1 uppercase tracking-wider">Duration (Mins)</label>
                <input
                  type="number"
                  value={durationMinutes}
                  onChange={(e) => setDurationMinutes(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-2 text-xs text-white"
                />
              </div>

              <div>
                <label className="block text-[10px] font-semibold text-slate-400 mb-1 uppercase tracking-wider">Max Marks</label>
                <input
                  type="number"
                  value={maximumMarks}
                  onChange={(e) => setMaximumMarks(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-2 text-xs text-white font-bold text-emerald-400"
                />
              </div>
            </div>
          </div>

          {/* Section Builder Component */}
          <div className="bg-slate-900/90 p-6 rounded-3xl border border-slate-800 space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Layers className="w-5 h-5 text-emerald-400" /> Section Configuration
              </h2>
              <button
                type="button"
                onClick={handleAddSectionConfig}
                className="text-xs font-semibold px-2.5 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/30 flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" /> Add Section
              </button>
            </div>

            {sectionsConfig.map((sec, idx) => (
              <div key={idx} className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <input
                    type="text"
                    value={sec.name}
                    onChange={(e) => {
                      const updated = [...sectionsConfig];
                      updated[idx].name = e.target.value;
                      setSectionsConfig(updated);
                    }}
                    className="bg-transparent font-bold text-xs text-amber-300 focus:outline-none border-b border-dashed border-amber-500/40 pb-0.5"
                  />
                  {sectionsConfig.length > 1 && (
                    <button
                      type="button"
                      onClick={() => handleRemoveSectionConfig(idx)}
                      className="text-slate-500 hover:text-rose-400 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <label className="block text-[10px] text-slate-400 mb-1">Question Type</label>
                    <select
                      value={sec.question_type}
                      onChange={(e) => {
                        const updated = [...sectionsConfig];
                        updated[idx].question_type = e.target.value;
                        setSectionsConfig(updated);
                      }}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg px-2 py-1.5 text-xs text-white"
                    >
                      {QUESTION_TYPES.map((t) => (
                        <option key={t} value={t}>{t}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-[10px] text-slate-400 mb-1">Questions</label>
                    <input
                      type="number"
                      min="1"
                      max="100"
                      value={sec.num_questions}
                      onChange={(e) => {
                        const updated = [...sectionsConfig];
                        updated[idx].num_questions = Math.max(1, Number(e.target.value));
                        setSectionsConfig(updated);
                      }}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg px-2 py-1.5 text-xs text-white text-center font-bold"
                    />
                  </div>

                  <div>
                    <label className="block text-[10px] text-slate-400 mb-1">Marks/Q</label>
                    <input
                      type="number"
                      value={sec.marks_per_question}
                      onChange={(e) => {
                        const updated = [...sectionsConfig];
                        updated[idx].marks_per_question = Math.max(0.5, Number(e.target.value));
                        setSectionsConfig(updated);
                      }}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg px-2 py-1.5 text-xs text-white text-center"
                    />
                  </div>
                </div>
              </div>
            ))}

            {/* Total Questions & Marks Footer */}
            <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-xs font-bold text-slate-300">
              <span>Total Requested: <strong className="text-amber-400">{totalRequestedQuestions} Questions</strong></span>
              <span>Calculated Marks: <strong className="text-emerald-400">{totalCalculatedMarks} Pts</strong></span>
            </div>

            {/* Generate Button */}
            <button
              type="button"
              disabled={generating}
              onClick={handleGenerate}
              className="w-full py-4 rounded-2xl bg-gradient-to-r from-amber-500 via-amber-600 to-amber-500 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-black text-sm uppercase tracking-wider shadow-lg shadow-amber-500/20 flex items-center justify-center gap-2 transition-all"
            >
              {generating ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Synthesizing Exam Paper...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  <span>Generate Exam Paper ({totalRequestedQuestions} Questions)</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: AI Analysis Card & Paper Preview */}
        <div className="lg:col-span-7 space-y-6">

          {/* AI Curriculum & Topic Analysis Card */}
          {analysisResult && (
            <div className="bg-slate-900/90 rounded-3xl border border-amber-500/30 p-6 space-y-4 shadow-xl">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-sm font-bold text-amber-300 uppercase tracking-wider flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-amber-400" /> AI Topic & Curriculum Analysis
                </h3>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  {analysisResult.topic} (Class {analysisResult.class_level})
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div>
                  <strong className="text-slate-300 block mb-1">Key Curriculum Concepts:</strong>
                  <ul className="list-disc list-inside text-slate-400 space-y-1">
                    {analysisResult.key_concepts.map((kc, i) => (
                      <li key={i}>{kc}</li>
                    ))}
                  </ul>
                </div>

                <div>
                  <strong className="text-slate-300 block mb-1">Learning Objectives:</strong>
                  <ul className="list-disc list-inside text-slate-400 space-y-1">
                    {analysisResult.learning_objectives.map((lo, i) => (
                      <li key={i}>{lo}</li>
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
                    onClick={() => setShowAssignModal(true)}
                    className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white text-xs font-bold shadow-lg shadow-emerald-500/20 flex items-center gap-1.5"
                  >
                    <Send className="w-3.5 h-3.5" /> Assign Exam
                  </button>
                </div>
              </div>

              {/* Tabs: Question Paper vs Answer Key */}
              <div className="flex border-b border-slate-800 gap-4">
                <button
                  onClick={() => setActiveTab('paper')}
                  className={`pb-3 text-xs font-bold border-b-2 transition-colors flex items-center gap-2 ${
                    activeTab === 'paper' ? 'border-amber-400 text-amber-400' : 'border-transparent text-slate-400 hover:text-white'
                  }`}
                >
                  <BookOpen className="w-4 h-4" /> QUESTION PAPER
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
                      <h3 className="text-sm font-bold text-amber-300 uppercase tracking-wider border-b border-slate-800 pb-2">
                        {sec.name} ({sec.num_questions} Questions × {sec.marks_per_question} Marks = {sec.section_total_marks} Marks)
                      </h3>

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
                              <button
                                onClick={() => setEditingQuestion({ secIdx, qIdx, q: { ...q } })}
                                className="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded-lg bg-slate-800 text-slate-300 hover:text-white"
                              >
                                <Edit3 className="w-3.5 h-3.5" />
                              </button>
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
          <div className="bg-slate-900 rounded-3xl border border-slate-800 p-6 max-w-lg w-full space-y-4 shadow-2xl">
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
          <div className="bg-slate-900 rounded-3xl border border-slate-800 p-6 max-w-md w-full space-y-4 shadow-2xl">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Send className="w-4 h-4 text-emerald-400" /> Assign Exam to Student Class
            </h3>

            <p className="text-xs text-slate-400">
              Publishing this exam will make it active for students of the selected class. Students will see this exam on their dashboard and can start attempts.
            </p>

            <div className="space-y-2">
              <label className="block text-xs font-semibold text-slate-300">Select Target Class</label>
              <select
                defaultValue={activePaper.class_level}
                id="assignClassSelect"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white font-bold"
              >
                {CLASS_OPTIONS.map((c) => (
                  <option key={c} value={c}>Class {c}</option>
                ))}
              </select>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setShowAssignModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                disabled={publishing}
                onClick={() => {
                  const selectEl = document.getElementById('assignClassSelect') as HTMLSelectElement;
                  const selectedClass = selectEl ? Number(selectEl.value) : activePaper.class_level;
                  handlePublishAndAssign(selectedClass);
                }}
                className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white text-xs font-bold flex items-center gap-1.5"
              >
                {publishing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Publish & Assign Now'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
