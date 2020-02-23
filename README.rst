==========
yamlreader
==========
Merge YAML data from a directory, a list of files or a file glob. With a
directory, the YAML files (`*.yaml`) are sorted alphabetically. The YAML
files are expected to contain a complex key-value structure and merged
with the following rules:

* lists get appended
* hashes get merged by key
* scalars (numbers, strings) are overwritten
* everything else will fail

The purpose is to allow several YAML files instead of a single YAML file. We
use it to help our software read configuration data from an arbitrary amount
of YAML files instead of a single YAML file.

Running
=======
The package installs a command line script ``yamlreader`` that can be used to
read one or many YAML files and dump the merge result as a YAML document.

Use it in your software
=======================
Wherever you had been using the ``safe_load`` function of
`PyYAML <http://pyyaml.org/>`_ to read a single YAML file you can use
the ``yamlreader.yaml_load`` function as a replacement to read all ``*.yaml``
files in a directory::

    from yamlreader import yaml_load

    defaultconfig = {
            "loglevel" : "error",
            "some" : "value"
    }

    config = yaml_load("/etc/myapp", defaultconfig)

yaml_load
---------
::

    def yaml_load(source,defaultdata=None):
        """merge YAML data from files found in source

        Always returns a dict. The YAML files are expected to contain some kind of
        key:value structures, possibly deeply nested. When merging, lists are
        appended and dict keys are replaced. The YAML files are read with the
        yaml.safe_load function.

        source can be a file, a dir, a list/tuple of files or a string containing
        a glob expression (with ?*[]).

        For a dir all *.yaml files will be read in alphabetical order.

        defaultdata can be used to initialize the data.
        """
