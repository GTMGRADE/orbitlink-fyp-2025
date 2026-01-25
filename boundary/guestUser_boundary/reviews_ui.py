from flask import Blueprint, render_template
# <<<<<<< HEAD
from Controller.guestUser_controller.reviews_controller import ReviewsController
# =======
from Controller.guestUser_controller.reviews_controller import ReviewsController
# >>>>>>> development
import logging

logger = logging.getLogger(__name__)

reviews_bp = Blueprint('reviews', __name__, template_folder='templates')

@reviews_bp.route('/reviews')
def show_reviews():
    logger.info("Reviews page accessed")
    
    # Create controller instance and get data
    controller = ReviewsController()
    reviews_data = controller.get_reviews()
    
    # Pass data to template
    return render_template('reviews.html', **reviews_data)
