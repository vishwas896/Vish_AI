"""
VISH AI - Dataset Manager
Handles data collection, storage, and preprocessing for continuous learning
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path
import pandas as pd
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VishDatasetManager:
    """Manages dataset collection, storage, and preprocessing"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.dataset_file = self.data_dir / "vish_dataset.jsonl"
        self.feedback_file = self.data_dir / "feedback.jsonl"
        self.research_file = self.data_dir / "research_data.jsonl"
        
        # Initialize files if they don't exist
        for file in [self.dataset_file, self.feedback_file, self.research_file]:
            if not file.exists():
                file.touch()
    
    def add_interaction(
        self,
        user_prompt: str,
        ai_response: str,
        category: str = "assistant",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a user interaction to the dataset"""
        
        interaction = {
            "id": self._generate_id(user_prompt, ai_response),
            "user_prompt": user_prompt,
            "ai_response": ai_response,
            "category": category,  # assistant, resume, research, business
            "timestamp": datetime.utcnow().isoformat(),
            "feedback_score": None,
            "metadata": metadata or {}
        }
        
        # Append to dataset file
        with open(self.dataset_file, 'a') as f:
            f.write(json.dumps(interaction) + '\n')
        
        logger.info(f"Added interaction {interaction['id']} to dataset")
        return interaction['id']
    
    def add_feedback(
        self,
        interaction_id: str,
        score: int,
        comment: Optional[str] = None
    ):
        """Add user feedback for an interaction"""
        
        feedback = {
            "interaction_id": interaction_id,
            "score": score,  # 1-5
            "comment": comment,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        with open(self.feedback_file, 'a') as f:
            f.write(json.dumps(feedback) + '\n')
        
        logger.info(f"Added feedback for interaction {interaction_id}: {score}/5")
    
    def add_research_data(
        self,
        query: str,
        source: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add research data from web searches"""
        
        research = {
            "id": self._generate_id(query, content),
            "query": query,
            "source": source,  # duckduckgo, wikipedia, etc.
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        with open(self.research_file, 'a') as f:
            f.write(json.dumps(research) + '\n')
        
        logger.info(f"Added research data from {source}")
    
    def get_dataset_stats(self) -> Dict[str, Any]:
        """Get dataset statistics"""
        
        stats = {
            "total_interactions": 0,
            "by_category": {},
            "total_feedback": 0,
            "avg_feedback_score": 0.0,
            "total_research": 0,
            "last_updated": None
        }
        
        # Count interactions
        if self.dataset_file.exists():
            with open(self.dataset_file, 'r') as f:
                interactions = [json.loads(line) for line in f if line.strip()]
            
            stats["total_interactions"] = len(interactions)
            
            # Category breakdown
            for interaction in interactions:
                category = interaction.get("category", "unknown")
                stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            
            if interactions:
                stats["last_updated"] = interactions[-1].get("timestamp")
        
        # Count feedback
        if self.feedback_file.exists():
            with open(self.feedback_file, 'r') as f:
                feedbacks = [json.loads(line) for line in f if line.strip()]
            
            stats["total_feedback"] = len(feedbacks)
            if feedbacks:
                avg_score = sum(f.get("score", 0) for f in feedbacks) / len(feedbacks)
                stats["avg_feedback_score"] = round(avg_score, 2)
        
        # Count research
        if self.research_file.exists():
            with open(self.research_file, 'r') as f:
                research = [json.loads(line) for line in f if line.strip()]
            stats["total_research"] = len(research)
        
        return stats
    
    def prepare_training_data(
        self,
        min_feedback_score: float = 3.0,
        max_samples: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """Prepare and clean dataset for training"""
        
        logger.info("Preparing training data...")
        
        # Load all interactions
        interactions = []
        if self.dataset_file.exists():
            with open(self.dataset_file, 'r') as f:
                interactions = [json.loads(line) for line in f if line.strip()]
        
        # Load feedback
        feedback_map = {}
        if self.feedback_file.exists():
            with open(self.feedback_file, 'r') as f:
                for line in f:
                    if line.strip():
                        fb = json.loads(line)
                        feedback_map[fb["interaction_id"]] = fb["score"]
        
        # Filter and prepare
        training_data = []
        seen_hashes = set()
        
        for interaction in interactions:
            interaction_id = interaction.get("id")
            score = feedback_map.get(interaction_id, 5.0)  # Default to high if no feedback
            
            # Filter by feedback score
            if score < min_feedback_score:
                continue
            
            # Deduplicate
            content_hash = self._generate_id(
                interaction["user_prompt"],
                interaction["ai_response"]
            )
            if content_hash in seen_hashes:
                continue
            seen_hashes.add(content_hash)
            
            # Format for training
            training_data.append({
                "prompt": interaction["user_prompt"],
                "response": interaction["ai_response"],
                "category": interaction.get("category", "assistant")
            })
        
        # Limit samples if specified
        if max_samples and len(training_data) > max_samples:
            training_data = training_data[-max_samples:]
        
        logger.info(f"Prepared {len(training_data)} training samples")
        return training_data
    
    def export_to_csv(self, output_path: Optional[str] = None) -> str:
        """Export dataset to CSV for analysis"""
        
        if output_path is None:
            output_path = str(self.data_dir / "vish_dataset.csv")
        
        interactions = []
        if self.dataset_file.exists():
            with open(self.dataset_file, 'r') as f:
                interactions = [json.loads(line) for line in f if line.strip()]
        
        df = pd.DataFrame(interactions)
        df.to_csv(output_path, index=False)
        
        logger.info(f"Exported {len(interactions)} interactions to {output_path}")
        return output_path
    
    def clear_low_quality_data(self, min_score: float = 2.0):
        """Remove low-quality interactions based on feedback"""
        
        # Load feedback
        feedback_map = {}
        if self.feedback_file.exists():
            with open(self.feedback_file, 'r') as f:
                for line in f:
                    if line.strip():
                        fb = json.loads(line)
                        feedback_map[fb["interaction_id"]] = fb["score"]
        
        # Filter interactions
        filtered_interactions = []
        removed_count = 0
        
        if self.dataset_file.exists():
            with open(self.dataset_file, 'r') as f:
                for line in f:
                    if line.strip():
                        interaction = json.loads(line)
                        score = feedback_map.get(interaction["id"], 5.0)
                        
                        if score >= min_score:
                            filtered_interactions.append(interaction)
                        else:
                            removed_count += 1
        
        # Rewrite dataset
        with open(self.dataset_file, 'w') as f:
            for interaction in filtered_interactions:
                f.write(json.dumps(interaction) + '\n')
        
        logger.info(f"Removed {removed_count} low-quality interactions (score < {min_score})")
    
    @staticmethod
    def _generate_id(text1: str, text2: str) -> str:
        """Generate unique ID from content"""
        content = f"{text1}{text2}"
        return hashlib.md5(content.encode()).hexdigest()[:12]


# Global dataset manager instance
_dataset_manager = None


def get_dataset_manager() -> VishDatasetManager:
    """Get or create global dataset manager instance"""
    global _dataset_manager
    if _dataset_manager is None:
        _dataset_manager = VishDatasetManager()
    return _dataset_manager
