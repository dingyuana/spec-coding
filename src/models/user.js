/**
 * User 模型
 * Iter 2: 数据模型层 — 内存 Map 存储
 */
const users = new Map();
let nextId = 1;

const UserModel = {
  findByUsername(username) {
    return Array.from(users.values()).find((u) => u.username === username);
  },

  findById(id) {
    return users.get(id);
  },

  create({ username, passwordHash }) {
    const now = new Date();
    const user = { id: nextId++, username, passwordHash, createdAt: now };
    users.set(user.id, user);
    return user;
  },

  clear() {
    users.clear();
    nextId = 1;
  },
};

module.exports = UserModel;