/**
 * User 模型 — TDD 测试
 * Iter 2: 数据模型层
 */

const UserModel = require('../../src/models/user');

describe('UserModel', () => {
  beforeEach(() => {
    UserModel.clear();
  });

  describe('create', () => {
    it('应创建用户并返回完整信息', () => {
      const user = UserModel.create({ username: 'alice', passwordHash: 'hash123' });
      expect(user.id).toBe(1);
      expect(user.username).toBe('alice');
      expect(user.passwordHash).toBe('hash123');
      expect(user.createdAt).toBeInstanceOf(Date);
    });
  });

  describe('findByUsername', () => {
    it('存在时返回用户', () => {
      UserModel.create({ username: 'alice', passwordHash: 'hash123' });
      const user = UserModel.findByUsername('alice');
      expect(user).toBeDefined();
      expect(user.username).toBe('alice');
    });

    it('不存在时返回 undefined', () => {
      const user = UserModel.findByUsername('nobody');
      expect(user).toBeUndefined();
    });
  });

  describe('findById', () => {
    it('存在时返回用户', () => {
      const created = UserModel.create({ username: 'alice', passwordHash: 'hash123' });
      const user = UserModel.findById(created.id);
      expect(user).toBeDefined();
      expect(user.id).toBe(created.id);
    });

    it('不存在时返回 undefined', () => {
      expect(UserModel.findById(999)).toBeUndefined();
    });
  });

  describe('clear', () => {
    it('应清空所有用户', () => {
      UserModel.create({ username: 'alice', passwordHash: 'hash123' });
      UserModel.clear();
      expect(UserModel.findByUsername('alice')).toBeUndefined();
    });
  });
});