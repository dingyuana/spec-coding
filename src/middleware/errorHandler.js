/**
 * 全局异常处理
 * Iter 4: HTTP 接口层
 */
const { AppError } = require('../utils/errors');

function errorHandler(err, ctx) {
  if (err instanceof AppError) {
    ctx.status = err.statusCode;
    ctx.body = { error: err.message };
    return;
  }
  ctx.status = 500;
  ctx.body = { error: '服务器内部错误' };
}

module.exports = errorHandler;