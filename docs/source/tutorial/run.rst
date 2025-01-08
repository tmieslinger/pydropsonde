Running pydropsonde
===================

To run ``pydropsonde`` on a set of sonde profiles, you first need to create a respective configuration file (see :doc:`Config Files <configs>`).
Further, you can provide the path to the config file through the ``-c`` option.
By default, ``pydropsonde`` would search for `dropsonde.cfg` in the current directory.

.. code-block:: bash

        pydropsonde -c <path_to_config_file>

Notes on processing to Level_1
______________________________

The processing from Level_0 to Level_1 (using `aspen <https://www.eol.ucar.edu/content/aspen>`_) is included in ``pydropsonde``.
It makes use of a docker image containing the ASPEN software.
Before actually calling pydropsonde, you therefore need to install `docker <https://www.docker.com/>`_ and start a docker daemon (dockerd) locally to be able to use the ASPEN docker image.
The simplest way would be to install Docker Desktop (on MacOS also possible via ``brew install --cask docker``) and open the application before executing pydropsonde.
Further information can be found in the respective `aspenqc <https://github.com/atmdrops/aspenqc>`_ repository.

Alternatively, you can use the GUI provided by ASPEN to process Level_0 to Level_1. ``pydropsonde`` won't reprocess Level_1 if the respective files are already available.
