Title: 把Capslock重定向为Ctrl
Tags: Linux
Summary: 以前的脚本莫名其妙的在新系统上不能用了，换个好点的脚本

Capslock这键平时没多大用，而Ctrl则用的非常多，所以把Capslock换成Ctrl也算是个比较常见的需求。

以前我是把xmodmap里swap脚本小改一下，也算在Arch上能用。
    
    remove Lock = Caps_Lock
    remove Control = Control_L
    keysym Control_L = Control_L
    keysym Caps_Lock = Control_L
    add Lock = Caps_Lock
    add Control = Control_L

最近换了deepin后，这脚本会让Capslock啥也不做。于是找了个更加合理的脚本


    remove Lock = Caps_Lock
    remove Control = Control_L
    keysym Caps_Lock = Control_L
    add Lock = Caps_Lock
    add Control = Control_L

比较一下， 就是少了一行对Control的设置，我猜之前出错的原因是Control_L不能被绑到两个keysym上
