import asyncio
from functools import wraps
import pkgutil

import docker
import Pyro4

Pyro4.config.SERIALIZER = 'dill'

def future(f):
    '''
    Decorator which run a function asynchronously in the default event loop.
    '''
    def wrapper(*args, **kw):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, **kw)
    
    return wrapper

class RemoteJob():
    next_port = 8100
    image = 'gillesdami/remotejob'

    def __init__(self,
        base_url='unix://var/run/docker.sock',
        host_name='0.0.0.0',
        port=None,
        **clientArgs):
        '''
        Create a RemoteJob instance connecting to a Docker server.
        You should use it with the `with` statement or ensure RemoteJob.close 
        is called and free the resources on the docker server.

        params:
          base_url: URL to the Docker server. For example, 
            unix:///var/run/docker.sock or tcp://127.0.0.1:1234
          host_name: Host name of the exposed ports on the machine. 
            For example 0.0.0.0 or example.com
          port: Port to expose on the remote machine. Default 8100 
            and is incremented for each instance.
          **clientArgs: optional arguments of DockerClient. 
            See https://docker-py.readthedocs.io/en/stable/client.html#client-reference
        '''

        port = port if port else RemoteJob.next_port
        RemoteJob.next_port += 1

        self.docker = docker.DockerClient(base_url=base_url, **clientArgs)
        self.container = self.docker.containers.run(
            RemoteJob.image,
            detach=True,
            auto_remove=True,
            tty=True,
            ports={'8000/tcp': port})

        try:
            # retrieve the pyro object id in the container's logs
            pyro_obj_id = ''
            for log in self.container.logs(stream=True):
                pyro_obj_id += log.decode()

                if log.decode() == '\r':
                    break

            pyro_obj_id = pyro_obj_id.strip().split('@')[0]
            
            self.pyro = Pyro4.Proxy('{}@{}:{}'.format(pyro_obj_id, host_name, str(port)))
        except Exception as e:
            self.close()
            raise e
    
    @future
    def pip_install(self, *args):
        '''
        Install a pip dependency on the slave.

        params:
          *args: Arguments passed to 'python -m pip install'
        '''
        return self.pyro.pip_install(*args)
    
    @future
    def send_module_recursive(self, module, prefix = None):
        '''
        Copy a module sources on the remote container.

        params:
          module: Module to copy on the slave
          prefix: Namespace of the module
        
        example:
        from m1.m2 import m3
        from remotejob import RemoteJob

        with RemoteJob() as job:
            job.send_module_recursive(m2, 'm1.m2')
        '''
        prefix = prefix if prefix else module.__name__ + '.'
        
        with open(module.__file__) as h:
            self.pyro.create_module(module.__name__, h.read(), True)

        for loader, module_name, is_pkg in pkgutil.walk_packages(module.__path__, prefix):
            path = loader.find_module(module_name).path
            
            with open(path) as h:
                self.pyro.create_module(module_name, h.read(), is_pkg)

    @future
    def run(self, fn, *args, **arg_dict):
        '''
        Run a function in the remote container and return the result.
        The function source must be available on the remote container
        (native, pip installed, or in a module passed to send_module_recursive).
        All arguments and the returned value must be serializable by 
        [dill](https://github.com/uqfoundation/dill) a pickle extension.

        params:
          fn: a reference to the function
          *args: fn parameters
          **arg_dict: fn parameters
        '''
        return self.pyro.run(fn, *args, **arg_dict)

    def close(self):
        '''
        Remove the container.
        '''
        self.container.stop()
        self.docker.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.close()
