import React from 'react';
import { AlertCircle } from 'lucide-react';

export default function DisclaimerBanner() {
  return (
    <div className="bg-amber-50 border-y border-amber-200 py-2 px-4 text-xs text-amber-900">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-amber-700 shrink-0" />
          <span>
            <strong>Legal Information Notice:</strong> LawForce is an AI legal research and statutory information assistant grounded strictly in verified Pakistani laws. It does not provide formal legal advice or substitute for representation by a licensed Pakistani advocate.
          </span>
        </div>
        <span className="hidden sm:inline-block text-[11px] font-semibold text-amber-800 shrink-0">
          Pakistan Bar Council Ethics Adherent
        </span>
      </div>
    </div>
  );
}
