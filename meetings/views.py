from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import uuid
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
import os
from .models import Meeting, JoinRequest
from .utils import generate_jitsi_jwt

def signup(request):
    """
    User registration view.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def index(request):
    """
    Landing page for authenticated users.
    """
    msg = request.GET.get('msg')
    return render(request, 'meetings/index.html', {'msg': msg})

@login_required
def create_meeting(request):
    """
    Host-only meeting creation with duplicate handling.
    """
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        if not room_name:
            room_name = str(uuid.uuid4())[:8]
        
        # Check if room already exists
        existing_meeting = Meeting.objects.filter(room_name=room_name).first()
        
        if existing_meeting:
            if existing_meeting.host == request.user:
                # User already owns this room, just ensure it's active
                existing_meeting.is_active = True
                existing_meeting.save()
                return redirect('meeting', room_name=room_name)
            else:
                # Room taken by someone else
                return render(request, 'meetings/index.html', {
                    'msg': 'RoomNameTaken',
                    'error': f'The room name "{room_name}" is already taken by another host. Please choose a different name.'
                })
        
        # Create new meeting
        meeting = Meeting.objects.create(
            room_name=room_name,
            host=request.user,
            is_public=True  # Ensure participants can join by default
        )
        return redirect('meeting', room_name=meeting.room_name)
    
    return redirect('index')

@login_required
def meeting(request, room_name):
    """
    Production-quality Jitsi join view.
    Ensures roles are strictly detected and authorized before joining.
    """
    meeting = get_object_or_404(Meeting, room_name=room_name, is_active=True)
    
    # Permission logic
    is_host = (meeting.host == request.user)
    is_authorized = meeting.is_public or is_host or meeting.authorized_participants.filter(id=request.user.id).exists()
    
    if not is_authorized:
        return HttpResponseForbidden("You are not authorized to join this meeting.")

    # ✅ CUSTOM APPROVAL GATE
    if not is_host:
        join_request = JoinRequest.objects.filter(meeting=meeting, user=request.user).first()
        if not join_request or join_request.status != 'APPROVED':
            return redirect('waiting_room', room_name=room_name)

    from django.conf import settings
    # Ensure domain handling is consistent with JWT logic
    jitsi_domain = getattr(settings, 'JITSI_DOMAIN', 'meet.jit.si')

    from django.utils.text import slugify
    normalized_room = slugify(room_name).lower()

    # Generate JWT using helper with explicit is_host role
    jwt_token = generate_jitsi_jwt(request.user, normalized_room, is_host=is_host)

    return render(request, 'meetings/meeting.html', {
        'room_name': room_name,
        'room_name_slug': normalized_room,
        'jitsi_domain': jitsi_domain,
        'jwt_token': jwt_token,
        'is_host': is_host,
        'username': request.user.username,
    })

def end_meeting(request, room_name):
    """
    Host ends the meeting permanently.
    """
    meeting = get_object_or_404(Meeting, room_name=room_name)
    if meeting.host == request.user:
        meeting.is_active = False
        meeting.save()
    return redirect(f"{reverse('index')}?msg=MeetingEnded")
@login_required
def waiting_room(request, room_name):
    """
    Participant waits here for host approval.
    """
    meeting = get_object_or_404(Meeting, room_name=room_name)
    join_request, created = JoinRequest.objects.get_or_create(meeting=meeting, user=request.user)
    
    if join_request.status == 'APPROVED':
        return redirect('meeting', room_name=room_name)
        
    return render(request, 'meetings/waiting_room.html', {
        'room_name': room_name,
        'status': join_request.status
    })

@login_required
def check_request_status(request, room_name):
    """
    AJAX endpoint for participants to poll their status.
    """
    join_request = JoinRequest.objects.filter(meeting__room_name=room_name, user=request.user).first()
    if not join_request:
        return JsonResponse({'status': 'NONE'})
    return JsonResponse({'status': join_request.status})

@login_required
def manage_requests(request, room_name):
    """
    Host view to see and manage pending requests (AJAX).
    """
    meeting = get_object_or_404(Meeting, room_name=room_name)
    if meeting.host != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    pending = JoinRequest.objects.filter(meeting=meeting, status='PENDING').select_related('user')
    data = [{'id': r.id, 'username': r.user.username} for r in pending]
    return JsonResponse({'requests': data})

@csrf_exempt
@login_required
def respond_to_request(request, room_name):
    """
    Host action to Accept or Deny (AJAX).
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
        
    meeting = get_object_or_404(Meeting, room_name=room_name)
    if meeting.host != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    data = json.loads(request.body)
    request_id = data.get('request_id')
    new_status = data.get('status') # 'APPROVED' or 'DENIED'
    
    if new_status not in ['APPROVED', 'DENIED']:
        return JsonResponse({'error': 'Invalid status'}, status=400)
        
    join_req = get_object_or_404(JoinRequest, id=request_id, meeting=meeting)
    join_req.status = new_status
    join_req.save()
    
    return JsonResponse({'success': True})
