/**
 * JWT 工具 — TDD 测试
 * Iter 1: 工具函数层
 * payload 格式: { user_id, exp }
 */

const jwt = require('jsonwebtoken');
const config = require('../../src/config');
const { signToken, verifyToken } = require('../../src/utils/jwt');

jest.mock('jsonwebtoken');

describe('jwt utils', () => {
  beforeEach(() => { jest.clearAllMocks(); });

  describe('signToken', () => {
    it('签发 token 应使用 user_id', () => {
      jwt.sign.mockReturnValue('mock-token');
      const token = signToken(1);
      expect(jwt.sign).toHaveBeenCalledWith(
        { user_id: 1 },
        config.jwt.secret,
        { expiresIn: config.jwt.expiresIn }
      );
      expect(token).toBe('mock-token');
    });
  });

  describe('verifyToken', () => {
    it('有效 token 应返回 decoded payload', () => {
      const payload = { user_id: 1, exp: 9999999999 };
      jwt.verify.mockReturnValue(payload);
      const result = verifyToken('valid-token');
      expect(jwt.verify).toHaveBeenCalledWith('valid-token', config.jwt.secret);
      expect(result).toEqual(payload);
    });

    it('无效 token 应抛出异常', () => {
      jwt.verify.mockImplementation(() => { throw new Error('jwt malformed'); });
      expect(() => verifyToken('bad-token')).toThrow();
    });
  });
});