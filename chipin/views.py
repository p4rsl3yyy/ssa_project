from django.http import HttpResponse 
from django.shortcuts import render
from .models import GroupJoinRequest
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import GroupJoinRequest
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

def accept_invite(request, group_id):
    return HttpResponse(f"Accepted invite for group {group_id}")

from django.http import HttpResponse

def create_group(request):
    return HttpResponse("Group created successfully!")

from django.http import HttpResponse

def group_detail(request, group_id):
    return HttpResponse(f"Details of group with ID: {group_id}")

from django.http import HttpResponse

def invite_users(request):
    return HttpResponse("Invite users functionality.")

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Group

def delete_group(request, group_id):
    if request.method == "POST":  # Ensure it's a POST request
        group = get_object_or_404(Group, id=group_id)
        group.delete()
        return JsonResponse({"message": "Group deleted successfully"})
    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def request_to_join_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    # Check if the user is already a member
    if request.user in group.members.all():
        messages.info(request, "You are already a member of this group.")
        return redirect('chipin:group_detail', group_id=group.id)
    # Check if the user has already submitted a join request
    join_request, created = GroupJoinRequest.objects.get_or_create(user=request.user, group=group)
    if created:
        messages.success(request, "Your request to join the group has been submitted.")
    else:
        messages.info(request, "You have already requested to join this group.")
    return redirect('chipin:group_detail', group_id=group.id)

@login_required
def delete_join_request(request, request_id):
    join_request = get_object_or_404(GroupJoinRequest, id=request_id, user=request.user)
    # Ensure the logged-in user can only delete their own join requests
    if join_request.user == request.user:
        join_request.delete()
        messages.success(request, "Your join request has been successfully deleted.")
    else:
        messages.error(request, "You are not authorised to delete this join request.")
    return redirect('chipin:home')  
    

@login_required
def leave_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    # Check if the user is a member of the group
    if request.user in group.members.all():
        group.members.remove(request.user)  # Remove the user from the group
        messages.success(request, f'You have left the group {group.name}.')
    else:
        messages.error(request, 'You are not a member of this group.') 
    return redirect('chipin:home')  

@login_required
def home(request):
    # Get all groups where the user has been invited but not accepted the invite
    pending_invitations = Group.objects.filter(invited_users=request.user)
    
    # Get all join requests submitted by the current user
    user_join_requests = GroupJoinRequest.objects.filter(user=request.user)

    # Get all groups where the user is NOT a member
    available_groups = Group.objects.exclude(members=request.user)

    return render(request, 'chipin/home.html', { # Pass data to the template
        'pending_invitations': pending_invitations, 
        'user_join_requests': user_join_requests, 
        'available_groups': available_groups  
    })

@login_required
def vote_on_join_request(request, group_id, request_id, vote):
    group = get_object_or_404(Group, id=group_id)
    join_request = get_object_or_404(GroupJoinRequest, id=request_id) 
    if request.user not in group.members.all():
        messages.error(request, "You must be a member of the group to vote.")
        return redirect('chipin:group_detail', group_id=group.id)  
    if request.user in join_request.votes.all():
        messages.info(request, "You have already voted.")
        return redirect('chipin:group_detail', group_id=group.id)
        
    # Register the user's vote
    join_request.votes.add(request.user)
    
    # Calculate if more than 60% of members have approved
    total_members = group.members.count()
    total_votes = join_request.votes.count() 
    if total_votes / total_members >= 0.6:
        join_request.is_approved = True
        group.members.add(join_request.user)  # Add the user to the group
        join_request.save()
        messages.success(request, f"{join_request.user.profile.nickname} has been approved to join the group!") 
    return redirect('chipin:group_detail', group_id=group.id)