from flask import Blueprint, render_template

from CTFd.api import CTFd_API_v1
from CTFd.plugins import (
    register_plugin_assets_directory,
    register_admin_plugin_menu_bar,
)
from CTFd.utils.decorators import admins_only
from CTFd.utils import get_config, set_config
from CTFd.plugins.migrations import upgrade
from CTFd.plugins.challenges import CHALLENGE_CLASSES

from .api import user_namespace, admin_namespace
from .utils.setup import setup_default_configs
from .models import DynamicIaCChallenge, DynamicIaCValueChallenge

import requests
import json

def load(app):

    app.config['RESTX_ERROR_404_HELP'] = False
    # upgrade()
    plugin_name = __name__.split('.')[-1]
    set_config('chall-manager:plugin_name', plugin_name)
    app.db.create_all()
    if not get_config("chall-manager:setup"):
        setup_default_configs()

    register_plugin_assets_directory(
        app, base_path=f"/plugins/{plugin_name}/assets",
        endpoint='plugins.ctfd-chall-manager.assets'
    )

    upgrade(plugin_name="ctfd-chall-manager") # don't knonw what does this
    CHALLENGE_CLASSES["dynamic_iac"] = DynamicIaCValueChallenge # register our challenge type in http://localhost:4000/admin/challenges/new


    page_blueprint = Blueprint(
        "ctfd-chall-manager",
        __name__,
        template_folder="templates",
        static_folder="assets",
        url_prefix="/plugins/ctfd-chall-manager"
    )

    # create namespaces in /api/v1/plugins/ctfd-chall-manager/xx/xx
    CTFd_API_v1.add_namespace(admin_namespace, path="/plugins/ctfd-chall-manager/admin")
    CTFd_API_v1.add_namespace(user_namespace, path="/plugins/ctfd-chall-manager")

    # Route to configure Chall-manager plugins
    @page_blueprint.route('/admin/settings')
    @admins_only
    def admin_list_configs():
        return render_template("chall_manager_config.html")


    # Route to monitor & manage running instances
    @page_blueprint.route('/admin/instances')
    @admins_only
    def admin_list_challenges():
        cm_api_url = get_config("chall-manager:chall-manager_api_url")
        url = f"{cm_api_url}/challenge"

        s = requests.Session()
        instances = list()

        with s.get(url, headers=None, stream=True) as resp:
            for line in resp.iter_lines():
                if line:
                    print(line)
                    res = line.decode("utf-8")
                    res = json.loads(res)

                    if res['result']['instances'] :
                        instances_of_current_chall = res['result']['instances']
                        for i in instances_of_current_chall:
                            instances.append(i)

        print(instances)
        return render_template("chall_manager_instances.html", instances=instances)

    app.register_blueprint(page_blueprint)