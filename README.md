# RS-DPCF: Modularized Distributed Parallel Computing Framework

[![DOI](https://img.shields.io/badge/DOI-10.1016%2Fj.compag.2023.108057-blue)](https://doi.org/10.1016/j.compag.2023.108057)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-active-green.svg)]()

> A high-performance, modularized parallel distributed computing framework for simulating seasonal frost dynamics in cold regions, specifically designed to accelerate RZ-SHAW model calibration and multi-site simulations.

## 🌟 Overview

**RS-DPCF** is a cutting-edge Python-based framework that revolutionizes cold region hydro-agricultural modeling through advanced parallel and distributed computing techniques. Originally developed for the RZ-SHAW model, this framework enables researchers to conduct large-scale simulations across numerous Canadian croplands with unprecedented efficiency.

### 🎯 Why RS-DPCF?

The winter/spring season in cold climate regions represents a critical period for:
- 🌱 Cropland nutrient dynamics
- 🌍 Greenhouse gas emissions
- ❄️ Frost and freeze-thaw processes
- 🌡️ Climate change vulnerability assessment

RS-DPCF addresses the computational challenges of modeling these complex processes at scale, delivering **up to 47.5× faster calibration** compared to traditional serial approaches.

## ✨ Key Features

### 🚀 **High-Performance Computing**
- **Multi-threading (MT)**: Dynamic thread allocation based on CPU resources
- **Multi-processing (MP)**: Process-based parallelization for CPU-intensive tasks
- **Distributed Computing**: Master-worker architecture for scalable workloads
- **Socket-based Communication**: Efficient inter-node data exchange

### 🤖 **Intelligent Automation**
- **Auto-Calibration**: Sobol sequence-based parameter optimization
- **Data Retrieval**: Automatic integration with Canadian climate/soil databases
- **Scenario Generation**: Automated RZ-SHAW input file creation
- **Performance Metrics**: NSE, MBE, KGE, IOA statistical evaluation

### 🧩 **Modular Architecture**
```
RS-DPCF Framework
├── RZ-SHAW Parser Module
├── Scenario Generation Module
├── Data Retrieval Module
├── Distributed Computing Module
├── Database Control Module
├── Parallel Computing Module
└── Auto-Calibration Module
```

### 📊 **Comprehensive Data Integration**
- Environment and Climate Change Canada (ECCC) weather stations
- Canadian historical snow survey data
- Detailed Soil Survey (DSS) compilations
- High-resolution digital elevation models
- Annual crop inventory datasets

## 🛠️ Installation

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.6+ | Core framework |
| RZ-SHAW | Latest | RZWQM2 with SHAW option |
| MySQL | 5.7+ | Database backend |

### Quick Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/RS-DPCF.git
   cd RS-DPCF
   ```

2. **Install dependencies**:
   ```bash
   pip install mysql-connector-python numpy torch geopy statistics matplotlib
   ```

3. **Database configuration**:
   ```python
   # Edit: central_database_control_module/db_connection.py
   db = mysql.connector.connect(
       host="your_host",
       user="your_username", 
       passwd="your_password",
       database="your_database"
   )
   ```

4. **Framework configuration**:
   ```json
   {
       "role": "master",
       "mode": "worker_oriented",
       "worker_index": 1,
       "master_ip": "127.0.0.1",
       "master_port": 5000,
       "worker_ip": "127.0.0.1", 
       "worker_port": 5001,
       "autocalibration": "True",
       "calibrating_parameter": "snow_density",
       "calibrating_parameter_range": "[20, 100]",
       "number_of_maximum_iterations": "2000",
       "parallel_mode": "MT"
   }
   ```

## 🚀 Usage Guide

### Master Node Setup

**Step 1**: Configure as master node
```bash
# Update config.json
{
    "role": "master",
    "mode": "worker_oriented"  # or "master_oriented"
}
```

**Step 2**: Launch master node
```bash
python distributed_computing/socket_rs.py
```

### Worker Node Setup

**Step 1**: Configure worker parameters
```bash
# Update config.json  
{
    "role": "worker",
    "master_ip": "192.168.1.100",  # Master node IP
    "master_port": 5000,
    "worker_ip": "192.168.1.101",  # This worker's IP
    "worker_port": 5001
}
```

**Step 2**: Launch worker node
```bash
python distributed_computing/socket_rs.py
```

### Auto-Calibration Modes

#### 🎯 **Master-Oriented Calibration**
Master controls parameter generation and distribution:

```python
calibrate_for_one_station(
    station=station_id,
    project_path=project_directory, 
    table_name='calibration_results',
    parameters=['snow_ini', 'snow_max'],
    parameter_type='snow_properties',
    worker_number=4
)
```

#### 🔄 **Worker-Oriented Calibration**
Workers independently generate parameter sets:

```python
config = load_config()
config['mode'] = 'worker_oriented'
config['calibrating_parameter'] = 'snow_density'
config['calibrating_parameter_range'] = '[20, 100]'
# Launch worker with updated config
```

### Multi-Site Parallel Simulation

#### Threading Approach (Recommended)
```python
from concurrent.futures import ThreadPoolExecutor

config = load_config()
if config["parallel_mode"] == "MT":
    with ThreadPoolExecutor(max_workers=48) as pool:
        futures = []
        for site in canadian_cropland_sites:
            future = pool.submit(
                calibrate_for_one_station,
                site, project_path, table_name, 
                parameters, parameter_type, worker_number
            )
            futures.append(future)
        
        # Collect results
        results = [future.result() for future in futures]
```

#### Process-Based Approach
```python
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor(max_workers=20) as executor:
    for site in sites:
        executor.submit(
            calibrate_for_one_station,
            site, project_path, table_name,
            parameters, parameter_type, worker_number
        )
```

## 📈 Performance Benchmarks

| Configuration | Threads/Processes | Speedup | Efficiency |
|---------------|------------------|---------|------------|
| Serial | 1 | 1.0× | 100% |
| MT (Dynamic) | 48 | **47.5×** | 99% |
| MP (Static) | 20 | 19.2× | 96% |
| Distributed | 4 nodes × 12 cores | 45.8× | 95% |

> 💡 **Pro Tip**: Multi-threading (MT) with dynamic allocation delivers optimal performance for RZ-SHAW calibration tasks.

## 🗃️ Data Sources & Integration

### Climate Data
- **🌡️ ECCC Weather Stations**: Real-time and historical meteorological data
- **🌨️ Snow Survey Data**: Canadian historical snow depth and density measurements
- **🌧️ Adjusted Precipitation**: Wang et al. (2017) rainfall and snowfall dataset

### Geospatial Data
- **🏔️ Digital Elevation**: High-resolution topographic models
- **🌾 Crop Inventory**: Annual Canadian agricultural land use
- **🏞️ Soil Surveys**: Detailed soil classification and properties

### Agricultural Data
- **📋 Management Practices**: Provincial crop guides and farming protocols
- **🚜 Field Operations**: Planting, harvesting, and tillage schedules

## 🔬 Research Applications

### Supported Analysis Types
- ❄️ **Seasonal Frost Dynamics**: Freeze-thaw cycle modeling
- 💧 **Soil Water Movement**: Cold region hydrology simulation  
- 🌱 **Crop Growth Modeling**: Cold-adapted agriculture systems
- 🌍 **Climate Impact Assessment**: Future scenario analysis
- 📊 **Multi-Site Calibration**: Regional parameter optimization

### Case Studies
- Canadian Prairie cropland frost simulation
- Regional climate change impact assessment
- Multi-year calibration across agricultural sites
- Distributed computing performance evaluation

## 📚 Citation

If you use RS-DPCF in your research, please cite our paper:

```bibtex
@article{li2023modularized,
  title={A modularized parallel distributed High-Performance computing framework for simulating seasonal frost dynamics in Canadian croplands},
  author={Li, Ziwei and Qi, Zhiming and Liu, Yuchen and Zheng, Yue and Yang, Yiqing},
  journal={Computers and Electronics in Agriculture},
  volume={212},
  pages={108057},
  year={2023},
  publisher={Elsevier},
  doi={10.1016/j.compag.2023.108057}
}
```

## 🛣️ Future Roadmap

### Planned Enhancements
- [ ] **Linux Deployment**: Native Linux system support
- [ ] **Distributed Databases**: Multi-node database framework
- [ ] **Internal Parallelization**: RZ-SHAW model-level optimization
- [ ] **Global Optimization**: Advanced calibration algorithms
- [ ] **Multi-Model Ensemble**: Integrated modeling capabilities
- [ ] **Cloud Integration**: AWS/Azure deployment options

### Community Contributions
We welcome contributions! Areas where help is needed:
- 🐧 Linux compatibility testing
- 📊 Additional statistical metrics
- 🌐 Web interface development
- 📖 Documentation improvements

## 🤝 Support & Community

### Getting Help
- 📧 **Email**: [Contact information]
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/RS-DPCF/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/RS-DPCF/discussions)

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgments

This research was supported by:

- **🇨🇦 Natural Sciences and Engineering Research Council of Canada (NSERC)** - Grant 2019-05662
- **🇨🇳 Chinese Scholarship Council (CSC)** - Scholarship 202107970011  
- **🎓 Angus F. MacKenzie Graduate Fellowship**

Special thanks to the research team and collaborating institutions that made this framework possible.

## 📄 License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for complete details.

### License Summary
- ✅ **Commercial use**
- ✅ **Modification** 
- ✅ **Distribution**
- ✅ **Private use**
- ❌ **Liability**
- ❌ **Warranty**

---

<div align="center">

**RS-DPCF** - Revolutionizing cold region agricultural modeling through high-performance computing

[🌟 Star us on GitHub](https://github.com/yourusername/RS-DPCF) | [📖 Read the Paper](https://doi.org/10.1016/j.compag.2023.108057) | [🚀 Get Started](#-installation)

*Developed with ❄️ for cold region research*

</div>
