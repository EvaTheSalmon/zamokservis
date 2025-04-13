const postcssDiscardComments = require('postcss-discard-comments');
const postcssPresetEnv = require('postcss-preset-env');
const postcssShort = require('postcss-short');
const postcssColorShort = require('postcss-color-short');
const postcssSize = require('postcss-size');
const autoprefixer = require('autoprefixer');
const purgecss = require('@fullhuman/postcss-purgecss');
const cssnano = require('cssnano');

module.exports = {
    plugins: [
        postcssDiscardComments({
            removeAll: true
        }),
        postcssPresetEnv({
            stage: 3,
            features: {
                'nesting-rules': true
            },
            browsers: 'last 4 versions',
            autoprefixer: { grid: true }
        }),
        postcssShort,
        postcssColorShort,
        postcssSize,
        autoprefixer({
            overrideBrowserslist: 'last 4 versions'
        }),
        purgecss({
            content: [
                './themes/hugo-whisper-theme/layouts/**/*.html',
                './themes/hugo-whisper-theme/assets/js/**/*.js',
                './layouts/**/*.html'
            ],
            safelist: ['blockquote', 'photos', 'table', 'th', 'tr', 'thead', 'tbody', 'td']
        }),
        cssnano({
            preset: ['default', { discardComments: true }]
        })
    ],
    sourceMap: true
} 