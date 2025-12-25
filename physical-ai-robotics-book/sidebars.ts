import type { SidebarsConfig } from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    {
      type: 'doc',
      id: 'intro',
      label: 'Introduction',
    },
    {
      type: 'category',
      label: 'Module 1: AI Basics',
      items: ['module-1/chapter-1', 'module-1/chapter-2'],
    },
    {
      type: 'category',
      label: 'Module 2: Robotic Systems',
      items: ['module-2/chapter-1', 'module-2/chapter-2'],
    },
    {
      type: 'category',
      label: 'Module 3: Humanoid Robotics',
      items: ['module-3/chapter-1', 'module-3/chapter-2'],
    },
    {
      type: 'category',
      label: 'Module 4: Future Trends',
      items: ['module-4/chapter-1', 'module-4/chapter-2'],
    },
  ],
};

export default sidebars;
