from rest_framework.permissions import BasePermission


class IsScenarioOwner(BasePermission):
    message = "Сцена принадлежит другому сценарию"

    def has_object_permission(self, request, _view, obj):
        return obj.scenario.owner_id == request.user.id
