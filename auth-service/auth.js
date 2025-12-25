import { betterAuth } from "better-auth";
import pg from "pg";
const { Pool } = pg;

// Create pool with better connection management
const pool = new Pool({
    connectionString: process.env.NEON_DB_URL,
    max: 10, // Maximum pool size
    idleTimeoutMillis: 30000, // Close idle connections after 30s
    connectionTimeoutMillis: 10000, // Wait 10s for a connection
});

// Handle pool errors
pool.on('error', (err) => {
    console.error('Unexpected database pool error:', err);
});

export const auth = betterAuth({
    database: pool,
    secret: process.env.BETTER_AUTH_SECRET,
    baseURL: "http://localhost:3001/api/auth",
    emailAndPassword: {
        enabled: true,
        autoSignIn: true
    },
    trustedOrigins: [
        "https://asmamasood.github.io",
        "http://localhost:3000",
        "http://localhost:3001"
    ]
});
