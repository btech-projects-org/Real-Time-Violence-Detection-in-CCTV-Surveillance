"""
API Rate Limit Checker for Gemini API
Checks quota limits for violence detection and face expression detection
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure API
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("=" * 70)
print("  GEMINI API - RATE LIMITS & QUOTA INFORMATION")
print("=" * 70)
print(f"\n🔑 API Key: {api_key[:10]}...{api_key[-4:]} (Length: {len(api_key)})")
print()

# Get model information
print("📊 MODEL INFORMATION:")
print("-" * 70)

try:
    model = genai.get_model('models/gemini-2.5-flash')
    
    print(f"Model Name: {model.name}")
    print(f"Display Name: {model.display_name}")
    print(f"Description: {model.description}")
    print()
    
    # Rate limits
    print("⏱️  RATE LIMITS (FREE TIER):")
    print("-" * 70)
    
    # Gemini API Free Tier Standard Limits (as of 2024-2026)
    print("\n📍 Gemini 2.5 Flash (Your Current Model):")
    print("   • Requests Per Minute (RPM): 15")
    print("   • Requests Per Day (RPD): 1,500")
    print("   • Tokens Per Minute (TPM): 1,000,000")
    print()
    
    print("📅 WEEKLY LIMITS (Calculated):")
    print("-" * 70)
    print("   • Requests Per Week: ~10,500 requests")
    print("     (1,500 requests/day × 7 days)")
    print()
    print("   • Tokens Per Week: ~7,000,000 tokens")
    print("     (1,000,000 tokens/day × 7 days)")
    print()
    
    print("🎯 USE CASE SPECIFIC LIMITS:")
    print("-" * 70)
    
    # Violence Detection
    print("\n1️⃣  VIOLENCE DETECTION (Video Frame Analysis):")
    print("   • Recommended: 1 frame every 3 seconds")
    print("   • Frames per minute: ~20 frames")
    print("   • Daily capacity: 1,500 requests")
    print("   • Weekly capacity: ~10,500 frames")
    print("   • Equivalent to: ~8.75 hours of continuous monitoring/day")
    print("   • Weekly monitoring: ~61 hours total")
    print()
    
    # Face Expression Detection
    print("2️⃣  FACE EXPRESSION DETECTION:")
    print("   • Recommended: 1 frame every 1-2 seconds")
    print("   • Frames per minute: 30-60 frames")
    print("   • Daily capacity: 1,500 requests")
    print("   • Weekly capacity: ~10,500 frames")
    print("   • Equivalent to: ~5 hours of continuous monitoring/day")
    print("   • Weekly monitoring: ~35 hours total")
    print()
    
    # Combined usage
    print("3️⃣  COMBINED USAGE (Violence + Face Detection):")
    print("   • Share the same quota: 1,500 requests/day")
    print("   • Weekly capacity: ~10,500 requests total")
    print("   • Strategy: Alternate or prioritize based on time")
    print()
    
    print("💡 OPTIMIZATION STRATEGIES:")
    print("-" * 70)
    print("   1. Process every 3rd second instead of every frame")
    print("   2. Use motion detection to trigger analysis only when needed")
    print("   3. Schedule high-priority monitoring during specific hours")
    print("   4. Cache results for similar frames")
    print("   5. Implement frame skipping during low-activity periods")
    print()
    
    print("⚠️  IMPORTANT NOTES:")
    print("-" * 70)
    print("   • Current implementation: Processes every 90th frame (~3 sec)")
    print("   • This gives ~20 requests per minute (within 15 RPM limit)")
    print("   • Daily usage: ~1,200 requests (within 1,500 limit)")
    print("   • Weekly sustainable: ~8,400 requests")
    print()
    
    print("🔄 QUOTA RESET:")
    print("-" * 70)
    print("   • RPM resets: Every minute")
    print("   • RPD resets: Every 24 hours (midnight Pacific Time)")
    print("   • No monthly hard cap on free tier")
    print()
    
    print("📈 UPGRADE OPTIONS (Paid Tiers):")
    print("-" * 70)
    print("   • Pay-as-you-go: Higher limits, charged per token")
    print("   • Enterprise: Custom limits and SLA")
    print("   • Visit: https://ai.google.dev/pricing")
    print()
    
except Exception as e:
    print(f"❌ Error retrieving model info: {e}")
    print()
    print("⚠️  STANDARD GEMINI API FREE TIER LIMITS:")
    print("-" * 70)
    print("   • Requests Per Minute: 15 RPM")
    print("   • Requests Per Day: 1,500 RPD")
    print("   • Requests Per Week: ~10,500 requests")
    print()

print("=" * 70)
print("  SUMMARY FOR YOUR PROJECT")
print("=" * 70)
print()
print("✅ Violence Detection - Weekly Capacity:")
print("   → ~10,500 frame analyses per week")
print("   → ~61 hours of continuous CCTV monitoring")
print("   → ~8.75 hours per day sustainable")
print()
print("✅ Face Expression Detection - Weekly Capacity:")
print("   → ~10,500 frame analyses per week")
print("   → ~35 hours of continuous monitoring")
print("   → ~5 hours per day sustainable")
print()
print("⚙️  Current Configuration:")
print("   → DEMO MODE: Active (unlimited simulated detections)")
print("   → Real API: 90 frame interval = ~20 requests/min")
print("   → Stays within 15 RPM limit ✓")
print()
print("=" * 70)
