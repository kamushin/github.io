Title: Why shouldn't use component wrap a Route
Tags: react-route
Summary: 研究下react-route的源码找到如何正确分离route配置的方法

### 背景

由于我希望每个子项目管理自己的route，于是想维护一个`route`的component在各个子目录中，在index.js中import各个子项目的`route`.  
以此简化index.js中的需要import的依赖数量。


### react-route是如何配置规则的

举个例子：

``` jsx

  <Router history={browserHistory}>
    <Route path='/' component={Layout}>
      <Route path='signup' component={SignupPage} />
    </Route>
  </Router>

```

`Router`组件在`componentWillMount`时会尝试加载children中的`Route`配置, 通过遍历children，找到他们的props, 然后把props加入`route`数组中。
也就是说`Route`组件实际上作为一个配置用的组件，会直接被`Router`读取，所以`Route`也没有实际意义上的render方法。

ps.这提供给我一个思路，如何一个组件的配置太过于多和复杂，那么可以搞出个专门用来做配置用的子组件，在渲染前读取子组件的配置，加载成自己的配置。这样的好处是大大提高了可读性。让配置成为声明而不是运算。



``` javascript
/**
 * Creates and returns a routes object from the given ReactChildren. JSX
 * provides a convenient way to visualize how routes in the hierarchy are
 * nested.
 *
 *   import { Route, createRoutesFromReactChildren } from 'react-router'
 *   
 *   const routes = createRoutesFromReactChildren(
 *     <Route component={App}>
 *       <Route path="home" component={Dashboard}/>
 *       <Route path="news" component={NewsFeed}/>
 *     </Route>
 *   )
 *
 * Note: This method is automatically used when you provide <Route> children
 * to a <Router> component.
 */

function createRoutesFromReactChildren(children, parentRoute){...}
```

### 为什么不能用一个wrapper组件来隐藏子route的细节

有了上面的知识后，这个问题就显而易见了，因为配置是通过读取children的`props`来加载的。在children外包裹一层wrapper会导致读到wrapper的`props`。

### 怎么实现我想要的功能

最简单的方法就是写个函数来直接return route。这样既达到了分割的目的，也不会加入中间层。

### 为什么一开始会想用wrapper呢

一开始不够了解react-route的原理，以为只要能渲染出来，效果是一样的。

### SO 相关问题链接

[点我](http://stackoverflow.com/questions/35048738/react-router-import-routes)
