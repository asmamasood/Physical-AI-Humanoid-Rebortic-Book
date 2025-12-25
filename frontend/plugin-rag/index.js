/**
 * RAG Chatboard Plugin for Docusaurus
 * 
 * Injects the ChatBoard component into all pages.
 */

const path = require('path');

module.exports = function pluginRagChatboard(context, options) {
    return {
        name: 'docusaurus-plugin-rag-chatboard',

        /**
         * Return path to theme components directory.
         */
        getThemePath() {
            return path.resolve(__dirname, './src/theme');
        },

        /**
         * Return client modules to be bundled and executed in browser.
         */
        getClientModules() {
            return [path.resolve(__dirname, './src/client-module.js')];
        },

        /**
         * Inject CSS and meta tags.
         */
        injectHtmlTags() {
            return {
                headTags: [
                    {
                        tagName: 'link',
                        attributes: {
                            rel: 'stylesheet',
                            href: '/css/chatboard.css',
                        },
                    },
                ],
            };
        },

        /**
         * Configure webpack aliases.
         */
        configureWebpack(config, isServer) {
            return {
                resolve: {
                    alias: {
                        // Ensure plugin uses the same React instance as Docusaurus
                        react: path.resolve(context.siteDir, 'node_modules/react'),
                        'react-dom': path.resolve(context.siteDir, 'node_modules/react-dom'),
                    },
                },
            };
        },
    };
};
