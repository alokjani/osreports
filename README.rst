osreports: OpenStack tenant utilization reporter
================================================

Introduction
------------

`osreports` is a python utility for OpenStack Clouds that can provide
reporting for resource utilization, per tenant usage etc.

`osreports` is useful in cloud management activities like capacity planning.
It can also be useful to generate simplified MIS style reports in low variance
clouds esp. in the absence of Ceilometer.


Installation
------------

1. To get the last official release

.. sourcecode:: console
   
   $ sudo pip install osreports

or alternatively

.. sourcecode:: console

    $ sudo pip install -e git+https://github.com/alokjani/osreports.git#egg=osreports


Development
-----------

## Setup 

To Install into virtual environment

.. sourcecode:: console

    $ git clone https://github.com/alokjani/osreports.git
    $ cd osreports/
    $ virtualenv .venv
    $ . .venv/bin/activate
    $ pip install -r requirements.txt

              
## Build documentation

TODO

## Contributing

- License: Apache License, Version 2.0
- [Source] (https://github.com/alokjani/osreports)
- [Bugs] (https://github.com/alokjani/osreports/issues) - Issue tracking

## Testing

TODO
