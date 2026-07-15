/**
 * 认证服务
 * Iter 3: 服务层
 * 依赖：UserModel, password, jwt
 */
const UserModel = require('../models/user');
const { verifyPassword } = require('../utils/password');
const { signToken } = require('../utils/jwt');
const { Errors } = require('../utils/errors');

const AuthService = {
  async login({ username, password }) {
    const user = UserModel.findByUsername(username);
    if (!user) throw Errors.INVALID_CREDENTIALS;
    const isValid = await verifyPassword(password, user.passwordHash);
    if (!isValid) throw Errors.INVALID_CREDENTIALS;
    const token = signToken(user.id);
    return { token };
  },
};

module.exports = AuthService;