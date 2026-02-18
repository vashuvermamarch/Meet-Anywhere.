import os
import dj_database_url
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_url = os.environ.get('DATABASE_URL')

if not db_url:
    print("❌ ERROR: No DATABASE_URL found in your .env file!")
    print("Please paste your Neon connection string into .env first.")
else:
    print(f"🔄 Attempting to connect to: {db_url.split('@')[-1]}...")
    try:
        # Parse the URL
        config = dj_database_url.parse(db_url)
        
        # Try a direct connection with psycopg2
        conn = psycopg2.connect(
            dbname=config['NAME'],
            user=config['USER'],
            password=config['PASSWORD'],
            host=config['HOST'],
            port=config['PORT'],
            sslmode='require'
        )
        print("✅ SUCCESS! Your database credentials are correct.")
        conn.close()
    except Exception as e:
        print(f"❌ CONNECTION FAILED: {e}")
        print("\nPossible reasons:")
        print("1. Your password in the URL is incorrect.")
        print("2. Your password contains special characters (like @, #, !) that need encoding.")
        print("3. Your IP address isn't allowed in Neon's firewall settings.")
