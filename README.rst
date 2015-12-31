OpenStack Utilization and Capacity Reporter
===========================================

`osreports` is an operators' tool, with the aim to simplify capacity planning
for OpenStack Clouds.

`osreports` generates simplified utilization reports on per tenant basis, that
helps is identifying utilization patterns per tenant. Using this a cloud
provider can make effective data-driven decisions for the future.

`osreports` is useful in enterprise clouds, especially in the absence of proper
metering/billing solutions.

Installation
============

To get the last official release

.. sourcecode:: console
   
   $ pip install osreports

For the latest version 

.. sourcecode:: console

    $ pip install -e git+https://github.com/alokjani/osreports.git#egg=osreports


Development
===========

To setup a dev/test environment 

.. sourcecode:: console

    $ git clone https://github.com/alokjani/osreports.git
    $ cd osreports/
    $ virtualenv .venv
    $ . .venv/bin/activate
    $ pip install -r requirements.txt


- `Source Code`_ : Github for submitting patches
- Bugs_ : Launchpad for Issue tracking
- Build documentation & Testing : Coming Soon 
- License : Apache License, Version 2.0

.. _Source Code: https://github.com/alokjani/osreports
.. _Bugs: https://bugs.launchpad.net/osreports



Author
======

- Alok Jani


