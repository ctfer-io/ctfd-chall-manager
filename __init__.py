
import json
from flask import Blueprint, render_template

from CTFd.api import CTFd_API_v1 # type: ignore
from CTFd.plugins import ( # type: ignore
    register_plugin_assets_directory,
)
from CTFd.utils.decorators import admins_only # type: ignore
from CTFd.utils import get_config, set_config # type: ignore # type: ignore
from CTFd.utils.challenges import get_all_challenges # type: ignore
from CTFd.plugins.migrations import upgrade # type: ignore
from CTFd.plugins.challenges import CHALLENGE_CLASSES # type: ignore

from .api import user_namespace, admin_namespace
from .utils.setup import setup_default_configs
from .utils.challenge_store import query_challenges
from .models import DynamicIaCValueChallenge

from .utils.mana_coupon import get_all_mana


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

    # apply migration scripts
    upgrade()

    # register our challenge type in http://localhost:4000/admin/challenges/new
    CHALLENGE_CLASSES["dynamic_iac"] = DynamicIaCValueChallenge 

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
    def admin_settings():
        return render_template("chall_manager_config.html")


    # Route to monitor & manage running instances
    @page_blueprint.route('/admin/instances')
    @admins_only
    def admin_instances():

        result = list()

        try:
            result = query_challenges()
        except Exception as e:
            print(f"ERROR : {e}") # TODO use logging
        
        instances = list()

        for challenge in result:
            for instance in challenge["instances"]:
                instances.append(instance)
        
        user_mode = get_config("user_mode")
        for i in instances:
            i["challengeName"] = get_all_challenges(admin=True, id=i["challengeId"])[0].name
        
        return render_template("chall_manager_instances.html", 
                                instances=instances, 
                                user_mode=user_mode)

    # Route to monitor & manage running instances
    @page_blueprint.route('/admin/mana')
    @admins_only
    def admin_mana():
        user_mode = get_config("user_mode")

        sources = get_all_mana()

        return render_template("chall_manager_mana.html",
                                user_mode=user_mode,
                                sources=sources)

    # Route to monitor & manage running instances
    @page_blueprint.route('/admin/panel')
    @admins_only
    def admin_panel():
        # retrieve custom challenges
        challenges = get_all_challenges(admin=True, type="dynamic_iac")

        return render_template("chall_manager_panel.html",
                                challenges=challenges)
    
    app.register_blueprint(page_blueprint)
