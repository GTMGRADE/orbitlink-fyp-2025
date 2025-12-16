# For now, this entity is minimal since we're serving static content
# Can be expanded later for dynamic content management

class LandingContent:
    @staticmethod
    def get_static_content():
        """Returns static content for the landing page"""
        return {
            'about_us': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
            'contact_email': 'support@analyticsplatform.com',
            'current_year': '2024'
        }