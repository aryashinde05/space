import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { migrate } from './db.js';
import spacesRouter from './routes/spaces.js';

dotenv.config();

const app = express();

const corsOriginsEnv = process.env.CORS_ORIGIN;
const corsOptions = {};
if (!corsOriginsEnv || corsOriginsEnv === '*' ) {
  corsOptions.origin = true; // reflect request origin
} else {
  corsOptions.origin = corsOriginsEnv.split(',').map(s => s.trim());
}

app.use(cors(corsOptions));
app.use(express.json());

app.get('/healthz', (_req, res) => {
  res.json({ status: 'ok', time: new Date().toISOString() });
});

app.use('/api/spaces', spacesRouter);

const port = Number(process.env.PORT || 4000);

async function start() {
  try {
    await migrate();
    app.listen(port, () => {
      console.log(`API listening on port ${port}`);
    });
  } catch (err) {
    console.error('Failed to start server', err);
    process.exit(1);
  }
}

start();
