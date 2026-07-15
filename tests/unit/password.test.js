/**
 * 密码工具 — TDD 测试
 * Iter 1: 工具函数层
 */

const bcrypt = require('bcryptjs');
const { hashPassword, verifyPassword } = require('../../src/utils/password');

jest.mock('bcryptjs');

describe('password utils', () => {
  beforeEach(() => { jest.clearAllMocks(); });

  describe('hashPassword', () => {
    it('应返回哈希后的密码', async () => {
      bcrypt.genSalt.mockResolvedValue('fake-salt');
      bcrypt.hash.mockResolvedValue('hashed-password-123');
      const result = await hashPassword('mypassword123');
      expect(bcrypt.genSalt).toHaveBeenCalledWith(10);
      expect(bcrypt.hash).toHaveBeenCalledWith('mypassword123', 'fake-salt');
      expect(result).toBe('hashed-password-123');
    });

    it('密码少于 6 位时应抛出错误', async () => {
      await expect(hashPassword('12')).rejects.toThrow('密码长度不能少于 6 位');
    });
  });

  describe('verifyPassword', () => {
    it('密码匹配时应返回 true', async () => {
      bcrypt.compare.mockResolvedValue(true);
      const result = await verifyPassword('mypassword', 'hashed-value');
      expect(result).toBe(true);
    });

    it('密码不匹配时应返回 false', async () => {
      bcrypt.compare.mockResolvedValue(false);
      const result = await verifyPassword('wrongpass', 'hashed-value');
      expect(result).toBe(false);
    });
  });
});