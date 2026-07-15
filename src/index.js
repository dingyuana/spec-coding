/**
 * 入口
 * Iter 4: HTTP 接口层
 */
const config = require('./config');
const { createApp } = require('./app');
const { seedDatabase } = require('../scripts/seed');

async function main() {
  await seedDatabase();
  const app = createApp();
  app.listen(config.port, () => {
    console.log(`[server] http://localhost:${config.port}`);
  });
}

main().catch((err) => { console.error(err.message); process.exit(1); });