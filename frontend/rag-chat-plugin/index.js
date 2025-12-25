// frontend/rag-chat-plugin/index.js
import path from 'path';

export default function(context, options) {
  return {
    name: 'docusaurus-rag-chat-plugin',

    // Add plugin-specific CSS
    injectHtmlTags() {
      return {
        headTags: [
          {
            tagName: 'link',
            attributes: {
              rel: 'stylesheet',
              href: '/css/ChatPlugin.css', // Path to the CSS within the static build directory
            },
          },
        ],
      };
    },

    getClientModules() {
      // Return a path to the client module that will be bundled by webpack
      // and run in the browser.
      return [path.resolve(__dirname, './src/client-module')];
    },

    configureWebpack(config, isServer) {
      return {
        resolve: {
          alias: {
            // This alias ensures that if your plugin also has React dependencies,
            // it uses the same React instance as Docusaurus itself, avoiding conflicts.
            react: path.resolve(__dirname, '../../node_modules/react'),
            'react-dom': path.resolve(__dirname, '../../node_modules/react-dom'),
          },
        },
      };
    },
  };
}
