import googleapiclient.discovery
from flask import abort, current_app
from google.oauth2 import service_account
from donormotor.auth.user import _find_or_create_user
from donormotor.auth.utils import login_user, get_user_roles
from donormotor.auth.view_utils import log_auth_success, log_auth_failure, \
        redirect_back

GOOGLE_METADATA_URL = \
    'https://accounts.google.com/.well-known/openid-configuration'


def register_google(oauth):
    # client_id, client_secret, and any authorize_url/authorize_params
    # overrides are read from the GOOGLE_* app config keys by Authlib
    oauth.register(
        'google',
        api_base_url='https://www.googleapis.com/',
        server_metadata_url=GOOGLE_METADATA_URL,
        client_kwargs={'scope': 'openid email profile'})


def get_groups(user_info):
    credentials = service_account.Credentials.from_service_account_file(
        current_app.config['GOOGLE_SERVICE_ACCOUNT_FILE'],
        scopes=['https://www.googleapis.com/auth/admin.directory.group.'
                'readonly'],
        subject=current_app.config['GOOGLE_ADMIN_SUBJECT'])

    dirapi = googleapiclient.discovery.build('admin', 'directory_v1',
                                             credentials=credentials)
    groups = dirapi.groups().list(userKey=user_info['email']).execute()

    return [g['email'] for g in groups['groups']]


def handle_authorize(remote, token, user_info):
    if user_info is None:
        log_auth_failure("google", None)
        abort(401)

    if len(current_app.config['GOOGLE_ALLOWED_DOMAINS']) > 0 \
            and not user_info.get('hd') in \
            current_app.config['GOOGLE_ALLOWED_DOMAINS']:
        log_auth_failure("google", user_info['sub'])
        abort(401)

    user = _find_or_create_user(
        user_info['sub'], user_info['name'], user_info['email'])
    user_groups = get_groups(user_info)
    login_user(user, get_user_roles(user, user_groups))

    log_auth_success("google", user_info['sub'])

    return redirect_back('admin.index')
