import React, { useState, useMemo } from 'react';
import * as xlsx from 'xlsx';
import mammoth from 'mammoth';
import { UploadCloud, FileSpreadsheet, FileText, CheckCircle2, AlertCircle, Play, Download, ChevronDown, ChevronUp, User, Award, Clock, XCircle, LayoutGrid, Table as TableIcon, Filter, ArrowUpDown } from 'lucide-react';

export default function App() {
  // --- State Variables ---
  // Input Data
  const [candidates, setCandidates] = useState([]);
  const [rubricText, setRubricText] = useState('');
  const [rubricFileName, setRubricFileName] = useState('');
  const [excelFileName, setExcelFileName] = useState('');
  const [candidateColumns, setCandidateColumns] = useState([]);

  // UI State
  const [isRubricExpanded, setIsRubricExpanded] = useState(false);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [evaluationProgress, setEvaluationProgress] = useState({ current: 0, total: 0, statusLabel: '' });
  const [results, setResults] = useState([]);
  const [cohortSummary, setCohortSummary] = useState('');
  const [error, setError] = useState(null);

  // View State
  const [viewMode, setViewMode] = useState('card'); // 'card' or 'table'
  const [filterVerdict, setFilterVerdict] = useState('ALL');
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

  // --- Handlers for File Uploads ---

  const handleExcelUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setExcelFileName(file.name);

    const reader = new FileReader();
    reader.onload = (evt) => {
      try {
        const bstr = evt.target.result;
        const workbook = xlsx.read(bstr, { type: 'binary' });
        const wsname = workbook.SheetNames[0];
        const ws = workbook.Sheets[wsname];
        const data = xlsx.utils.sheet_to_json(ws, { defval: "" });

        if (data.length > 0) {
          // Auto-detect columns
          const cols = Object.keys(data[0]);
          setCandidateColumns(cols);
          setCandidates(data);
          setError(null);
        } else {
          setError("Excel file appears to be empty.");
        }
      } catch (err) {
        setError(`Error parsing Excel: ${err.message}`);
      }
    };
    reader.readAsBinaryString(file);
  };

  const handleRubricUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setRubricFileName(file.name);

    try {
      if (file.name.endsWith('.docx')) {
        const arrayBuffer = await file.arrayBuffer();
        const result = await mammoth.extractRawText({ arrayBuffer });
        setRubricText(result.value);
      } else if (file.name.endsWith('.xlsx')) {
        const reader = new FileReader();
        reader.onload = (evt) => {
          const workbook = xlsx.read(evt.target.result, { type: 'binary' });
          const textChunks = [];
          workbook.SheetNames.forEach(sheet => {
            const data = xlsx.utils.sheet_to_csv(workbook.Sheets[sheet]);
            textChunks.push(`--- Sheet: ${sheet} ---\n${data}`);
          });
          setRubricText(textChunks.join('\n'));
        };
        reader.readAsBinaryString(file);
      } else {
        const text = await file.text(); // text or md
        setRubricText(text);
      }
    } catch (err) {
      setError(`Error parsing Rubric: ${err.message}`);
    }
  };

  // --- Evaluation Logic ---

  const runEvaluation = async () => {
    if (!apiKey) {
      setError("Please enter your Anthropic API Key to proceed.");
      return;
    }
    if (candidates.length === 0 || !rubricText) {
      setError("Please upload both Candidate Data and a Rubric before evaluating.");
      return;
    }

    setIsEvaluating(true);
    setResults([]);
    setCohortSummary('');
    setError(null);
    setEvaluationProgress({ current: 0, total: candidates.length, statusLabel: 'Evaluating candidates...' });

    const client = new Anthropic({
      apiKey: apiKey,
      dangerouslyAllowBrowser: true
    });

    const evaluatedResults = [];

    for (let i = 0; i < candidates.length; i++) {
      const candidate = candidates[i];
      const nameField = candidateColumns.find(c => c.toLowerCase().includes('name')) || candidateColumns[0];
      const candidateName = candidate[nameField] || `Candidate ${i + 1}`;

      // Prepare Answers string
      const answersList = candidateColumns
        .filter(c => c !== nameField)
        .map(c => `Q: ${c}\nA: ${candidate[c]}`)
        .join('\n\n');

      const prompt = `Here is the Rubric for evaluation:
<rubric>
${rubricText}
</rubric>

Here is the candidate's submission:
Candidate Name: ${candidateName}
<answers>
${answersList}
</answers>`;

      try {
        const response = await client.messages.create({
          model: 'claude-3-5-sonnet-20241022',
          max_tokens: 4096,
          system: "You are an expert evaluator for technical/professional assessments. You will be given a rubric defining evaluation criteria and a candidate's responses. Evaluate each answer against the rubric dimensions. Score each dimension out of 10. Provide specific reasoning for each score. Then give an overall verdict: SELECTED (strong candidate), ON HOLD (borderline, needs review), or REJECTED (does not meet criteria). Return ONLY valid JSON matching this schema: {\"candidate_name\": string, \"verdict\": \"SELECTED\" | \"ON HOLD\" | \"REJECTED\", \"overall_score\": number, \"confidence\": \"High\" | \"Medium\" | \"Low\", \"dimension_scores\": [{\"dimension\": string, \"score\": number, \"reasoning\": string}], \"strengths\": string[], \"weaknesses\": string[], \"detailed_reasoning\": string, \"recommendation_note\": string}",
          messages: [{ role: 'user', content: prompt }]
        });

        // Parse response content
        const jsonText = response.content[0].text;
        const matchIndex = jsonText.indexOf('{');
        const endMatchIndex = jsonText.lastIndexOf('}');
        const cleanJson = jsonText.substring(matchIndex, endMatchIndex + 1);

        const resultObj = JSON.parse(cleanJson);
        evaluatedResults.push({ ...candidate, _evaluation: resultObj });
        setResults(prev => [...prev, { ...candidate, _evaluation: resultObj }]);
      } catch (err) {
        console.error(err);
        const errorEval = {
          candidate_name: candidateName,
          verdict: "ERROR",
          detailed_reasoning: "Failed to evaluate due to API error: " + err.message
        };
        evaluatedResults.push({ ...candidate, _error: true, _evaluation: errorEval });
        setResults(prev => [...prev, { ...candidate, _error: true, _evaluation: errorEval }]);
      }

      setEvaluationProgress(prev => ({ ...prev, current: i + 1 }));

      // Rate limiting
      if (i < candidates.length - 1) {
        await new Promise(r => setTimeout(r, 500));
      }
    }

    // Generate Cohort Summary
    setEvaluationProgress(prev => ({ ...prev, statusLabel: 'Generating cohort summary...' }));

    try {
      const cohortData = evaluatedResults.map(r => {
        const ev = r._evaluation;
        return `Candidate: ${ev.candidate_name} | Verdict: ${ev.verdict} | Score: ${ev.overall_score || 'N/A'}\nStrengths: ${(ev.strengths || []).join(', ')}\nWeaknesses: ${(ev.weaknesses || []).join(', ')}`;
      }).join('\n\n');

      const summaryResponse = await client.messages.create({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 1024,
        system: "You are an expert talent acquisition director. Review the evaluation results for a cohort of candidates and write a concise, professional 'Evaluation Summary' paragraph (approx 3-5 sentences) that highlights the overall quality of the pool, common strengths, shared weaknesses, and any notable trends. Output ONLY the summary text.",
        messages: [{ role: 'user', content: `Here are the evaluation results for the cohort:\n<results>\n${cohortData}\n</results>\n\nPlease provide the Evaluation Summary paragraph.` }]
      });
      setCohortSummary(summaryResponse.content[0].text.trim());
    } catch (err) {
      console.error("Summary generation failed:", err);
      setCohortSummary("Failed to generate cohort summary.");
    }

    setIsEvaluating(false);
  };


  // --- Export UI Logic ---
  const exportToExcel = () => {
    if (results.length === 0) return;

    const exportData = results.map(row => {
      const evalData = row._evaluation || {};
      const baseObj = { ...row };
      delete baseObj._evaluation;
      delete baseObj._error;

      return {
        ...baseObj,
        "AI_Verdict": evalData.verdict || "N/A",
        "AI_Overall_Score": evalData.overall_score || "N/A",
        "AI_Confidence": evalData.confidence || "N/A",
        ...((evalData.dimension_scores || []).reduce((acc, dim) => {
          acc[`Score_${dim.dimension}`] = dim.score;
          acc[`Reason_${dim.dimension}`] = dim.reasoning;
          return acc;
        }, {})),
        "AI_Strengths": (evalData.strengths || []).join('; '),
        "AI_Weaknesses": (evalData.weaknesses || []).join('; '),
        "AI_Detailed_Reasoning": evalData.detailed_reasoning || "N/A",
        "AI_Recommendation": evalData.recommendation_note || "N/A"
      };
    });

    const worksheet = xlsx.utils.json_to_sheet(exportData);
    const workbook = xlsx.utils.book_new();
    xlsx.utils.book_append_sheet(workbook, worksheet, "Evaluation Results");
    xlsx.writeFile(workbook, "ML_Evaluation_Results.xlsx");
  };

  // --- Handlers & Sorting / Filtering ---

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') direction = 'desc';
    setSortConfig({ key, direction });
  };

  const getVerdictWeight = (v) => {
    if (v === 'SELECTED') return 3;
    if (v === 'ON HOLD') return 2;
    if (v === 'REJECTED') return 1;
    return 0;
  };

  const filteredAndSortedResults = useMemo(() => {
    let processData = [...results];

    // Filter
    if (filterVerdict !== 'ALL') {
      processData = processData.filter(r => (r._evaluation?.verdict || 'ERROR') === filterVerdict);
    }

    // Sort
    if (sortConfig.key) {
      processData.sort((a, b) => {
        const evalA = a._evaluation || {};
        const evalB = b._evaluation || {};
        let valA, valB;

        if (sortConfig.key === 'score') {
          valA = evalA.overall_score || 0;
          valB = evalB.overall_score || 0;
        } else if (sortConfig.key === 'verdict') {
          valA = getVerdictWeight(evalA.verdict);
          valB = getVerdictWeight(evalB.verdict);
        } else if (sortConfig.key === 'name') {
          valA = evalA.candidate_name || '';
          valB = evalB.candidate_name || '';
          // string compare
          if (valA < valB) return sortConfig.direction === 'asc' ? -1 : 1;
          if (valA > valB) return sortConfig.direction === 'asc' ? 1 : -1;
          return 0;
        }

        if (valA < valB) return sortConfig.direction === 'asc' ? -1 : 1;
        if (valA > valB) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }

    return processData;
  }, [results, filterVerdict, sortConfig]);


  const updateVerdict = (idx, newVerdict) => {
    // Create a new array and replace the evaluation for that item
    setResults(prev => prev.map((r, i) => {
      if (i === idx) {
        return { ...r, _evaluation: { ...r._evaluation, verdict: newVerdict } };
      }
      return r;
    }));
  };

  // --- Render Helpers ---

  const getVerdictColor = (verdict) => {
    switch (verdict) {
      case 'SELECTED': return 'bg-teal-500/20 text-teal-accent border-teal-500/30';
      case 'ON HOLD': return 'bg-gold-accent/20 text-gold-accent border-gold-accent/30';
      case 'REJECTED': return 'bg-red-500/20 text-red-500 border-red-500/30';
      default: return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
    }
  };

  const getVerdictIcon = (verdict) => {
    switch (verdict) {
      case 'SELECTED': return <CheckCircle2 className="w-5 h-5" />;
      case 'ON HOLD': return <Clock className="w-5 h-5" />;
      case 'REJECTED': return <XCircle className="w-5 h-5" />;
      default: return <AlertCircle className="w-5 h-5" />;
    }
  };

  // SUMMARY CALCULATIONS
  const totalEvaluated = results.length;
  const selectedCount = results.filter(r => r._evaluation?.verdict === 'SELECTED').length;
  const holdCount = results.filter(r => r._evaluation?.verdict === 'ON HOLD').length;
  const rejectedCount = results.filter(r => r._evaluation?.verdict === 'REJECTED').length;

  return (
    <div className="min-h-screen bg-navy-900 text-slate-200 p-4 md:p-8 selection:bg-teal-accent/30 selection:text-teal-accent tracking-wide">
      <div className="max-w-7xl mx-auto space-y-8">

        {/* Header */}
        <header className="text-center space-y-4 mb-12">
          <div className="inline-flex items-center justify-center p-3 bg-teal-accent/10 rounded-full mb-4">
            <Award className="w-8 h-8 text-teal-accent shadow-[0_0_20px_rgba(20,184,166,0.3)]" />
          </div>
          <h1 className="text-4xl md:text-5xl font-display font-bold text-white tracking-tight">
            ML Candidate <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-emerald-300">Evaluator</span>
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Intelligent assessment platform analyzing candidate responses against custom rubrics.
          </p>
        </header>

        {/* Global Error Banner */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-lg flex items-center space-x-3">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <p>{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

          {/* Candidates Upload Card */}
          <div className="glass-card rounded-2xl p-6 space-y-4 transition-all hover:border-slate-600/50">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-blue-500/10 rounded-lg">
                <FileSpreadsheet className="w-6 h-6 text-blue-400" />
              </div>
              <h2 className="text-xl font-display font-semibold text-white">1. Candidate Data</h2>
            </div>

            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-slate-700 border-dashed rounded-xl cursor-pointer bg-navy-800/50 hover:bg-slate-800/50 transition-colors">
              <div className="flex flex-col items-center justify-center pt-5 pb-6 text-center">
                <UploadCloud className="w-8 h-8 text-slate-400 mb-2" />
                <p className="text-sm text-slate-400"><span className="font-semibold text-teal-accent">Upload Excel</span> (.xlsx)</p>
                <p className="text-xs text-slate-500 mt-1">First row should be headers</p>
              </div>
              <input type="file" accept=".xlsx, .xls, .csv" className="hidden" onChange={handleExcelUpload} />
            </label>

            {excelFileName && (
              <div className="flex items-center justify-between text-sm bg-slate-800/50 p-3 rounded-lg border border-slate-700/50">
                <span className="text-slate-300 truncate font-medium flex items-center gap-2">
                  <FileSpreadsheet className="w-4 h-4 text-slate-400" /> {excelFileName}
                </span>
                <span className="bg-blue-500/20 text-blue-400 px-2.5 py-1 rounded-md font-semibold text-xs border border-blue-500/20">
                  {candidates.length} rows loaded
                </span>
              </div>
            )}

            {candidates.length > 0 && (
              <div className="mt-2 space-y-1">
                <p className="text-xs text-slate-500 font-medium uppercase tracking-wider">Detected Columns</p>
                <div className="flex flex-wrap gap-1.5">
                  {candidateColumns.slice(0, 5).map(c => (
                    <span key={c} className="text-[10px] bg-slate-800 border border-slate-700 text-slate-300 px-2 py-1 rounded font-mono">{c}</span>
                  ))}
                  {candidateColumns.length > 5 && <span className="text-[10px] bg-slate-800 border border-slate-700 text-slate-500 px-2 py-1 rounded">+{candidateColumns.length - 5} more</span>}
                </div>
              </div>
            )}
          </div>

          {/* Rubric Upload Card */}
          <div className="glass-card rounded-2xl p-6 space-y-4 transition-all hover:border-slate-600/50">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-purple-500/10 rounded-lg">
                <FileText className="w-6 h-6 text-purple-400" />
              </div>
              <h2 className="text-xl font-display font-semibold text-white">2. Evaluation Rubric</h2>
            </div>

            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-slate-700 border-dashed rounded-xl cursor-pointer bg-navy-800/50 hover:bg-slate-800/50 transition-colors">
              <div className="flex flex-col items-center justify-center pt-5 pb-6 text-center">
                <UploadCloud className="w-8 h-8 text-slate-400 mb-2" />
                <p className="text-sm text-slate-400"><span className="font-semibold text-teal-accent">Upload Document</span></p>
                <p className="text-xs text-slate-500 mt-1">DOCX, XLSX, TXT, MD</p>
              </div>
              <input type="file" accept=".docx, .xlsx, .txt, .md" className="hidden" onChange={handleRubricUpload} />
            </label>

            {rubricFileName && (
              <div className="flex items-center justify-between text-sm bg-slate-800/50 p-3 rounded-lg border border-slate-700/50">
                <span className="text-slate-300 truncate font-medium flex items-center gap-2">
                  <FileText className="w-4 h-4 text-slate-400" /> {rubricFileName}
                </span>
                <span className="bg-purple-500/20 text-purple-400 px-2.5 py-1 rounded-md font-semibold text-xs border border-purple-500/20">
                  Parsed Successfully
                </span>
              </div>
            )}

            {rubricText && (
              <div className="mt-2 text-sm bg-slate-800/30 rounded-lg border border-slate-700/30 overflow-hidden text-slate-300">
                <button
                  onClick={() => setIsRubricExpanded(!isRubricExpanded)}
                  className="w-full flex items-center justify-between p-3 hover:bg-slate-800/50 transition-colors outline-none"
                >
                  <span className="font-medium text-slate-400 text-xs uppercase tracking-widest">Preview Rubric Text</span>
                  {isRubricExpanded ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
                </button>
                {isRubricExpanded && (
                  <div className="p-3 pt-0 text-xs font-mono text-slate-400 max-h-48 overflow-y-auto whitespace-pre-wrap leading-relaxed border-t border-slate-700/30">
                    {rubricText}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Run Execution Bar */}
        <div className="glass-card rounded-2xl p-6 border-slate-700/50 flex flex-col items-center justify-between gap-6">
          <div className="w-full flex flex-col items-center pb-1">
            {candidates.length > 0 && rubricText && (
              <p className="text-sm text-teal-accent mb-4">Ready to run local analysis on {candidates.length} candidates.</p>
            )}
            <button
              onClick={runEvaluation}
              disabled={isEvaluating || candidates.length === 0 || !rubricText}
              className="w-full md:w-1/2 flex justify-center items-center gap-2 bg-gradient-to-r from-teal-500 to-emerald-400 hover:from-teal-400 hover:to-emerald-300 text-navy-900 font-bold py-3.5 px-6 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-teal-500/20 hover:shadow-teal-500/40 transform hover:-translate-y-0.5"
            >
              {isEvaluating ? (
                <>
                  <div className="w-5 h-5 border-2 border-navy-900/30 border-t-navy-900 rounded-full animate-spin"></div>
                  Processing Local Heuristics...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Run Local Evaluation
                </>
              )}
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        {isEvaluating && (
          <div className="glass-card rounded-2xl p-6 text-center space-y-4 shadow-teal-accent/5 border-teal-500/20 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-teal-500/0 via-teal-500/50 to-teal-500/0 animate-pulse"></div>
            <h3 className="text-xl font-display font-semibold text-white animate-pulse">AI Analysis Active</h3>
            <p className="text-sm text-slate-400">{evaluationProgress.statusLabel} ({evaluationProgress.current} out of {evaluationProgress.total})</p>
            <div className="w-full bg-slate-800 rounded-full h-3 overflow-hidden border border-slate-700 shadow-inner mt-4">
              <div
                className="bg-gradient-to-r from-teal-500 to-emerald-400 h-3 rounded-full transition-all duration-300 ease-out"
                style={{ width: `${(evaluationProgress.current / evaluationProgress.total) * 100}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Results Dashboard */}
        {results.length > 0 && !isEvaluating && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">

            <div className="flex flex-col md:flex-row items-center justify-between gap-4 border-b border-slate-800 pb-4">
              <h2 className="text-3xl font-display font-bold text-white tracking-tight flex items-center gap-3">
                Results Dashboard
                <span className="text-xs bg-slate-800 px-2 py-1 rounded-md text-slate-400 font-mono font-medium align-middle">
                  {results.length} Evaluated
                </span>
              </h2>
              <button
                onClick={exportToExcel}
                className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-600 px-5 py-2.5 rounded-xl transition-all font-semibold text-sm shadow-md hover:shadow-xl"
              >
                <Download className="w-4 h-4 text-teal-accent" /> Export Data
              </button>
            </div>

            {/* Evaluation Summary */}
            {cohortSummary && (
              <div className="glass-card rounded-2xl p-6 relative overflow-hidden">
                <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-gradient-to-b from-teal-400 to-blue-500"></div>
                <h3 className="text-lg font-display font-bold text-white mb-2 flex items-center gap-2">
                  Evaluation Summary
                  <span className="text-[10px] uppercase tracking-widest bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded border border-blue-500/20">AI Generated</span>
                </h3>
                <p className="text-slate-300 text-sm leading-relaxed">{cohortSummary}</p>
              </div>
            )}

            {/* Summary Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-navy-800/80 border border-slate-700 rounded-2xl p-5 hover:border-slate-600 transition-colors shadow-lg">
                <p className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2 flex items-center gap-2"><User className="w-4 h-4" /> Total</p>
                <p className="text-4xl font-display font-bold text-white">{totalEvaluated}</p>
              </div>
              <div className="bg-teal-900/10 border border-teal-500/20 rounded-2xl p-5 hover:border-teal-500/30 transition-colors shadow-lg">
                <p className="text-teal-500/80 text-sm font-medium uppercase tracking-wider mb-2 flex items-center gap-2"><CheckCircle2 className="w-4 h-4" /> Selected</p>
                <p className="text-4xl font-display font-bold text-teal-accent">{selectedCount}</p>
              </div>
              <div className="bg-gold-accent/5 border border-gold-accent/20 rounded-2xl p-5 hover:border-gold-accent/30 transition-colors shadow-lg">
                <p className="text-gold-accent/80 text-sm font-medium uppercase tracking-wider mb-2 flex items-center gap-2"><Clock className="w-4 h-4" /> On Hold</p>
                <p className="text-4xl font-display font-bold text-gold-accent">{holdCount}</p>
              </div>
              <div className="bg-red-900/10 border border-red-500/20 rounded-2xl p-5 hover:border-red-500/30 transition-colors shadow-lg">
                <p className="text-red-500/80 text-sm font-medium uppercase tracking-wider mb-2 flex items-center gap-2"><XCircle className="w-4 h-4" /> Rejected</p>
                <p className="text-4xl font-display font-bold text-red-500">{rejectedCount}</p>
              </div>
            </div>

            {/* Toolbar */}
            <div className="flex flex-col md:flex-row items-center justify-between gap-4 bg-navy-800/50 p-3 rounded-xl border border-slate-700/50">
              <div className="flex items-center gap-3 w-full md:w-auto">
                <div className="flex bg-navy-900 rounded-lg p-1 border border-slate-700">
                  <button
                    onClick={() => setViewMode('card')}
                    className={`p-1.5 rounded-md transition-colors ${viewMode === 'card' ? 'bg-slate-700 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
                    title="Card View"
                  >
                    <LayoutGrid className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setViewMode('table')}
                    className={`p-1.5 rounded-md transition-colors ${viewMode === 'table' ? 'bg-slate-700 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
                    title="Table View"
                  >
                    <TableIcon className="w-4 h-4" />
                  </button>
                </div>

                <div className="h-6 w-px bg-slate-700 hidden md:block"></div>

                <div className="flex items-center gap-2 text-sm text-slate-300 w-full md:w-auto">
                  <Filter className="w-4 h-4 text-slate-400" />
                  <select
                    className="bg-navy-900 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-teal-accent flex-grow md:flex-grow-0"
                    value={filterVerdict}
                    onChange={(e) => setFilterVerdict(e.target.value)}
                  >
                    <option value="ALL">All Verdicts</option>
                    <option value="SELECTED">Selected</option>
                    <option value="ON HOLD">On Hold</option>
                    <option value="REJECTED">Rejected</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center gap-2 text-sm text-slate-300 w-full md:w-auto">
                <ArrowUpDown className="w-4 h-4 text-slate-400" />
                <span className="hidden md:inline">Sort by:</span>
                <div className="flex gap-2">
                  <button onClick={() => handleSort('score')} className={`px-3 py-1.5 rounded-lg border transition-colors ${sortConfig.key === 'score' ? 'bg-slate-700 text-white border-slate-600' : 'bg-navy-900 border-slate-700 text-slate-400 hover:bg-slate-800'}`}>
                    Score {sortConfig.key === 'score' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                  </button>
                  <button onClick={() => handleSort('verdict')} className={`px-3 py-1.5 rounded-lg border transition-colors ${sortConfig.key === 'verdict' ? 'bg-slate-700 text-white border-slate-600' : 'bg-navy-900 border-slate-700 text-slate-400 hover:bg-slate-800'}`}>
                    Verdict {sortConfig.key === 'verdict' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                  </button>
                  <button onClick={() => handleSort('name')} className={`px-3 py-1.5 rounded-lg border transition-colors ${sortConfig.key === 'name' ? 'bg-slate-700 text-white border-slate-600' : 'bg-navy-900 border-slate-700 text-slate-400 hover:bg-slate-800'}`}>
                    Name {sortConfig.key === 'name' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                  </button>
                </div>
              </div >
            </div >

            {/* Candidate List (Card or Table View) */}
            {
              viewMode === 'card' ? (
                <div className="space-y-4">
                  {filteredAndSortedResults.map((result, idx) => {
                    // Find the original index to safely update
                    const origIdx = results.findIndex(r => r === result);
                    const evaluation = result._evaluation || {};
                    const verdict = evaluation.verdict || "ERROR";
                    const nameField = candidateColumns.find(c => c.toLowerCase().includes('name')) || candidateColumns[0];
                    const candidateName = evaluation.candidate_name || result[nameField] || `Candidate ${idx + 1}`;

                    return (
                      <details key={idx} className="group glass-card rounded-2xl overflow-hidden [&_summary::-webkit-details-marker]:hidden">
                        <summary className="flex items-center justify-between p-5 cursor-pointer hover:bg-slate-800/80 transition-colors">
                          <div className="flex items-center gap-5">
                            <div className={`p-3 rounded-xl border-2 ${getVerdictColor(verdict)}`}>
                              {getVerdictIcon(verdict)}
                            </div>
                            <div>
                              <h3 className="text-xl font-bold text-white mb-1.5">{candidateName}</h3>
                              <div className="flex items-center gap-3">
                                <span className={`text-xs font-bold px-2 py-0.5 rounded border uppercase tracking-widest ${getVerdictColor(verdict)}`}>
                                  {verdict}
                                </span>
                                {evaluation.overall_score !== undefined && (
                                  <span className="text-sm font-medium text-slate-400 border-l border-slate-700 pl-3 flex items-center gap-1">
                                    Score: <span className="text-slate-200 font-bold">{evaluation.overall_score}/100</span>
                                  </span>
                                )}
                                {evaluation.confidence && (
                                  <span className="text-xs text-slate-500 uppercase tracking-widest border-l border-slate-700 pl-3">
                                    {evaluation.confidence} conf.
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-4">
                            {/* Manual Override Dropdown */}
                            <div className="hidden md:block" onClick={(e) => e.preventDefault()}>
                              <select
                                value={verdict}
                                onChange={(e) => updateVerdict(origIdx, e.target.value)}
                                className="bg-navy-900 border border-slate-600 rounded p-1 text-xs text-slate-300 focus:outline-none focus:border-teal-accent"
                              >
                                <option value="SELECTED">Override: SELECTED</option>
                                <option value="ON HOLD">Override: ON HOLD</option>
                                <option value="REJECTED">Override: REJECTED</option>
                              </select>
                            </div>
                            <div className="p-2 rounded-full bg-slate-800 group-hover:bg-slate-700 transition-colors">
                              <ChevronDown className="w-5 h-5 text-slate-400 group-open:rotate-180 transition-transform duration-300" />
                            </div>
                          </div>
                        </summary >

                        <div className="p-6 border-t border-slate-700/50 bg-navy-900/50 space-y-6 shadow-inner">
                          <div className="md:hidden mb-4 pb-4 border-b border-slate-800">
                            <label className="text-xs text-slate-500 block mb-1 uppercase tracking-wider">Manual Override</label>
                            <select
                              value={verdict}
                              onChange={(e) => updateVerdict(origIdx, e.target.value)}
                              className="w-full bg-navy-900 border border-slate-600 rounded p-2 text-sm text-slate-300 focus:outline-none focus:border-teal-accent"
                            >
                              <option value="SELECTED">SELECTED</option>
                              <option value="ON HOLD">ON HOLD</option>
                              <option value="REJECTED">REJECTED</option>
                            </select>
                          </div>

                          {/* Reasoning */}
                          <div className="bg-slate-800/40 p-5 rounded-xl border border-slate-700/50 shadow-sm relative overflow-hidden">
                            <div className="absolute left-0 top-0 bottom-0 w-1 bg-slate-600"></div>
                            <h4 className="text-sm font-bold text-slate-300 mb-2 uppercase tracking-wide">Detailed Reasoning</h4>
                            <p className="text-sm text-slate-300 leading-relaxed">{evaluation.detailed_reasoning || "No reasoning provided."}</p>
                          </div>

                          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {/* Dimension Scores */}
                            {evaluation.dimension_scores && evaluation.dimension_scores.length > 0 && (
                              <div className="space-y-4">
                                <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wide">Dimension Scores</h4>
                                <div className="space-y-3">
                                  {evaluation.dimension_scores.map((dim, dIdx) => (
                                    <div key={dIdx} className="bg-navy-800/80 p-4 rounded-xl border border-slate-700/50 text-sm">
                                      <div className="flex justify-between items-center mb-2">
                                        <span className="font-semibold text-slate-200">{dim.dimension}</span>
                                        <span className="text-teal-400 font-bold bg-teal-900/30 px-2 py-0.5 rounded text-xs">{dim.score}/10</span>
                                      </div>
                                      <div className="w-full bg-slate-800 rounded-full h-2 mb-3 overflow-hidden border border-slate-700">
                                        <div className="bg-gradient-to-r from-teal-500 to-emerald-400 h-2 rounded-full" style={{ width: `${(dim.score / 10) * 100}%` }}></div>
                                      </div>
                                      <p className="text-xs text-slate-400 leading-normal">{dim.reasoning}</p>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Strengths & Weaknesses */}
                            <div className="space-y-6">
                              {evaluation.strengths && evaluation.strengths.length > 0 && (
                                <div className="bg-teal-900/10 border border-teal-500/20 p-4 rounded-xl">
                                  <h4 className="text-sm font-bold text-teal-accent uppercase tracking-wide mb-3 flex items-center gap-2"><CheckCircle2 className="w-4 h-4" /> Key Strengths</h4>
                                  <ul className="space-y-2">
                                    {evaluation.strengths.map((s, idx) => (
                                      <li key={idx} className="flex gap-2 text-sm text-slate-300">
                                        <span className="text-teal-500 mt-0.5">•</span>
                                        <span className="leading-snug">{s}</span>
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                              {evaluation.weaknesses && evaluation.weaknesses.length > 0 && (
                                <div className="bg-red-900/10 border border-red-500/20 p-4 rounded-xl">
                                  <h4 className="text-sm font-bold text-red-500 uppercase tracking-wide mb-3 flex items-center gap-2"><AlertCircle className="w-4 h-4" /> Areas for Improvement</h4>
                                  <ul className="space-y-2">
                                    {evaluation.weaknesses.map((w, idx) => (
                                      <li key={idx} className="flex gap-2 text-sm text-slate-300">
                                        <span className="text-red-500 mt-0.5">•</span>
                                        <span className="leading-snug">{w}</span>
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                              {evaluation.recommendation_note && (
                                <div className="mt-4 bg-blue-900/20 border border-blue-500/30 p-4 rounded-xl relative overflow-hidden">
                                  <div className="absolute top-0 left-0 w-1 h-full bg-blue-500"></div>
                                  <h4 className="text-xs font-bold text-blue-400 uppercase tracking-widest mb-2">Recommendation Note</h4>
                                  <p className="text-sm text-slate-300 italic">"{evaluation.recommendation_note}"</p>
                                </div>
                              )}
                            </div>
                          </div>
                        </div >
                      </details >
                    );
                  })
                  }
                </div >
              ) : (
                <div className="glass-card rounded-2xl overflow-hidden border-slate-700/50">
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm text-slate-300">
                      <thead className="text-xs text-slate-400 uppercase bg-slate-800/80 border-b border-slate-700/80 font-mono">
                        <tr>
                          <th className="px-6 py-4">Name</th>
                          <th className="px-6 py-4">Score</th>
                          <th className="px-6 py-4">Verdict</th>
                          <th className="px-6 py-4">Confidence</th>
                          <th className="px-6 py-4">Override</th>
                          <th className="px-6 py-4">Notes</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredAndSortedResults.map((result, idx) => {
                          const origIdx = results.findIndex(r => r === result);
                          const evaluation = result._evaluation || {};
                          const verdict = evaluation.verdict || "ERROR";
                          const nameField = candidateColumns.find(c => c.toLowerCase().includes('name')) || candidateColumns[0];
                          const candidateName = evaluation.candidate_name || result[nameField] || `Candidate ${idx + 1}`;

                          return (
                            <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-800/40 transition-colors">
                              <td className="px-6 py-4 font-medium text-white whitespace-nowrap">{candidateName}</td>
                              <td className="px-6 py-4">
                                {evaluation.overall_score !== undefined ? (
                                  <span className="font-bold">{evaluation.overall_score}<span className="text-slate-500 text-xs">/100</span></span>
                                ) : 'N/A'}
                              </td>
                              <td className="px-6 py-4">
                                <span className={`text-xs font-bold px-2 py-1 rounded border uppercase tracking-widest ${getVerdictColor(verdict)}`}>
                                  {verdict}
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                {evaluation.confidence || 'N/A'}
                              </td>
                              <td className="px-6 py-4">
                                <select
                                  value={verdict}
                                  onChange={(e) => updateVerdict(origIdx, e.target.value)}
                                  className="bg-navy-900 border border-slate-700 hover:border-slate-500 rounded p-1 text-xs text-slate-300 focus:outline-none focus:border-teal-accent transition-colors"
                                >
                                  <option value="SELECTED">SELECTED</option>
                                  <option value="ON HOLD">ON HOLD</option>
                                  <option value="REJECTED">REJECTED</option>
                                </select>
                              </td>
                              <td className="px-6 py-4 max-w-xs truncate" title={evaluation.recommendation_note}>
                                {evaluation.recommendation_note || 'None'}
                              </td>
                            </tr>
                          )
                        })}
                      </tbody>
                    </table>
                  </div>
                </div >
              )
            }
          </div >
        )
        }
      </div >
    </div >
  );
}
