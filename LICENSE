#### *ProcessC* <img src="https://github.com/lzwei196/ProcessC/blob/main/logo/logo_processc.jpg" width="100" />


**_ProcessC_ is a program designed to monitor energy usage and carbon emissions for running process-based modelling simulations.
It provides detailed tracking and analysis of CPU, GPU, and RAM power consumption and calculates the total carbon emissions based on
country or regional grid carbon intensity.**

Update
**ProcessC now offers the ability to provide the smart computation grid algorithm based on the computation power of the desginated CPU/GPU requirement.

## Features
Monitors CPU, GPU, and RAM energy usage.\
Calculates total carbon emissions for running simulations.\
Supports both Intel and AMD CPUs.\
Provides options for using existing projects or creating new ones.\
Fetches carbon intensity data from various sources.\
Requirements
Python 3.x
Required Python libraries: os, json, datetime, pprint, tabulate, requests, pandas, psutil, cpuinfo, GPUtil, logging, csv, art
Installation
Clone the repository.

Install the required Python libraries using pip:

pip install -r requirements.txt\
Ensure that the configuration file conf.json is available in the working directory.

# Usage
## Running _ProcessC_
**Before running the _ProcessC_, Several pieces of information need to be available**
1. The CMD your process-based model could be running from CLI\ (Your model has to be able to run from CLI if you want to use bash mode otherwise direct mode only)
2. The name of your program showing in the subprocess when running
3. The directory of your model
   
To start monitoring, run the main script:
python main.py
Configuration

The program checks for a configuration file (conf.json) to load existing projects. 
You will be prompted to create a new project if no projects are found.

## Creating a New Project
Enter the name of the new project.
Choose the monitoring mode: Bash mode or Direct mode.
Provide the necessary details for the chosen mode.
Input system specifications, such as CPU and GPU info, manually if not auto-detected.
Select the source for grid carbon intensity data.
Save the new project configuration.
Monitoring Process
After selecting or creating a project, _ProcessC_ will:

### Start monitoring energy usage and emissions.
Log the CPU, GPU, and RAM power consumption.
Calculate the total energy usage and carbon emissions.
Output the results in a tabular format and save them to a CSV file.
Example Output

| Metric                          | Value     |
|---------------------------------|-----------|
| Project_name                    | MyProject |
| Elapsed Time (seconds)          | 3600      |
| CPU Energy (kWh)                | 0.05      |
| GPU Energy (kWh)                | 0.03      |
| RAM Power Usage (kWh)           | 0.02      |
| Total Energy Usage (kWh)        | 0.10      |
| Grid Carbon Intensity (g/CO2 Eq)| 500.0     |
| Total Carbon Emission (g/CO2 Eq)| 50.0      |

## For monitoring the entire auto-calibration process
The main function could be edited as a wrapper to execute the auto-calibration program
Currently, _ProcessC_ supports auto-calibration of RS-DPCF
Contact us if you need support with other auto-calibration software.

## Logging
After each monitoring project is finished, a CSV file containing all the output with the project name as the file name would be stored in the output folder.

## Additional Functions
System Specifications: Automatically retrieves and displays CPU, GPU, and RAM information.

Internet Connection Check: Verifies if an internet connection is available.

Location Detection: Automatically detects the user's region and country.

## THINGS TO LOOKOUT FOR WHEN MONITORING WITH _ProcessC_

**AMD CPUs can not use the Intel power gadget under Win, so the default TDP for each type of CPU provided by AMD is used**

**When running direct mode, _ProcessC_ checks if the desired program is running.**

**However, for cmd-based executables, all names may be "OpenConsole.log",**

**So make sure other programs that are also named "OpenConsole.log" are closed**

**OurWorldInData is a local database.\ Electricitymap requires paid subscriptions, or you can manually check the grid carbon intensity in the given location during a specific year.**

***Developer: Ziwei Li Zhiming Qi Birk Li Junzeng Xu Ruiqi Wu Yuchen Liu***

***Developed @ Qi lab McGill University Bioresource Engineering and Hohai University***

## Any questions Please email leo.li@mail.mcgill.ca

**Please let us know if any additional support is needed for other process-based models**


License
This project is licensed under the MIT License.
