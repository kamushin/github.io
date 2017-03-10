Title: Nodejs os.cpu return not allowed cpu
Tags: Nodejs
Summary: Nodejs process should use /proc/self/status to get allowed cpu.

The `os.cpus()` API added in Nodejs v0.3.3 shows all processors in `/proc/cpuinfo`. 
This API is often used to give a suggestion of how many worker processes created by cluster. However, in a docker/lxc environment, some  
of the cpus are not allowed to be used by a container.  
For more accurate information, we should cat `/proc/self/status`. This file will show the specific allowed cpus. Or use the command `nproc`.
