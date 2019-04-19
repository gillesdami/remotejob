# RemoteJob

Run python3 functions in remote containers.

This is usefull to work locally but distribute part of the work in docker clusters.

```bash
pip install remotejob
```

## Example

```python3
import remotejob

import mymodule
from mymodule import myfunction

async def myfunction_in_docker():
    with remotejob.RemoteJob() as runner:
        try:
            await runner.pip_install(['numpy', 'sklearn'])
            await runner.send_module_recursive([mymodule])

            res = await runner.run(myfunction, *args, **options)
```

remotejob.RemoteJob connect itself to the local docker deamon by default but you can specify a remote cluster. 

For example: remotejob.RemoteJob('user@mycluster.com', 'mycluster.com')

##  API

### class RemoteJob

#### \_\_init\_\_(base_url='unix://var/run/docker.sock', host_name='0.0.0.0', port=None, **clientArgs)

Connect to a remote docker server and create a slave container. You should use it with the `with` statement or ensure RemoteJob.close is called to free the resources on the docker server.

Args:

- base_url: `str` URL to the Docker server. see docker.DockerClient.
- host_name: `str` Adress from which the container will be accessible.
- port: `str` An unused and accessible port of the host. By default affect a port by RemoteJob instance from 8100.
- **clientArgs: Options passed to docker.DockerClient.

#### async RemoteJob.pip_install(*args)

Util which run `python -m pip install` on the remote container

Args:

- *args: Arguments passed to 'python -m pip install'

#### async RemoteJob.send_module_recursive(*args)

Util which copy a module sources on the remote container.

Args:

- *args: List of python module to copy in the runner

#### async RemoteJob.run(fn, *args, **arg_dict)

Run a function in the remote container and return the result. The function source must be available on the remote container (native, pip installed, or in a module passed to send_module_recursive). All arguments and the returned value must be serializable by [dill](https://github.com/uqfoundation/dill) a pickle extension.

Args:

- fn: `callable` Function to be executed remotely
- *args: Passed to fn
- **arg_dict: Passed fo fn

## Build

### Docker image

```bash
docker build . -t remotejob
```