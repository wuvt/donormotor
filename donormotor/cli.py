import click
import os
import random
import string
from donormotor import app, db
from donormotor.auth.models import User
import donormotor.donate.models


@app.cli.command()
def init_embedded_db():
    """Initialize and seed the embedded database with sample data."""

    # The SQLALCHEMY_DATABASE_URI config option will match the corresponding
    # environment variable when we are using the embedded database.
    #if app.config['SQLALCHEMY_DATABASE_URI'] != \
    #        os.getenv('SQLALCHEMY_DATABASE_URI'):
    #    return

    click.echo("Initialize the database...")

    # Generate a random password for the admin user
    password = ''.join(random.SystemRandom().sample(
        string.ascii_letters + string.digits, 12))
    click.echo('Password for admin will be set to: {0}'.format(password))
    username="admin"

    db.create_all()
    user = User(str(username), str(username),
                "{0}@localhost".format(username))
    user.set_password(str(password))
    db.session.add(user)
    db.session.commit()

    click.echo("Database initialized.")


@app.cli.command()
@click.option('--username', default="admin")
@click.password_option()
def initdb(username, password):
    """Initialize the database."""
    click.echo("Initialize the database...")
    db.create_all()
    user = User(str(username), str(username),
                "{0}@localhost".format(username))
    user.set_password(str(password))
    db.session.add(user)
    db.session.commit()
    click.echo("Database initialized.")

