/**
 * 用户角色常量定义
 * 与后端 app/models/user.py 中的 UserRole 保持一致
 */

// 角色常量
export const UserRole = {
  SUPER_ADMIN: 'super_admin',          // 超级管理员
  ANPU_STAFF: 'anpu_staff',            // 安普员工
  ENTERPRISE_ADMIN: 'enterprise_admin', // 企业管理员
  ENTERPRISE_STAFF: 'enterprise_staff'  // 企业员工
}

// 所有有效角色
export const ALL_ROLES = [
  UserRole.SUPER_ADMIN,
  UserRole.ANPU_STAFF,
  UserRole.ENTERPRISE_ADMIN,
  UserRole.ENTERPRISE_STAFF
]

// 具有管理权限的角色
export const ADMIN_ROLES = [
  UserRole.SUPER_ADMIN,
  UserRole.ANPU_STAFF,
  UserRole.ENTERPRISE_ADMIN
]

// 安普内部角色
export const ANPU_ROLES = [
  UserRole.SUPER_ADMIN,
  UserRole.ANPU_STAFF
]

// 企业角色
export const ENTERPRISE_ROLES = [
  UserRole.ENTERPRISE_ADMIN,
  UserRole.ENTERPRISE_STAFF
]

// 角色中文名称映射
export const ROLE_NAMES = {
  [UserRole.SUPER_ADMIN]: '超级管理员',
  [UserRole.ANPU_STAFF]: '安普员工',
  [UserRole.ENTERPRISE_ADMIN]: '企业管理员',
  [UserRole.ENTERPRISE_STAFF]: '企业员工'
}

/**
 * 获取角色中文名称
 * @param {string} role 角色标识
 * @returns {string} 角色中文名称
 */
export function getRoleName(role) {
  return ROLE_NAMES[role] || '未知角色'
}

/**
 * 检查是否是管理员角色
 * @param {string} role 角色标识
 * @returns {boolean}
 */
export function isAdminRole(role) {
  return ADMIN_ROLES.includes(role)
}

/**
 * 检查是否是安普内部角色
 * @param {string} role 角色标识
 * @returns {boolean}
 */
export function isAnpuRole(role) {
  return ANPU_ROLES.includes(role)
}

/**
 * 检查是否是超级管理员
 * @param {string} role 角色标识
 * @returns {boolean}
 */
export function isSuperAdmin(role) {
  return role === UserRole.SUPER_ADMIN
}

export default {
  UserRole,
  ALL_ROLES,
  ADMIN_ROLES,
  ANPU_ROLES,
  ENTERPRISE_ROLES,
  ROLE_NAMES,
  getRoleName,
  isAdminRole,
  isAnpuRole,
  isSuperAdmin
}
