from django.contrib.auth.models import Group


def get_user_type(user):
    """
    Determine user type based on group membership.
    Priority: admin > creator > public
    """
    if user.groups.filter(name='admin').exists():
        return 'admin'
    elif user.groups.filter(name='creator').exists():
        return 'creator'
    elif user.groups.filter(name='public').exists():
        return 'public'
    else:
        # Default to public if no group is assigned
        return 'public'


def assign_user_to_group(user, group_name):
    """
    Assign a user to a specific group, removing them from other user type groups.
    """
    # Remove user from all user type groups
    user_type_groups = ['public', 'creator', 'admin']
    for group in user_type_groups:
        try:
            g = Group.objects.get(name=group)
            user.groups.remove(g)
        except Group.DoesNotExist:
            pass
    
    # Add user to the specified group
    try:
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
        return True
    except Group.DoesNotExist:
        return False


def get_available_user_types():
    """
    Get list of available user types.
    """
    return ['public', 'creator', 'admin']
