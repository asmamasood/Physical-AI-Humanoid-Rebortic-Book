import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

// Load .env FIRST
const __dirname = dirname(fileURLToPath(import.meta.url));
const envPath = join(__dirname, '.env');
console.log('Loading .env from:', envPath);
dotenv.config({ path: envPath });

console.log('BETTER_AUTH_SECRET present:', !!process.env.BETTER_AUTH_SECRET);
if (process.env.BETTER_AUTH_SECRET) {
    console.log('Secret length:', process.env.BETTER_AUTH_SECRET.length);
} else {
    console.error('CRITICAL: BETTER_AUTH_SECRET is missing!');
}
console.log('NEON_DB_URL present:', !!process.env.NEON_DB_URL);

// Dynamically import dependencies AFTER env is loaded
const express = (await import('express')).default;
const cors = (await import('cors')).default;
const { toNodeHandler } = await import("better-auth/node");
const { auth } = await import("./auth.js");

const app = express();
// app.use(express.json());

import fs from 'fs';

app.use(cors({
    origin: process.env.CORS_ORIGINS ? process.env.CORS_ORIGINS.split(',') : ["http://localhost:3000"],
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'Cookie']
}));

app.use((req, res, next) => {
    const log = `[${new Date().toISOString()}] ${req.method} ${req.url} Origin:${req.get('origin')}\n`;
    console.log(log.trim());
    fs.appendFileSync('debug.log', log);
    next();
});

try {
    console.log("Registering auth handler...");
    const handler = toNodeHandler(auth);
    console.log("Handler type:", typeof handler);
    // Use app.use to handle all /api/auth/* subroutes
    // This works with Express v5 without wildcards
    app.use("/api/auth", handler);
    console.log("Auth handler registered successfully.");
} catch (err) {
    console.error("CRITICAL ERROR registering auth handler:");
    console.error("Message:", err.message);
    console.error("Stack:", err.stack);
    console.error("Keys:", Object.keys(err));
    try { console.error("JSON:", JSON.stringify(err, null, 2)); } catch (e) { }
}

const PORT = 3001;
app.listen(PORT, () => {
    console.log(`Auth service running on http://localhost:${PORT}`);
    console.log(`Database: ${process.env.NEON_DB_URL ? 'Connected' : 'NOT CONFIGURED'}`);
});
