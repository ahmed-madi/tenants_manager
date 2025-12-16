# Copyright (c) 2025, opinov8 and contributors
# For license information, please see license.txt

import os
import subprocess

import frappe
from frappe import _
from frappe.utils import random_string, get_bench_path, get_date_str, cint
from frappe.utils.background_jobs import is_job_enqueued, enqueue
from frappe.utils.scheduler import is_scheduler_inactive
from frappe.installer import update_site_config
from frappe.model.document import Document

from tenants_manager.utils.site import (
    write_config_to_temp,
    clean_failed_site_creation,
    delete_temp_config,
)


class BusinessSite(Document):
    def validate(self):
        self.update_hash_code()
        self.check_and_get_site_settings()
        # if self.site_exists():
        #     frappe.throw(_("Site {} already exists".format(self.site_name)))

    def on_submit(self):
        self.set_site_name()
        self.db_set("progress_status", "Pending")
        self.db_set("status", "Pending")

    def on_cancel(self):
        self.db_set("progress_status", "Cancelled")
        self.db_set("status", "Cancelled")

    def update_hash_code(self):
        hashcode = random_string(32)
        list_subscription = frappe.get_all("Business Site", pluck="hashcode")
        while hashcode in list_subscription:
            hashcode = random_string(32)
        self.hashcode = hashcode

    def check_and_get_site_settings(self):
        settings = frappe.get_single("Business Site Settings")
        errors = []

        if not settings.db_password or len(settings.db_password) == 0:
            errors.append(_("Database Password"))
        if not settings.admin_email or len(settings.admin_email) == 0:
            errors.append(_("Admin or Support User Email"))
        if not settings.domain or len(settings.domain) == 0:
            errors.append(_("Domain Name"))
        if cint(settings.build_in_remote) == 1:
            if not settings.remote_host or len(settings.remote_host) == 0:
                errors.append(_("Remote Host Address"))
            if not settings.remote_port or len(settings.remote_port) == 0:
                errors.append(_("Remote Host Port"))
        if len(errors) > 0:
            errors = "".join([f"<li>{err}</li>" for err in errors])
            errors = f"<ul>{errors}</ul><br/>"
            link = frappe.bold(_("In Business Site Settings"))
            message = (
                errors
                + f"<a href='/app/business-site-settings' target='_blank'>{link}</a>"
            )

            frappe.throw(title=_("Missing Configurations"), msg=message)
        return (
            settings.get_password(fieldname="db_password"),
            settings.admin_email,
            cint(settings.build_in_remote),
            settings.remote_host,
            settings.remote_port,
        )

    def prepare_configs(self, support_pass, admin_email):
        business_user = frappe.get_doc("Business Owner", self.business_owner)
        business = frappe.get_doc("Business", self.business)
        settings = frappe.get_single("Business Site Settings")
        enable_oauth = cint(settings.enable_oauth)
        client_auth = {
            "enable_oauth": enable_oauth,
        }
        if enable_oauth == 1 and settings.oauth_client:
            oauth_client = frappe.get_doc("OAuth Client", settings.oauth_client)
            base_url = oauth_client.default_redirect_uri.split("/api/")[0]
            app_name = oauth_client.app_name
            client_id = oauth_client.client_id
            client_secret = oauth_client.client_secret
            client_auth.update({
                "app_name": app_name,
                "client_id": client_id,
                "client_secret": client_secret,
                "base_url": base_url,
            })

        site_config = {
            "support_user": {
                "support_name": "Support",
                "support_email": admin_email,
                "password": support_pass,
            },
            "business_user": {
                "first_name": business_user.first_name,
                "last_name": business_user.last_name,
                "email_address": business_user.email_address,
                "phone_number": business_user.phone_number,
                "date_of_birth": get_date_str(business_user.date_of_birth),
                "password": random_string(8),
            },
            "business_details": {
                "business_type": business_user.business_type,
                "business_legal_name": business.business_name or business_user.business_legal_name,
                "business_id": business_user.business_id,
            },
            "business_address": {
                "address_line_1": business_user.address_line_1,
                "address_line_2": business_user.address_line_2,
                "city": business_user.city,
                "state": business_user.state,
                "zip_code": business_user.zip_code,
                "country": business_user.country,
            },
            "client_auth": client_auth,
            "is_suspended": 0,
            "run_as_saas": 1,
            "maintenance_mode": 0,
        }
        return site_config

    def site_exists(self):
        # check sites in the system
        used_sites_names = list(
            filter(
                lambda x: x not in ["apps.txt", "apps.json", "common_site_config.json"],
                os.listdir(get_bench_path() + "/sites"),
            )
        )
        return self.site_name in used_sites_names

    def can_run_job(self):
        if is_scheduler_inactive() and not frappe.flags.in_test:
            return False
        return True

    def set_site_name(self):
        from frappe.model.naming import make_autoname

        domain = frappe.db.get_single_value("Business Site Settings", "domain")
        business_domain = str(self.business_domain).strip().lower().replace(" ", "")
        series_name = business_domain + "." + domain
        self.db_set("site_name", series_name)

    @frappe.whitelist()
    def create_site(self):
        if self.docstatus != 1:
            frappe.msgprint(_("Can not create site for Draft details"))
            return
        if self.status not in ["Pending", "Failed"]:
            frappe.msgprint(_("Can not create site for {} site".format(self.status)))
            frappe.log_error(
                message="Can not create site for {} site".format(self.status),
                title="Failed in Pre Create",
            )
            return

        db_pass, admin_email, is_remote_host, remote_host, remote_port = (
            self.check_and_get_site_settings()
        )

        admin_pass = random_string(8)
        support_pass = random_string(8)

        if not isinstance(db_pass, str):
            db_pass = ""

        if len(db_pass) == 0:
            frappe.log_error(
                message="Database Config Error, Set database password",
                title="Failed in Pre Create",
            )
            self.db_set("progress_status", "Failed")
            self.db_set("status", "Failed")
            return

        if self.site_exists():
            frappe.msgprint(_("Site {} already exists".format(self.site_name)))
            frappe.log_error(
                message="Site {} already exists".format(self.site_name),
                title="Failed in Pre Create",
            )
            self.db_set("progress_status", "Failed")
            self.db_set("status", "Failed")
            return

        if not self.can_run_job():
            frappe.msgprint(_("Scheduler Inactive"))
            frappe.log_error(
                message="Scheduler Inactive",
                title="Failed in Pre Create",
            )
            self.db_set("progress_status", "Failed")
            self.db_set("status", "Failed")
            frappe.db.commit()
            return

        self.db_set("progress_status", "In Progress")
        self.db_set("status", "In Progress")
        frappe.db.commit()

        job_id = f"site-creation::{self.name}"
        if not is_job_enqueued(job_id):
            config = self.prepare_configs(support_pass, admin_email)
            enqueue(
                create_site_job,
                site_doc=self.name,
                site_name=self.site_name,
                db_user="root",
                db_pass=db_pass,
                admin_pass=admin_pass,
                support_pass=support_pass,
                is_remote_host=is_remote_host,
                remote_host=remote_host,
                remote_port=remote_port,
                config=config,
                timeout=5600,
                queue="long",
            )
        return


