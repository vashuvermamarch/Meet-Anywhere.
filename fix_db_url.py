import urllib.parse

print("--- Database URL Encoder ---")
print("If your password has special characters like @, #, !, or :, you MUST encode it for the DATABASE_URL to work.")

user = input("Enter database username (e.g. neondb_owner): ")
password = input("Enter database password: ")
host = input("Enter database host (e.g. ep-silent-lab...neon.tech): ")
dbname = input("Enter database name (usually 'neondb'): ")

encoded_password = urllib.parse.quote_plus(password)

final_url = f"postgres://{user}:{encoded_password}@{host}/{dbname}?sslmode=require"

print("\n--- YOUR CORRECT DATABASE_URL ---")
print("Copy and paste the line below into your Render Environment Variables:")
print(f"\n{final_url}\n")
