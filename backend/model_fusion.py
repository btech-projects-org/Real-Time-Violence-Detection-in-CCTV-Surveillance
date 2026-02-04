"""
Detection Fusion Module
Combines results from weapon detection and violence detection
Implements fusion logic for hybrid surveillance system
"""

from typing import Dict, List, Tuple
from enum import Enum
from datetime import datetime


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"      # Weapon + Violence detected
    HIGH = "high"               # Only weapon detected
    MEDIUM = "medium"           # Only violence detected
    LOW = "low"                 # Suspicious activity
    NONE = "none"              # Normal


class DetectionFusionEngine:
    """
    Fusion engine for combining multiple detection streams
    - Stream 1: Weapon Detection (DETR/YOLOv8) - Frame-level
    - Stream 2: Violence Detection (CNN-LSTM) - Sequence-level
    """
    
    def __init__(self, 
                 weapon_threshold: float = 0.75,
                 violence_threshold: float = 0.60,
                 fusion_mode: str = "adaptive"):
        """
        Initialize fusion engine
        
        Args:
            weapon_threshold: Confidence threshold for weapon detection (0-1)
            violence_threshold: Confidence threshold for violence detection (0-1)
            fusion_mode: 'adaptive', 'conservative', or 'aggressive'
                - adaptive: Balance between sensitivity and false positives
                - conservative: Only alert for high confidence detections
                - aggressive: Alert on any detection from either stream
        """
        self.weapon_threshold = weapon_threshold
        self.violence_threshold = violence_threshold
        self.fusion_mode = fusion_mode
        
        # Detection history for context
        self.detection_history = []
        self.max_history = 100
        
    def fuse_detections(self, 
                       weapon_result: Dict,
                       violence_result: Dict) -> Dict:
        """
        Fuse results from both detection streams
        
        Args:
            weapon_result: Output from weapon detection (DETR/YOLOv8)
            violence_result: Output from violence detection (CNN-LSTM)
        
        Returns:
            Fused detection result with severity and recommendation
        """
        
        # Extract detection flags
        weapon_detected = weapon_result.get("detected", False) and \
                         weapon_result.get("confidence", 0) >= self.weapon_threshold
        
        violence_detected = violence_result.get("detected", False) and \
                           violence_result.get("confidence", 0) >= self.violence_threshold
        
        # Get confidence scores
        weapon_confidence = weapon_result.get("confidence", 0.0)
        violence_confidence = violence_result.get("confidence", 0.0)
        
        # Apply fusion logic
        fused_result = self._apply_fusion_logic(
            weapon_detected=weapon_detected,
            violence_detected=violence_detected,
            weapon_confidence=weapon_confidence,
            violence_confidence=violence_confidence,
            weapon_result=weapon_result,
            violence_result=violence_result
        )
        
        # Store in history
        self._add_to_history(fused_result)
        
        return fused_result
    
    def _apply_fusion_logic(self,
                           weapon_detected: bool,
                           violence_detected: bool,
                           weapon_confidence: float,
                           violence_confidence: float,
                           weapon_result: Dict,
                           violence_result: Dict) -> Dict:
        """
        Apply fusion logic based on fusion mode
        """
        
        if self.fusion_mode == "conservative":
            return self._conservative_fusion(
                weapon_detected, violence_detected,
                weapon_confidence, violence_confidence,
                weapon_result, violence_result
            )
        elif self.fusion_mode == "aggressive":
            return self._aggressive_fusion(
                weapon_detected, violence_detected,
                weapon_confidence, violence_confidence,
                weapon_result, violence_result
            )
        else:  # adaptive (default)
            return self._adaptive_fusion(
                weapon_detected, violence_detected,
                weapon_confidence, violence_confidence,
                weapon_result, violence_result
            )
    
    def _critical_threat_fusion(self, 
                               weapon_detected: bool,
                               violence_detected: bool,
                               weapon_result: Dict,
                               violence_result: Dict) -> Dict:
        """
        Both weapon AND violence detected
        Highest alert level - Immediate response required
        """
        return {
            "detected": True,
            "type": "critical_threat",
            "severity": AlertSeverity.CRITICAL,
            "severity_score": 1.0,
            "description": f"🚨 CRITICAL: Weapon + Aggressive behavior detected!\n"
                          f"   Weapon: {weapon_result.get('description', 'Unknown')}\n"
                          f"   Behavior: {violence_result.get('description', 'Aggressive')}",
            "weapon_detection": weapon_result,
            "violence_detection": violence_result,
            "confidence": (weapon_result.get("confidence", 0) + 
                          violence_result.get("confidence", 0)) / 2,
            "action": "IMMEDIATE_ALERT",
            "recommended_response": [
                "Sound alarm immediately",
                "Alert security personnel",
                "Notify law enforcement",
                "Record all footage"
            ]
        }
    
    def _weapon_only_fusion(self,
                           weapon_result: Dict) -> Dict:
        """
        Only weapon detected, no violence pattern
        High alert - Potential threat
        """
        weapon_type = weapon_result.get("description", "Unknown weapon")
        confidence = weapon_result.get("confidence", 0)
        
        return {
            "detected": True,
            "type": "weapon_detected",
            "severity": AlertSeverity.HIGH,
            "severity_score": 0.9,
            "description": f"⚠️ HIGH: Weapon detected\n"
                          f"   {weapon_type}\n"
                          f"   Confidence: {confidence:.1%}",
            "weapon_detection": weapon_result,
            "violence_detection": {"detected": False},
            "confidence": confidence,
            "action": "IMMEDIATE_ALERT",
            "recommended_response": [
                "Alert security immediately",
                "Track person with weapon",
                "Record all angles",
                "Prepare emergency response"
            ]
        }
    
    def _violence_only_fusion(self,
                             violence_result: Dict) -> Dict:
        """
        Only violence detected, no weapon
        Medium alert - Requires investigation
        """
        violence_confidence = violence_result.get("confidence", 0)
        
        return {
            "detected": True,
            "type": "violence_detected",
            "severity": AlertSeverity.MEDIUM,
            "severity_score": 0.7,
            "description": f"⚠️ MEDIUM: Aggressive behavior detected\n"
                          f"   {violence_result.get('description', 'Violent activity')}\n"
                          f"   Confidence: {violence_confidence:.1%}",
            "weapon_detection": {"detected": False},
            "violence_detection": violence_result,
            "confidence": violence_confidence,
            "action": "ALERT_AND_MONITOR",
            "recommended_response": [
                "Alert security to monitor",
                "Zoom in for details",
                "Prepare to intervene if needed",
                "Record incident"
            ]
        }
    
    def _suspicious_activity_fusion(self,
                                   violence_result: Dict) -> Dict:
        """
        Low confidence violence detection - Suspicious but not confirmed
        Low alert - Requires manual verification
        """
        violence_confidence = violence_result.get("confidence", 0)
        
        return {
            "detected": True,
            "type": "suspicious_activity",
            "severity": AlertSeverity.LOW,
            "severity_score": 0.4,
            "description": f"⚠️ LOW: Suspicious activity detected\n"
                          f"   {violence_result.get('description', 'Unusual activity')}\n"
                          f"   Confidence: {violence_confidence:.1%}",
            "weapon_detection": {"detected": False},
            "violence_detection": violence_result,
            "confidence": violence_confidence,
            "action": "MONITOR",
            "recommended_response": [
                "Keep monitoring",
                "Manual verification recommended",
                "Check for context clues"
            ]
        }
    
    def _normal_fusion(self) -> Dict:
        """
        No threats detected - Normal activity
        No alert
        """
        return {
            "detected": False,
            "type": "normal",
            "severity": AlertSeverity.NONE,
            "severity_score": 0.0,
            "description": "✅ Normal activity - No threats detected",
            "weapon_detection": {"detected": False},
            "violence_detection": {"detected": False},
            "confidence": 0.0,
            "action": "NONE",
            "recommended_response": []
        }
    
    def _adaptive_fusion(self,
                        weapon_detected: bool,
                        violence_detected: bool,
                        weapon_confidence: float,
                        violence_confidence: float,
                        weapon_result: Dict,
                        violence_result: Dict) -> Dict:
        """
        Adaptive fusion: Balance sensitivity and specificity
        
        FIX: Removed over-sensitive 0.45 threshold that caused false positives
        Now only alerts on actual detections above thresholds
        """
        # Scenario 1: Both detected - CRITICAL
        if weapon_detected and violence_detected:
            return self._critical_threat_fusion(
                weapon_detected, violence_detected,
                weapon_result, violence_result
            )
        
        # Scenario 2: Weapon only - HIGH
        if weapon_detected:
            return self._weapon_only_fusion(weapon_result)
        
        # Scenario 3: Violence only
        if violence_detected:
            return self._violence_only_fusion(violence_result)
        
        # Scenario 4: REMOVED - Was triggering false positives at 0.45 confidence
        # Only alert on confirmed detections above thresholds
        
        # Scenario 5: Normal
        return self._normal_fusion()
    
    def _conservative_fusion(self,
                            weapon_detected: bool,
                            violence_detected: bool,
                            weapon_confidence: float,
                            violence_confidence: float,
                            weapon_result: Dict,
                            violence_result: Dict) -> Dict:
        """
        Conservative fusion: High confidence required for alerts
        Reduces false positives, may miss some threats
        """
        # Only alert if very high confidence
        if weapon_detected and weapon_confidence > 0.90:
            return self._weapon_only_fusion(weapon_result)
        
        if violence_detected and violence_confidence > 0.80:
            return self._violence_only_fusion(violence_result)
        
        if weapon_detected and violence_detected:
            return self._critical_threat_fusion(
                weapon_detected, violence_detected,
                weapon_result, violence_result
            )
        
        return self._normal_fusion()
    
    def _aggressive_fusion(self,
                          weapon_detected: bool,
                          violence_detected: bool,
                          weapon_confidence: float,
                          violence_confidence: float,
                          weapon_result: Dict,
                          violence_result: Dict) -> Dict:
        """
        Aggressive fusion: Lower threshold, more alerts
        Higher sensitivity, more false positives
        """
        # Alert on any detection
        if weapon_detected:
            return self._weapon_only_fusion(weapon_result)
        
        if violence_detected:
            return self._violence_only_fusion(violence_result)
        
        # Even low confidence triggers alert
        if violence_confidence > 0.50:
            return self._suspicious_activity_fusion(violence_result)
        
        return self._normal_fusion()
    
    def _add_to_history(self, detection: Dict):
        """Add detection to history for trend analysis"""
        detection_with_timestamp = {
            **detection,
            "timestamp": datetime.now().isoformat()
        }
        self.detection_history.append(detection_with_timestamp)
        
        # Keep history manageable
        if len(self.detection_history) > self.max_history:
            self.detection_history.pop(0)
    
    def get_trend_analysis(self, window_size: int = 10) -> Dict:
        """
        Analyze recent detections for trends
        Useful for detecting escalating threats
        """
        if not self.detection_history:
            return {"trend": "none", "recent_alerts": 0}
        
        recent_detections = self.detection_history[-window_size:]
        alert_count = sum(1 for d in recent_detections if d["detected"])
        average_severity = sum(d["severity_score"] for d in recent_detections) / len(recent_detections)
        
        trend = "escalating" if alert_count > window_size * 0.5 else "normal"
        
        return {
            "trend": trend,
            "recent_alerts": alert_count,
            "average_severity": round(average_severity, 2),
            "detection_rate": f"{(alert_count/window_size)*100:.1f}%"
        }
    
    def get_system_status(self) -> Dict:
        """Get overall system status"""
        if not self.detection_history:
            return {
                "status": "operational",
                "total_alerts": 0,
                "last_alert": None
            }
        
        recent_alerts = [d for d in self.detection_history if d["detected"]]
        
        return {
            "status": "operational",
            "total_alerts": len(recent_alerts),
            "last_alert": self.detection_history[-1].get("timestamp"),
            "alerts_last_10": len([d for d in self.detection_history[-10:] if d["detected"]])
        }


# Fusion configuration presets
FUSION_PRESETS = {
    "balanced": {
        "fusion_mode": "adaptive",
        "weapon_threshold": 0.75,
        "violence_threshold": 0.60,
        "description": "Balanced approach - good sensitivity and specificity"
    },
    "high_security": {
        "fusion_mode": "aggressive",
        "weapon_threshold": 0.70,
        "violence_threshold": 0.50,
        "description": "High security - more alerts, lower thresholds"
    },
    "low_false_positives": {
        "fusion_mode": "conservative",
        "weapon_threshold": 0.85,
        "violence_threshold": 0.75,
        "description": "Conservative - fewer alerts, higher thresholds"
    }
}
