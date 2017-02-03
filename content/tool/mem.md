Title:
Tags:
Summary:


```
#!/bin/bash
mem (){
echo "********************"
    date
    COLUMNS=9999 top -n1 -c -b | head -n7 | sed '1,6d' && COLUMNS=9999 top -n1 -c -b | sed '1,6d' | grep $1;
    ps aux | grep $1 | grep -v grep | awk -F " " '{ sum += $6 } END { printf "Total Memory Usage: %.1f MB\n", sum/1024 }'
}
```
