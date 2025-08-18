"""
Strategy Predictor - Phase 4 Advanced Intelligence

Implements predictive modeling for negotiation strategy optimization:
- Contextual bandit for scenario selection
- Simple logistic baseline for acceptance probability
- Real-time adaptation based on feedback
- MongoDB persistence for model state

Uses Thompson Sampling for exploration-exploitation balance.
"""

import os
import uuid
import math
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

# ==========================
# Pydantic Models
# ==========================

class FeedbackEvent(BaseModel):
    session_id: str
    scenario_id: str
    accepted: bool
    counterparty_delay_sec: Optional[int] = None
    notes: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class PredictorHealth(BaseModel):
    status: str = "ok"
    model_version: str
    last_update: Optional[str] = None
    total_feedback_events: int = 0
    sessions_trained: int = 0

class StrategyUpdate(BaseModel):
    session_id: str
    updated_at: str
    suggested_scenario: str
    predicted_acceptance: Dict[str, float]  # scenario_name -> probability
    confidence: float
    next_best_action: str

# ==========================
# Bandit Algorithm Classes  
# ==========================

@dataclass
class BanditArm:
    """Represents one scenario type (Stretch, Balanced, Conservative)"""
    name: str
    alpha: float = 1.0  # Prior successes (Thompson Sampling)
    beta: float = 1.0   # Prior failures
    n_pulls: int = 0
    total_reward: float = 0.0
    last_reward: Optional[float] = None

class ContextualBandit:
    """
    Multi-armed bandit for scenario selection using Thompson Sampling.
    Maintains separate bandits per session for personalization.
    """
    
    def __init__(self):
        self.global_arms: Dict[str, BanditArm] = {
            "Stretch": BanditArm("Stretch", alpha=1.2, beta=1.8),    # Slightly pessimistic prior
            "Balanced": BanditArm("Balanced", alpha=1.5, beta=1.5),  # Neutral prior  
            "Conservative": BanditArm("Conservative", alpha=1.8, beta=1.2)  # Slightly optimistic prior
        }
    
    def get_session_arms(self, session_data: Optional[Dict] = None) -> Dict[str, BanditArm]:
        """Get arms for specific session, or global if no session data"""
        if not session_data or 'bandit_arms' not in session_data:
            return {name: BanditArm(name, arm.alpha, arm.beta) for name, arm in self.global_arms.items()}
        
        arms = {}
        for name, arm_data in session_data['bandit_arms'].items():
            arms[name] = BanditArm(
                name=name,
                alpha=arm_data.get('alpha', 1.0),
                beta=arm_data.get('beta', 1.0),
                n_pulls=arm_data.get('n_pulls', 0),
                total_reward=arm_data.get('total_reward', 0.0)
            )
        return arms
    
    def thompson_sample(self, arms: Dict[str, BanditArm]) -> str:
        """Select arm using Thompson Sampling"""
        samples = {}
        for name, arm in arms.items():
            # Sample from Beta(alpha, beta) distribution
            sample = np.random.beta(arm.alpha, arm.beta)
            samples[name] = sample
            
        # Return arm with highest sample
        return max(samples, key=samples.get)
    
    def update_arm(self, arms: Dict[str, BanditArm], arm_name: str, reward: float) -> None:
        """Update arm with observed reward (0 or 1)"""
        if arm_name in arms:
            arm = arms[arm_name]
            arm.n_pulls += 1
            arm.total_reward += reward
            arm.last_reward = reward
            
            # Update Beta parameters
            if reward > 0.5:  # Success
                arm.alpha += 1
            else:  # Failure
                arm.beta += 1

class LogisticPredictor:
    """
    Simple logistic regression for acceptance probability prediction.
    Uses lightweight features from session context.
    """
    
    def __init__(self):
        # Simple hand-tuned weights (can be updated incrementally)
        self.weights = {
            'intercept': 0.55,        # Base acceptance rate
            'leverage_score': 0.3,    # Higher leverage -> higher acceptance
            'strength_score': 0.15,   # Higher strength -> higher acceptance  
            'urgency': -0.1,          # Higher urgency -> lower acceptance
            'scenario_multiplier': -0.2,  # Higher price multiplier -> lower acceptance
            'conversation_sentiment': 0.1,  # Positive sentiment -> higher acceptance
            'time_since_last': -0.05      # Longer delays -> lower acceptance
        }
    
    def predict_acceptance(self, features: Dict[str, float]) -> float:
        """Predict acceptance probability using logistic function"""
        score = self.weights['intercept']
        
        for feature, value in features.items():
            if feature in self.weights:
                score += self.weights[feature] * value
        
        # Apply logistic function
        probability = 1 / (1 + math.exp(-score))
        return max(0.05, min(0.95, probability))
    
    def update_weights(self, features: Dict[str, float], actual_outcome: float, learning_rate: float = 0.01):
        """Simple gradient descent update"""
        predicted = self.predict_acceptance(features)
        error = actual_outcome - predicted
        
        # Update intercept
        self.weights['intercept'] += learning_rate * error
        
        # Update feature weights
        for feature, value in features.items():
            if feature in self.weights:
                self.weights[feature] += learning_rate * error * value

