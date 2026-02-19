from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import uuid
import json
from .models import MeetingRoom, JoinRequest

def index(request):
    """
    Landing page with options to Host or Join a meeting.
    """
    msg = request.GET.get('msg')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        room_name = request.POST.get('room_name')
        
        if action == 'host':
            # Generate a random room name for hosting
            new_room = str(uuid.uuid4())[:8]
            
            # Create/Update MeetingRoom record
            MeetingRoom.objects.update_or_create(
                room_name=new_room,
                defaults={'is_host_active': True}
            )
            
            # Store in session that this user is the host
            request.session['hosting_' + new_room] = True
            request.session.save()
            
            target_url = reverse('meeting', kwargs={'room_name': new_room})
            return redirect(f"{target_url}?role=host")
        
        elif action == 'join' and room_name:
            return redirect('meeting', room_name=room_name)
            
    return render(request, 'meetings/index.html', {'msg': msg})

def meeting(request, room_name):
    """
    Meeting room page where Gatekeeper or Jitsi is shown.
    """
    is_host = request.session.get('hosting_' + room_name, False) or request.GET.get('role') == 'host'
    room, created = MeetingRoom.objects.get_or_create(room_name=room_name)
    
    # If Host, ensure room is active
    if is_host:
        room.is_host_active = True
        room.save()
        # Ensure session is set if they joined via URL param
        request.session['hosting_' + room_name] = True
        request.session.save()

    # If Guest, check if they have an approved request in this session
    approved_request_id = request.session.get('approved_request_' + room_name)
    is_approved = False
    if approved_request_id:
        try:
            join_req = JoinRequest.objects.get(id=approved_request_id, room=room, status='APPROVED')
            is_approved = True
        except JoinRequest.DoesNotExist:
            pass

    return render(request, 'meetings/meeting.html', {
        'room_name': room_name,
        'is_host': is_host,
        'is_approved': is_approved,
        'is_room_active': room.is_host_active
    })

# --- GATEKEEPER API ENDPOINTS ---

@csrf_exempt
def api_request_join(request, room_name):
    """Guest submits a request to join."""
    if request.method == 'POST':
        data = json.loads(request.body)
        guest_name = data.get('name', 'Anonymous')
        room = get_object_or_404(MeetingRoom, room_name=room_name)
        
        join_req = JoinRequest.objects.create(room=room, guest_name=guest_name)
        return JsonResponse({'request_id': join_req.id, 'status': join_req.status})
    return JsonResponse({'error': 'Invalid method'}, status=400)

def api_check_status(request, request_id):
    """Guest polls for approval status."""
    join_req = get_object_or_404(JoinRequest, id=request_id)
    
    if join_req.status == 'APPROVED':
        # Store in session so they don't have to knock again if they refresh
        request.session['approved_request_' + join_req.room.room_name] = join_req.id
        request.session.save()
        
    return JsonResponse({'status': join_req.status})

def api_get_requests(request, room_name):
    """Host gets pending requests."""
    if not request.session.get('hosting_' + room_name, False):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    room = get_object_or_404(MeetingRoom, room_name=room_name)
    requests = JoinRequest.objects.filter(room=room, status='PENDING').values('id', 'guest_name', 'created_at')
    return JsonResponse({'requests': list(requests)})

@csrf_exempt
def api_approve_request(request, request_id):
    """Host approves or rejects a request."""
    join_req = get_object_or_404(JoinRequest, id=request_id)
    
    if not request.session.get('hosting_' + join_req.room.room_name, False):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action') # 'APPROVED' or 'REJECTED'
        if action in ['APPROVED', 'REJECTED']:
            join_req.status = action
            join_req.save()
            return JsonResponse({'status': 'success'})
            
    return JsonResponse({'error': 'Invalid request'}, status=400)

def end_meeting(request, room_name):
    """Host ends the meeting, clearing active room and requests."""
    if request.session.get('hosting_' + room_name, False):
        MeetingRoom.objects.filter(room_name=room_name).update(is_host_active=False)
        JoinRequest.objects.filter(room__room_name=room_name).delete()
        request.session['hosting_' + room_name] = False
    return redirect(f"{reverse('index')}?msg=MeetingEnded")
