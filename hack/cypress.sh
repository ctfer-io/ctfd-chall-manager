export CYPRESS_CTFD_NAME="ctfer"
export CYPRESS_CTFD_PASSWORD="ctfer"
export CYPRESS_CTFD_URL="http://localhost:8000" 
export CYPRESS_SCENARIO="registry:5000/examples/deploy:latest"
export CYPRESS_PLUGIN_SETTINGS_CM_API_URL="http://chall-manager:8080/api/v1"
export CYPRESS_PLUGIN_SETTINGS_CM_MANA_TOTAL="10"

npx cypress open
