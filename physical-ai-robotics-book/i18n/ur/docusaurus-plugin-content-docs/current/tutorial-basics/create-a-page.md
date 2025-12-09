---
sidebar_position: 1
---

# Create a Page (Urdu - Placeholder)

Add **Markdown or React** files to `src/pages` to create a **standalone page**: (Urdu - Placeholder)

- `src/pages/index.js` → `localhost:3000/` (Urdu - Placeholder)
- `src/pages/foo.md` → `localhost:3000/foo` (Urdu - Placeholder)
- `src/pages/foo/bar.js` → `localhost:3000/foo/bar` (Urdu - Placeholder)

## Create your first React Page (Urdu - Placeholder)

Create a file at `src/pages/my-react-page.js`: (Urdu - Placeholder)

```jsx title="src/pages/my-react-page.js"
import React from 'react';
import Layout from '@theme/Layout';

export default function MyReactPage() {
  return (
    <Layout>
      <h1>My React page (Urdu - Placeholder)</h1>
      <p>This is a React page (Urdu - Placeholder)</p>
    </Layout>
  );
}
```

A new page is now available at [http://localhost:3000/my-react-page](http://localhost:3000/my-react-page). (Urdu - Placeholder)

## Create your first Markdown Page (Urdu - Placeholder)

Create a file at `src/pages/my-markdown-page.md`: (Urdu - Placeholder)

```mdx title="src/pages/my-markdown-page.md"
# My Markdown page (Urdu - Placeholder)

This is a Markdown page (Urdu - Placeholder)
```

A new page is now available at [http://localhost:3000/my-markdown-page](http://localhost:3000/my-markdown-page). (Urdu - Placeholder)
