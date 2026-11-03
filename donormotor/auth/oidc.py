from flask import abort, current_app, json
from donormotor.auth.user import _find_or_create_user
from donormotor.auth.utils import login_user, get_user_roles
from donormotor.auth.view_utils import log_auth_success, log_auth_failure, \
        redirect_back


def register_oidc(oauth, name, client_secrets_file=None, scopes=None):
    client_secrets = {}
    with open(client_secrets_file) as f:
        client_secrets = json.load(f)

    if scopes is None:
        scopes = ['openid', 'profile', 'email']

    issuer_url = client_secrets['web']['issuer']

    # The issuer's discovery document supplies the JWKS used to verify ID
    # tokens and the expected issuer; the endpoints in client_secrets take
    # precedence over the discovered ones.
    oauth.register(
        name,
        client_id=client_secrets['web']['client_id'],
        client_secret=client_secrets['web']['client_secret'],
        access_token_url=client_secrets['web']['token_uri'],
        authorize_url=client_secrets['web']['auth_uri'],
        server_metadata_url='{0}/.well-known/openid-configuration'.format(
            issuer_url.rstrip('/')),
        client_kwargs={'scope': ' '.join(scopes)})


def handle_authorize(remote, token, user_info):
    if user_info is None:
        log_auth_failure("oidc", None)
        abort(401)

    user = _find_or_create_user(
        user_info['sub'], user_info['name'], user_info['email'])
    user_groups = user_info.get(
        current_app.config.get('OIDC_GROUPS_CLAIM', 'groups'))
    login_user(user, get_user_roles(user, user_groups))

    log_auth_success("oidc", user_info['sub'])

    return redirect_back('admin.index')