def create_site_job(
    site_doc,
    site_name,
    db_user,
    db_pass,
    admin_pass,
    support_pass,
    is_remote_host,
    remote_host,
    remote_port,
    config,
):
    # add config to temp file
    write_config_to_temp(site_name, config)
    admin_pass = f"{admin_pass}"
    failed = False

    # Step 1: create site
    try:
        cmd = [
            "bench",
            "new-site",
            "--db-name",
            site_name,
            "--mariadb-root-username",
            db_user,
            "--mariadb-root-password",
            db_pass,
            "--admin-password",
            admin_pass,
            # "--install-app", "erpnext",
            # "--install-app", "engine",
            # site_name,
        ]
        if is_remote_host == 1:
            cmd.extend(["--db-host", remote_host, "--db-port", remote_port])
        cmd.append(site_name)
        p = subprocess.run(cmd, capture_output=True, cwd=get_bench_path())
        if p.returncode != 0:
            raise Exception(
                "Failed To Create Site {}\n\n{}".format(site_name, p.stderr)
            )
    except Exception as e:
        frappe.db.set_value("Business Site", site_doc, "status", "Failed")
        frappe.log_error(message=e, title="Failed To Create Site")
        clean_failed_site_creation(site_name, db_pass)
        return

    # step 2: install apps (erpnext and other apps)
    frappe.db.set_value("Business Site", site_doc, "progress_status", "Installing Apps")
    frappe.db.commit()

    default_apps = [
        app[0]
        for app in frappe.db.sql(
            """SELECT app_name FROM `tabBusiness App To Install` WHERE parenttype='Business Site Settings'"""
        )
        if isinstance(app[0], str) and len(app[0]) > 0 and app[0] != "tenant_engine"
    ]
    custom_apps = [
        app[0]
        for app in frappe.db.sql(
            """SELECT app_name FROM `tabBusiness App To Install` WHERE parenttype='Business Site' AND parent='{}'""".format(
                site_doc
            )
        )
        if isinstance(app[0], str) and len(app[0]) > 0 and app[0] != "tenant_engine"
    ]
    apps_to_install = set(default_apps + custom_apps)
    if len(apps_to_install) > 0:
        try:
            for app in apps_to_install:
                cmd = ["bench", "--site", site_name, "install-app", app]
                p = subprocess.run(cmd, capture_output=True, cwd=get_bench_path())
                # code for DeprecationWarning warning is 1, skip in this case failed
                if p.returncode != 0:
                    raise Exception(
                        "Failed To Install Apps {} in {}\n\n{}\n\nreturn code {}".format(
                            " ".join(apps_to_install), site_name, p.stderr, p.returncode
                        )
                    )
        except Exception as e:
            frappe.db.set_value("Business Site", site_doc, "status", "Failed")
            frappe.log_error(message=e, title="Failed To install Apps")
            clean_failed_site_creation(site_name, db_pass)
            return

    # Step 3: (complete) add users and setup settings (install engine app)
    frappe.db.set_value("Business Site", site_doc, "progress_status", "Completed")
    frappe.db.commit()
    try:
        cmd = ["bench", "--site", site_name, "install-app", "tenant_engine"]
        p = subprocess.run(cmd, capture_output=True, cwd=get_bench_path())
        if p.returncode != 0 and "DeprecationWarning" not in str(p.stderr):
            raise Exception(
                "Failed To Install Engine App in {}\n\n{}".format(site_name, p.stderr)
            )
    except Exception as e:
        frappe.db.set_value("Business Site", site_doc, "status", "Failed")
        frappe.log_error(message=e, title="Failed To install Apps")
        clean_failed_site_creation(site_name, db_pass)
        return

    # Step 4: cleanup
    frappe.db.set_value("Business Site", site_doc, "progress_status", "Cleanup")
    frappe.db.commit()
    # Create Log
    create_logs(site_doc, site_name, "Create")
    # Create Subscription Security to store administrator/support passwords
    create_security(site_doc, site_name, admin_pass, support_pass)
    # update config of new site
    config_path = os.path.join(get_bench_path(), "sites", site_name, "site_config.json")
    for key, value in config.items():
        if key in ["support_user", "business_user"]:
            del value["password"]
        key = frappe.scrub(key)
        update_site_config(f"{key}", value, site_config_path=config_path)
    # delete config temp file
    delete_temp_config(site_name)
    # Setup NGINX
    try:
        cmd = ["bench", "setup", "nginx", "--yes"]
        p = subprocess.run(cmd, capture_output=True, cwd=get_bench_path())
        if p.returncode != 0:
            raise Exception(
                "Failed To Create NGINX setup to Site {}\n\n{}".format(
                    site_name, p.stderr
                )
            )
    except Exception as e:
        frappe.log_error(
            message=e, title=f"Failed To Create NGINX setup for {site_name}"
        )
    # Reload NGINX
    try:
        cmd = ["sudo", "service", "nginx", "reload"]
        p = subprocess.run(cmd, capture_output=True, cwd=get_bench_path())
        if p.returncode != 0:
            raise Exception(
                "Failed To Reload NGINX to Site {}\n\n{}".format(site_name, p.stderr)
            )
    except Exception as e:
        frappe.log_error(message=e, title=f"Failed To Reload NGINX for {site_name}")

    # Step 5: ready to use
    frappe.db.set_value("Business Site", site_doc, "progress_status", "Ready to Use")
    frappe.db.set_value("Business Site", site_doc, "status", "Ready to Use")

    frappe.db.commit()


def create_logs(site_doc_name, site_name, action):
    action_at = frappe.utils.now_datetime()
    logs = frappe.new_doc("Business Site User Action Log")
    logs.business_site_id = site_doc_name
    logs.site_name = site_name
    logs.action = action
    logs.action_by = frappe.session.user
    logs.action_at = action_at
    logs.title = f"{frappe.session.user} {action} {site_name} at {action_at}"
    logs.save(ignore_permissions=True)
    logs.submit()


def create_security(site_doc_name, site_name, admin_pass, support_pass):
    ss = frappe.new_doc("Business Site Security")
    ss.business_site_id = site_doc_name
    ss.site_name = site_name
    ss.administrator_password = admin_pass
    ss.support_password = support_pass
    ss.insert(ignore_permissions=True)
    ss.submit()
