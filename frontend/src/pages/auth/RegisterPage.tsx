import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../auth/AuthProvider';
import { UserRole } from '../../types/auth';
import { Shield, Lock, Mail, AlertCircle, Loader2, UserCheck, Eye, EyeOff, Cpu, CheckCircle2, Terminal, Activity } from 'lucide-react';

export const RegisterPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [role, setRole] = useState<UserRole>('candidate');
  const [classLevel, setClassLevel] = useState<number>(7);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { register, user, loading: authLoading } = useAuth();
  const navigate = useNavigate();

  // Automatically redirect authenticated users to their dashboard
  useEffect(() => {
    if (user && !authLoading) {
      const target = user.role === 'candidate' ? '/candidate' : '/recruiter';
      navigate(target, { replace: true });
    }
  }, [user, authLoading, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    if (role === 'candidate' && (classLevel < 1 || classLevel > 12)) {
      setError('Student class must be between Class 1 and Class 12.');
      return;
    }
    setError('');
    setLoading(true);

    try {
      const profile = await register(email, password, role, role === 'candidate' ? classLevel : undefined);
      const target = profile.role === 'candidate' ? '/candidate' : '/recruiter';
      navigate(target, { replace: true });
    } catch (err: any) {
      setError(err.message || 'Failed to create account.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 rounded-3xl border border-slate-800 bg-slate-900/90 shadow-2xl overflow-hidden">
      {/* Left Column: Branding & Highlights */}
      <div className="lg:col-span-6 p-5 sm:p-8 lg:p-12 bg-gradient-to-br from-indigo-950/80 via-slate-900 to-slate-950 flex flex-col justify-between border-b lg:border-b-0 lg:border-r border-slate-800/80 relative overflow-hidden">
        <div className="absolute -top-24 -left-24 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="relative z-10 space-y-6">
          <div className="inline-flex items-center gap-3 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold tracking-wide">
            <Cpu className="w-4 h-4 animate-pulse" />
            <span>EXAMPORTAL ACCOUNT CREATION</span>
          </div>

          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-indigo-600 text-white shadow-lg shadow-indigo-600/30">
                <Shield className="w-7 h-7" />
              </div>
              <span className="text-2xl font-black tracking-tight text-white">ExamPortal</span>
            </div>
            <h2 className="text-3xl font-extrabold text-white leading-tight">
              Create Your Assessment Profile
            </h2>
            <p className="text-sm text-slate-400 leading-relaxed">
              Join candidates and recruiters leveraging automated multi-agent code evaluation and proctored environment security.
            </p>
          </div>

          <div className="space-y-3.5 pt-4">
            <div className="flex items-start gap-3 text-sm text-slate-300">
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
              <span><strong>Candidate Account:</strong> Take technical assessments with real-time code runner & telemetry.</span>
            </div>
            <div className="flex items-start gap-3 text-sm text-slate-300">
              <Terminal className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
              <span><strong>Recruiter Account:</strong> Create exams, manage test cases, monitor live sessions & analytics.</span>
            </div>
          </div>
        </div>

        <div className="relative z-10 pt-8 mt-8 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-500">
          <span>Production AWS EKS Infrastructure</span>
          <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
            Operational
          </span>
        </div>
      </div>

      {/* Right Column: Register Form Card */}
      <div className="lg:col-span-6 p-5 sm:p-8 lg:p-12 flex flex-col justify-center bg-slate-900/60">
        <div className="max-w-md w-full mx-auto space-y-5">
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">Create Account</h2>
            <p className="text-sm text-slate-400 mt-1">Get started with Proctored Exam & Evaluation Platform.</p>
          </div>

          {error && (
            <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-3 text-rose-300 text-sm">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3.5">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1 uppercase tracking-wider">Email Address</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="user@example.com"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1 uppercase tracking-wider">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  minLength={6}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="At least 6 characters"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-11 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-3.5 text-slate-500 hover:text-slate-300 transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1 uppercase tracking-wider">Confirm Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Repeat password"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1 uppercase tracking-wider">Account Role</label>
              <div className="relative">
                <UserCheck className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value as UserRole)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
                >
                  <option value="candidate">Student (Take Exams)</option>
                  <option value="recruiter">Teacher (Create & Grade Exams)</option>
                </select>
              </div>
            </div>

            {role === 'candidate' && (
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1 uppercase tracking-wider">Student Class</label>
                <select
                  value={classLevel}
                  onChange={(e) => setClassLevel(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
                >
                  {Array.from({ length: 12 }, (_, index) => index + 1).map((level) => (
                    <option key={level} value={level}>Class {level}</option>
                  ))}
                </select>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-3 rounded-xl flex items-center justify-center gap-2 transition-colors shadow-lg shadow-indigo-600/25 disabled:opacity-50 mt-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Creating account...</span>
                </>
              ) : (
                <span>Register Account</span>
              )}
            </button>
          </form>

          <div className="text-center text-xs text-slate-400 pt-2 border-t border-slate-800/80">
            Already registered?{' '}
            <Link to="/login" className="text-indigo-400 font-semibold hover:underline">
              Sign in here
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
