import os
from pathlib import Path

from flask import Flask, request, render_template, redirect, url_for, session, send_file, abort
import bcrypt
from dotenv import load_dotenv
from database import new_user_data
from database import db_connection, user_validation
from database import license_service

from __init__ import get_logger

logger = get_logger(__name__)

env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

app = Flask(__name__)
app.secret_key = "your-secret-key"


def get_fingerprint_tool_path() -> Path:
    rel_path = os.getenv("finger_print_path", "downloadable/fingerprint_tool.exe")
    file_path = Path(rel_path)
    if not file_path.is_absolute():
        file_path = Path(__file__).parent / file_path
    return file_path.resolve()


@app.route("/download/fingerprint-tool")
def download_fingerprint_tool():
    file_path = get_fingerprint_tool_path()
    if not file_path.is_file():
        logger.error(f"Fingerprint tool not found at: {file_path}")
        abort(404, description=f"Fingerprint tool not found at: {file_path}")

    return send_file(
        file_path,
        as_attachment=True,
        download_name=file_path.name,
    )


@app.route("/", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        fname            = request.form.get("fname")
        lname            = request.form.get("lname")
        email            = request.form.get("email")
        password         = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        user_type        = request.form.get("user_type")
        role             = request.form.get("role")

        logger.info("Retrieved user data from frontend")

        if password != confirm_password:
            session["error"] = "Passwords do not match."
            return redirect(url_for("signup"))

        logger.info("Password hashing started")
        salt            = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        logger.info("Password hashing successful")

        try:
            new_user = new_user_data.InsertNewUser()
            logger.info("Sending user data to database")
            new_user.new_client(
                fname         = fname,
                lname         = lname,
                user_type     = user_type,
                role          = role,
                email         = email,
                password_hash = hashed_password,
            )
            logger.info("User created successfully")
            return redirect(url_for("signin"))

        except ValueError as e:
            session["error"] = str(e)
            return redirect(url_for("signup"))

        except Exception as e:
            logger.exception(f"Unexpected error during signup: {e}")
            session["error"] = "Something went wrong. Please try again."
            return redirect(url_for("signup"))

    error = session.pop("error", None)
    return render_template("signup.html", error=error)


@app.route("/signin", methods=["GET", "POST"])
def signin():

    if request.method == "POST":

        email    = request.form.get("email")
        password = request.form.get("password")
    

        try:
            user_id = user_validation.signin_validation.validate(email, password)
            session["email"] = email
            session["user_id"] = user_id
            logger.info("User signed in successfully")
            return redirect(url_for("dashboard"))

        except ValueError as e:
            session["signin_error"] = str(e)
            return redirect(url_for("signin"))

        except Exception as e:
            logger.exception(f"Unexpected error during signin: {e}")
            session["signin_error"] = "Something went wrong. Please try again."
            return redirect(url_for("signin"))

    error = session.pop("signin_error", None)
    return render_template("signin.html", error=error)


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/licence", methods=["GET", "POST"])
def generate_license():
    email = session.get("email")
    if not email:
        return redirect(url_for("signin"))

    if request.method == "POST":
        fingerprint_id = request.form.get("fingerprint_id")
        plan           = request.form.get("plan")
        quota_raw      = request.form.get("quota")

        try:
            user_id = session.get("user_id")
            if user_id is None:
                user_id = license_service.get_user_id_by_email(email)
                session["user_id"] = user_id

            quota = int(quota_raw) if quota_raw and quota_raw.strip() else None

            payload, license_path = license_service.create_user_license(
                user_id=user_id,
                email=email,
                fingerprint_id=fingerprint_id,
                plan=plan,
                quota=quota,
            )

            logger.info(f"Licence generated for user {user_id} | plan={plan}")
            return send_file(
                license_path,
                as_attachment=True,
                download_name="license.lic",
            )

        except ValueError as e:
            session["licence_error"] = str(e)
            return redirect(url_for("generate_license"))

        except Exception as e:
            logger.exception(f"Unexpected error during licence generation: {e}")
            session["licence_error"] = "Something went wrong. Please try again."
            return redirect(url_for("generate_license"))

    success = session.pop("licence_success", None)
    error   = session.pop("licence_error", None)
    return render_template("generate_license.html", email=email, success=success, error=error)


@app.route("/licence/latest")
def latest_license():
    email = session.get("email")
    if not email:
        return redirect(url_for("signin"))

    try:
        license_path = license_service.latest_license_retrival(email)
        if not license_path.is_file():
            logger.error(f"Licence file not found on disk: {license_path}")
            abort(404, description="Licence file not found.")

        logger.info(f"Latest licence downloaded for {email}")
        return send_file(
            license_path,
            as_attachment=True,
            download_name="license.lic",
        )

    except ValueError as e:
        session["licence_error"] = str(e)
        return redirect(url_for("generate_license"))

    except Exception as e:
        logger.exception(f"Unexpected error retrieving latest licence: {e}")
        session["licence_error"] = "Something went wrong. Please try again."
        return redirect(url_for("generate_license"))


if __name__ == "__main__":
    app.run(debug=True)