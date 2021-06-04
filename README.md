# DonorMotor

This is a stub repository for WUVT's donation management platform, to be spun out of
[wuvt/wuvt-site](https://github.com/wuvt/wuvt-site).

Goals are to:

1. Provide more advanced donor tracking and handling
2. Provide better configurability of premiums
3. Better integrate with Stripe API

Further, this should provide an approachable framework for other stations looking to
adopt a simple donation platform (as AudienceEngine has never materialised), without
dragging in the relative bloat of wuvt-site (this is the same reason we spun out
trackman).

## TODO:

- Prune non-donation code from wuvt-site to populate this repo

## About the Name

DonorMotor is a pun off of [AudienceEngine](https://en.wikipedia.org/wiki/The_Audience_Engine),
WFMU's vaporware donation management platform. It has a nice ring to it, and doesn't rely on
thermodynamics.

### Deployment
These instructions are for Linux; instructions for other platforms may vary.

First, clone the repo, create an empty config, and build the appropriate Docker
image for your environment. We provide Dockerfile.dev which is configured to
use SQLite and runs Redis directly in the image, and Dockerfile, which is
recommended for production deployments as it does not run any of the required
services inside the container itself.

For Dockerfile.dev:
```
git clone https://github.com/wuvt/donormotor.git
cd donormotor
docker build -t donormotor -f Dockerfile.dev .
```

Now, go ahead and copy config/config_example.json to config/config.json and
configure as necessary. The most important thing is to set a random value for
`SECRET_KEY`. You can generate a random value using the following command:
```
xxd -l 28 -p /dev/urandom
```

Finally, run it:
```
docker run --rm -v $PWD/config:/data/config -e APP_CONFIG_PATH=/data/config/config.json -p 9070:8080 wuvt-site:latest
```

You can now access the site at <http://localhost:9070/>. An admin user account
will be created for you; the password is automatically generated and displayed
when you launch the container.

### License

Besides the exceptions noted below, the entirety of this software is available
under the GNU Affero General Public License:

```
Copyright 2021 Eric C. Landgraf, James Schwinabart

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
```
The following files are JavaScript libraries and CSS files, freely available
under the MIT license as noted in their headers:

- donormotor/static/js/jquery.js
- donormotor/static/js/jquery.dataTables.min.js
- donormotor/static/js/moment.min.js
- donormotor/static/bootstrap/*
