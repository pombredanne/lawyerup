=============================
LawyerUp
=============================

LawyerUp adds license headers to your code.

Inspired by lice_.

.. _lice: https://github.com/licenses/lice

Installation
------------

::

  pip install lawyerup


Usage
-----

::

  $ lawyerup --help
  usage: lawyerup [-h] [--vars | --context [KEY=VALUE [KEY=VALUE ...]]] LICENSE

  Add license headers to files passed in on stdin

  positional arguments:
    LICENSE               the license to add, one of GPR, GRR, generic

  optional arguments:
    -h, --help            show this help message and exit
    --vars                list template variables for specified license
    --context [KEY=VALUE [KEY=VALUE ...]]
                          KEY=VALUE formatted variables to generate the license


::

  $ cat list-of-files | lawyerup <license> --context KEY1=VAL1 KEY2=VAL2 ...


Available Licenses
------------------

* Government Purpose Rights (``GPR``)
* Government Restricted Rights (``GRR``)
* Generic "see COPYING file in the root of this distribution" (``generic``)
