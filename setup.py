import logging
import os.path
import subprocess
from setuptools import Command, setup


class RenderSVGsCommand(Command):
    user_options = []

    def initialize_options(self):
        self.img_path = 'donormotor/static/img'
        self.sources = [
            ('logo.svg', 200, 85)
        ]

    def finalize_options(self):
        pass

    def run(self):
        """Render the SVGs into PNGs."""
        for source in self.sources:
            self.announce(
                "Rendering SVG: {0}".format(source[0]),
                level=logging.INFO)
            for zoom in (1, 2):
                outname = source[0].replace('.svg', '-{0:d}x.png'.format(zoom))
                subprocess.check_call([
                    'rsvg-convert',
                    '-w', str(source[1] * zoom),
                    '-h', str(source[2] * zoom),
                    '-o', os.path.join(self.img_path, outname),
                    os.path.join(self.img_path, source[0]),
                ])
                subprocess.check_call([
                    'optipng', '-quiet', '-nb', '-nc', '-np',
                    os.path.join(self.img_path, outname),
                ])


setup(
    name="donormotor",
    py_modules=["donormotor"],
    description="Next generation donation manager for WUVT-FM",
    license="AGPL3",
    author="donormotor authors",
    keywords="donormotor wuvt",
    url="https://github.com/wuvt/donormotor",
    install_requires=[
        "Authlib",
        "boto3",
        "cachelib",
        "click",
        "email-validator",
        "Flask",
        "Flask-Migrate",
        "Flask-SQLAlchemy",
        "Flask-WTF",
        "google-api-python-client",
        "google-auth",
        "humanize",
        "loginpass",
        "passlib",
        "psycopg",
        "PyMySQL",
        "python-dateutil",
        "redis",
        "requests",
        "sentry-sdk[flask]",
        "SQLAlchemy",
        "stripe",
        "Unidecode",
    ],
    cmdclass={
        "render_svgs": RenderSVGsCommand,
    }
)
