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

from .utils.setup import setup_default_configs
from .models import DynamicIaCChallenge, DynamicIaCValueChallenge

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

    upgrade(plugin_name="ctfd-chall-manager")
    CHALLENGE_CLASSES["dynamic_iac"] = DynamicIaCValueChallenge


    page_blueprint = Blueprint(
        "ctfd-chall-manager",
        __name__,
        template_folder="templates",
        static_folder="assets",
        url_prefix="/plugins/ctfd-chall-manager"
    )
    # CTFd_API_v1.add_namespace(admin_namespace, path="/plugins/ctfd-chall-manager/admin")
    # CTFd_API_v1.add_namespace(user_namespace, path="/plugins/ctfd-chall-manager")

    # Route to configure Chall-manager plugins
    @page_blueprint.route('/admin/settings')
    @admins_only
    def admin_list_configs():
        return render_template("chall_manager_config.html")


    # Route to monitor & manage running challenges
    @page_blueprint.route('/admin/challenges')
    @admins_only
    def admin_list_challenges():
        return render_template("chall_manager_challenges.html", 
                               plugin_name=plugin_name,
                               containers=result['data']['containers'],
                               pages=result['data']['pages'],
                               curr_page=abs(request.args.get("page", 1, type=int)),
                               curr_page_start=result['data']['page_start'])


    app.register_blueprint(page_blueprint)