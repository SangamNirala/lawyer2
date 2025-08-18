import React, { useEffect, useMemo, useState } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

const currency = (v, ccy = 'USD') => {
  if (typeof v !== 'number') return '-';
  try { return new Intl.NumberFormat(undefined, { style: 'currency', currency: ccy }).format(v); } catch { return v; }
};

const AcceptanceBar = ({ value }) => (
  <div className="w-full bg-gray-200 rounded h-2">
    <div className="bg-green-500 h-2 rounded" style={{ width: `${Math.round(value*100)}%` }} />
  </div>
);

export default function CounterOfferGenerator({ sessionId, goals = [], keyTerms = [], baseOffer }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [strategy, setStrategy] = useState(null);

  const [form, setForm] = useState({
    price: baseOffer?.price ?? '',
    currency: baseOffer?.currency ?? 'USD',
    term_months: baseOffer?.term_months ?? 12,
    payment_terms: baseOffer?.payment_terms ?? 'Net 30',
    goals: goals.join(', '),
    key_terms: keyTerms.join(', ')
  });

  const parsedGoals = useMemo(() => form.goals.split(',').map(s => s.trim()).filter(Boolean), [form.goals]);
  const parsedKeyTerms = useMemo(() => form.key_terms.split(',').map(s => s.trim()).filter(Boolean), [form.key_terms]);
  const baseOfferPayload = useMemo(() => ({
    price: form.price === '' ? undefined : Number(form.price),
    currency: form.currency,
    term_months: Number(form.term_months) || undefined,
    payment_terms: form.payment_terms || undefined
  }), [form]);

  const payload = useMemo(() => ({ session_id: sessionId, goals: parsedGoals, key_terms: parsedKeyTerms, base_offer: baseOfferPayload }), [sessionId, parsedGoals, parsedKeyTerms, baseOfferPayload]);

  const fetchStrategy = async () => {
    setLoading(true); setError(null);
    try {
      const res = await fetch(`${API}/api/ai-agents/contract-negotiation/generate-counter-offer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setStrategy(data);
    } catch (e) {
      setError(e.message || 'Failed to generate');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { if (sessionId) fetchStrategy(); }, [sessionId]);

  if (!sessionId) return <div className="text-sm text-gray-500">Session not ready.</div>;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Counter-Offer Generator</h3>
        <button onClick={fetchStrategy} disabled={loading} className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50">{loading ? 'Generating...' : 'Generate'}</button>
      </div>

      {/* Config form */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-2 text-xs">
        <div className="flex flex-col">
          <label className="text-gray-600 mb-1">Price</label>
          <input type="number" value={form.price} onChange={e => setForm(f => ({...f, price: e.target.value}))} className="border rounded px-2 py-1" placeholder="80000" />
        </div>
        <div className="flex flex-col">
          <label className="text-gray-600 mb-1">Currency</label>
          <select value={form.currency} onChange={e => setForm(f => ({...f, currency: e.target.value}))} className="border rounded px-2 py-1">
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
            <option value="GBP">GBP</option>
          </select>
        </div>
        <div className="flex flex-col">
          <label className="text-gray-600 mb-1">Term (months)</label>
          <input type="number" value={form.term_months} onChange={e => setForm(f => ({...f, term_months: e.target.value}))} className="border rounded px-2 py-1" placeholder="12" />
        </div>
        <div className="flex flex-col md:col-span-2">
          <label className="text-gray-600 mb-1">Payment Terms</label>
          <input value={form.payment_terms} onChange={e => setForm(f => ({...f, payment_terms: e.target.value}))} className="border rounded px-2 py-1" placeholder="Net 30" />
        </div>
        <div className="flex flex-col md:col-span-2">
          <label className="text-gray-600 mb-1">Goals (comma separated)</label>
          <input value={form.goals} onChange={e => setForm(f => ({...f, goals: e.target.value}))} className="border rounded px-2 py-1" placeholder="clarity, speed" />
        </div>
        <div className="flex flex-col md:col-span-3">
          <label className="text-gray-600 mb-1">Key Terms (comma separated)</label>
          <input value={form.key_terms} onChange={e => setForm(f => ({...f, key_terms: e.target.value}))} className="border rounded px-2 py-1" placeholder="payment terms, ip" />
        </div>
      </div>

      {error && <div className="text-sm text-red-600">{error}</div>}
      {!strategy ? (
        <div className="text-sm text-gray-500">No strategy yet.</div>
      ) : (
        <div className="space-y-4">
          {strategy.anchor_strategy && (
            <div className="p-3 bg-blue-50 border border-blue-100 rounded text-sm text-blue-800">{strategy.anchor_strategy}</div>
          )}
          {strategy.sequencing_plan && strategy.sequencing_plan.length > 0 && (
            <div className="p-3 bg-gray-50 border rounded">
              <div className="text-sm font-medium mb-2">Strategic Sequencing</div>
              <ol className="list-decimal pl-6 space-y-1 text-sm">
                {strategy.sequencing_plan.map((s, i) => (
                  <li key={i}><span className="font-semibold">{s.scenario}</span> — If rejected: {s.if_rejected}</li>
                ))}
              </ol>
            </div>
          )}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {strategy.scenarios.map((sc) => (
              <div key={sc.scenario_id} className="border rounded p-3 bg-white">
                <div className="text-sm font-semibold mb-1">{sc.name}</div>
                <div className="text-xs text-gray-500 mb-2">{sc.description}</div>
                {typeof sc.target_price === 'number' && (
                  <div className="text-sm mb-1">Target Price: <span className="font-mono">{currency(sc.target_price, baseOfferPayload?.currency)}</span></div>
                )}
                {typeof sc.price_impact === 'number' && (
                  <div className="text-xs text-gray-600 mb-1">Price Impact: {(sc.price_impact>=0?'+':'')}{Math.round(sc.price_impact*100)}%</div>
                )}
                {typeof sc.risk_adjusted_value === 'number' && (
                  <div className="text-xs text-gray-600 mb-2">Risk-Adjusted Value: {currency(sc.risk_adjusted_value, baseOfferPayload?.currency)}</div>
                )}
                <div className="text-xs text-gray-600 mb-2">Predicted Acceptance</div>
                <AcceptanceBar value={sc.predicted_acceptance} />
                <div className="text-xs text-gray-500 mt-1">{Math.round(sc.predicted_acceptance*100)}%</div>
                {sc.tactic && <div className="text-xs text-gray-700 mt-2"><span className="font-medium">Tactic:</span> {sc.tactic}</div>}
                {sc.narrative && <div className="text-xs text-gray-700 mt-1">{sc.narrative}</div>}
                {sc.asks?.length > 0 && (
                  <div className="mt-2">
                    <div className="text-xs font-medium">Asks</div>
                    <ul className="list-disc pl-5 text-xs text-gray-700 space-y-0.5">
                      {sc.asks.map((a, i) => <li key={i}>{a}</li>)}
                    </ul>
                  </div>
                )}
                {sc.concessions?.length > 0 && (
                  <div className="mt-2">
                    <div className="text-xs font-medium">Concessions</div>
                    <ul className="list-disc pl-5 text-xs text-gray-700 space-y-0.5">
                      {sc.concessions.map((c, i) => <li key={i}>{c}</li>)}
                    </ul>
                  </div>
                )}
                {sc.dependencies?.length > 0 && (
                  <div className="mt-2">
                    <div className="text-xs font-medium">Dependencies</div>
                    <ul className="list-disc pl-5 text-xs text-gray-700 space-y-0.5">
                      {sc.dependencies.map((d, i) => <li key={i}>{d}</li>)}
                    </ul>
                  </div>
                )}
                {sc.anchor_rationale && <div className="text-xs text-gray-600 mt-2">{sc.anchor_rationale}</div>}
              </div>
            ))}
          </div>
          {strategy.recommendations?.length > 0 && (
            <div className="p-3 border rounded bg-gray-50">
              <div className="text-sm font-medium mb-1">Recommendations</div>
              <ul className="list-disc pl-5 text-sm text-gray-700 space-y-1">
                {strategy.recommendations.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>
          )}
          {strategy.ai_insight && (
            <div className="text-xs text-purple-700 bg-purple-50 border border-purple-100 rounded p-2">{strategy.ai_insight}</div>
          )}
        </div>
      )}
    </div>
  );
}
