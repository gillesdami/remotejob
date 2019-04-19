import pkgutil
import asyncio

import docker
import Pyro4

Pyro4.config.SERIALIZER = 'dill'

class RemoteJob():
    next_port = 8100
    image = 'remotejobslave'

    def __init__(self, base_url='unix://var/run/docker.sock', host_name='0.0.0.0', port=None, **clientArgs):
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
            self.pyro = Pyro4.Proxy(self._get_pyro_obj(host_name, port))
        except Exception as e:
            self.close()
            raise e
    
    async def pip_install(self, *args):
        return await self._future(self._pip_install, *args)
    
    async def send_module_recursive(self, module, prefix = None):
        return await self._future(self._send_module_recursive, module, prefix)

    async def run(self, fn, *args, **arg_dict):
        return await self._future(self._run, fn, arg_dict, *args)

    def _get_pyro_obj(self, host=None, port=None):
        pyro_obj_id = ''
        for log in self.container.logs(stream=True):
            pyro_obj_id += log.decode()

            if log.decode() == '\r':
                break

        pyro_obj_id = pyro_obj_id.strip().split('@')[0]
        
        return '{}@{}:{}'.format(pyro_obj_id, host, str(port))

    async def _future(self, fn, *args):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, fn, *args)
        
    def _pip_install(self, *args):
        return self.pyro.pip_install(*args)

    def _send_module_recursive(self, module, prefix = None):
        prefix = prefix if prefix else module.__name__ + '.'
        
        with open(module.__file__) as h:
            self.pyro.create_module(module.__name__, h.read(), True)

        for loader, module_name, is_pkg in pkgutil.walk_packages(module.__path__, prefix):
            path = loader.find_module(module_name).path
            
            with open(path) as h:
                self.pyro.create_module(module_name, h.read(), is_pkg)

    def _run(self, fn, arg_dict= {}, *args):
        return self.pyro.run(fn, *args, **arg_dict)

    def close(self):
        self.container.stop()
        self.docker.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.close()
