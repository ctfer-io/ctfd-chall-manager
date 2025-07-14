# Tests

## How to run tests locally

1. Start a fresh install of CTFd

```bash
cd hack
docker compose down -v 
docker compose up
```

2. Create accounts and variable
```bash
# Retrieve admin token 
cd hack/token

export CTFD_URL="http://localhost:8000"
export CTFD_NAME="ctfer"
export CTFD_PASSWORD="ctfer"

export CTFD_API_KEY=$(go run main.go)
cd -

# Create accounts
cd hack/config
export PULUMI_CONFIG_PASSPHRASE=""
pulumi login --local 
pulumi stack init test
pulumi up -y
cd -

# Retrieve token for account
cd hack/token
export CTFD_NAME="ctfer"
export CTFD_PASSWORD="ctfer"
export CTFD_API_TOKEN_ADMIN=$(go run main.go)


export CTFD_NAME="user1"
export CTFD_PASSWORD="user1"
export CTFD_API_TOKEN_USER=$(go run main.go)
cd -

```

3. Deploy example scenario in registry
```bash
cd hack/deploy
bash build.sh
cd -
```

4. Run Python Tests

```bash
python -m unittest test/test_api_challenges.py
python -m unittest test/test_api_admin_instance.py
python -m unittest test/test_api_instance.py
python -m unittest test/test_api_mana.py
```



# How to reset your environment 

1. Delete Pulumi resource
```bash
cd hack/config
export PULUMI_CONFIG_PASSPHRASE=""
pulumi login --local 
pulumi stack --select test
pulumi destroy -y 
cd -

```