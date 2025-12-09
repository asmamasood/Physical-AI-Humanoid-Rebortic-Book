---
sidebar_position: 2
---

# Create a Document (Urdu - Placeholder)

Documents are **groups of pages** connected through: (Urdu - Placeholder)

- a **sidebar** (Urdu - Placeholder)
- **previous/next navigation** (Urdu - Placeholder)
- **versioning** (Urdu - Placeholder)

## Create your first Doc (Urdu - Placeholder)

Create a Markdown file at `docs/hello.md`: (Urdu - Placeholder)

```md title="docs/hello.md"
# Hello (Urdu - Placeholder)

This is my **first Docusaurus document**! (Urdu - Placeholder)
```

A new document is now available at [http://localhost:3000/docs/hello](http://localhost:3000/docs/hello). (Urdu - Placeholder)

## Configure the Sidebar (Urdu - Placeholder)

Docusaurus automatically **creates a sidebar** from the `docs` folder. (Urdu - Placeholder)

Add metadata to customize the sidebar label and position: (Urdu - Placeholder)

```md title="docs/hello.md" {1-4}
---
sidebar_label: 'Hi! (Urdu - Placeholder)'
sidebar_position: 3
---

# Hello (Urdu - Placeholder)

This is my **first Docusaurus document**! (Urdu - Placeholder)
```

It is also possible to create your sidebar explicitly in `sidebars.js`: (Urdu - Placeholder)

```js title="sidebars.js"
export default {
  tutorialSidebar: [
    'intro',
    // highlight-next-line
    'hello',
    {
      type: 'category',
      label: 'Tutorial (Urdu - Placeholder)',
      items: ['tutorial-basics/create-a-document'],
    },
  ],
};
```
