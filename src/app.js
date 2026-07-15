/**
 * 应用工厂
 * Iter 4: HTTP 接口层
 */
const Koa = require('koa');
const bodyParser = require('koa-bodyparser');
const authRouter = require('./routes/auth');
const errorHandler = require('./middleware/errorHandler');

function createApp() {
  const app = new Koa();
  app.use(bodyParser());
  app.use(async (ctx, next) => {
    try { await next(); }
    catch (err) { errorHandler(err, ctx); }
  });
  app.use(authRouter.routes());
  app.use(authRouter.allowedMethods());
  return app;
}

module.exports = { createApp };