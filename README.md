# Installation

1. Prepare .env

Create the .env file and fill in environment variables.
```
cp .env.dist .env
```
The API address and access token can be obtained at https://sphere-engine.com/tokens?service=applications.

Example:
```
SECO_URL=XXXXXXXX.containers.sphere-engine.com
SECO_API_URL=https://XXXXXXXX.containers.sphere-engine.com/api/v1
SECO_API_ACCESS_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

2. Prepare environment

```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

3. Start server

```
./start.sh
```

Application is available at http://localhost:5000/.
