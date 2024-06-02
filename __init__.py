
import json
from flask import Blueprint, render_template

from CTFd.api import CTFd_API_v1
from CTFd.plugins import (
    register_plugin_assets_directory,
    register_admin_plugin_menu_bar,
)
from CTFd.utils.decorators import admins_only
from CTFd.utils import get_config, set_config
from CTFd.utils.user import get_user_attrs, get_team_attrs
from CTFd.utils.challenges import get_all_challenges
from CTFd.plugins.migrations import upgrade
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from CTFd.models import Users, db

import time
from sqlalchemy import text
import requests
from .api import user_namespace, admin_namespace
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

        retries = 0
        try:
            with s.get(url, headers=None, stream=True) as resp:
                for line in resp.iter_lines():
                    if line:
                        res = line.decode("utf-8")
                        res = json.loads(res)

                        if res['result']['instances'] :
                            instances_of_current_chall = res['result']['instances']
                            for i in instances_of_current_chall:
                                instances.append(i)
        except requests.ConnectionError as e:
            print(f"ConnectionError: {e}")  # Debug print

        
        user_mode = get_config("user_mode")
        for i in instances:
            if user_mode == "users":
                i["sourceName"] = get_user_attrs(i["sourceId"]).name   
            if user_mode == "teams":
                i["sourceName"] = get_team_attrs(i["sourceId"]).name
           
            i["challengeName"] = get_all_challenges(id=i["challengeId"])[0].name
        
        return render_template("chall_manager_instances.html", 
                                instances=instances, 
                                user_mode=user_mode)

    # Route to monitor & manage running instances
    @page_blueprint.route('/admin/mana')
    @admins_only
    def admin_list_mana():
        cm_mana_total = get_config("chall-manager:chall-manager_mana_total")
        user_mode = get_config("user_mode")

        if user_mode == "users":
            query_sql = """select id,name,mana from users;"""
        
        elif user_mode == "teams":
            query_sql = """select id,name,mana from teams;"""

        data = db.session.execute(text(query_sql)).fetchall()

        # Convert to the desired dictionary format
        sources = {
            "data": [
                {
                    "id": item[0],
                    "name": item[1],
                    "mana": str(item[2])  # Convert the mana value to string
                }
                for item in data
            ]
        } 

        return render_template("chall_manager_mana.html",
                                user_mode=user_mode,
                                sources=sources["data"])

    
    app.register_blueprint(page_blueprint)
