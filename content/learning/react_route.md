Title: hashHistory and browserHistory in React-Router
Tags: react
Summary: something I met about hashHistory and browserHistory

`hashHistory` and `browserHistory` are two kinds of common React-Router `Histories` implementations.  
When I was using React-Router v1.0, I read the doc in github and wrote the code like this  

```javascript
import { Router} from 'react-router'
ReactDOM.render (( 
 <Router>
   ...
), document.body);
```
I found something in url like `#/home/k=ckuvupr`. What the hell is this?  
I went back to the doc and changed the code with `browserHistory`. With the doc, I knew the default implementation is `hashHistory`, 
which will make a `#` -- hash in url.

```javascript
import { browserHistory } from 'react-router'
ReactDOM.render (( 
 <Router history={browserHistory} >
   ...
), document.body);
```

However, it would not effect in v1.0, it's the way in v2.0. So I didn't see anything changed. And just for a while, 
I forgot to deal with this, and went to write other codes.  

Today when I c&p this chunk of code to my new project, using some new tools. The build tool automatically install
react-router v2.0 for me. While the hash tag is gone, and url looks like the **real** url.
But it cause another problem, that is when the url is like the **real** url, it means that I should set the server side route to `/* -> index.html` rather than `/ -> index.html`.  
Otherwise, it will get a 404 error when the url `/home` is re-flushed. And the problem will not raise while using `hashHistory`, because the url is like `/#/home` and it is still `/`, the string after hash tag is not in the route rule.
[Docs about them.](https://github.com/reactjs/react-router/blob/master/docs/guides/Histories.md)  

I havn't find the correct way to set the server side route, because I am using a `webpack-dev-server`-like tool, I don't know how to change the route.  
So I go back to use the ugly `hashHistory`.

It seems a waste of time, my fault is reading doc but not paid attention to version, but I still hate the doc because the difference between v1.0 and v2.0 is not heightlighted.



