from flask import Blueprint, render_template, redirect, url_for
import logging

logger = logging.getLogger(__name__)

landing_bp = Blueprint('landing', __name__, template_folder='templates')

@landing_bp.route('/')
def landing_page():
    logger.info("Landing page accessed")
    # For now, just render the static landing page
    return render_template('landing.html')