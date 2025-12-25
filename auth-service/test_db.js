import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import pg from 'pg';

const __dirname = dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: join(__dirname, '.env') });

const { Pool } = pg;
console.log("Connecting to:", process.env.NEON_DB_URL.replace(/:[^:/@]+@/, ":***@"));

const pool = new Pool({
    connectionString: process.env.NEON_DB_URL,
    ssl: { rejectUnauthorized: false } // Try relaxed SSL
});

async function test() {
    try {
        const client = await pool.connect();
        console.log("Connected successfully!");
        const res = await client.query('SELECT NOW()');
        console.log("Time:", res.rows[0]);
        client.release();
        await pool.end();
    } catch (err) {
        console.error("Connection failed:", err);
    }
}

test();
