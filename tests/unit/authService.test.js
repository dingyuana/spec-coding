/**
 * 认证服务 — TDD 测试
 * Iter 3: 服务层
 * 覆盖：正常登录 / 密码错误 / 用户不存在
 */

const mockUserModel = { findByUsername: jest.fn() };
const mockPassword = { verifyPassword: jest.fn() };
const mockJwt = { signToken: jest.fn() };

jest.mock('../../src/models/user', () => mockUserModel);
jest.mock('../../src/utils/password', () => mockPassword);
jest.mock('../../src/utils/jwt', () => mockJwt);

const AuthService = require('../../src/services/authService');

describe('AuthService.login', () => {
  const mockUser = { id: 1, username: 'admin', passwordHash: 'hashed-password' };

  beforeEach(() => { jest.clearAllMocks(); });

  it('用户名密码正确应返回 token', async () => {
    mockUserModel.findByUsername.mockReturnValue(mockUser);
    mockPassword.verifyPassword.mockResolvedValue(true);
    mockJwt.signToken.mockReturnValue('valid-token');

    const result = await AuthService.login({ username: 'admin', password: 'admin123' });
    expect(mockUserModel.findByUsername).toHaveBeenCalledWith('admin');
    expect(mockPassword.verifyPassword).toHaveBeenCalledWith('admin123', 'hashed-password');
    expect(mockJwt.signToken).toHaveBeenCalledWith(1);
    expect(result).toEqual({ token: 'valid-token' });
  });

  it('密码错误应抛出 INVALID_CREDENTIALS', async () => {
    mockUserModel.findByUsername.mockReturnValue(mockUser);
    mockPassword.verifyPassword.mockResolvedValue(false);
    await expect(AuthService.login({ username: 'admin', password: 'wrongpass' }))
      .rejects.toMatchObject({ statusCode: 401, message: '用户名或密码错误' });
  });

  it('用户不存在应抛出 INVALID_CREDENTIALS', async () => {
    mockUserModel.findByUsername.mockReturnValue(undefined);
    await expect(AuthService.login({ username: 'ghost', password: 'x' }))
      .rejects.toMatchObject({ statusCode: 401, message: '用户名或密码错误' });
  });
});