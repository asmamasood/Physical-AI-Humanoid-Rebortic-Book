---
sidebar_position: 1
---

# Manage Docs Versions (Urdu - Placeholder)

Docusaurus can manage multiple versions of your docs. (Urdu - Placeholder)

## Create a docs version (Urdu - Placeholder)

Release a version 1.0 of your project: (Urdu - Placeholder)

```bash
npm run docusaurus docs:version 1.0
```

The `docs` folder is copied into `versioned_docs/version-1.0` and `versions.json` is created. (Urdu - Placeholder)

Your docs now have 2 versions: (Urdu - Placeholder)

- `1.0` at `http://localhost:3000/docs/` for the version 1.0 docs (Urdu - Placeholder)
- `current` at `http://localhost:3000/docs/next/` for the **upcoming, unreleased docs** (Urdu - Placeholder)

## Add a Version Dropdown (Urdu - Placeholder)

To navigate seamlessly across versions, add a version dropdown. (Urdu - Placeholder)

Modify the `docusaurus.config.js` file: (Urdu - Placeholder)

```js title="docusaurus.config.js"
export default {
  themeConfig: {
    navbar: {
      items: [
        // highlight-start
        {
          type: 'docsVersionDropdown',
        },
        // highlight-end
      ],
    },
  },
};
```

The docs version dropdown appears in your navbar: (Urdu - Placeholder)

![Docs Version Dropdown](./img/docsVersionDropdown.png) (Urdu - Placeholder)

## Update an existing version (Urdu - Placeholder)

It is possible to edit versioned docs in their respective folder: (Urdu - Placeholder)

- `versioned_docs/version-1.0/hello.md` updates `http://localhost:3000/docs/hello` (Urdu - Placeholder)
- `docs/hello.md` updates `http://localhost:3000/docs/next/hello` (Urdu - Placeholder)
