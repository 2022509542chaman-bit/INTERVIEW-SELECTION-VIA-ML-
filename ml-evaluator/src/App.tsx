/**
 * App.tsx
 * Main application with routing between evaluation form and dashboard
 */

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { BarChart3, Home, Settings } from 'lucide-react';
import { EvaluationForm } from './components/EvaluationForm';
import { ScoreCard } from './components/ScoreCard';
import { Dashboard } from './components/Dashboard';
import './App.css';

const API_BASE_URL = '';

interface EvaluationResult {
  id: number;
  name: string;
  total_score: number;
  decision: string;
  grade: string;
  star_rating: number;
  confidence: number;
  coverage: number;
  keyword_match_rate: number;
  breakdown: any[];
  recommendation: string;
  borderline_analysis?: any;
}

function EvaluationPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<EvaluationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (candidateName: string, responseText: string) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      // Create FormData for file upload
      const formData = new FormData();

      // Create a simple CSV with the candidate data
      const csvContent = `Name,Response\n"${candidateName}","${responseText.replace(/"/g, '""')}"`;
      const blob = new Blob([csvContent], { type: 'text/csv' });
      formData.append('candidates_file', blob, 'candidates.csv');

      // Create a simple rubric
      const rubricContent = `Senior Backend Software Engineer Evaluation Rubric

Evaluation Criteria:
- System Design & Architecture
- Backend Development Skills
- Database & Data Management
- Message Queue & Event Streaming
- Containerization & Orchestration
- Testing & Code Quality
- DevOps & Deployment

Interview Response: ${candidateName}'s Answer`;
      const rubricBlob = new Blob([rubricContent], { type: 'text/plain' });
      formData.append('rubric_file', rubricBlob, 'rubric.txt');
      formData.append('batch_name', `Individual: ${candidateName}`);

      const apiResponse = await fetch(`${API_BASE_URL}/evaluate`, {
        method: 'POST',
        body: formData,
      });

      if (!apiResponse.ok) {
        throw new Error(`Evaluation failed: ${apiResponse.statusText}`);
      }

      const data = await apiResponse.json();
      if (data.data && data.data.length > 0) {
        setResult(data.data[0]);
      } else {
        setError('No evaluation results returned');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      console.error('Evaluation error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
      <div className="container mx-auto">
        {!result ? (
          <EvaluationForm onSubmit={handleSubmit} isLoading={isLoading} />
        ) : (
          <div className="space-y-6">
            <button
              onClick={() => setResult(null)}
              className="text-blue-600 hover:text-blue-800 font-semibold mb-4 flex items-center gap-2"
            >
              ← Evaluate Another Candidate
            </button>
            <ScoreCard
              candidateName={result.name}
              score={result.total_score}
              decision={result.decision}
              grade={result.grade}
              starRating={result.star_rating}
              confidence={result.confidence}
              coverage={result.coverage}
              keywordMatch={result.keyword_match_rate}
              breakdown={result.breakdown}
              recommendation={result.recommendation}
              borderlineAnalysis={result.borderline_analysis}
            />
          </div>
        )}

        {error && (
          <div className="mt-6 max-w-2xl mx-auto bg-red-50 border-2 border-red-300 rounded-lg p-4">
            <p className="text-red-800 font-semibold">Error: {error}</p>
          </div>
        )}
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Navigation */}
        <nav className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center gap-8">
                <Link to="/" className="flex items-center gap-2 text-xl font-bold text-gray-900">
                  <BarChart3 size={28} className="text-blue-600" />
                  ML Evaluator
                </Link>
                <div className="hidden md:flex gap-6">
                  <Link
                    to="/"
                    className="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition font-medium"
                  >
                    <Home size={20} />
                    Evaluate
                  </Link>
                  <Link
                    to="/dashboard"
                    className="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition font-medium"
                  >
                    <BarChart3 size={20} />
                    Dashboard
                  </Link>
                </div>
              </div>
              <div className="text-sm text-gray-600">
                API: <span className="font-mono bg-gray-100 px-2 py-1 rounded">{API_BASE_URL}</span>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<EvaluationPage />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 py-6 text-center text-gray-600 text-sm">
          <p>ML Evaluator Platform © 2025 | Senior Backend Engineer Selection</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
