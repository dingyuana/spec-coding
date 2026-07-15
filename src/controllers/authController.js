/**
 * 认证控制器
 * Iter 4: HTTP 接口层
 */
const AuthService = require('../services/authService');
const { Errors } = require('../utils/errors');

const AuthController = {
  async login(ctx) {
    const { username, password } = ctx.request.body;
    if (!username || !password) throw Errors.MISSING_PARAMS('用户名和密码不能为空');
    const { token } = await AuthService.login({ username, password });
    ctx.status = 200;
    ctx.body = { token };
  },
};

module.exports = AuthController;