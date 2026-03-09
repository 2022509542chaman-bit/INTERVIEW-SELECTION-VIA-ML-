import { useState, useEffect } from 'react'
import { Upload, FileType, CheckCircle, XCircle, FileText, ChevronRight, Sparkles } from 'lucide-react'
import { SpiralAnimation } from '@/components/ui/spiral-animation'

interface EvaluationResult {
  id: string;
  name: string;
  score: number;
  decision: 'Hire' | 'Reject';
  reason: string;
  response_snippet: string;
}

interface Summary {
  total: number;
  hired: number;
  rejected: number;
}

function App() {
  const [showLanding, setShowLanding] = useState(true);
  const [fadeOut, setFadeOut] = useState(false);
  const [enterVisible, setEnterVisible] = useState(false);

  const [candidatesFile, setCandidatesFile] = useState<File | null>(null);
  const [rubricFile, setRubricFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<EvaluationResult[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Show enter button after a delay
  useEffect(() => {
    if (showLanding) {
      const timer = setTimeout(() => setEnterVisible(true), 2000);
      return () => clearTimeout(timer);
    }
  }, [showLanding]);

  const handleEnter = () => {
    setFadeOut(true);
    setTimeout(() => setShowLanding(false), 1200);
  };

  const handleEvaluate = async () => {
    if (!candidatesFile || !rubricFile) {
      setError("Please upload both candidates Excel and Rubric file.");
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("candidates_file", candidatesFile);
    formData.append("rubric_file", rubricFile);

    try {
      const response = await fetch("/evaluate", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to evaluate candidates");
      }

      setResults(data.data);
      setSummary(data.summary);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred.");
      }
    } finally {
      setLoading(false);
    }
  };

  // ── LANDING PAGE (Spiral Animation) ──────────────────────────────────
  if (showLanding) {
    return (
      <div className={`fixed inset-0 w-full h-full overflow-hidden bg-black transition-opacity duration-1000 ${fadeOut ? 'opacity-0' : 'opacity-100'}`}>
        {/* Spiral Animation Background */}
        <div className="absolute inset-0">
          <SpiralAnimation />
        </div>

        {/* Overlay content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center z-10">
          {/* Title */}
          <div className={`text-center mb-16 transition-all duration-1000 ease-out ${enterVisible ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-8'}`}>
            <div className="flex items-center justify-center gap-3 mb-4">
              <Sparkles className="w-8 h-8 text-blue-400 animate-pulse" />
              <h1 className="text-5xl md:text-7xl font-extralight tracking-[0.15em] text-white uppercase">
                Evaluator
              </h1>
              <Sparkles className="w-8 h-8 text-blue-400 animate-pulse" />
            </div>
            <p className="text-blue-300/60 text-sm tracking-[0.4em] uppercase font-light">
              ML-Powered Candidate Assessment
            </p>
          </div>

          {/* Enter Button */}
          <div className={`transition-all duration-[1500ms] ease-out ${enterVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'}`}>
            <button
              onClick={handleEnter}
              className="group relative px-12 py-4 border border-white/20 rounded-full text-white text-lg tracking-[0.25em] uppercase font-extralight
                transition-all duration-700 hover:border-white/50 hover:bg-white/5 hover:tracking-[0.35em] hover:shadow-[0_0_40px_rgba(59,130,246,0.15)]
                active:scale-95"
            >
              <span className="relative z-10">Enter</span>
              <div className="absolute inset-0 rounded-full bg-gradient-to-r from-blue-500/0 via-blue-500/10 to-blue-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
            </button>
          </div>
        </div>

        {/* Bottom attribution */}
        <div className={`absolute bottom-8 left-1/2 -translate-x-1/2 z-10 transition-all duration-1000 delay-[2500ms] ${enterVisible ? 'opacity-40' : 'opacity-0'}`}>
          <p className="text-white/40 text-xs tracking-[0.3em] uppercase font-light">
            Powered by TF-IDF & Cosine Similarity
          </p>
        </div>
      </div>
    );
  }

  // ── MAIN DASHBOARD ───────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-blue-500/30 animate-fadeIn">

      {/* Header */}
      <header className="bg-slate-900/80 backdrop-blur-xl border-b border-slate-800 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-gradient-to-br from-blue-500 to-indigo-600 p-2.5 rounded-xl shadow-lg shadow-blue-500/20">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-xl font-bold tracking-tight">
              Candidate Evaluator <span className="bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">AI</span>
            </h1>
          </div>
          <button
            onClick={() => { setShowLanding(true); setFadeOut(false); setEnterVisible(false); }}
            className="text-slate-500 text-sm hover:text-slate-300 transition-colors"
          >
            ← Back to Intro
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">

        {/* Upload Section */}
        <section className="bg-slate-900/50 backdrop-blur-sm rounded-2xl border border-slate-800 p-6 md:p-10 transition-all hover:border-slate-700">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold tracking-tight text-white">Upload Evaluation Data</h2>
            <p className="text-slate-400 mt-2">Upload your candidates spreadsheet and assessment rubric to begin analysis.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

            {/* Candidates File Drop */}
            <div
              className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center text-center transition-all cursor-pointer ${candidatesFile
                  ? 'border-blue-500/50 bg-blue-500/5'
                  : 'border-slate-700 hover:border-blue-500/30 hover:bg-slate-800/50'
                }`}
            >
              <input
                type="file"
                accept=".xlsx, .xls, .csv"
                className="hidden"
                id="candidates-upload"
                onChange={(e) => {
                  if (e.target.files && e.target.files.length > 0) {
                    setCandidatesFile(e.target.files[0]);
                  }
                }}
              />
              <label htmlFor="candidates-upload" className="cursor-pointer flex flex-col items-center w-full h-full">
                <div className={`p-4 rounded-full mb-4 transition-colors ${candidatesFile
                    ? 'bg-blue-500/10 text-blue-400'
                    : 'bg-slate-800 text-slate-500'
                  }`}>
                  <FileType className="w-8 h-8" />
                </div>
                <span className="font-semibold text-slate-200 mb-1">
                  {candidatesFile ? candidatesFile.name : 'Candidates Spreadsheet'}
                </span>
                <span className="text-sm text-slate-500">
                  {candidatesFile ? '✓ File selected' : 'Excel or CSV file'}
                </span>
              </label>
            </div>

            {/* Rubric File Drop */}
            <div
              className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center text-center transition-all cursor-pointer ${rubricFile
                  ? 'border-blue-500/50 bg-blue-500/5'
                  : 'border-slate-700 hover:border-blue-500/30 hover:bg-slate-800/50'
                }`}
            >
              <input
                type="file"
                accept=".txt, .md, .docx"
                className="hidden"
                id="rubric-upload"
                onChange={(e) => {
                  if (e.target.files && e.target.files.length > 0) {
                    setRubricFile(e.target.files[0]);
                  }
                }}
              />
              <label htmlFor="rubric-upload" className="cursor-pointer flex flex-col items-center w-full h-full">
                <div className={`p-4 rounded-full mb-4 transition-colors ${rubricFile
                    ? 'bg-blue-500/10 text-blue-400'
                    : 'bg-slate-800 text-slate-500'
                  }`}>
                  <Upload className="w-8 h-8" />
                </div>
                <span className="font-semibold text-slate-200 mb-1">
                  {rubricFile ? rubricFile.name : 'Assessment Rubric'}
                </span>
                <span className="text-sm text-slate-500">
                  {rubricFile ? '✓ File selected' : 'Text or Markdown file'}
                </span>
              </label>
            </div>
          </div>

          {error && (
            <div className="mt-6 bg-red-500/10 text-red-400 border border-red-500/20 p-4 rounded-lg flex items-center space-x-2 text-sm font-medium">
              <XCircle className="w-5 h-5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="mt-8 flex justify-center">
            <button
              onClick={handleEvaluate}
              disabled={loading || !candidatesFile || !rubricFile}
              className={`group px-8 py-3.5 rounded-full font-semibold text-white transition-all transform flex items-center space-x-2 ${loading || !candidatesFile || !rubricFile
                  ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 hover:scale-105 active:scale-95'
                }`}
            >
              {loading ? (
                <>
                  <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <span>Evaluate Candidates</span>
                  <ChevronRight className="w-5 h-5 group-hover:translate-x-0.5 transition-transform" />
                </>
              )}
            </button>
          </div>
        </section>

        {/* Results Section */}
        {results.length > 0 && summary && (
          <section className="space-y-6 animate-fadeIn">
            {/* Dashboard Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-slate-900/50 backdrop-blur-sm rounded-2xl p-6 border border-slate-800 flex flex-col justify-center">
                <span className="text-slate-500 font-medium tracking-wide text-sm uppercase mb-2">Total Analyzed</span>
                <span className="text-4xl font-bold text-white">{summary.total}</span>
              </div>
              <div className="bg-slate-900/50 backdrop-blur-sm rounded-2xl p-6 border border-emerald-500/20 border-b-2 border-b-emerald-500 flex flex-col justify-center">
                <span className="text-emerald-400 font-medium tracking-wide text-sm uppercase mb-2">Recommended Hire</span>
                <span className="text-4xl font-bold text-emerald-400">{summary.hired}</span>
              </div>
              <div className="bg-slate-900/50 backdrop-blur-sm rounded-2xl p-6 border border-red-500/20 border-b-2 border-b-red-500 flex flex-col justify-center">
                <span className="text-red-400 font-medium tracking-wide text-sm uppercase mb-2">Rejected</span>
                <span className="text-4xl font-bold text-red-400">{summary.rejected}</span>
              </div>
            </div>

            {/* Detailed Table */}
            <div className="bg-slate-900/50 backdrop-blur-sm rounded-2xl border border-slate-800 overflow-hidden">
              <div className="px-6 py-5 border-b border-slate-800 flex justify-between items-center">
                <h3 className="text-lg font-bold text-white">Candidate Breakdown</h3>
                <button
                  onClick={() => {
                    const csvContent = "data:text/csv;charset=utf-8,"
                      + "Name,Decision,Score,Reason\n"
                      + results.map(e => `${e.name},${e.decision},${e.score},"${e.reason.replace(/"/g, '""')}"`).join("\n");
                    const encodedUri = encodeURI(csvContent);
                    const link = document.createElement("a");
                    link.setAttribute("href", encodedUri);
                    link.setAttribute("download", "evaluations.csv");
                    document.body.appendChild(link);
                    link.click();
                  }}
                  className="text-blue-400 font-medium text-sm hover:text-blue-300 transition-colors"
                >
                  Export CSV ↓
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-800/50 text-slate-400 text-sm border-b border-slate-800">
                      <th className="px-6 py-4 font-semibold w-1/5">Candidate</th>
                      <th className="px-6 py-4 font-semibold w-1/12">Score</th>
                      <th className="px-6 py-4 font-semibold w-1/12">Decision</th>
                      <th className="px-6 py-4 font-semibold w-2/5">Evaluation Reason</th>
                      <th className="px-6 py-4 font-semibold w-1/5">Response Snippet</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50">
                    {results.map((res) => (
                      <tr key={res.id} className="hover:bg-slate-800/30 transition-colors">
                        <td className="px-6 py-4 font-medium text-white">{res.name}</td>
                        <td className="px-6 py-4 text-slate-300 font-mono text-sm">{res.score}</td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold ${res.decision === 'Hire'
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                              : 'bg-red-500/10 text-red-400 border border-red-500/20'
                            }`}>
                            {res.decision === 'Hire' ? <CheckCircle className="w-3 h-3 mr-1" /> : <XCircle className="w-3 h-3 mr-1" />}
                            {res.decision}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-400 leading-relaxed">{res.reason}</td>
                        <td className="px-6 py-4 text-xs text-slate-500 italic truncate max-w-[200px]" title={res.response_snippet}>
                          "{res.response_snippet}"
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
