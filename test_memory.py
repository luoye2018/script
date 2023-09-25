import sys
import os
import xmlrpc.server
from oslo_concurrency import processutils
import psutil
import humanize
from memory_profiler import profile
import subprocess

pid = os.getpid()
print("The process ID is", pid)

process = psutil.Process(pid)

PORT = 8009

kwargs = {
	'shell': True
}

def print_memory():
	print("rss mem:", humanize.naturalsize(process.memory_info().rss))
	print("vms mem:", humanize.naturalsize(process.memory_info().vms))


class MyServer:
	@profile
	def run(self, cmd):
		print('cmd:', cmd)
		print_memory()
		result = processutils.execute(cmd, **kwargs)
		print('result:', len(result[0]))
		print_memory()
		return result

	@profile
	def run2(self, cmd):
		print('cmd:', cmd)
		print_memory()
		processutils.execute(cmd, **kwargs)
		print_memory()
		return
	
	@profile
	def run3(self):
		print_memory()
		return


def run_server():
	server = xmlrpc.server.SimpleXMLRPCServer(("localhost", PORT), allow_none=True)
	server.register_instance(MyServer())
	server.serve_forever()

def run_client():
	import xmlrpc.client
	server = xmlrpc.client.ServerProxy("http://localhost:" + str(PORT))

	if len(sys.argv) > 1 and sys.argv[1] == '2':
		server.run2('cat /root/test/testfile')
	elif len(sys.argv) > 1 and sys.argv[1] == '3':
		server.run3()
	else:
		result = server.run('cat /root/test/testfile')
		print(result[0][:100], len(result[0]))


if __name__ == '__main__':
	if len(sys.argv) > 1 and sys.argv[1] == 'server':
		print('server running')
		run_server()
	else:
		print('client running')
		run_client()
