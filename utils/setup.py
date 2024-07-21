from CTFd.utils import set_config # type: ignore


def setup_default_configs():
    for key, val in {
        'setup': 'true',
        'chall-manager_api_url': 'http://localhost:9090/api/v1',
        'chall-manager_mana_total': 0
    }.items():
        set_config('chall-manager:' + key, val)