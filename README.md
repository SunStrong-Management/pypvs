# PyPVS

**PyPVS** is a Python package that provides a Python API for interacting with **SunStrong Management PVS6** and **PVS5** gateways. It enables developers to access gateway data and issue commands programmatically.  

![GitHub Release](https://img.shields.io/github/v/release/SunStrong-Management/pypvs)

---

## Firmware Requirements

Before using PyPVS, ensure your gateway is running the minimum required firmware version.  
You can verify the installed firmware version in the **SunStrong Connect** mobile app under the **Profile → System Info** section, where it appears as **“PVS Firmware Version.”**

### PVS5 Gateway  
- **Minimum version:** 2025.11, build 5412  

### PVS6 Gateway  
- **Minimum version:** 2025.06, build 61839  

---

## Installation

Install **PyPVS** directly from PyPI:

![PyPI - Version](https://img.shields.io/pypi/v/pypvs)  
**PyPI:** [pypvs](https://pypi.org/project/pypvs/)

```bash
pip install pypvs
```
    
## Documentation

- [Description of API Gateway](https://github.com/SunStrong-Management/pypvs/blob/main/doc/LocalAPI.md)

Reference of PVS Gateway public variables

- [PVS5 variables](https://github.com/SunStrong-Management/pypvs/blob/main/doc/varserver-variables-public-pvs5.csv)
- [PVS6 variables](https://github.com/SunStrong-Management/pypvs/blob/main/doc/varserver-variables-public-pvs6.csv)

Documentation of Legacy API
- [Legacy API](https://github.com/SunStrong-Management/pypvs/blob/main/doc/dl_cgi.md)


## Run Locally

Clone the project

```bash
  git clone https://github.com/SunStrong-Management/pypvs.git
```

Go to the project directory

```bash
  cd pypvs
```

Prepare virtual environment
```bash
  python3 -m venv venv
```

Install dependencies

```bash
  source venv/activate
  pip install -r requirements.txt
```

Install in development mode (optional)

```bash
  pip install -e .
```

Set the environment variables

```bash
  export PVS_HOST=192.168.1.100
  export PVS_SN=ZT240685000549F0020
```

Start one of the examples

```bash
  python3 examples/simple_fcgi_async.py
```


## Disclaimer

Use of this interface is at your own risk. 
SunStrong Management is releasing these components **as-is**, and assume **no liability** for use/mis-use of these components. 
## License

[MIT](https://choosealicense.com/licenses/mit/)


## Related

Here are some related projects

- **Home Assistant plugin using PyPVS**: [pvs-hass](https://github.com/SunStrong-Management/pvs-hass)
