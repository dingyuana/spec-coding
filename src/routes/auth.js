/**
 * 路由
 * Iter 4: HTTP 接口层
 */
const Router = require('koa-router');
const AuthController = require('../controllers/authController');

const router = new Router({ prefix: '/api/auth' });
router.post('/login', AuthController.login);

module.exports = router;