from enum import Enum

class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"

ROLE_PERMISSIONS = {
    UserRole.USER.value: [
        "transcribe:use",
        "profile:view",
        "profile:edit"
    ],
    UserRole.ADMIN.value: [
        "admin:access",
        "users:view",
        "users:edit",
        "users:delete",
        "subscriptions:view",
        "subscriptions:manage",
        "statistics:view"
    ]
}