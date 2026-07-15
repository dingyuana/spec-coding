/**
 * 种子数据脚本
 * Iter 2: 数据模型层
 * 预置 admin 用户，支持幂等性
 */
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

const UserModel = require('../src/models/user');
const { hashPassword } = require('../src/utils/password');

const SEED_USER = { username: 'admin', password: 'admin123' };

async function seedDatabase() {
  const existing = UserModel.findByUsername(SEED_USER.username);
  if (existing) {
    console.log(`[seed] ${SEED_USER.username} 已存在，跳过`);
    return existing;
  }
  const passwordHash = await hashPassword(SEED_USER.password);
  const user = UserModel.create({ username: SEED_USER.username, passwordHash });
  console.log(`[seed] ${user.username} 创建成功 (id=${user.id})`);
  return user;
}

if (require.main === module) {
  seedDatabase().then(() => process.exit(0)).catch((err) => { console.error(err.message); process.exit(1); });
}

module.exports = { seedDatabase, SEED_USER };