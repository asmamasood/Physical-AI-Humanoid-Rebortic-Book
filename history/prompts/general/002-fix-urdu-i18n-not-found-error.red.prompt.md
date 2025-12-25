---
phr_id: 002
phr_title: Fix Urdu I18n Not Found Error
phr_stage: red
phr_date_iso: 2025-12-09
phr_surface: agent
phr_model: gemini-1.5-pro-a
phr_feature: i18n-fix
phr_branch: main
phr_user: user
phr_command: when i click urdu toggle button in book modules chapters shows not found error
phr_labels: ["bug-fix", "i18n", "docusaurus"]
phr_links:
  spec: null
  ticket: null
  adr: null
  pr: null
phr_files_yaml:
  - physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/intro.md
  - physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/tutorial-basics/_category_.json
  - physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/tutorial-basics/congratulations.md
  - physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/tutorial-basics/create-a-blog-post.md
  - physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/tutorial-basics/create-a-document.md
  - physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/tutorial-basics/create-a-page.md
  - physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/tutorial-basics/deploy-your-site.md
  - physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/tutorial-basics/markdown-features.mdx
  - physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/tutorial-extras/_category_.json
  - physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/tutorial-extras/manage-docs-versions.md
  - physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/tutorial-extras/translate-your-site.md
  - physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/tutorial-extras/img/docsVersionDropdown.png
  - physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/tutorial-extras/img/localeDropdown.png
phr_tests_yaml: []
---
## Prompt
when i click urdu toggle button in book modules chapters shows not found error

## Response
The "not found error" when switching to Urdu was likely due to missing localized content files and directories in the `i18n/ur/docusaurus-plugin-content-docs/current` path, specifically `intro.md`, `tutorial-basics`, and `tutorial-extras`.

### Actions Taken:
1.  **Copied `intro.md`:** The English version of `intro.md` was copied to `physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/intro.md`.
2.  **Copied `tutorial-basics` content:**
    *   The directory `physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/tutorial-basics` was created.
    *   All content files (`_category_.json`, `congratulations.md`, `create-a-blog-post.md`, `create-a-document.md`, `create-a-page.md`, `deploy-your-site.md`, `markdown-features.mdx`) from `physical-ai-robotics-book/docs/tutorial-basics` were copied to their corresponding paths in the Urdu i18n directory. Placeholder text "(Urdu - Placeholder)" was appended to their content to indicate they need translation.
3.  **Copied `tutorial-extras` content:**
    *   The directory `physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/tutorial-extras` was created.
    *   All content files (`_category_.json`, `manage-docs-versions.md`, `translate-your-site.md`) from `physical-ai-robotics-book/docs/tutorial-extras` were copied to their corresponding paths in the Urdu i18n directory. Placeholder text "(Urdu - Placeholder)" was appended to their content.
    *   The `img` directory within `physical-ai-robotics-book/docs/tutorial-extras` was replicated in the Urdu i18n path, and the image files (`docsVersionDropdown.png`, `localeDropdown.png`) were copied directly.

### Outcome:
The necessary directory structure and placeholder content for `intro.md`, `tutorial-basics`, and `tutorial-extras` are now present in the Urdu i18n locale. This should resolve the "not found error" when navigating these sections after switching to Urdu.

**Next Steps for User:**
*   You will need to manually translate the content in the Urdu placeholder files (`physical-ai-robotics-book/i18n/ur/...`).
*   Consider making a commit with these changes and pushing to your repository to update the deployed GitHub Pages site.
