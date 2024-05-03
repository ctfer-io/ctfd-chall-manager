from CTFd.utils import set_config


def setup_default_configs():
    for key, val in {
        'setup': 'true',
        'chall-manager_api_url': 'http://localhost:9090/api/v1'
    }.items():
        set_config('chall-manager:' + key, val)