# ==========================
# Main Predictor Engine
# ==========================

class StrategyPredictor:
    """
    Main predictor engine combining bandit and logistic regression.
    Handles MongoDB persistence and provides prediction interface.
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.bandit = ContextualBandit()
        self.logistic = LogisticPredictor()
        self.model_version = "1.0.0"
        self.cache = {}  # Simple in-memory cache for recent sessions
        self.cache_expiry = timedelta(minutes=10)
        
    async def initialize_collections(self):
        """Initialize MongoDB collections and indexes"""
        try:
            # Feedback events
            await self.db.feedback_events.create_index([("session_id", 1), ("created_at", -1)])
            await self.db.feedback_events.create_index([("scenario_id", 1)])
            
            # Bandit sessions  
            await self.db.bandit_sessions.create_index([("session_id", 1)], unique=True)
            await self.db.bandit_sessions.create_index([("updated_at", -1)])
            
            # Model state
            await self.db.models.create_index([("model_type", 1), ("version", 1)])
            
            logger.info("✅ StrategyPredictor: Collections initialized")
        except Exception as e:
            logger.error(f"❌ StrategyPredictor: Init error: {e}")
    
    async def fit_incremental(self, feedback: FeedbackEvent) -> Dict[str, Any]:
        """
        Update models incrementally with new feedback.
        Returns summary of model updates.
        """
        try:
            # Store feedback event
            await self.db.feedback_events.insert_one(feedback.model_dump())
            
            # Get session bandit state
            session_doc = await self.db.bandit_sessions.find_one({"session_id": feedback.session_id})
            session_arms = self.bandit.get_session_arms(session_doc)
            
            # Extract scenario name from strategy data
            scenario_name = await self._get_scenario_name(feedback.scenario_id, feedback.session_id)
            
            if scenario_name and scenario_name in session_arms:
                # Update bandit
                reward = 1.0 if feedback.accepted else 0.0
                self.bandit.update_arm(session_arms, scenario_name, reward)
                
                # Update logistic predictor
                features = await self._extract_features(feedback.session_id, scenario_name)
                self.logistic.update_weights(features, reward)
                
                # Persist updated bandit state
                await self._persist_bandit_state(feedback.session_id, session_arms)
                
                # Clear cache for this session
                self.cache.pop(feedback.session_id, None)
                
                logger.info(f"✅ Model updated: session={feedback.session_id}, scenario={scenario_name}, reward={reward}")
                
                return {
                    "status": "updated",
                    "session_id": feedback.session_id,
                    "scenario_updated": scenario_name,
                    "reward": reward,
                    "new_alpha": session_arms[scenario_name].alpha,
                    "new_beta": session_arms[scenario_name].beta
                }
            
            else:
                logger.warning(f"⚠️ Scenario not found for feedback: {feedback.scenario_id}")
                return {"status": "feedback_stored", "scenario_found": False}
                
        except Exception as e:
            logger.error(f"❌ Incremental fit error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def predict_acceptance(self, session_id: str, scenario_features: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """
        Predict acceptance probability for each scenario.
        
        Args:
            session_id: Session identifier
            scenario_features: Dict of scenario_name -> feature_dict
            
        Returns:
            Dict of scenario_name -> predicted_probability
        """
        try:
            predictions = {}
            
            for scenario_name, features in scenario_features.items():
                # Get bandit confidence  
                session_doc = await self.db.bandit_sessions.find_one({"session_id": session_id})
                session_arms = self.bandit.get_session_arms(session_doc)
                
                # Combine logistic prediction with bandit confidence
                logistic_prob = self.logistic.predict_acceptance(features)
                
                if scenario_name in session_arms:
                    arm = session_arms[scenario_name]
                    # Use posterior mean as confidence adjustment
                    bandit_confidence = arm.alpha / (arm.alpha + arm.beta)
                    # Weighted combination
                    final_prob = 0.7 * logistic_prob + 0.3 * bandit_confidence
                else:
                    final_prob = logistic_prob
                
                predictions[scenario_name] = round(final_prob, 3)
            
            return predictions
            
        except Exception as e:
            logger.error(f"❌ Prediction error: {e}")
            return {"Stretch": 0.55, "Balanced": 0.65, "Conservative": 0.75}  # Fallback
    
    async def get_next_best_scenario(self, session_id: str) -> Tuple[str, float]:
        """
        Use Thompson Sampling to select next best scenario.
        
        Returns:
            Tuple of (scenario_name, confidence_score)
        """
        try:
            session_doc = await self.db.bandit_sessions.find_one({"session_id": session_id})
            session_arms = self.bandit.get_session_arms(session_doc)
            
            # Thompson sampling
            best_scenario = self.bandit.thompson_sample(session_arms)
            
            # Calculate confidence based on arm statistics
            arm = session_arms[best_scenario]
            confidence = arm.alpha / (arm.alpha + arm.beta)
            
            return best_scenario, round(confidence, 3)
            
        except Exception as e:
            logger.error(f"❌ Next scenario selection error: {e}")
            return "Balanced", 0.65  # Safe fallback
    
    async def get_health(self) -> PredictorHealth:
        """Get predictor health and statistics"""
        try:
            # Count feedback events
            total_events = await self.db.feedback_events.count_documents({})
            
            # Count trained sessions
            trained_sessions = await self.db.bandit_sessions.count_documents({})
            
            # Get last update time
            last_event = await self.db.feedback_events.find_one({}, sort=[("created_at", -1)])
            last_update = last_event.get("created_at") if last_event else None
            
            return PredictorHealth(
                model_version=self.model_version,
                last_update=last_update,
                total_feedback_events=total_events,
                sessions_trained=trained_sessions
            )
            
        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
            return PredictorHealth(
                status="error", 
                model_version=self.model_version,
                total_feedback_events=0,
                sessions_trained=0
            )
    
    # Private helper methods
    
    async def _get_scenario_name(self, scenario_id: str, session_id: str) -> Optional[str]:
        """Extract scenario name from strategy data"""
        try:
            strategy = await self.db.counter_offer_strategies.find_one(
                {"session_id": session_id, "scenarios.scenario_id": scenario_id}
            )
            if strategy:
                for scenario in strategy.get("scenarios", []):
                    if scenario.get("scenario_id") == scenario_id:
                        return scenario.get("name")
            return None
        except Exception:
            return None
    
    async def _extract_features(self, session_id: str, scenario_name: str) -> Dict[str, float]:
        """Extract features for logistic regression"""
        try:
            features = {
                'leverage_score': 0.5,
                'strength_score': 0.5, 
                'urgency': 0.5,
                'scenario_multiplier': 1.0,
                'conversation_sentiment': 0.5,
                'time_since_last': 0.0
            }
            
            # Get latest position analysis
            pos_analysis = await self.db.position_analyses.find_one(
                {"session_id": session_id}, sort=[("created_at", -1)]
            )
            if pos_analysis:
                features['leverage_score'] = pos_analysis.get('leverage_score', 0.5)
                features['strength_score'] = pos_analysis.get('strength_score', 5) / 10.0  # Normalize to 0-1
                features['urgency'] = pos_analysis.get('timeline_impact', {}).get('urgency', 5) / 10.0
            
            # Get scenario multiplier from counter-offer strategy
            strategy = await self.db.counter_offer_strategies.find_one(
                {"session_id": session_id}, sort=[("created_at", -1)]
            )
            if strategy:
                for scenario in strategy.get("scenarios", []):
                    if scenario.get("name") == scenario_name:
                        base_price = scenario.get("target_price")
                        if base_price and strategy.get("metrics", {}).get("balanced_target"):
                            balanced_price = strategy["metrics"]["balanced_target"]
                            if balanced_price:
                                features['scenario_multiplier'] = base_price / balanced_price
                        break
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Feature extraction error: {e}")
            return {
                'leverage_score': 0.5,
                'strength_score': 0.5,
                'urgency': 0.5, 
                'scenario_multiplier': 1.0,
                'conversation_sentiment': 0.5,
                'time_since_last': 0.0
            }
    
    async def _persist_bandit_state(self, session_id: str, arms: Dict[str, BanditArm]):
        """Save bandit state to MongoDB"""
        try:
            bandit_data = {
                "session_id": session_id,
                "updated_at": datetime.utcnow().isoformat(),
                "bandit_arms": {}
            }
            
            for name, arm in arms.items():
                bandit_data["bandit_arms"][name] = {
                    "alpha": arm.alpha,
                    "beta": arm.beta, 
                    "n_pulls": arm.n_pulls,
                    "total_reward": arm.total_reward,
                    "last_reward": arm.last_reward
                }
            
            await self.db.bandit_sessions.replace_one(
                {"session_id": session_id},
                bandit_data,
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"❌ Bandit persistence error: {e}")

# ==========================
# Global Instance
# ==========================

_strategy_predictor: Optional[StrategyPredictor] = None

async def get_strategy_predictor(db: AsyncIOMotorDatabase) -> StrategyPredictor:
    """Get or create strategy predictor instance"""
    global _strategy_predictor
    if _strategy_predictor is None:
        _strategy_predictor = StrategyPredictor(db)
        await _strategy_predictor.initialize_collections()
    return _strategy_predictor