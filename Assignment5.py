
import argparse
import csv
from queue import Queue


class Request:
    def __init__(self, timestamp, path, process_time):
        self.timestamp = int(timestamp)
        self.path = path
        self.process_time = int(process_time)
        self.wait_time = 0


class Server:
    def __init__(self):
        self.current_task = None
        self.time_remaining = 0

    def busy(self):
        return self.current_task is not None

    def start_next(self, request):
        self.current_task = request
        self.time_remaining = request.process_time

    def tick(self):
        if self.current_task:
            self.time_remaining -= 1
            if self.time_remaining <= 0:
                self.current_task = None


def simulateOneServer(filename):
    request_queue = Queue()
    server = Server()
    wait_times = []

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            request = Request(*row)
            request_queue.put(request)

    current_time = 0
    while not request_queue.empty() or server.busy():
        while not request_queue.empty() and request_queue.queue[0].timestamp == current_time:
            request = request_queue.get()
            request.wait_time = max(0, current_time - request.timestamp)
            wait_times.append(request.wait_time)
            if not server.busy():
                server.start_next(request)
            else:
                request_queue.put(request)  # Requeue if server is busy

        server.tick()
        current_time += 1

    return sum(wait_times) / len(wait_times) if wait_times else 0


def simulateManyServers(filename, num_servers):
    request_queues = [Queue() for _ in range(num_servers)]
    servers = [Server() for _ in range(num_servers)]
    wait_times = []

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        requests = [Request(*row) for row in reader]

    for index, request in enumerate(requests):
        request_queues[index % num_servers].put(request)

    current_time = 0
    while any(not q.empty() for q in request_queues) or any(s.busy() for s in servers):
        for i in range(num_servers):
            while not request_queues[i].empty() and request_queues[i].queue[0].timestamp == current_time:
                request = request_queues[i].get()
                request.wait_time = max(0, current_time - request.timestamp)
                wait_times.append(request.wait_time)
                if not servers[i].busy():
                    servers[i].start_next(request)
                else:
                    request_queues[i].put(request)  # Requeue if server is busy

        for server in servers:
            server.tick()
        current_time += 1

    return sum(wait_times) / len(wait_times) if wait_times else 0


def main():
    file_path = 'requests.csv'  # Corrected file path
    num_servers = 2
    avg_wait = 0
    import os
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found. Please make sure the file is in the correct directory.")
        return

    if num_servers == 1:
        avg_wait = simulateOneServer(file_path)
    else:
        avg_wait = simulateManyServers(file_path, num_servers)

    print(f'Average Wait Time: {avg_wait:.2f} seconds')


if __name__ == '__main__':
    main()
    num_servers = 1
    file_path = 'requests.csv'
    if num_servers == 1:
        avg_wait = simulateOneServer(file_path)
    else:
        avg_wait = simulateManyServers(file_path, num_servers)

    print(f'Average Wait Time: {avg_wait:.2f} seconds')

