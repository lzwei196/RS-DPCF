# RS-DPCF: RZ-SHAW Distributed Parallel Computing Framework

A modularized parallel distributed high-performance computing framework for simulating seasonal frost dynamics in cold regions.

[![DOI](https://img.shields.io/badge/DOI-10.1016/j.compag.2023.108057-blue)](https://doi.org/10.1016/j.compag.2023.108057)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Description

RS-DPCF is a Python-based modularized parallel distributed computing framework developed explicitly for the RZ-SHAW model to facilitate multi-site simulation and faster calibration. This framework integrates parallel computing techniques with distributed computing capabilities, allowing for significant reduction in simulation runtimes and improved scalability of computational resources.

The winter/spring season in cold climate regions has been recognized as a critical period for cropland nutrient loss and greenhouse gas emissions, and is predicted to be vulnerable to climate change. RS-DPCF enables researchers to optimize the use of available computing resources for large-scale simulations of overwintering conditions across numerous croplands in Canada.

## Features

- **Parallel Computing Options**:
  - Multi-threading (MT) capability
  - Multi-processing (MP) capability
  - Dynamic thread/process allocation based on CPU resources

- **Distributed Computing**:
  - Master-worker architecture for distributed workloads
  - Worker-oriented and master-oriented calibration modes
  - Socket-based communication between nodes

- **Automatic Data Retrieval**:
  - Automatic retrieval of RZ-SHAW-related input data
  - Automatic generation of RZ-SHAW scenarios for each site
  - Integration with various Canadian climate and soil databases

- **Auto-Calibration**:
  - Random-sampling-based parameter generation (Sobol sequence)
  - Automatic statistical evaluation of simulations
  - Support for various performance metrics (NSE, MBE, KGE, IOA)

- **Modular Design**:
  - RZ-SHAW parser module
  - Scenario generation module 
  - Data retrieval module
  - Distributed computing module
  - Database control module
  - Parallel computing module
  - Auto-calibration module

## Installation

### Prerequisites

- Python 3.6 or higher
- RZ-SHAW model (RZWQM2 with SHAW option enabled)
- MySQL database

### Dependencies

```bash
pip install mysql-connector-python numpy torch geopy statistics matplotlib
```

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/RS-DPCF.git
   cd RS-DPCF
   ```

2. Configure database connection in `central_database_control_module/db_connection.py`:
   ```python
   db = mysql.connector.connect(
       host="your_host",
       user="your_username",
       passwd="your_password",
       database="your_database"
   )
   ```

3. Set up your configuration in `config.json`:
   ```json
   {
       "role": "master",  # or "worker"
       "mode": "worker_oriented",  # or "master_oriented"
       "worker_index": 1,
       "master_ip": "127.0.0.1",
       "master_port": 5000,
       "worker_ip": "127.0.0.1",
       "worker_port": 5001,
       "autocalibration": "True",
       "calibrating_parameter": "snow_density",
       "calibrating_parameter_range": "[20, 100]",
       "specific_site": "",
       "all_sites": {},
       "number_of_maximum_iterations": "2000",
       "running_mode": "",
       "parallel_mode": "MT"  # or "MP"
   }
   ```

## Usage

### Running as Master

```bash
python distributed_computing/socket_rs.py
```

### Running as Worker

1. Update `config.json` to set role as "worker"
2. Set the master IP and port
3. Run:
   ```bash
   python distributed_computing/socket_rs.py
   ```

### Running Auto-Calibration

The framework provides two calibration modes:

1. **Master-Oriented Mode**: The master node controls parameter generation and distribution.
   ```python
   # Example
   calibrate_for_one_station(station, project_path, 'table_name', ['snow_ini', 'snow_max'], 'snow_properties', worker_number)
   ```

2. **Worker-Oriented Mode**: Workers generate parameter sets independently.
   ```python
   # Example
   config = load_config()
   config['mode'] = 'worker_oriented'
   # Run as worker
   ```

### Multi-Site Simulation

For a comprehensive multi-site simulation across Canadian croplands:

```python
# Run from parallel_computing module
config = load_config()
if config["parallel_mode"] == "MT":
    # Thread-based parallelization
    pool = ThreadPoolExecutor(number_of_threads)
    for site in sites:
        pool.submit(calibrate_for_one_station, site, project_path, table_name, parameters, parameter_type, worker_number)
else:
    # Process-based parallelization
    executor = ProcessPoolExecutor(max_workers=20)
    for site in sites:
        executor.submit(calibrate_for_one_station, site, project_path, table_name, parameters, parameter_type, worker_number)
```

## Data Sources

The framework integrates with various Canadian data sources:

- **Weather Data**:
  - Environment and Climate Change Canada (ECCC) weather stations
  - Adjusted Daily Rainfall and Snowfall Dataset (Wang et al., 2017)
  - Canadian historical snow survey data

- **Soil Data**:
  - Detailed Soil Survey (DSS) compilations dataset

- **Topographic Data**:
  - High-Resolution Digital Elevation Model dataset

- **Agricultural Data**:
  - Canada annual crop inventory dataset
  - Provincial crop guides and management practices

## Performance

The MT approach with dynamic threading mode delivered the best parallelization performance during testing, with up to 48 Python threads running RZ-SHAW models concurrently, achieving a 47.5-fold reduction in calibration time compared to serialized computation.

## Publication

This software was developed as part of the following research:

Li, Z., Qi, Z., Liu, Y., Zheng, Y., & Yang, Y. (2023). A modularized parallel distributed High-Performance computing framework for simulating seasonal frost dynamics in Canadian croplands. Computers and Electronics in Agriculture, 212, 108057. https://doi.org/10.1016/j.compag.2023.108057

## Future Improvements

Potential future improvements include:

1. Enabling deployment on Linux systems
2. Integration of a distributed database framework
3. Parallelization inside the RZ-SHAW simulation
4. Integration of global optimization algorithms
5. Multi-model ensemble simulation capability

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Natural Sciences and Engineering Research Council of Canada (NSERC) 2019-05662
- Chinese Scholarship Council (CSC) scholarship 202107970011
- Angus F. MacKenzie Graduate Fellowship
