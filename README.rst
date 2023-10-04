===========================================
sphinxcontrib-versioning for PyTorch-Ignite
===========================================

Sphinx extension that allows building versioned docs for PyTorch-Ignite.

Install:

.. code:: bash

    pip install git+https://github.com/pytorch-ignite/sphinxcontrib-versioning.git

Usage:

.. code:: bash

    sphinx-versioning --use-master-conf --use-master-templates build --greatest-tag --whitelist-branches master docs/source docs/build/html
