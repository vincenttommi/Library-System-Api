from  rest_framework.permissions import BasePermission




class IsAdminUser(BasePermission):
    """_summary_
custom permission to allow  only admin users to perform certain actions
    """
    def has_permission(self, request, view):
        return request.user  and request.user.is_authenticated and  request.user.is_admin
    