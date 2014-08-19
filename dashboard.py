import threading


class Dashboard:
    def __getMemoryInfo(self, container_id):
        dest = "/sys/fs/cgroup/memory/docker/%s/memory.stat" % container_id
        file = open(dest, 'r')
        return file.read()

    def __getCpuInfo(self, container_id):
        dest = "/sys/fs/cgroup/cpuacct/docker/%s/cpuacct.stat" % container_id
        file = open(dest, 'r')
        return file.read()


if __name__ == '__main__':
    d = Dashboard()
    d.getMemoryInfo('6d3f04bfcc2d7c86f0c688c7f67738fa41dd30cf03e332e3fdc72f5ba72b47c2')
    d.getCpuInfo('6d3f04bfcc2d7c86f0c688c7f67738fa41dd30cf03e332e3fdc72f5ba72b47c2')
