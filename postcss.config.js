module.exports = {
    plugins: {
        'postcss-discard-comments':{
            removeAll: true
        },
        'postcss-preset-env':{
            /* use stage 3 features + css nesting rules */
            stage: 3,
            features: {
                'nesting-rules': true
            },
            browsers: 'last 4 versions',
            autoprefixer: { grid: true }
        },
        'postcss-short':{},
        'postcss-color-short':{},
        'postcss-size':{},
        'autoprefixer':{
            overrideBrowserslist:'last 4 version'
        },
        '@fullhuman/postcss-purgecss':{
            content: [
                './themes/hugo-whisper-theme/layouts/**/*.html',
                './themes/hugo-whisper-theme/assets/js/**/*.js',
                './layouts/**/*.html'
            ],
            safelist: ['blockquote', 'photos', 'table', 'th', 'tr', 'thead', 'tbody', 'td']
        },
        'cssnano':{preset:
                ['default', { discardComments: true }]
        }
    },
    sourceMap: true,

}