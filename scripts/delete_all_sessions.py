import os
from pathlib import Path

def delete_all_sessions():
    """Delete all session files and reset active_sessions.json."""
    # Determine project root
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent
    sessions_dir = project_root / "data" / "sessions"
    
    if not sessions_dir.exists():
        print("No sessions directory found.")
        return

    print(f"🗑️  Deleting all sessions in {sessions_dir}...")
    
    # Delete all .json and .tmp files
    files_to_delete = list(sessions_dir.glob("*.json")) + list(sessions_dir.glob("*.tmp"))
    
    deleted_count = 0
    errors = 0
    
    for file in files_to_delete:
        # Skip active_sessions.json for a moment, we'll reset it
        if file.name == "active_sessions.json":
            continue
            
        try:
            file.unlink()
            print(f"Deleted: {file.name}")
            deleted_count += 1
        except Exception as e:
            print(f"❌ Error deleting {file.name}: {e}")
            errors += 1

    # Reset active_sessions.json
    active_sessions_file = sessions_dir / "active_sessions.json"
    try:
        with open(active_sessions_file, "w", encoding="utf-8") as f:
            f.write("{}")
        print("✅ Reset active_sessions.json")
    except Exception as e:
        print(f"❌ Error resetting active_sessions.json: {e}")

    print(f"\n📊 Summary:")
    print(f"  - Deleted: {deleted_count} files")
    print(f"  - Errors: {errors}")
    print(f"\n⚠️  IMPORTANT: Please restart the server to clear in-memory sessions!")

if __name__ == "__main__":
    delete_all_sessions()
