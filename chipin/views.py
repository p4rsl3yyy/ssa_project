from django.http import HttpResponse 
from django.shortcuts import render

def home(request):
    return render(request, "chipin/home.html")
    @login_required
    def home(request):
        pending_invitations = Group.objects.filter(invited_users__email=request.user.email)
        return render(request, "chipin/home.html", {'pending_invitations': pending_invitations})


    @login_required
    def invite_users(request, group_id):
        group = get_object_or_404(Group, id=group_id)
        users_not_in_group = User.objects.exclude(id__in=group.members.values_list('id', flat=True))
        if request.method == 'POST':
            user_id = request.POST.get('user_id')
        invited_user = get_object_or_404(User, id=user_id)      
        if invited_user in group.invited_users.all():
            messages.info(request, f'{invited_user.profile.nickname} has already been invited.')
        else:
            group.invited_users.add(invited_user)
            messages.success(request, f'Invitation sent to {invited_user.profile.nickname}.')
        return redirect('chipin:group_detail', group_id=group.id)  
    return render(request, 'chipin/invite_users.html', {
        'group': group,
        'users_not_in_group': users_not_in_group
    })