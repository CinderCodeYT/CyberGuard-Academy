"""
Quick script to clean up old session files that don't have the is_active field.
Run this once to fix compatibility issues with old session data.
"""

import json
from pathlib import Path

def cleanup_sessions():
    """Add is_active field to old session files."""
    # Determine project root (parent of scripts directory)
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent
    sessions_dir = project_root / "data" / "sessions"
    
    if not sessions_dir.exists():
        print("No sessions directory found.")
        return
    
    updated_count = 0
    error_count = 0
    
    # First, clear the active_sessions registry since we're marking all as inactive
    active_sessions_file = sessions_dir / "active_sessions.json"
    if active_sessions_file.exists():
        try:
            with open(active_sessions_file, 'w') as f:
                json.dump({}, f, indent=2)
            print("✅ Cleared active_sessions registry")
        except Exception as e:
            print(f"❌ Error clearing active_sessions registry: {e}")
    
    for session_file in sessions_dir.glob("*.json"):
        if session_file.name == "active_sessions.json":
            continue
            
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            # Check if is_active field exists
            if "is_active" not in session_data:
                # Add is_active field (set to False for old sessions)
                session_data["is_active"] = False
                
                # Save back to file
                with open(session_file, 'w') as f:
                    json.dump(session_data, f, indent=2)
                
                updated_count += 1
                print(f"✅ Updated: {session_file.name}")
        
        except Exception as e:
            error_count += 1
            print(f"❌ Error processing {session_file.name}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"  - Updated: {updated_count} sessions")
    print(f"  - Errors: {error_count} sessions")
    print(f"\n✅ Cleanup complete!")

if __name__ == "__main__":
    cleanup_sessions()
