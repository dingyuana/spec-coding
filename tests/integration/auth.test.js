/**
 * 登录 API — 集成测试
 * Iter 4: HTTP 接口层
 * 覆盖 4 个 Scenario
 */

const request = require('supertest');
const { createApp } = require('../../src/app');
const { seedDatabase } = require('../../scripts/seed');
const UserModel = require('../../src/models/user');

let app;

beforeEach(async () => {
  UserModel.clear();
  await seedDatabase();
  app = createApp();
});

// ── Scenario 1: 正常登录 ──

describe('Scenario 1: 正常登录', () => {
  it('admin 正确密码应返回 200 和 JWT token', async () => {
    const res = await request(app.callback())
      .post('/api/auth/login')
      .send({ username: 'admin', password: 'admin123' });
    expect(res.status).toBe(200);
    expect(res.body.token).toBeDefined();
    expect(res.body.token.split('.')).toHaveLength(3);
  });

  it('JWT payload 应包含 user_id', async () => {
    const res = await request(app.callback())
      .post('/api/auth/login')
      .send({ username: 'admin', password: 'admin123' });
    const jwt = require('jsonwebtoken');
    const config = require('../../src/config');
    const decoded = jwt.verify(res.body.token, config.jwt.secret);
    expect(decoded.user_id).toBe(1);
  });
});

// ── Scenario 2: 密码错误 ──

describe('Scenario 2: 密码错误', () => {
  it('应返回 401 和错误消息', async () => {
    const res = await request(app.callback())
      .post('/api/auth/login')
      .send({ username: 'admin', password: 'wrongpass' });
    expect(res.status).toBe(401);
    expect(res.body.error).toBe('用户名或密码错误');
  });
});

// ── Scenario 3: 用户不存在 ──

describe('Scenario 3: 用户不存在', () => {
  it('应返回 401', async () => {
    const res = await request(app.callback())
      .post('/api/auth/login')
      .send({ username: 'hacker', password: 'x' });
    expect(res.status).toBe(401);
    expect(res.body.error).toBe('用户名或密码错误');
  });

  it('错误消息与密码错误完全一致（防枚举）', async () => {
    const [wrongPass, notFound] = await Promise.all([
      request(app.callback()).post('/api/auth/login').send({ username: 'admin', password: 'wrong' }),
      request(app.callback()).post('/api/auth/login').send({ username: 'ghost', password: 'x' }),
    ]);
    expect(wrongPass.body).toEqual(notFound.body);
  });
});

// ── Scenario 4: 参数缺失 ──

describe('Scenario 4: 参数缺失', () => {
  it('缺少 username 应返回 400', async () => {
    const res = await request(app.callback())
      .post('/api/auth/login')
      .send({ password: 'admin123' });
    expect(res.status).toBe(400);
    expect(res.body.error).toBe('用户名和密码不能为空');
  });

  it('缺少 password 应返回 400', async () => {
    const res = await request(app.callback())
      .post('/api/auth/login')
      .send({ username: 'admin' });
    expect(res.status).toBe(400);
    expect(res.body.error).toBe('用户名和密码不能为空');
  });

  it('两个字段都缺失应返回 400', async () => {
    const res = await request(app.callback())
      .post('/api/auth/login')
      .send({});
    expect(res.status).toBe(400);
    expect(res.body.error).toBe('用户名和密码不能为空');
  });
});