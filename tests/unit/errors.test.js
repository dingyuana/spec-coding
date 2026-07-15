/**
 * 错误类 — TDD 测试
 * Iter 1: 工具函数层
 */

const { AppError, Errors } = require('../../src/utils/errors');

describe('AppError', () => {
  it('应携带 message 和 statusCode', () => {
    const err = new AppError('自定义错误', 400);
    expect(err).toBeInstanceOf(Error);
    expect(err.message).toBe('自定义错误');
    expect(err.statusCode).toBe(400);
  });

  it('默认 statusCode 应为 500', () => {
    const err = new AppError('服务器错误');
    expect(err.statusCode).toBe(500);
  });

  it('应正确捕获堆栈', () => {
    const err = new AppError('测试');
    expect(err.stack).toBeDefined();
    expect(err.stack).toContain('AppError');
  });
});

describe('Errors 预定义错误', () => {
  it('INVALID_CREDENTIALS: 401 用户名或密码错误', () => {
    expect(Errors.INVALID_CREDENTIALS.statusCode).toBe(401);
    expect(Errors.INVALID_CREDENTIALS.message).toBe('用户名或密码错误');
  });

  it('MISSING_PARAMS: 工厂函数应生成动态消息', () => {
    const err = Errors.MISSING_PARAMS('用户名和密码不能为空');
    expect(err.statusCode).toBe(400);
    expect(err.message).toBe('用户名和密码不能为空');
  });

  it('INTERNAL: 500 服务器内部错误', () => {
    expect(Errors.INTERNAL.statusCode).toBe(500);
    expect(Errors.INTERNAL.message).toBe('服务器内部错误');
  });
});