Title: KernelRestarter: restart failed in Jupyter
Tags: Jupyter Docker
Summary: Kernel start failed in case of running Jupyter as pid 1.

If run `jupyter notebook` as Docker entrypoint, then `jupyter` will be the root process with pid 1.  
For some reason, this doesn't play well with IPython, and the Kernel won't be started successfully.  
Errors may occur like below:

```
[I 08:49:49.637 NotebookApp] KernelRestarter: restarting kernel (1/5)
[D 08:49:49.638 NotebookApp] Starting kernel: ['/usr/bin/python', '-m', 'ipykernel', '-f', u'/root/.local/share/jupyter/runtime/kernel-5a23f4ca-734b-422f-9c1c-e0ad126f6552.json']
[D 08:49:49.643 NotebookApp] Connecting to: tcp://127.0.0.1:54341
[I 08:49:52.646 NotebookApp] KernelRestarter: restarting kernel (2/5)
[D 08:49:52.647 NotebookApp] Starting kernel: ['/usr/bin/python', '-m', 'ipykernel', '-f', u'/root/.local/share/jupyter/runtime/kernel-5a23f4ca-734b-422f-9c1c-e0ad126f6552.json']
[D 08:49:52.652 NotebookApp] Connecting to: tcp://127.0.0.1:54341
[I 08:49:55.655 NotebookApp] KernelRestarter: restarting kernel (3/5)
[D 08:49:55.656 NotebookApp] Starting kernel: ['/usr/bin/python', '-m', 'ipykernel', '-f', u'/root/.local/share/jupyter/runtime/kernel-5a23f4ca-734b-422f-9c1c-e0ad126f6552.json']
[D 08:49:55.662 NotebookApp] Connecting to: tcp://127.0.0.1:54341
[W 08:49:56.713 NotebookApp] Timeout waiting for kernel_info reply from 5a23f4ca-734b-422f-9c1c-e0ad126f6552
[D 08:49:56.715 NotebookApp] Opening websocket /api/kernels/5a23f4ca-734b-422f-9c1c-e0ad126f6552/channels
[D 08:49:56.715 NotebookApp] Connecting to: tcp://127.0.0.1:42528
[D 08:49:56.715 NotebookApp] Connecting to: tcp://127.0.0.1:58272
[D 08:49:56.716 NotebookApp] Connecting to: tcp://127.0.0.1:52503
[I 08:49:58.664 NotebookApp] KernelRestarter: restarting kernel (4/5)
WARNING:root:kernel 5a23f4ca-734b-422f-9c1c-e0ad126f6552 restarted
[D 08:49:58.665 NotebookApp] Starting kernel: ['/usr/bin/python', '-m', 'ipykernel', '-f', u'/root/.local/share/jupyter/runtime/kernel-5a23f4ca-734b-422f-9c1c-e0ad126f6552.json']
[D 08:49:58.670 NotebookApp] Connecting to: tcp://127.0.0.1:54341
[W 08:50:01.672 NotebookApp] KernelRestarter: restart failed
```

Then I try to use `sh -c 'jupyter notebook'` as the entrypoint, it maybe works for someone else, but for my specfic docker version, `jupyter` still run as root process.   
The final solution is using a `start.sh` to wrapp `sh -c 'jupyter notebook'`. That works for me.
