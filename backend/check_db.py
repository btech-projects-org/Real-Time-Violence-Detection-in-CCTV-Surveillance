import asyncio
from .database import init_db, get_incidents

async def main():
    await init_db()
    incidents = await get_incidents()
    
    print("\n" + "="*60)
    print(f"TOTAL INCIDENTS IN DATABASE: {len(incidents)}")
    print("="*60)
    
    if len(incidents) > 0:
        print("\nRECENT INCIDENTS:")
        for i, incident in enumerate(incidents[:10], 1):
            print(f"\n{i}. {incident['type']}")
            print(f"   Time: {incident['timestamp']}")
            print(f"   Confidence: {incident['confidence']}")
            print(f"   Description: {incident['description']}")
    else:
        print("\n⚠️ No incidents found in database")
        print("This is normal if:")
        print("  • You just started using the system")
        print("  • No threats have been detected yet")
        print("  • You're testing with normal facial expressions")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
