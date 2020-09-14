module.exports = {
    plugins: {
        'postcss-discard-comments':{},
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
        '@fullhuman/postcss-purgecss':{
            content: [
                './themes/hugo-whisper-theme/layouts/**/*.html',
                './themes/hugo-whisper-theme/assets/js/*.js',
                './themes/hugo-whisper-theme/static/js/*.js',
                './layouts/**/*.html',
                './static/js/*.js',
                './layouts/shortcodes/*.html'
            ]
        },
        'autoprefixer':{
            browsers:'last 4 version'
        },
        'cssnano':{preset:
            ['default', { discardComments: true }]
        }
    },
    sourceMap: true
}