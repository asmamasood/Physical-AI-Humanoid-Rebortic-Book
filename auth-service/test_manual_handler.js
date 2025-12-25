import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: join(__dirname, '.env') });

import { auth } from "./auth.js";
console.log("Secret present:", !!process.env.BETTER_AUTH_SECRET);

async function testCore() {
    console.log("Testing Core API...");
    try {
        // Mock request context? auth.api usually requires headers or request?
        // Server-side call might need ctx.
        // Actually better-auth client is for browser. server-side api is auth.api.
        const res = await auth.api.signInEmail({
            body: { email: "test@test.com", password: "pass" },
            headers: new Headers({ "host": "localhost:3001" }) // Mock headers
        });
        console.log("Core API Result:", res);
    } catch (e) {
        console.error("Core API Error:", e);
    }
}

async function testUrl(u) {
    console.log(`Testing ${u}...`);
    try {
        const req = new Request(u, {
            method: "GET",
            headers: { "origin": "http://localhost:3000", "host": "localhost:3001" }
        });
        const res = await auth.handler(req);
        console.log(`Status: ${res.status}`);
        const txt = await res.text();
        console.log(`Body: ${txt.substring(0, 100)}`);
    } catch (e) {
        console.error("Test Error:", e);
    }
}

async function test() {
    await testCore();
    await testUrl("http://localhost:3001/api/auth/session");
    await testUrl("http://localhost:3001/session");
}

test();
