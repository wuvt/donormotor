import distutils.cmd
import distutils.log
import os.path
import subprocess
from setuptools import setup


class RenderSVGsCommand(distutils.cmd.Command):
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
                level=distutils.log.INFO)
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
        "bleach",
        "celery",
        "click",
        "Flask",
        "Flask-Migrate",
        "Flask-RESTful",
        "Flask-SQLAlchemy",
        "Flask-WTF",
        "humanize",
        "Markdown",
        "musicbrainzngs",
        "netaddr",
        "passlib",
        "psycopg2",
        "pyasn1",
        "pyasn1-modules",
        "PyMySQL",
        "python-dateutil",
        "python-editor",
        "python-redis-lock",
        "pytz",
        "redis",
        "requests",
        "SQLAlchemy-Utils",
        "stripe",
        "Unidecode",
    ],
    dependency_links=[
        "git+https://github.com/wuvt/python-musicbrainzngs#egg=musicbrainzngs",
    ],
    cmdclass={
        "render_svgs": RenderSVGsCommand,
    }
)
