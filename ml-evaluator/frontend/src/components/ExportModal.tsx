import { useState } from 'react';
import { X, Download, FileText, AlertCircle } from 'lucide-react';

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onExportCSV: () => void;
  title?: string;
  resultsCount?: number;
}

export function ExportModal({
  isOpen,
  onClose,
  onExportCSV,
  title = 'Export Results',
  resultsCount = 0
}: ExportModalProps) {
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async () => {
    setIsExporting(true);
    try {
      await onExportCSV();
    } finally {
      setIsExporting(false);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 transition-opacity"
        onClick={onClose}
      />

      {/* Modal Container */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="w-full max-w-md bg-gradient-to-br from-slate-900 to-slate-950 rounded-2xl shadow-2xl border border-slate-700 overflow-hidden animate-in fade-in scale-in-95 duration-300">
          {/* Header */}
          <div className="relative px-6 py-8 border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <Download className="w-5 h-5 text-blue-400" />
                  {title}
                </h2>
                <p className="text-sm text-slate-400 mt-1">
                  Export your evaluation results in multiple formats
                </p>
              </div>
              <button
                onClick={onClose}
                className="text-slate-400 hover:text-slate-200 transition-colors p-1 hover:bg-slate-700 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="px-6 py-8 space-y-6">
            {/* Info Alert */}
            <div className="flex gap-3 p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
              <AlertCircle className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm text-blue-300 font-medium">Ready to export</p>
                <p className="text-xs text-blue-200/70 mt-1">
                  {resultsCount} candidates will be included in the export
                </p>
              </div>
            </div>

            {/* CSV Export Option */}
            <div className="space-y-3">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Export Format</p>
              <button
                onClick={handleExport}
                disabled={isExporting}
                className="w-full flex items-center gap-4 p-4 rounded-xl bg-gradient-to-r from-blue-600/20 to-cyan-600/20 border border-blue-500/30 hover:border-blue-400/50 hover:from-blue-600/30 hover:to-cyan-600/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
              >
                <div className="p-3 rounded-lg bg-blue-500/20 group-hover:bg-blue-500/30 transition-colors">
                  <FileText className="w-5 h-5 text-blue-400" />
                </div>
                <div className="flex-1 text-left">
                  <p className="text-sm font-semibold text-white">CSV Report</p>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Comprehensive spreadsheet with all evaluation details
                  </p>
                </div>
                {isExporting ? (
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-400">Exporting...</span>
                    <div className="w-4 h-4 rounded-full border-2 border-blue-400 border-t-transparent animate-spin" />
                  </div>
                ) : (
                  <Download className="w-5 h-5 text-slate-400 group-hover:text-blue-400 transition-colors" />
                )}
              </button>
            </div>

            {/* Features List */}
            <div className="space-y-2">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">What's Included</p>
              <ul className="space-y-2">
                {[
                  'Overall scores and rankings',
                  'Detailed performance breakdown',
                  'Skills and keyword analysis',
                  'Decision recommendations',
                  'Confidence metrics',
                  'Historical comparison data'
                ].map((feature, idx) => (
                  <li key={idx} className="flex items-center gap-2 text-sm text-slate-300">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-400/60" />
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Footer */}
          <div className="px-6 py-4 bg-slate-900/30 border-t border-slate-700 flex gap-3">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-sm transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
