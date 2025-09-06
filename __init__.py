"""
This modules defines the entrypoint of the plugin (load)
and all Admins pages endpoints.
"""

import requests
from CTFd.api import CTFd_API_v1
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from CTFd.plugins.ctfd_chall_manager.api import admin_namespace, user_namespace
from CTFd.plugins.ctfd_chall_manager.models import (DynamicIaCChallenge,
                                                    DynamicIaCValueChallenge)
from CTFd.plugins.ctfd_chall_manager.utils.chall_manager_error import \
    ChallManagerException
from CTFd.plugins.ctfd_chall_manager.utils.challenge_store import \
    query_challenges
from CTFd.plugins.ctfd_chall_manager.utils.logger import configure_logger
from CTFd.plugins.ctfd_chall_manager.utils.mana_coupon import get_all_mana
from CTFd.plugins.ctfd_chall_manager.utils.setup import setup_default_configs
from CTFd.plugins.migrations import upgrade
from CTFd.utils import get_config, set_config
from CTFd.utils.challenges import get_all_challenges
from CTFd.utils.decorators import admins_only
from flask import Blueprint, render_template, request

# Configure logger for this module
logger = configure_logger(__name__)


def load(app):  # pylint: disable=too-many-statements
    """
    Initiate all CTFd configuration for the plugin.
    """
    app.config["RESTX_ERROR_404_HELP"] = False

    plugin_name = __name__.rsplit(".", maxsplit=1)[-1]
    set_config("chall-manager:plugin_name", plugin_name)
    app.db.create_all()
    logger.debug("Database initialized and plugin name set.")

    if not get_config("chall-manager:setup"):
        logger.info(
            "Initial setup configurations not found. Setting up default configs."
        )
        setup_default_configs()

    register_plugin_assets_directory(
        app,
        base_path=f"/plugins/{plugin_name}/assets",
        endpoint="plugins.ctfd_chall_manager.assets",
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
        url_prefix="/plugins/ctfd-chall-manager",
    )

    # create namespaces in /api/v1/plugins/ctfd-chall-manager/xx/xx
    CTFd_API_v1.add_namespace(admin_namespace, path="/plugins/ctfd-chall-manager/admin")
    CTFd_API_v1.add_namespace(user_namespace, path="/plugins/ctfd-chall-manager")

    logger.info("API namespaces added.")

    # Route to configure Chall-manager plugins
    @page_blueprint.route("/admin/settings")
    @admins_only
    def admin_settings():  # pylint: disable=unused-variable
        logger.debug("Accessing admin settings page.")

        try:
            logger.debug("getting connection status with chall-manager")
            health_url = (
                f'{get_config("chall-manager:chall-manager_api_url")}/healthcheck'
            )
            requests.get(health_url, timeout=5).raise_for_status()
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.warning("cannot communicate with CM provided got %s", e)
            cm_api_reachable = False
        else:
            logger.info("communication with CM configured successfully")
            cm_api_reachable = True

        return render_template(
            "chall_manager_config.html", cm_api_reachable=cm_api_reachable
        )

    # Route to monitor & manage running instances
    @page_blueprint.route("/admin/instances")
    @admins_only
    def admin_instances():  # pylint: disable=unused-variable
        logger.debug("Accessing admin instances page.")
        result = []

        try:
            result = query_challenges()
            logger.info("retrieved %s challenges successfully", len(result))
        except ChallManagerException as e:
            logger.error("error querying challenges: %s", e)

        instances = []

        for challenge in result:
            for instance in challenge["instances"]:
                instances.append(instance)

        user_mode = get_config("user_mode")
        for i in instances:
            challenge_name = get_all_challenges(admin=True, id=i["challengeId"])[0].name
            i["challengeName"] = challenge_name
            logger.debug("instance: %s", i)

        return render_template(
            "chall_manager_instances.html", instances=instances, user_mode=user_mode
        )

    # Route to monitor & manage mana
    @page_blueprint.route("/admin/mana")
    @admins_only
    def admin_mana():
        logger.debug("Accessing admin mana page.")
        user_mode = get_config("user_mode")

        sources = get_all_mana()
        logger.info("retrieved mana data for %s sources", len(sources))

        return render_template(
            "chall_manager_mana.html", user_mode=user_mode, sources=sources
        )

    # Route to monitor & manage panel
    @page_blueprint.route("/admin/panel")
    @admins_only
    def admin_panel():  # pylint: disable=unused-variable
        q = request.args.get("q")
        field = request.args.get("field")
        filters = []

        if q:
            # The field exists as an exposed column
            if DynamicIaCChallenge.__mapper__.has_property(field):
                filters.append(getattr(DynamicIaCChallenge, field).like(f"%{q}%"))

        query = DynamicIaCChallenge.query.filter(*filters).order_by(
            DynamicIaCChallenge.id.asc()
        )
        challenges = query.all()
        total = query.count()

        return render_template(
            "chall_manager_panel.html",
            challenges=challenges,
            total=total,
            q=q,
            field=field,
        )

    app.register_blueprint(page_blueprint)
    logger.info("Blueprint registered.")
