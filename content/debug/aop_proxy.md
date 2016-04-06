Title: Alter dataSource in Spring By AOP And Annotation
Tags: aop java
Summary: About how to use AOP to alter dataSource. And something interesting about proxy in Spring framework.

Here is an article of how to use AOP and Annotation mechanism to alter dataSource elegantly.  
First, I want make sure that everyone knows how to build multiple dataSource. Please check this article [Dynamic-DataSource-Routing](https://spring.io/blog/2007/01/23/dynamic-datasource-routing/)  
After this, we will have a `DataSourceHolder` class, in the case above, it is called `CustomerContextHolder`.  
Let's remove the customer logic and make `Holder` purer.  
```Java

public class DataSourceHolder {
	
	private static final ThreadLocal<String> contextHolder = new ThreadLocal<String>();

	public static String getCurrentDataSource() {
		return (String) contextHolder.get();
	}   
	
	public static void setDataSource(String dataSource){
		contextHolder.set(dataSource);
	}
	
	public static void setDefaultDataSource(){
		contextHolder.set(null);
	}
	
	public static void clearCustomerType() {
		contextHolder.remove();   
	}  

}

```

### When should we call `setDataSource`

In the project I take charge of, they invoke `setDataSource` in each `controller`. IMHO, I don't think it's an 
elegant way. I think `dataSource` should be an attribute of a `DAO` method or a `Service` method. And since
`transactionManager` is a `advice` to `Service` method in this project, `dataSource` must be an attribute of a `Service` method.


### Use Annotation to describe a Service method
First, we should define a runtime annotation.
```
@Target({ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
public @interface DataSource {
    String name() default DataSource.DEFAULT;

    public final static String DEFAULT     = "foo";

    public final static String BAR  	     = "bar";

    public final static String BAZ   	     = "baz";

}
```
Then, we use the annotation to describe a `Service` method.

```
	@Override
	@DataSource(name=DataSource.BAR)
	public Object getSomething() {
		return dao.getSomething();
	}

```


### Use AOP to invoke setDataSource
First, define a `pointcut`.

```
		<aop:pointcut id="serviceWithAnnotation"
	expression="@annotation(com.yourpackageName.DataSource)" />

```
Second, define a `advisor`.
```
    <aop:advisor advice-ref="dataSourceExchange" pointcut-ref="serviceWithAnnotation" order="1"/>
    <bean id="dataSourceExchange" class="com.yourpackageName.DataSourceExchange"/>
```
Now, the AOP mechanism will make sure that some methods of `DataSourceExchange` will run if Service method which `DataSource` annotation decorated is invoked.

Last, define `DataSourceExchange`.

```JAVA
class DataSourceExchange implements MethodInterceptor {

    private Logger             logger = LoggerFactory.getLogger(DataSourceExchange.class);

	@Override
	public Object invoke(MethodInvocation invocation) throws Throwable {
		System.out.println("Method name : "
				+ invocation.getMethod().getName());
		System.out.println("Method arguments : "
				+ Arrays.toString(invocation.getArguments()));
		DataSource dataSource = this.getDataSource(invocation);
		if(dataSource == null) {
			logger.error("dataSource in invocation is null");
		}
		String dbnameString = dataSource.name();
		Object result;
		try {
			DataSourceHolder.setDataSource(dbnameString);
			result = invocation.proceed();
		} finally {
			DataSourceHolder.setDefaultDataSource();
		}
		return result;
	}

	private DataSource getDataSource(MethodInvocation invocation) throws Throwable {
  //TODO
  }

```	
The hardest part in this bunch of code is how should us impl the `getDataSource` method.
I spent several hours of this method.
First, I've seen some code online, which tell me it's quite simple to do this. Just like the code below
```JAVA

	private DataSource getDataSource(MethodInvocation invocation) throws Throwable {
		return invocation.getMethod().getAnnotation(DataSource.class);
  }

```
But it won't work, because `invocation.getMethod()` will not return the method you defined above, it will
return a `proxy` method. It's a mechanism called `Proxy` in Spring framework.  
So we should find out the real method.  
Again I searched stackoverflow.com, some answers tell me `AnnotationUtils.findAnnotation` will be useful to me.
```JAVA

	private DataSource getDataSource(MethodInvocation invocation) throws Throwable {
		return AnnotationUtils.findAnnotation(invocation.getMethod(), DataSource.class);
  }

```
`AnnotationUtils.findAnnotation` will recursively find the super class of the proxy method, to find the annotation decorated on the real method you defined above.  
But it's **not** the complete answer.   
Let's see the source code of `AnnotationUtils.findAnnotation`  
```

	/**
	 * Get a single {@link Annotation} of <code>annotationType</code> from the supplied {@link Method},
	 * traversing its super methods if no annotation can be found on the given method itself.
	 * <p>Annotations on methods are not inherited by default, so we need to handle this explicitly.
	 * @param method the method to look for annotations on
	 * @param annotationType the annotation class to look for
	 * @return the annotation found, or <code>null</code> if none found
	 */
	public static <A extends Annotation> A findAnnotation(Method method, Class<A> annotationType) {
		A annotation = getAnnotation(method, annotationType);
		Class<?> cl = method.getDeclaringClass();
		if (annotation == null) {
			annotation = searchOnInterfaces(method, annotationType, cl.getInterfaces());
		}
		while (annotation == null) {
			cl = cl.getSuperclass();
			if (cl == null || cl == Object.class) {
				break;
			}
			try {
				Method equivalentMethod = cl.getDeclaredMethod(method.getName(), method.getParameterTypes());
				annotation = getAnnotation(equivalentMethod, annotationType);
				if (annotation == null) {
					annotation = searchOnInterfaces(method, annotationType, cl.getInterfaces());
				}
			}
			catch (NoSuchMethodException ex) {
				// We're done...
			}
		}
		return annotation;
	}

```
Here we have a precondition to let `AnnotationUtils.findAnnotation` works, that is the `Proxy` mechanism is implemented by `inherit`.
There are two ways of `proxy` in Spring. [What is the difference between JDK dynamic proxy and CGLib](http://stackoverflow.com/questions/10664182/what-is-the-difference-between-jdk-dynamic-proxy-and-cglib). `CGLib` is implemented by `inherit` but `JDK dynamic proxy` is not.  
So `AnnotationUtils.findAnnotation` won't work for `JDK dynamic proxy`. We should write some more code to deal with this situation.
Here is my final solution.

```
	private DataSource getDataSource(MethodInvocation invocation) throws Throwable {
		DataSource dataSource = AnnotationUtils.findAnnotation(invocation.getMethod(), DataSource.class);
		if(dataSource != null) {
			return dataSource; // if use CGlib proxy
		}

		Method proxyedMethod = invocation.getMethod(); // or use jdk proxy
		Method realMethod = invocation.getThis().getClass().getDeclaredMethod(proxyedMethod.getName(), proxyedMethod.getParameterTypes());
		dataSource =  AnnotationUtils.findAnnotation(realMethod, DataSource.class);
		return dataSource;
	}


```

### Summary

In this case, I learnt

- how to use AOP and annotation
- there is a mechanism called proxy used by Spring
- there are two implements of proxy mechanism, they are different
- how to use reflection in Java

I hope it would help u.








