Data
====


This section outlines procedures for how to go about doing the quality control, the processing and the generation of data products.

Data Products
-------------

``pydropsonde`` splits the processing into several steps resulting in four data products.
Below, the processing and (intermediate) data products are described in short in tabular form with links to detailed subpages.

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Data Product
     - Data Files
     - Description
   * - :doc:`Level_0 <level0>`
     - One file per sonde
     - Raw files from the AVAPS software (A-files, D-files, ...)
   * - :doc:`Level_1 <level1>`
     - One file per sonde
     - ASPEN-processed netCDF files including a first QC
   * - :doc:`Level_2 <level2>`
     - One file per sonde
     - Sonde profiles that passed additional QC tests
   * - :doc:`Level_3 <level3>`
     - one single file
     - One dataset (file) containing all Level_2 soundings gridded on a uniform vertical grid and including some derived variables
   * - Level_4
     - one single file
     - Circle products from all circles flown during a measurement sequence, e.g. divergence


.. _data_directory_structure:

Data Directory Structure
------------------------

Before processing you need to store your dropsonde profile data in a coherent way and communicate that to the processing software via the config file.
Most commonly, a sonde profile is associated with a ``platform`` from which it was dropped and a ``flight_id`` from the respective measurement flight.
The AVAPS software is a standard tool for conducting dropsonde measurements in atmospheric science and the ``pydropsonde`` package builds on the AVAPS generated raw files (Level_0) and the ASPEN software designed by NCAR for applying a first quality control and changing the file format (Level_1). The resultign Data Levels are described in detail below.

We suggest you to use as a default directory structure which fits the default output of the AVAPS and ASPEN software.
At the end of a research flight with dropsonde measurements the AVAPS software saves individual sonde profile data in single files and adds several metadata files related to the whole flight.
A possible data directory structure would therefore be:

.. code-block:: ini

        platform
            |__ Level_0
                |__ flight_id1
                    |__ raw files
                |__ flight_id2
                    |__ raw files

This is the assumed default structure and translates into the following statement to be made in the config file:

.. code-block:: ini

        [OPTIONAL]
        path_to_flight_ids = {platform}/Level_0
        path_to_l0_files = {platform}/Level_0/{flight_id}

However, you are free in defining your favourite data strucutre that fits your use case and you could likewise save the data in another structure, e.g.


.. code-block:: ini

        flight_id1
            |__ Level_0
                    |__ raw files
        flight_id2
            |__ Level_0
                    |__ raw files

with the respective config file entry:

.. code-block:: ini

        [OPTIONAL]
        path_to_flight_ids = ./
        path_to_l0_files = {flight_id}/Level_0

.. toctree::
    :caption: Level Description
In the course of the processing further data products or levels will be added at the respective places.
In the first case Level_1 files would be saved to a single folder at ``platform / Level_1 / {flight_id} / netCDF files``.
In the second case many Level_1 folders would be created following the pattern ``{flight_id} / Level_1 / netCDF files``.

    level2
    level3
Level_2 works similar to Level_1 concerning the data directory structure.
Up to this processing level each sonde profile is saved in a separate file.
Level_3 on the other side is different in the sense that all profile data is vertically interpolated (see details above) and saved to a single file in the top directory specified in the mandatory section of the config file.
Level_4 is likewise a single file stored next to Level_3.
