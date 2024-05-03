from CTFd.utils import set_config


def setup_default_configs():
    for key, val in {
        'setup': 'true',
        'chall-manager_api_url': 'chall-manager-svc-headless.svc.cluster.local'
    }.items():
        set_config('chall-manager:' + key, val)