class AuthenticationError(Exception):
    """认证异常"""
    pass


class PermissionError(Exception):
    """权限异常"""
    pass


class ResourceNotFoundError(Exception):
    """资源不存在异常"""
    pass
