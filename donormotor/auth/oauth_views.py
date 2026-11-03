from authlib.integrations.flask_client import OAuthError
from flask import Blueprint, current_app, url_for
from joserfc.errors import JoseError


def create_oauth_blueprint(name, oauth, handle_authorize):
    """Create a blueprint with /login and /auth routes for the named OAuth
    client. This replaces loginpass, keeping its URLs so that redirect URIs
    registered with identity providers continue to work."""
    remote = oauth.create_client(name)
    bp = Blueprint('auth_' + name, __name__)

    @bp.route('/auth')
    def auth():
        try:
            token = remote.authorize_access_token()
        except (OAuthError, JoseError) as exc:
            current_app.logger.warning(
                "donormotor: {0} authorization failed: {1}".format(name, exc))
            return handle_authorize(remote, None, None)

        return handle_authorize(remote, token, token.get('userinfo'))

    @bp.route('/login')
    def login():
        redirect_uri = url_for('.auth', _external=True)
        return remote.authorize_redirect(redirect_uri)

    return bp
