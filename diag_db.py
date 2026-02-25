import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meets_platform.settings')
django.setup()

from meetings.models import Meeting
from django.contrib.auth.models import User

print("--- Meeting Diagnostic ---")
all_meetings = Meeting.objects.all()
for m in all_meetings:
    print(f"ID: {m.id} | Room: '{m.room_name}' | Host: {m.host.username} | Active: {m.is_active}")

print("\n--- Normalizing ---")
count = 0
for m in all_meetings:
    old_name = m.room_name
    new_name = old_name.lower().strip()
    if old_name != new_name:
        m.room_name = new_name
        try:
            m.save()
            print(f"Normalized: '{old_name}' -> '{new_name}'")
            count += 1
        except Exception as e:
            print(f"Failed to normalize '{old_name}': {e}")
            print("Deleting duplicate...")
            m.delete()

print(f"\nDone. Normalized {count} rooms.")
