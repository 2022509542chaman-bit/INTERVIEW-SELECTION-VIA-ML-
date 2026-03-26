/**
 * ScoreCard.tsx
 * Displays a candidate's evaluation result with animated gauge, decision, and breakdown
 */

import React, { useEffect, useState } from 'react';
import { CheckCircle, AlertCircle, XCircle, TrendingUp, Award, Brain, Target } from 'lucide-react';

interface BreakdownItem {
  rubric_point: string;
  score: number;
  passed: boolean;
}

interface ScoreCardProps {
  candidateName: string;
  score: number;
  decision: string;
  grade: string;
  starRating: number;
  confidence: number;
  coverage: number;
  keywordMatch: number;
  breakdown: BreakdownItem[];
  recommendation: string;
  borderlineAnalysis?: any;
}

const getDecisionColor = (decision: string) => {
  switch (decision) {
    case 'SELECTED':
      return { bg: 'bg-green-50', border: 'border-green-300', badge: 'bg-green-100 text-green-800', text: 'text-green-700' };
    case 'BORDERLINE':
      return { bg: 'bg-yellow-50', border: 'border-yellow-300', badge: 'bg-yellow-100 text-yellow-800', text: 'text-yellow-700' };
    case 'REJECTED':
      return { bg: 'bg-orange-50', border: 'border-orange-300', badge: 'bg-orange-100 text-orange-800', text: 'text-orange-700' };
    case 'HARD_REJECTED':
      return { bg: 'bg-red-50', border: 'border-red-300', badge: 'bg-red-100 text-red-800', text: 'text-red-700' };
    default:
      return { bg: 'bg-gray-50', border: 'border-gray-300', badge: 'bg-gray-100 text-gray-800', text: 'text-gray-700' };
  }
};

const DecisionIcon = ({ decision }: { decision: string }) => {
  switch (decision) {
    case 'SELECTED':
      return <CheckCircle className="w-8 h-8 text-green-600" />;
    case 'BORDERLINE':
      return <AlertCircle className="w-8 h-8 text-yellow-600" />;
    case 'REJECTED':
    case 'HARD_REJECTED':
      return <XCircle className="w-8 h-8 text-red-600" />;
    default:
      return null;
  }
};

const AnimatedGauge = ({ score, animated = true }: { score: number; animated?: boolean }) => {
  const [displayScore, setDisplayScore] = useState(animated ? 0 : score);

  useEffect(() => {
    if (!animated) return;
    let current = 0;
    const interval = setInterval(() => {
      current += Math.ceil(score / 30);
      if (current >= score) {
        current = score;
        clearInterval(interval);
      }
      setDisplayScore(current);
    }, 30);
    return () => clearInterval(interval);
  }, [score, animated]);

  const getGaugeColor = () => {
    if (displayScore >= 65) return '#10b981';
    if (displayScore >= 40) return '#f59e0b';
    if (displayScore >= 18) return '#ef4444';
    return '#7c2d12';
  };

  return (
    <div className="flex flex-col items-center justify-center py-4">
      <div className="relative w-48 h-48">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 200 200">
          {/* Background circle */}
          <circle cx="100" cy="100" r="90" fill="none" stroke="#e5e7eb" strokeWidth="12" />
          {/* Progress circle */}
          <circle
            cx="100"
            cy="100"
            r="90"
            fill="none"
            stroke={getGaugeColor()}
            strokeWidth="12"
            strokeDasharray={`${(displayScore / 100) * 565.5} 565.5`}
            className="transition-all duration-300"
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className="text-5xl font-bold" style={{ color: getGaugeColor() }}>
            {Math.round(displayScore)}
          </div>
          <div className="text-gray-600 text-sm">%</div>
        </div>
      </div>
    </div>
  );
};

export const ScoreCard: React.FC<ScoreCardProps> = ({
  candidateName,
  score,
  decision,
  grade,
  starRating,
  confidence,
  coverage,
  keywordMatch,
  breakdown,
  recommendation,
  borderlineAnalysis,
}) => {
  const colors = getDecisionColor(decision);

  return (
    <div className={`${colors.bg} border-2 ${colors.border} rounded-lg p-6 max-w-4xl mx-auto`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-gray-900 mb-1">{candidateName}</h2>
          <div className="flex items-center gap-4">
            <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-semibold ${colors.badge}`}>
              <DecisionIcon decision={decision} />
              {decision}
            </span>
            <span className="text-lg font-semibold text-gray-700">Grade: {grade}</span>
            <span className="text-lg">{'⭐'.repeat(starRating)}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gauge */}
        <div className="flex items-center justify-center">
          <AnimatedGauge score={score} />
        </div>

        {/* Key Metrics */}
        <div className="space-y-4">
          <div className="bg-white rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Confidence</span>
              <span className="text-2xl font-bold text-gray-900">{confidence}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all"
                style={{ width: `${confidence}%` }}
              ></div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white rounded-lg p-4">
              <div className="flex items-center gap-2 mb-1">
                <Brain size={16} className="text-purple-600" />
                <span className="text-xs font-medium text-gray-600">Coverage</span>
              </div>
              <div className="text-2xl font-bold text-gray-900">{coverage.toFixed(1)}%</div>
            </div>

            <div className="bg-white rounded-lg p-4">
              <div className="flex items-center gap-2 mb-1">
                <Target size={16} className="text-orange-600" />
                <span className="text-xs font-medium text-gray-600">Keywords</span>
              </div>
              <div className="text-2xl font-bold text-gray-900">{keywordMatch.toFixed(1)}%</div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Award size={16} className="text-amber-600" />
              <span className="text-sm font-medium text-gray-700">Recommendation</span>
            </div>
            <p className="text-sm text-gray-700">{recommendation}</p>
          </div>
        </div>
      </div>

      {/* Breakdown */}
      {breakdown && breakdown.length > 0 && (
        <div className="mt-6 pt-6 border-t-2 border-gray-300">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Rubric Breakdown</h3>
          <div className="space-y-3">
            {breakdown
              .sort((a, b) => b.score - a.score)
              .slice(0, 6)
              .map((item, idx) => (
                <div key={idx} className="bg-white rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-900 line-clamp-2">
                      {item.rubric_point}
                    </span>
                    <span className={`text-sm font-bold ${item.passed ? 'text-green-600' : 'text-red-600'}`}>
                      {(item.score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${item.passed ? 'bg-green-500' : 'bg-red-500'}`}
                      style={{ width: `${item.score * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Borderline Analysis */}
      {borderlineAnalysis && decision === 'BORDERLINE' && (
        <div className="mt-6 pt-6 border-t-2 border-yellow-300 bg-yellow-100 rounded-lg p-4">
          <h3 className="font-semibold text-yellow-900 mb-3">Borderline Analysis</h3>
          <div className="space-y-2 text-sm text-yellow-800">
            <p>
              <strong>Distance to Hire:</strong> {borderlineAnalysis.proximity_to_hire}% of threshold
            </p>
            <p>
              <strong>Gap:</strong> {borderlineAnalysis.gap_percentage}%
            </p>
            <p>
              <strong>Assessment:</strong> {borderlineAnalysis.verdict}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
