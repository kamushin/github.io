Title: Use webpack together with browser-sync
Tags: front-end
Summary: Webpack is a module bundler. Browsersync makes your browser testing workflow faster by synchronising URLs, interactions and code changes across multiple devices.

Here are some tips about using `webpack` and `Browsersync` to improve working speed.

### Browsersync 
Browsersync makes your browser testing workflow faster by synchronising URLs, interactions and code changes across multiple devices.   
`npm install browser-sync@2.7.1 -g`

#### Proxy
    
    browser-sync start --proxy localhost:8888 --port 4000 --files index.html --files src/*

Used to proxy ajax request to back-end server.

### Webpack
With webpack, don't need `require.js` and `require-react-plugin` loading in `index.html`. Very useful to me.   
`npm install webpack -g`

#### Work together 
`npm install -g browser-sync-webpack-plugin`
And config `webpack.config.js`:

    var BrowserSyncPlugin = require('browser-sync-webpack-plugin');
    module.exports = {
    entry: './src/js/index.js',
    output: {
        publicPath: './dist/',
        path: './dist/',
        filename: 'bundle.js',
        pathinfo: true
    },
    resolve: {
        root: '.'
    },
    module: {
        loaders: [
        {test: /\.js/, loader: 'jsx-loader?harmony'}
        ]
    },
    plugins: [
        new BrowserSyncPlugin({
        host: 'localhost',
        port: 4000,
        proxy: 'localhost:8888',
        files: 'src/*',
        files: 'index.html'
    })  
    ]
    };
