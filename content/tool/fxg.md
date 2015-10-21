Title: 用正则来解决grep时行过长的问题
Tags: Linux
Summary: grep输出内容过长，行过长 


之前自己写了个函数用来查找文件中匹配关键字的
    
    fxg_old(){
        find . -type f -name $1 | xargs grep $2 
    }

但是今天在用的时候，发现如果匹配到的行过长的话，输出很难看，而且也不知道哪里匹配到了。

所以就想能不能对行的长度做限制，但是grep里并没有这个参数选项。于是想到了用正则去控制匹配串。在so上找到了这样的代码

     fxg(){
        find . -type f -name $1 | xargs grep -oE ".{0,20}$2.{0,20}"
     }

-o 只输出匹配的部分。 如果只加这个选项，那么就输出N行的$2。

-E 使用扩展的正则(有人提到用-P，Perl正则，但是在我这里出现错误)

后面的正则表达式用来匹配前后20个字符。

这样就满足了我的需求