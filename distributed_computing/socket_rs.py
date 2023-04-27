import socket
import json
import threading


def load_config():
    with open('config.json', 'r') as f:
        config = json.load(f)
    return config


def handle_worker_connection(conn, addr, config, parameters):
    print(f'Connected by {addr}')
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode()
            print(f'Received from Worker {message}')
            # check the number of the cores in the worker, and assigned the associated number of datasets
            if message == "ready":
                worker_index = int(message.split()[1])
                num_cores = get_worker_cores(worker_index)
                if num_cores is None:
                    print(f'Worker {worker_index} configuration not found in database')
                    continue
                if len(parameters) < num_cores:
                    num_cores = len(parameters)
                assigned_sets = [parameters.popleft() for _ in range(num_cores)]
                if config['mode'] == 'master_oriented':
                    if not config['specific_site']:
                        # check which site has not been calibrated yet
                        site = check_calibration_status()
                    else:
                        site = config['specific_site']
                    # generate
                    response = json.dumps({
                        "sitename": site,
                        "parameters": assigned_sets
                    })
                elif config['mode'] == 'worker_oriented':
                    response = json.dumps({
                        assigned_sets
                    })
                else:
                    print('Invalid mode in config.json')
                    continue

                conn.sendall(response.encode())


def master(config):
    if config['autocalibration'] and config['mode'] == 'master_oriented':
        parameters = generate_sobol_sequence(config['calibrating_parameter'],
                                             config['number_of_maximum_iterations'])
    elif config['autocalibration'] and config['mode'] == 'master_oriented':
        parameters = config["all_sites"]
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((config['master_ip'], config['master_port']))
        s.listen()
        while True:
            conn, addr = s.accept()

            worker_thread = threading.Thread(target=handle_worker_connection, args=(conn, addr, config, parameters))
            worker_thread.start()


def worker(config):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((config['master_ip'], config['master_port']))
        message = f'Hello from Worker {config["worker_index"]}'
        s.sendall(message.encode())
        s.sendall(b'ready')
        data = s.recv(1024)
        response = json.loads(data.decode())

        if 'sitename' in response:
            print(f'Received sitename and parameters: {response}')
        elif 'sitenames' in response:
            print(f'Received sitenames: {response}')


def generate_parameter_sets(num_sets):
    return [{"": f"value{i}_1"} for i in range(num_sets)]


if __name__ == '__main__':
    config = load_config()
    if config['role'] == 'master':
        master(config)
    elif config['role'] == 'worker':
        worker(config)
    else:
        print('Invalid role in config.json')
