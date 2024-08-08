import json
from flask import Blueprint, render_template

from CTFd.api import CTFd_API_v1  # type: ignore
from CTFd.plugins import register_plugin_assets_directory  # type: ignore
from CTFd.utils.decorators import admins_only  # type: ignore
from CTFd.utils import get_config, set_config  # type: ignore
from CTFd.utils.challenges import get_all_challenges  # type: ignore
from CTFd.plugins.migrations import upgrade  # type: ignore
from CTFd.plugins.challenges import CHALLENGE_CLASSES  # type: ignore

from .api import user_namespace, admin_namespace
from .utils.setup import setup_default_configs
from .utils.challenge_store import query_challenges
from .models import DynamicIaCValueChallenge

from .utils.mana_coupon import get_all_mana
from .utils.logger import configure_logger

# Configure logger for this module
logger = configure_logger(__name__)

def load(app):
    app.config['RESTX_ERROR_404_HELP'] = False

    plugin_name = __name__.split('.')[-1]
    set_config('chall-manager:plugin_name', plugin_name)
    app.db.create_all()
    logger.debug("Database initialized and plugin name set.")

    if not get_config("chall-manager:setup"):
        logger.info("Initial setup configurations not found. Setting up default configs.")
        setup_default_configs()

    register_plugin_assets_directory(
        app, base_path=f"/plugins/{plugin_name}/assets",
        endpoint='plugins.ctfd-chall-manager.assets'
    )
    logger.info("Plugin assets directory registered.")

    # apply migration scripts
    upgrade()
    logger.info("Database migrations applied.")

    # register our challenge type in http://localhost:4000/admin/challenges/new
    CHALLENGE_CLASSES["dynamic_iac"] = DynamicIaCValueChallenge
    logger.info("DynamicIaCValueChallenge registered.")

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

    logger.info("API namespaces added.")

    # Route to configure Chall-manager plugins
    @page_blueprint.route('/admin/settings')
    @admins_only
    def admin_settings():
        logger.debug("Accessing admin settings page.")
        return render_template("chall_manager_config.html")

    # Route to monitor & manage running instances
    @page_blueprint.route('/admin/instances')
    @admins_only
    def admin_instances():
        logger.debug("Accessing admin instances page.")
        result = list()

        try:
            result = query_challenges()
            logger.info(f"Retrieved {len(result)} challenges.")
        except Exception as e:
            logger.error(f"Error querying challenges: {e}")

        instances = list()

        for challenge in result:
            for instance in challenge["instances"]:
                instances.append(instance)

        user_mode = get_config("user_mode")
        for i in instances:
            challenge_name = get_all_challenges(admin=True, id=i["challengeId"])[0].name
            i["challengeName"] = challenge_name
            logger.debug(f"Instance: {i}")

        return render_template("chall_manager_instances.html",
                               instances=instances,
                               user_mode=user_mode)

    # Route to monitor & manage mana
    @page_blueprint.route('/admin/mana')
    @admins_only
    def admin_mana():
        logger.debug("Accessing admin mana page.")
        user_mode = get_config("user_mode")

        sources = get_all_mana()
        logger.info(f"Retrieved mana data for {len(sources)} sources.")

        return render_template("chall_manager_mana.html",
                               user_mode=user_mode,
                               sources=sources)

    # Route to monitor & manage panel
    @page_blueprint.route('/admin/panel')
    @admins_only
    def admin_panel():
        logger.debug("Accessing admin panel page.")
        # retrieve custom challenges
        challenges = get_all_challenges(admin=True, type="dynamic_iac")
        logger.info(f"Retrieved {len(challenges)} dynamic IAC challenges.")

        return render_template("chall_manager_panel.html",
                               challenges=challenges)

    app.register_blueprint(page_blueprint)
    logger.info("Blueprint registered.")
