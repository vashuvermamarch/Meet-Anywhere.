from django.shortcuts import render, redirect
import uuid

def index(request):
    """
    Landing page with options to Host or Join a meeting.
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        room_name = request.POST.get('room_name')
        
        if action == 'host':
            # Generate a random room name for hosting
            new_room = str(uuid.uuid4())[:8]
            return redirect('meeting', room_name=new_room)
        
        elif action == 'join' and room_name:
            # Join an existing room
            return redirect('meeting', room_name=room_name)
            
    return render(request, 'meetings/index.html')

def meeting(request, room_name):
    """
    Meeting room page where Jitsi is embedded.
    """
    return render(request, 'meetings/meeting.html', {
        'room_name': room_name
    })
