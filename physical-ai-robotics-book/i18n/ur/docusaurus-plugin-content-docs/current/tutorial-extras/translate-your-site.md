---
sidebar_position: 2
---

# Translate your site (Urdu - Placeholder)

Let's translate `docs/intro.md` to French. (Urdu - Placeholder)

## Configure i18n (Urdu - Placeholder)

Modify `docusaurus.config.js` to add support for the `fr` locale: (Urdu - Placeholder)

```js title="docusaurus.config.js"
export default {
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'fr'],
  },
};
```

## Translate a doc (Urdu - Placeholder)

Copy the `docs/intro.md` file to the `i18n/fr` folder: (Urdu - Placeholder)

```bash
mkdir -p i18n/fr/docusaurus-plugin-content-docs/current/

cp docs/intro.md i18n/fr/docusaurus-plugin-content-docs/current/intro.md
```

Translate `i18n/fr/docusaurus-plugin-content-docs/current/intro.md` in French. (Urdu - Placeholder)

## Start your localized site (Urdu - Placeholder)

Start your site on the French locale: (Urdu - Placeholder)

```bash
npm run start -- --locale fr
```

Your localized site is accessible at [http://localhost:3000/fr/](http://localhost:3000/fr/) and the `Getting Started` page is translated. (Urdu - Placeholder)

:::caution

In development, you can only use one locale at a time. (Urdu - Placeholder)

:::

## Add a Locale Dropdown (Urdu - Placeholder)

To navigate seamlessly across languages, add a locale dropdown. (Urdu - Placeholder)

Modify the `docusaurus.config.js` file: (Urdu - Placeholder)

```js title="docusaurus.config.js"
export default {
  themeConfig: {
    navbar: {
      items: [
        // highlight-start
        {
          type: 'localeDropdown',
        },
        // highlight-end
      ],
    },
  },
};
```

The locale dropdown now appears in your navbar: (Urdu - Placeholder)

![Locale Dropdown](./img/localeDropdown.png) (Urdu - Placeholder)

## Build your localized site (Urdu - Placeholder)

Build your site for a specific locale: (Urdu - Placeholder)

```bash
npm run build -- --locale fr
```

Or build your site to include all the locales at once: (Urdu - Placeholder)

```bash
npm run build
```
