"""
This modules defines the entrypoint of the plugin (load)
and all Admins pages endpoints.
"""

import os

import requests
from CTFd.plugins import register_plugin_assets_directory, register_user_page_menu_bar
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from CTFd.plugins.ctfd_chall_manager.api import register_api_endpoints
from CTFd.plugins.ctfd_chall_manager.models import (
    DynamicIaCChallenge,
    DynamicIaCValueChallenge,
)
from CTFd.plugins.ctfd_chall_manager.utils.chall_manager_error import (
    ChallManagerException,
)
from CTFd.plugins.ctfd_chall_manager.utils.challenge_store import query_challenges
from CTFd.plugins.ctfd_chall_manager.utils.helpers import (
    calculate_all_mana_used,
    calculate_mana_used,
)
from CTFd.plugins.ctfd_chall_manager.utils.instance_manager import query_instance
from CTFd.plugins.ctfd_chall_manager.utils.logger import configure_logger
from CTFd.plugins.ctfd_chall_manager.utils.setup import setup_default_configs
from CTFd.plugins.migrations import upgrade
from CTFd.utils import get_config, set_config
from CTFd.utils import user as current_user
from CTFd.utils.challenges import get_all_challenges
from CTFd.utils.config import is_teams_mode
from CTFd.utils.decorators import admins_only, authed_only
from flask import Blueprint, redirect, render_template, request, url_for

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

    register_api_endpoints()

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
            "chall_manager_admin_instances.html",
            instances=instances,
            user_mode=user_mode,
        )

    # Route to monitor & manage mana
    @page_blueprint.route("/admin/mana")
    @admins_only
    def admin_mana():
        logger.debug("Accessing admin mana page.")
        user_mode = get_config("user_mode")

        sources = []
        source_ids = {}
        try:
            source_ids = calculate_all_mana_used()
        except ChallManagerException as e:
            logger.error("error while calculating mana for all sources: %s", e)

        for item in source_ids.items():
            sources.append({"source_id": item[0], "mana": item[1]})
        logger.info("retrieved mana data for %s sources %s", len(sources), sources)

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

    # Route to monitor & manage running instances
    @page_blueprint.route("/instances")
    @authed_only
    def instances():  # pylint: disable=unused-variable
        mana_total = int(get_config("chall-manager:chall-manager_mana_total"))
        mana_enabled = mana_total > 0
        mana_remaining = mana_total
        mana_used = 0

        user_id = int(current_user.get_current_user().id)
        source_id = user_id
        if is_teams_mode():
            source_id = current_user.get_current_user().team_id
            # If user has no team
            if not source_id:
                logger.info(
                    "user %s has no team, abort",
                    user_id,
                )
                # return into team creation
                return redirect(url_for("teams.private", next=request.full_path))
        try:
            instances = query_instance(int(source_id))
            logger.info("retrieved %s challenges successfully", len(instances))
        except ChallManagerException as e:
            logger.error("error querying challenges: %s", e)
            return render_template(
                "chall_manager_instances.html",
                instances=[],  # empty instances if cm generate error
                mana_remaining="unknown",
                mana_total=mana_total,
                mana_enabled=mana_enabled,
            )

        for i in instances:
            # Add CTFd infos, admin=False means do no display hidden challenges
            challenge = get_all_challenges(admin=False, id=i["challengeId"])

            # if challenge is not hidden
            if len(challenge) == 1:
                i["challengeName"] = challenge[0].name
                i["challengeCategory"] = challenge[0].category
            else:  # if challenge is hidden
                i["challengeName"] = "hidden"
                i["challengeCategory"] = "hidden"
                i["connectionInfo"] = "hidden"

            challenge = DynamicIaCChallenge.query.filter_by(id=i["challengeId"]).first()
            i["manaCost"] = challenge.mana_cost

        if mana_enabled:
            # calculate mana only if its enabled
            try:
                mana_used = calculate_mana_used(source_id)
            except ChallManagerException:
                return render_template(
                    "chall_manager_instances.html",
                    instances=instances,
                    mana_remaining="unknown",
                    mana_total=mana_total,
                    mana_enabled=mana_enabled,
                )

            mana_remaining = mana_total - mana_used

        return render_template(
            "chall_manager_instances.html",
            instances=instances,
            mana_remaining=mana_remaining,
            mana_total=mana_total,
            mana_enabled=mana_enabled,
        )

    app.register_blueprint(page_blueprint)
    logger.info("Blueprint registered.")

    # https://github.com/ctfer-io/ctfd-chall-manager/issues/226
    instances_panel_enabled = (
        os.getenv("PLUGIN_SETTINGS_CM_UI_HIDE_INSTANCES_PANEL", "false").lower()
        != "true"
    )
    if instances_panel_enabled:
        register_user_page_menu_bar(
            "Instances", "/plugins/ctfd-chall-manager/instances"
        )
