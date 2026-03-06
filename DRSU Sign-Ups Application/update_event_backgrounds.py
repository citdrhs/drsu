import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST', 'drhscit.org'),
        database=os.environ.get('DB'),
        user=os.environ.get('DB_UN'),
        password=os.environ.get('DB_PW')
    )
    cur = conn.cursor()
    
    # Map event names to background images
    background_mapping = {
        'Winter': 'WinterBg.png',
        'winter': 'WinterBg.png',
        'Thanksgiving': 'ThanksgivingBG.jpg',
        'thanksgiving': 'ThanksgivingBG.jpg',
        'Project': 'testBG.png',
        'project': 'testBG.png',
    }
    
    # First, add background_image column if it doesn't exist
    cur.execute("""
        ALTER TABLE events 
        ADD COLUMN IF NOT EXISTS background_image VARCHAR(255) DEFAULT 'testBG.png';
    """)
    print("✓ Ensured background_image column exists")
    conn.commit()
    
    # Get all events
    cur.execute("SELECT id, name FROM events;")
    events = cur.fetchall()
    
    print(f"Found {len(events)} events without background images")
    
    for event_id, event_name in events:
        background = None
        
        # Check if event name contains keywords
        for keyword, bg_file in background_mapping.items():
            if keyword in event_name:
                background = bg_file
                break
        
        # Default to testBG.png if no match found
        if background is None:
            background = 'testBG.png'
        
        # Update the event
        cur.execute(
            "UPDATE events SET background_image = %s WHERE id = %s",
            (background, event_id)
        )
        print(f"Updated event '{event_name}' with background '{background}'")
    
    conn.commit()
    print("✓ Successfully updated event backgrounds")
    
    # Display updated events
    cur.execute("SELECT id, name, background_image FROM events;")
    updated_events = cur.fetchall()
    print("\nCurrent events:")
    for event_id, name, bg in updated_events:
        print(f"  - {name}: {bg}")
    
    cur.close()
    conn.close()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
