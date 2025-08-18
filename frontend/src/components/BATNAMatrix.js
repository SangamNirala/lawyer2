import React, { useEffect, useMemo, useState } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

const currency = (v, ccy = 'USD') => {
  if (typeof v !== 'number') return '-';
  try { return new Intl.NumberFormat(undefined, { style: 'currency', currency: ccy }).format(v); } catch { return v; }
};

function TinyTree({ tree }) {
  if (!tree) return null;
  return (
    <div className="text-xs">
      <div className="font-semibold mb-1">{tree.name}</div>
      <ul className="list-disc pl-5 space-y-1">
        {tree.children?.map((child, i) => (
          <li key={i}>
            <span className="font-medium">{child.name}</span>
            {typeof child.value === 'number' && <span className="ml-1 text-gray-600">({child.value})</span>}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function BATNAMatrix({ sessionId, baseOffer }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [batna, setBatna] = useState(null);

  const payload = useMemo(() => ({ session_id: sessionId, base_offer: baseOffer }), [sessionId, baseOffer]);

  const fetchBATNA = async () => {
    setLoading(true); setError(null);
    try {
      const res = await fetch(`${API}/api/ai-agents/contract-negotiation/batna-analysis`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setBatna(data);
    } catch (e) {
      setError(e.message || 'Failed to analyze');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { if (sessionId) fetchBATNA(); }, [sessionId]);

  if (!sessionId) return <div className="text-sm text-gray-500">Session not ready.</div>;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">BATNA Analysis</h3>
        <button onClick={fetchBATNA} disabled={loading} className="px-3 py-1.5 text-sm bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50">{loading ? 'Analyzing...' : 'Recalculate'}</button>
      </div>
      {error && <div className="text-sm text-red-600">{error}</div>}
      {!batna ? (
        <div className="text-sm text-gray-500">No BATNA yet.</div>
      ) : (
        <div className="space-y-4">
          <div className="p-3 border rounded bg-purple-50 text-purple-800 text-sm">
            Recommended walkaway (risk-adjusted): <span className="font-mono">{currency(batna.recommended_walkaway_point, baseOffer?.currency)}</span>
          </div>

          {batna.metrics && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
              <div className="p-2 border rounded bg-white">Best Alternative: <span className="font-semibold">{batna.metrics.best_alternative}</span></div>
              <div className="p-2 border rounded bg-white">Best Score: <span className="font-semibold">{batna.metrics.best_score}</span></div>
              <div className="p-2 border rounded bg-white">Avg Risk: <span className="font-semibold">{batna.metrics.avg_risk}</span></div>
              <div className="p-2 border rounded bg-white">Avg ROI: <span className="font-semibold">{batna.metrics.avg_roi}</span></div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {batna.alternatives.map((alt) => (
              <div key={alt.alt_id} className="border rounded p-3 bg-white">
                <div className="text-sm font-semibold mb-1">{alt.name}</div>
                <div className="text-xs text-gray-500 mb-2">{alt.description}</div>
                <div className="text-xs">Expected Value: <span className="font-mono">{currency(alt.expected_value, baseOffer?.currency)}</span></div>
                <div className="text-xs">Risk: {(alt.risk*100).toFixed(0)}%</div>
                <div className="text-xs">Time Cost: {alt.time_cost_months} months</div>
                {typeof alt.roi === 'number' && <div className="text-xs">ROI vs current: {(alt.roi*100).toFixed(1)}%</div>}
                {typeof alt.risk_adjusted_value === 'number' && <div className="text-xs">Risk-Adjusted: {currency(alt.risk_adjusted_value, baseOffer?.currency)}</div>}
                {typeof alt.relationship_impact === 'number' && <div className="text-xs">Relationship Impact: {alt.relationship_impact}</div>}
                {alt.scenarios && (
                  <div className="mt-2 text-xs">
                    <div className="font-medium">Scenarios</div>
                    <div className="grid grid-cols-3 gap-2">
                      {['best','likely','worst'].map(k => (
                        <div key={k} className="border rounded p-1">
                          <div className="font-semibold capitalize">{k}</div>
                          <div>Val: {currency(alt.scenarios[k]?.value, baseOffer?.currency)}</div>
                          <div>Prob: {(alt.scenarios[k]?.prob*100).toFixed(0)}%</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {batna.decision_tree && (
            <div className="p-3 border rounded bg-gray-50">
              <div className="text-sm font-medium mb-2">Decision Tree</div>
              <TinyTree tree={batna.decision_tree} />
            </div>
          )}

          {batna.decision_notes?.length > 0 && (
            <div className="p-3 border rounded bg-white">
              <div className="text-sm font-medium mb-1">Decision Notes</div>
              <ul className="list-disc pl-5 text-sm text-gray-700 space-y-1">
                {batna.decision_notes.map((n, i) => <li key={i}>{n}</li>)}
              </ul>
            </div>
          )}
          {batna.ai_insight && (
            <div className="text-xs text-purple-700 bg-purple-50 border border-purple-100 rounded p-2">{batna.ai_insight}</div>
          )}
        </div>
      )}
    </div>
  );
}
