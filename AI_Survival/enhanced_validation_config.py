# Enhanced rule validation configuration
ENHANCED_VALIDATION_CONFIG = {
    "quality_thresholds": {
        "min_confidence": 0.1,
        "min_evidence_count": 2,
        "min_success_rate": 0.4,
        "max_complexity": 8
    },
    "validation_strategies": {
        "immediate_validation": True,
        "progressive_confidence": True,
        "risk_aware_validation": True,
        "quality_based_promotion": True
    },
    "confidence_updates": {
        "success_multiplier": 1.3,
        "failure_penalty": 0.8,
        "partial_success_factor": 1.1,
        "consistency_bonus": 0.05
    }
}
