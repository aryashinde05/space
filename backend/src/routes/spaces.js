import { Router } from 'express';
import { query } from '../db.js';

const router = Router();

router.get('/', async (_req, res) => {
  try {
    const result = await query(
      `SELECT id, name, description, image_url, created_at
       FROM spaces
       ORDER BY created_at DESC`
    );
    res.json(result.rows);
  } catch (err) {
    console.error('Error listing spaces', err);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

router.get('/:id', async (req, res) => {
  const { id } = req.params;
  try {
    const result = await query(
      `SELECT id, name, description, image_url, created_at
       FROM spaces WHERE id = $1`,
      [id]
    );
    if (result.rowCount === 0) {
      return res.status(404).json({ error: 'Not found' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error('Error fetching space', err);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

router.post('/', async (req, res) => {
  const { name, description, image_url } = req.body ?? {};
  if (!name || typeof name !== 'string') {
    return res.status(400).json({ error: 'name is required' });
  }
  try {
    const result = await query(
      `INSERT INTO spaces (name, description, image_url)
       VALUES ($1, $2, $3)
       RETURNING id, name, description, image_url, created_at`,
      [name, description ?? null, image_url ?? null]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error('Error creating space', err);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

router.delete('/:id', async (req, res) => {
  const { id } = req.params;
  try {
    const result = await query(`DELETE FROM spaces WHERE id = $1`, [id]);
    if (result.rowCount === 0) {
      return res.status(404).json({ error: 'Not found' });
    }
    res.status(204).send();
  } catch (err) {
    console.error('Error deleting space', err);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

export default router;
