# properties/permissions.py

from rest_framework.permissions import BasePermission

from accounts.models import User


# Allow only owners
class IsOwner(BasePermission):

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.role == User.Role.OWNER
        )

class IsPropertyOwner(BasePermission):
    def has_object_permission(self,request,view,obj):
        return(
            request.user.is_authenticated
            and obj.owner_id==request.user.id
        )