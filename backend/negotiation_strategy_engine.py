"""
Negotiation Strategy Engine - Phase 1 Core

Provides basic deterministic algorithms for:
- Position Analysis
- Counter-Offer Generation
- BATNA Analysis

Integrates opportunistically with Gemini/Groq if keys are present, but never blocks.
Stores results in MongoDB using session-based collections with UUIDs.
"""
from __future__ import annotations

import os
import uuid
import math
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase

# Optional AI clients (opportunistic)
try:
    import google.generativeai as genai  # type: ignore
except Exception:  # pragma: no cover
    genai = None

try:
    from groq import Groq  # type: ignore
except Exception:  # pragma: no cover
    Groq = None  # type: ignore

logger = logging.getLogger(__name__)

# ==========================
# Pydantic Models (Contracts)
# ==========================

class BaseOffer(BaseModel):
    price: Optional[float] = None
    currency: Optional[str] = "USD"
    term_months: Optional[int] = None
    payment_terms: Optional[str] = None  # e.g., "Net 30", "Milestones"
    other_key_terms: Dict[str, Any] = Field(default_factory=dict)

class PositionAnalysisInput(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    timeline_urgency: int = Field(5, ge=1, le=10)
    risk_tolerance: int = Field(5, ge=1, le=10)
    relationship_importance: int = Field(5, ge=1, le=10)
    goals: List[str] = Field(default_factory=list)
    key_terms: List[str] = Field(default_factory=list)
    base_offer: Optional[BaseOffer] = None

class PositionAnalysisResult(BaseModel):
    analysis_id: str
    session_id: str
    created_at: str
    strength_score: int
    leverage_score: float
    leverage_factors: List[str]
    risk_profile: Dict[str, Any]
    market_benchmarking: Dict[str, Any]
    timeline_impact: Dict[str, Any]
    ai_insight: Optional[str] = None

class CounterOfferInput(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    goals: List[str] = Field(default_factory=list)
    key_terms: List[str] = Field(default_factory=list)
    base_offer: Optional[BaseOffer] = None

class CounterOfferScenario(BaseModel):
    scenario_id: str
    name: str
    description: str
    concessions: List[str]
    asks: List[str]
    predicted_acceptance: float
    sequence_order: int
    target_price: Optional[float] = None
    price_impact: Optional[float] = None
    risk_adjusted_value: Optional[float] = None
    tactic: Optional[str] = None
    narrative: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    anchor_rationale: Optional[str] = None

class CounterOfferStrategyResult(BaseModel):
    strategy_id: str
    session_id: str
    created_at: str
    scenarios: List[CounterOfferScenario]
    recommendations: List[str]
    anchor_strategy: Optional[str] = None
    sequencing_plan: List[Dict[str, Any]] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    ai_insight: Optional[str] = None

class BATNAInput(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    base_offer: Optional[BaseOffer] = None
    goals: List[str] = Field(default_factory=list)

class BATNAAlternative(BaseModel):
    alt_id: str
    name: str
    description: str
    expected_value: float
    risk: float  # 0-1
    time_cost_months: int
    score: float

class BATNAResult(BaseModel):
    batna_id: str
    session_id: str
    created_at: str
    alternatives: List[BATNAAlternative]
    recommended_walkaway_point: float
    decision_notes: List[str]
    ai_insight: Optional[str] = None

class StrategySessionSummary(BaseModel):
    session_id: str
    latest_position_analysis: Optional[PositionAnalysisResult] = None
    latest_counter_offer: Optional[CounterOfferStrategyResult] = None
    latest_batna: Optional[BATNAResult] = None

# ==========================
# Engine
# ==========================

class NegotiationStrategyEngine:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self._gemini_initialized = False
        self._groq_client = None
        self._maybe_init_ai()

    def _maybe_init_ai(self):
        try:
            gem_key = os.environ.get("GEMINI_API_KEY")
            if gem_key and genai:
                genai.configure(api_key=gem_key)
                self._gemini_initialized = True
                logger.info("✅ StrategyEngine: Gemini ready")
        except Exception as e:  # pragma: no cover
            logger.warning(f"⚠️ StrategyEngine: Gemini init failed: {e}")
            self._gemini_initialized = False

        try:
            groq_key = os.environ.get("GROQ_API_KEY")
            if groq_key and Groq:
                self._groq_client = Groq(api_key=groq_key)
                logger.info("✅ StrategyEngine: Groq ready")
        except Exception as e:  # pragma: no cover
            logger.warning(f"⚠️ StrategyEngine: Groq init failed: {e}")
            self._groq_client = None

    async def initialize_collections(self):
        try:
            await self.db.position_analyses.create_index([("session_id", 1), ("created_at", -1)])
            await self.db.counter_offer_strategies.create_index([("session_id", 1), ("created_at", -1)])
            await self.db.batna_analyses.create_index([("session_id", 1), ("created_at", -1)])
            await self.db.strategy_sessions.create_index([("session_id", 1)], unique=True)
            logger.info("✅ StrategyEngine: collections initialized")
        except Exception as e:
            logger.error(f"❌ StrategyEngine: init collections error: {e}")

    async def _get_ai_insight(self, prompt: str) -> Optional[str]:
        # Opportunistic: try Gemini, then Groq, else None
        try:
            if self._gemini_initialized and genai:
                resp = await self._run_in_thread(genai.GenerativeModel('gemini-1.5-pro').generate_content, prompt)
                if getattr(resp, 'text', None):
                    return str(resp.text)[:600]
        except Exception as e:
            logger.debug(f"Gemini insight failed: {e}")
        try:
            if self._groq_client:
                comp = await self._run_in_thread(self._groq_client.chat.completions.create,
                                                model="llama-3.3-70b-versatile",
                                                messages=[{"role": "user", "content": prompt}],
                                                temperature=0.1,
                                                max_tokens=256)
                content = comp.choices[0].message.content if comp and comp.choices else None
                if content:
                    return str(content)[:600]
        except Exception as e:
            logger.debug(f"Groq insight failed: {e}")
        return None

    async def _run_in_thread(self, fn, *args, **kwargs):
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: fn(*args, **kwargs))

    # -------------
    # Heuristics
    # -------------

    async def analyze_position(self, data: PositionAnalysisInput) -> PositionAnalysisResult:
        # Base strength on balanced factors
        strength = 5
        # Higher risk tolerance increases willingness to push
        strength += (data.risk_tolerance - 5) * 0.4
        # Higher urgency reduces strength (time pressure)
        strength -= (data.timeline_urgency - 5) * 0.5
        # Higher relationship importance tempers aggressiveness
        strength -= (data.relationship_importance - 5) * 0.3
        strength = max(1, min(10, int(round(strength))))

        # Leverage score (0-1)
        leverage_components: List[str] = []
        leverage = 0.5
        if any(k in (data.key_terms or []) for k in ["exclusivity", "ip", "termination"]):
            leverage += 0.1
            leverage_components.append("Critical terms priority identified")
        if data.base_offer and data.base_offer.price:
            leverage += 0.05
            leverage_components.append("Monetary anchor established")
        if len(data.goals) >= 2:
            leverage += 0.05
            leverage_components.append("Clear multi-goal strategy")
        leverage = max(0.0, min(1.0, round(leverage, 2)))

        # Risk profiling
        risks: List[str] = []
        mitigations: List[str] = []
        if data.base_offer and (data.base_offer.payment_terms or "" ).lower().startswith("net 30"):
            risks.append("Cash flow timing risk")
            mitigations.append("Consider milestone payments or shorter net terms")
        if "liability cap" not in [t.lower() for t in (data.key_terms or [])]:
            risks.append("Uncapped liability exposure")
            mitigations.append("Introduce liability cap at 1x-2x contract value")
        if "termination" not in [t.lower() for t in (data.key_terms or [])]:
            risks.append("Weak termination rights")
            mitigations.append("Add mutual termination for cause and convenience with notice")
        risk_profile = {
            "risk_level": "medium" if len(risks) <= 2 else "high",
            "key_risks": risks[:5],
            "mitigations": mitigations[:5]
        }

        # Market benchmarking (simplified)
        market = {
            "payment_terms": "Net 30-45 typical for SMB; milestones common for projects",
            "liability_cap": "1x-2x annual fees typical; carve-outs for IP/confidentiality",
            "termination_notice": "30 days common; longer for enterprise"
        }

        # Timeline impact
        timeline = {
            "urgency": data.timeline_urgency,
            "impact": "high" if data.timeline_urgency >= 8 else "moderate" if data.timeline_urgency >= 5 else "low",
            "recommendations": [
                "Sequence negotiations starting with non-monetary terms",
                "Prepare fallback clauses for time-sensitive items"
            ]
        }

        # Optional AI insight
        ai_note = await self._get_ai_insight(
            f"Provide one paragraph of negotiation position insight based on: goals={data.goals}, key_terms={data.key_terms}, urgency={data.timeline_urgency}, risk_tolerance={data.risk_tolerance}, relationship_importance={data.relationship_importance}. Keep concise and actionable.")

        result = PositionAnalysisResult(
            analysis_id=str(uuid.uuid4()),
            session_id=data.session_id,
            created_at=datetime.utcnow().isoformat(),
            strength_score=strength,
            leverage_score=leverage,
            leverage_factors=leverage_components,
            risk_profile=risk_profile,
            market_benchmarking=market,
            timeline_impact=timeline,
            ai_insight=ai_note
        )

        # Persist
        await self.db.position_analyses.insert_one(result.model_dump())
        await self._upsert_session(data.session_id, {"last_position_analysis_id": result.analysis_id})
        return result

    async def generate_counter_offers(self, data: CounterOfferInput) -> CounterOfferStrategyResult:
        # Advanced: build scenarios based on base price, urgency, and goals
        base_price = data.base_offer.price if (data.base_offer and data.base_offer.price) else None
        last_pos = await self.db.position_analyses.find_one({"session_id": data.session_id}, sort=[("created_at", -1)])
        urgency = (last_pos or {}).get("timeline_impact", {}).get("urgency", 5)
        leverage = (last_pos or {}).get("leverage_score", 0.5)
        strength = (last_pos or {}).get("strength_score", 5)

        # Determine anchor and bands
        # If no base_price, we can only provide qualitative asks without numeric target_price
        def target_for(mult: float) -> Optional[float]:
            return round(base_price * mult, 2) if base_price else None

        # Acceptance probability baseline using logistic-ish heuristic from leverage, strength, urgency
        def accept_base(mult: float) -> float:
            # Lower urgency and higher leverage/strength increases predicted acceptance
            raw = 0.55 + 0.15*(leverage-0.5)*2 + 0.1*((strength-5)/5) - 0.08*((urgency-5)/5) - 0.07*(mult-1.0)
            return max(0.05, min(0.95, raw))

        def scenario(name: str, order: int, mult: float, conces: List[str], asks: List[str], tactic: str, narrative: str, deps: List[str], anchor_rationale: Optional[str]) -> CounterOfferScenario:
            p = accept_base(mult)
            price = target_for(mult)
            riv = None
            if price is not None:
                # risk-adjusted value approx: price * leverage weighting
                riv = round(price * (0.5 + leverage/2), 2)
            return CounterOfferScenario(
                scenario_id=str(uuid.uuid4()),
                name=name,
                description=f"{name} trade-off package",
                concessions=conces,
                asks=asks,
                predicted_acceptance=p,
                sequence_order=order,
                target_price=price,
                price_impact=(None if (price is None or base_price is None) else round((price-base_price)/base_price, 3)),
                risk_adjusted_value=riv,
                tactic=tactic,
                narrative=narrative,
                dependencies=deps,
                anchor_rationale=anchor_rationale
            )

        scenarios: List[CounterOfferScenario] = []
        # Stretch (High anchor)
        scenarios.append(scenario(
            "Stretch", 1, 1.12,
            ["Premium service tier bundling"],
            ["Shorter payment terms (Net 15)", "IP ownership clarification", "Annual prepay"],
            tactic="High-anchor then trade-down",
            narrative="Open strong to set value anchor; be ready to exchange monetary asks for structural wins",
            deps=["Position analysis complete"],
            anchor_rationale="Signals confidence; creates room for principled concessions"
        ))
        # Balanced (Principled midpoint)
        scenarios.append(scenario(
            "Balanced", 2, 1.00,
            ["Scope optimization", "Standard SLAs"],
            ["Milestone payments", "Termination for convenience with notice"],
            tactic="Principled reciprocity",
            narrative="Fair compromise: trade limited price flexibility for stronger protections",
            deps=["Counterparty acknowledges scope"],
            anchor_rationale="Aligns with market; supports collaborative tone"
        ))
        # Conservative (Fallback)
        scenarios.append(scenario(
            "Conservative", 3, 0.94,
            ["Minor price concession", "Extended payment terms (Net 45)"],
            ["Longer commitment (12-18 months)", "Mutual liability cap at 1x fees"],
            tactic="Graceful fallback",
            narrative="Provide face-saving path to agreement while protecting core value",
            deps=["Deadlock on Balanced"],
            anchor_rationale="Preserves relationship and accelerates closure under time pressure"
        ))

        # Strategic sequencing plan
        sequencing_plan = [
            {"order": 1, "scenario": "Stretch", "if_rejected": "Move to Balanced; offer non-monetary concessions first"},
            {"order": 2, "scenario": "Balanced", "if_rejected": "Offer Conservative with conditional commitments"},
            {"order": 3, "scenario": "Conservative", "if_rejected": "Escalate to BATNA review and walkaway check"},
        ]

        # Recommendations tailored by urgency/leverage
        recs = []
        if urgency >= 8:
            recs.append("Time-sensitive: compress negotiation rounds; pre-prepare final form of Balanced scenario")
        if leverage >= 0.7:
            recs.append("Leverage advantage: maintain Stretch anchor longer; trade only non-core terms early")
        if strength <= 4:
            recs.append("Lower strength: emphasize relationship and risk mitigation; anchor closer to Balanced")
        if not recs:
            recs = [
                "Open with Stretch to set anchor, aim to close on Balanced, keep Conservative as time-bound fallback",
                "Link price concessions to increased term length or accelerated payments",
                "Sequence non-monetary wins first to build momentum"
            ]

        ai_note = await self._get_ai_insight(
            f"Given goals={data.goals} and terms={data.key_terms}, craft 2-4 tactical counter-offer pointers that emphasize sequencing, reciprocity, and anchors. Keep concise.")

        # Metrics snapshot
        metrics = {
            "avg_predicted_acceptance": round(sum(s.predicted_acceptance for s in scenarios)/len(scenarios), 3),
            "stretch_anchor": scenarios[0].target_price,
            "balanced_target": scenarios[1].target_price,
            "conservative_target": scenarios[2].target_price,
        }

        result = CounterOfferStrategyResult(
            strategy_id=str(uuid.uuid4()),
            session_id=data.session_id,
            created_at=datetime.utcnow().isoformat(),
            scenarios=scenarios,
            recommendations=recs,
            anchor_strategy="Start with Stretch anchor; trade to Balanced; reserve Conservative for deadline pressure",
            sequencing_plan=sequencing_plan,
            metrics=metrics,
            ai_insight=ai_note
        )

        await self.db.counter_offer_strategies.insert_one(result.model_dump())
        await self._upsert_session(data.session_id, {"last_counter_offer_id": result.strategy_id})
        return result

    async def analyze_batna(self, data: BATNAInput) -> BATNAResult:
        # Generate 3 generic alternatives
        contract_value = data.base_offer.price if (data.base_offer and data.base_offer.price) else 0.0

        alts = []
        def alt(name: str, desc: str, ev: float, risk: float, months: int) -> BATNAAlternative:
            score = max(0.0, min(1.0, round(ev * (1.0 - risk) / (contract_value + 1e-6 if contract_value else max(1.0, ev)), 3)))
            return BATNAAlternative(
                alt_id=str(uuid.uuid4()),
                name=name,
                description=desc,
                expected_value=round(ev, 2),
                risk=max(0.0, min(1.0, risk)),
                time_cost_months=months,
                score=score
            )

        alts.append(alt("Alternative Supplier", "Explore competitor proposals to create leverage", contract_value * 0.9 if contract_value else 50000.0, 0.35, 2))
        alts.append(alt("Delay & Re-negotiate", "Extend timeline to improve terms later", contract_value * 0.8 if contract_value else 30000.0, 0.25, 3))
        alts.append(alt("In-House Solution", "Build internally to avoid unfavorable terms", contract_value * 0.7 if contract_value else 20000.0, 0.5, 6))

        # Walkaway point: pick 80% of best risk-adjusted expected value
        best = max(alts, key=lambda a: a.expected_value * (1 - a.risk))
        walkaway = round(best.expected_value * (1 - best.risk) * 0.8, 2)
        notes = [
            f"Walk away if current deal EV (risk-adjusted) falls below {walkaway}",
            "Preserve relationship where possible if relationship_importance is high",
            "Consider opportunity cost relative to timeline constraints"
        ]

        ai_note = await self._get_ai_insight(
            f"Briefly evaluate BATNA alternatives {[(a.name, a.expected_value, a.risk) for a in alts]} and suggest a walkaway rationale in 2 sentences.")

        result = BATNAResult(
            batna_id=str(uuid.uuid4()),
            session_id=data.session_id,
            created_at=datetime.utcnow().isoformat(),
            alternatives=alts,
            recommended_walkaway_point=walkaway,
            decision_notes=notes,
            ai_insight=ai_note
        )

        await self.db.batna_analyses.insert_one(result.model_dump())
        await self._upsert_session(data.session_id, {"last_batna_id": result.batna_id})
        return result

    async def get_strategy_session(self, session_id: str) -> StrategySessionSummary:
        pos = await self.db.position_analyses.find_one({"session_id": session_id}, sort=[("created_at", -1)])
        cnt = await self.db.counter_offer_strategies.find_one({"session_id": session_id}, sort=[("created_at", -1)])
        bat = await self.db.batna_analyses.find_one({"session_id": session_id}, sort=[("created_at", -1)])

        def to_model(model_cls, data):
            return model_cls(**data) if data else None

        return StrategySessionSummary(
            session_id=session_id,
            latest_position_analysis=to_model(PositionAnalysisResult, pos),
            latest_counter_offer=to_model(CounterOfferStrategyResult, cnt),
            latest_batna=to_model(BATNAResult, bat),
        )

    async def _upsert_session(self, session_id: str, updates: Dict[str, Any]):
        updates = {**updates, "session_id": session_id, "updated_at": datetime.utcnow().isoformat()}
        await self.db.strategy_sessions.update_one({"session_id": session_id}, {"$set": updates}, upsert=True)


# Global engine instance
_strategy_engine: Optional[NegotiationStrategyEngine] = None

async def get_strategy_engine(db: AsyncIOMotorDatabase) -> NegotiationStrategyEngine:
    global _strategy_engine
    if _strategy_engine is None:
        _strategy_engine = NegotiationStrategyEngine(db)
        await _strategy_engine.initialize_collections()
        logger.info("🚀 StrategyEngine instance created and initialized")
    return _strategy_engine