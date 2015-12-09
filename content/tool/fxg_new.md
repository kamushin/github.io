Title: New fxg for me 
Tags: Ag, Linux
Summary: find then grep has a insufferable performace, and I use ag to instead.

[previos article about fxg](http://kamushin.github.io/tool/fxg.html)

`fxg` means `find` and `xargs` then `grep`. It has a insufferable performace, so   
I use `ag` to instead, after forking some tools made by [lilydjwg](https://github.com/lilydjwg/search-and-view)
The tool chain is used for finding pattern in files and opening file by vim.
I rewrite a simple version of `vv`.
    
    #!/usr/bin/env python
    import sys
    from subprocess import call
    line_number = int(sys.argv[1])
    with open('/tmp/fxg.log') as f:
        for index, line in enumerate(f.readlines()):
            if index == line_number - 1:
                args = line.split(':')
                filename = args[0].strip().split("\t")[1]
                file_line = args[1]
                print filename + ":" + file_line
                call(["vim", filename,  "+" + file_line])

Insert of writing regex pattern to match the complex colored output, I call ag the second time to gen a un-colored output to log file.
And I also add a `-G` for file pattern.

    fxg () {
        ag -s -G $1 --column --nogroup --color $2 | nl && ag -s -G $1 --column --nogroup $2 | nl > /tmp/fxg.log
    }

### Update: 15-12-9

`Ag` on my MacOSX has an unstable sorting result. It makes the twice call of `Ag` return different order.  
So I add `sort` to this command. 
`-0` or `-print0` will take `space` in filename as a special character.

    fxg () {
        ag -s -G $1 --column --nogroup --color -0 $2 | sort | nl && ag -s -G $1 --column --nogroup -0 $2 | sort | nl > /tmp/fxg.log
    }



