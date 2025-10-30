# pypvs

`pypvs` is a Python package that exposes data and commands for a SunStrong Management PVS6 gateway

## Installation

You can install it using pip:
```
pip install pypvs
```

# Running the examples

Initialize virtual environment and install requirements
```
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
```

Install `pypvs` in development mode
```
pip install -e .
```

Then run the example scripts
```
PVS_HOST=192.168.1.100 python examples/simple_fcgi_async.py

PVS_HOST=192.168.1.100 python examples/simple_pvs_async.py
```

# Access to the PVS via varserver

Please refer to [LocalAPI documentation](doc/LocalAPI.md) for details on accessing the PVS via varserver.
