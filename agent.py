import os
import sys
import asyncio
import traceback
from dotenv import load_dotenv  # <--- 1. Import this

# 2. Load the .env file immediately
load_dotenv()

# Check for API Key
if "GOOGLE_API_KEY" not in os.environ:
    print("❌ Error: GOOGLE_API_KEY not found in .env")
    sys.exit(1)

from google.cloud.sql.connector import Connector, IPTypes
from google.adk.agents import Agent
from google.adk.runners import Runner
#from google.adk.session_services import InMemorySessionService # <--- Don't forget this fix from before!

# --- CONFIGURATION (Dynamic) ---
# We build the config dictionary using os.getenv
DB_CONFIG = {
    "instance_connection_name": os.getenv("DB_INSTANCE_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "db_name": os.getenv("DB_NAME"),
    "ip_type": IPTypes.PUBLIC
}

# Verify critical vars are loaded (Optional but helpful debugging)
if not DB_CONFIG["instance_connection_name"] or not DB_CONFIG["password"]:
    print("❌ Error: DB credentials missing from .env file")
    sys.exit(1)

# --- STEP 1: DEFINE THE TOOL ---
def get_gcp_connection():
    with Connector() as connector:
        conn = connector.connect(
            DB_CONFIG["instance_connection_name"],
            "pymysql",
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            db=DB_CONFIG["db_name"],
            ip_type=DB_CONFIG["ip_type"]
        )
        return conn

def run_mysql_query(query: str) -> str:
    """Executes a SQL query against Google Cloud SQL."""
    conn = None
    cursor = None
    try:
        conn = get_gcp_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            if not rows: return "✅ Query executed. Rows returned: 0"
            
            result_str = f"Columns: {columns}\nRow Count: {len(rows)}\nData:\n"
            for row in rows:
                result_str += str(row) + "\n"
            return result_str
        else:
            conn.commit()
            return f"✅ Action executed. Rows affected: {cursor.rowcount}"

    except Exception as e:
        return f"❌ SQL ERROR: {e}"
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# --- STEP 2: DEFINE THE AGENT ---
root_agent = Agent(
    model="gemini-2.0-flash",
    name="cloud_sql_agent",
    tools=[run_mysql_query],
    instruction="""
    You are an expert Google Cloud SQL Database Agent.
    Your capabilities:
    1. Direct access to Cloud SQL via `run_mysql_query`.
    2. Discovery: You must run `SHOW TABLES` and `DESCRIBE` to learn the schema.
    3. Execution: Write valid MySQL queries.
    """
)

# --- STEP 3: RUNNER ---
async def main():
    # FIX: Using InMemorySessionService to solve the TypeError
    runner = Runner(
        agent=root_agent        
    )
    
    print(f"🤖 Connected to: {DB_CONFIG['instance_connection_name']}")
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]: break
            
            async for event in runner.run_async(user_message=user_input, session_id="sql_session_1"):
                if hasattr(event, "content") and event.content:
                    print(f"\n💬 AGENT: {event.content.parts[0].text}")
                elif hasattr(event, "tool_use"):
                    print(f"\n🛠️ RUNNING SQL: {event.tool_use.args['query']}")
        except KeyboardInterrupt:
            print("\n🛑 Stopped.")
            break

if __name__ == "__main__":
    asyncio.run(main())