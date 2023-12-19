Nomenclature
============

This library defines multiple new classes to deal with input and output data from the various SED fitting codes. The main classes the user needs to know are listed below:

+--------------------------+-----------------------------------------------------------------------------------------------------------------------+
| Class/term               | Description                                                                                                           |
+==========================+=======================================================================================================================+
| :py:class:`~.Catalogue`  | An intermediate object which contains preprocessed data to generate the SED fitting code configuration and data files |
+--------------------------+-----------------------------------------------------------------------------------------------------------------------+
| :py:class:`~.Filter`     | Object which stores data and variance map information relative to a **single** filter                                 |
+--------------------------+-----------------------------------------------------------------------------------------------------------------------+
| :py:class:`~.FilterList` | Object which stores all the :py:class:`~.Filter` objects into a single one                                            |
+--------------------------+-----------------------------------------------------------------------------------------------------------------------+
| :py:class:`~.Output`     | Abstract object which can read output data from the SED fitting codes and produce resolved maps                       |
+--------------------------+-----------------------------------------------------------------------------------------------------------------------+
| :py:class:`~.SED`        | Abstract object which includes methods to run the SED fitting code and read its output data                           |
+--------------------------+-----------------------------------------------------------------------------------------------------------------------+
