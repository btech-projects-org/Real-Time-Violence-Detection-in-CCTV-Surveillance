"""
Hybrid Detection System Configuration
Centralized configuration for both weapon and violence detection streams
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class WeaponDetectionConfig:
    """Configuration for weapon detection (Stream 1)"""
    
    # DETR Model Settings
    detr_model_name: str = "NabilaLM/detr-weapons-detection"
    detr_confidence_threshold: float = 0.75
    detr_enabled: bool = True
    
    # YOLOv8 Model Settings
    yolo_weights_path: str = "backend/weights/best.pt"
    yolo_confidence_threshold: float = 0.75
    yolo_enabled: bool = True
    yolo_fallback: bool = True  # Use YOLOv8n if custom weights missing
    
    # Processing Settings
    inference_device: str = "cuda"  # 'cuda' or 'cpu'
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "detr_model_name": self.detr_model_name,
            "detr_confidence_threshold": self.detr_confidence_threshold,
            "detr_enabled": self.detr_enabled,
            "yolo_weights_path": self.yolo_weights_path,
            "yolo_confidence_threshold": self.yolo_confidence_threshold,
            "yolo_enabled": self.yolo_enabled,
            "yolo_fallback": self.yolo_fallback,
            "inference_device": self.inference_device
        }


@dataclass
class ViolenceDetectionConfig:
    """Configuration for violence detection (Stream 2)"""
    
    # CNN-LSTM Model Settings
    lstm_hidden_size: int = 256
    lstm_num_layers: int = 2
    sequence_length: int = 16
    input_size: tuple = (224, 224)
    
    # Processing Settings
    frame_skip: int = 2  # Process every N-th frame to reduce computation
    confidence_threshold: float = 0.60
    inference_device: str = "cuda"  # 'cuda' or 'cpu'
    enabled: bool = False  # FIX: DISABLED by default - model is untrained
    
    # Model Architecture
    use_bidirectional: bool = True
    use_attention: bool = True
    dropout_rate: float = 0.3
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "lstm_hidden_size": self.lstm_hidden_size,
            "lstm_num_layers": self.lstm_num_layers,
            "sequence_length": self.sequence_length,
            "input_size": self.input_size,
            "frame_skip": self.frame_skip,
            "confidence_threshold": self.confidence_threshold,
            "inference_device": self.inference_device,
            "enabled": self.enabled,
            "use_bidirectional": self.use_bidirectional,
            "use_attention": self.use_attention,
            "dropout_rate": self.dropout_rate
        }


@dataclass
class FusionConfig:
    """Configuration for detection fusion"""
    
    # Fusion Settings
    fusion_mode: str = "adaptive"  # 'adaptive', 'conservative', 'aggressive'
    weapon_threshold: float = 0.75
    violence_threshold: float = 0.60
    
    # Alert Configuration
    enable_alerts: bool = True
    alert_cooldown_seconds: int = 5  # Minimum time between alerts
    
    # Logging
    log_all_detections: bool = True
    log_level: str = "INFO"  # 'DEBUG', 'INFO', 'WARNING', 'ERROR'
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "fusion_mode": self.fusion_mode,
            "weapon_threshold": self.weapon_threshold,
            "violence_threshold": self.violence_threshold,
            "enable_alerts": self.enable_alerts,
            "alert_cooldown_seconds": self.alert_cooldown_seconds,
            "log_all_detections": self.log_all_detections,
            "log_level": self.log_level
        }


@dataclass
class VideoProcessorConfig:
    """Configuration for video processing"""
    
    # Frame Processing
    process_frequency: int = 90  # Process every N-th frame
    fps: int = 30
    
    # Evidence Storage
    save_alert_frames: bool = True
    alert_frames_path: str = "alerts"
    
    # Database Logging
    log_to_database: bool = True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "process_frequency": self.process_frequency,
            "fps": self.fps,
            "save_alert_frames": self.save_alert_frames,
            "alert_frames_path": self.alert_frames_path,
            "log_to_database": self.log_to_database
        }


class HybridSystemConfig:
    """Main configuration for entire hybrid system"""
    
    def __init__(self, preset: str = "balanced"):
        """
        Initialize system configuration
        
        Args:
            preset: Configuration preset ('balanced', 'high_security', 'low_false_positives')
        """
        self.preset = preset
        
        # Load preset configuration
        if preset == "high_security":
            self.weapon_config = WeaponDetectionConfig(
                detr_confidence_threshold=0.70,
                yolo_confidence_threshold=0.70
            )
            self.violence_config = ViolenceDetectionConfig(
                confidence_threshold=0.50,
                frame_skip=1,  # Process every frame
                enabled=False  # FIX: Disabled - untrained model
            )
            self.fusion_config = FusionConfig(
                fusion_mode="aggressive",
                weapon_threshold=0.70,
                violence_threshold=0.50
            )
        
        elif preset == "low_false_positives":
            self.weapon_config = WeaponDetectionConfig(
                detr_confidence_threshold=0.85,  # FIX: Adjusted to 85%
                yolo_confidence_threshold=0.85   # FIX: Adjusted to 85%
            )
            self.violence_config = ViolenceDetectionConfig(
                confidence_threshold=0.75,
                frame_skip=4,  # Process less frequently
                enabled=False  # FIX: Disabled - untrained model
            )
            self.fusion_config = FusionConfig(
                fusion_mode="conservative",
                weapon_threshold=0.85,  # FIX: Adjusted to 85%
                violence_threshold=0.75
            )
        
        else:  # balanced (default)
            self.weapon_config = WeaponDetectionConfig()
            self.violence_config = ViolenceDetectionConfig(
                enabled=False  # FIX: Disabled - untrained model
            )
            self.fusion_config = FusionConfig()
        
        # Video processor always uses these settings
        self.video_config = VideoProcessorConfig()
    
    def get_full_config(self) -> Dict:
        """Get complete configuration as dictionary"""
        return {
            "preset": self.preset,
            "weapon_detection": self.weapon_config.to_dict(),
            "violence_detection": self.violence_config.to_dict(),
            "fusion": self.fusion_config.to_dict(),
            "video_processing": self.video_config.to_dict()
        }
    
    def print_config(self):
        """Print configuration nicely"""
        print("\n" + "=" * 60)
        print(f"HYBRID SURVEILLANCE SYSTEM - Configuration")
        print(f"Preset: {self.preset.upper()}")
        print("=" * 60)
        
        print("\n📊 WEAPON DETECTION (Stream 1)")
        print(f"  Model: {self.weapon_config.detr_model_name}")
        print(f"  DETR Threshold: {self.weapon_config.detr_confidence_threshold:.0%}")
        print(f"  YOLOv8 Threshold: {self.weapon_config.yolo_confidence_threshold:.0%}")
        print(f"  Device: {self.weapon_config.inference_device}")
        
        print("\n🧠 VIOLENCE DETECTION (Stream 2)")
        print(f"  Model: CNN-LSTM")
        print(f"  Sequence Length: {self.violence_config.sequence_length} frames")
        print(f"  Confidence Threshold: {self.violence_config.confidence_threshold:.0%}")
        print(f"  Frame Skip: Every {self.violence_config.frame_skip} frame(s)")
        print(f"  Device: {self.violence_config.inference_device}")
        print(f"  Enabled: {self.violence_config.enabled}")
        
        print("\n🔀 FUSION ENGINE")
        print(f"  Mode: {self.fusion_config.fusion_mode.upper()}")
        print(f"  Weapon Threshold: {self.fusion_config.weapon_threshold:.0%}")
        print(f"  Violence Threshold: {self.fusion_config.violence_threshold:.0%}")
        print(f"  Alert Cooldown: {self.fusion_config.alert_cooldown_seconds}s")
        
        print("\n📹 VIDEO PROCESSING")
        print(f"  Process Frequency: Every {self.video_config.process_frequency} frame(s)")
        print(f"  Save Evidence: {self.video_config.save_alert_frames}")
        print(f"  Database Logging: {self.video_config.log_to_database}")
        
        print("\n" + "=" * 60 + "\n")


# Predefined configurations
SYSTEM_CONFIGS = {
    "balanced": HybridSystemConfig("balanced"),
    "high_security": HybridSystemConfig("high_security"),
    "low_false_positives": HybridSystemConfig("low_false_positives")
}


def get_system_config(preset: str = "balanced") -> HybridSystemConfig:
    """
    Get system configuration by preset
    
    Args:
        preset: 'balanced', 'high_security', or 'low_false_positives'
    
    Returns:
        HybridSystemConfig instance
    """
    if preset in SYSTEM_CONFIGS:
        return SYSTEM_CONFIGS[preset]
    else:
        print(f"⚠️ Unknown preset '{preset}', using 'balanced'")
        return SYSTEM_CONFIGS["balanced"]
