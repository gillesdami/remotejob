# RemoteJob

Run python3.6 functions in remote containers.

This is usefull to work locally but distribute part of the work in docker servers.

```bash
pip install remotejob
```

## Example

```python3
from remotejob import RemoteJob

import mymodule
from mymodule import myfunction

async def my_job():
    with RemoteJob() as runner:
        await runner.pip_install(['numpy', 'sklearn'])
        await runner.send_module_recursive(mymodule)

        res = await runner.run(myfunction, *args, **options)
```

RemoteJob connect itself to the local docker deamon by default but you can specify a remote cluster.

For example: remotejob.RemoteJob('user@mycluster.com', 'mycluster.com')

## API

### class RemoteJob

All methods return [futures](https://docs.python.org/3/library/asyncio-future.html).

#### \_\_init\_\_(base_url='unix://var/run/docker.sock', host_name='0.0.0.0', port=None, **clientArgs)

Create a RemoteJob instance connecting to a Docker server.

You should use it with the `with` statement or ensure RemoteJob.close is called and free the resources on the docker server.

params:

- base_url: URL to the Docker server. For example, unix:///var/run/docker.sock or tcp://127.0.0.1:1234
- host_name: Host name of the exposed ports on the machine. For example 0.0.0.0 or example.com
- port: Port to expose on the remote machine. Default 8100 and is incremented for each instance.
- **clientArgs: optional arguments of DockerClient. See [Docker API docs](https://docker-py.readthedocs.io/en/stable/client.html#client-reference)

#### pip_install(*args)

Install a pip dependency on the slave.

params:

- *args: Arguments passed to 'python -m pip install'

#### send_module_recursive(*args)

Copy a module sources on the remote container.

params:

- module: Module to copy on the slave
- prefix: Namespace of the module

example:

```python3
from m1.m2 import m3
from remotejob import RemoteJob

with RemoteJob() as job:
    job.send_module_recursive(m2, 'm1.m2')
```

#### run(fn, *args, **arg_dict)

Run a function in the remote container and return the result. The function source must be available on the remote container (native, pip installed, or in a module passed to send_module_recursive). All arguments and the returned value must be serializable by [dill](https://github.com/uqfoundation/dill) a pickle extension.

Run a function in the remote container.

params:

- fn: a reference to the function
- *args: fn parameters
- **arg_dict: fn parameters

## Build

### Docker image

```bash
docker build . -t remotejob
```
