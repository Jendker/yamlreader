__version__ = '3.0.5'

from ruamel.yaml import safe_load_all, safe_dump
from ruamel.yaml.error import MarkedYAMLError
import sys

import glob
import os
import logging


class NoDefault(object):
    def __str__(self):
        return "No default data"


NO_DEFAULT = NoDefault()


class YamlReaderError(Exception):
    pass


def data_merge(a, b, overwrite_lists=True):
    """merges b into a and return merged result
    based on http://stackoverflow.com/questions/7204805/python-dictionaries-of-dictionaries-merge
    and extended to also merge arrays and to replace the content of keys with the same name

    NOTE: tuples and arbitrary objects are not handled as it is totally ambiguous what should happen"""
    key = None
    # ## debug output
    # sys.stderr.write("DEBUG: %s to %s\n" %(b,a))
    try:
        if overwrite_lists:
            is_instance = isinstance(a, (str, float, int, list))
        else:
            is_instance = isinstance(a, (str, float, int))
        if a is None or is_instance:
            # border case for first run or if a is a primitive
            a = b
        elif isinstance(a, list):
            # lists can be only appended
            if isinstance(b, list):
                # merge lists
                a.extend(b)
            else:
                # append to list
                a.append(b)
        elif isinstance(a, dict):
            # dicts must be merged
            if isinstance(b, dict):
                for key in b:
                    if key in a:
                        a[key] = data_merge(a[key], b[key])
                    else:
                        a[key] = b[key]
            else:
                raise YamlReaderError('Cannot merge non-dict "%s" into dict "%s"' % (b, a))
        else:
            raise YamlReaderError('NOT IMPLEMENTED "%s" into "%s"' % (b, a))
    except TypeError as e:
        raise YamlReaderError('TypeError "%s" in key "%s" when merging "%s" into "%s"' % (e, key, b, a))
    return a


def yaml_load(source=None, default_data=NO_DEFAULT, default_path=None):
    """merge YAML data from files found in source

    Always returns a dict. The YAML files are expected to contain some kind of
    key:value structures, possibly deeply nested. When merging, lists are
    appended and dict keys are replaced. The YAML files are read with the
    yaml.safe_load_all function.

    source can be a file, a dir, a list/tuple of files or a string containing
    a glob expression (with ?*[]).

    For a directory, all *.yaml files will be read in alphabetical order.

    `default_data` can be used to initialize the data.
    `default_path` load the data from it first and afterwards it will be extended/overwritten by data from `source`.
    """
    logger = logging.getLogger(__name__)
    logger.debug("initialized with source=%s, default_data=%s, default_path=%s", source, default_data, default_path)
    if default_data is NO_DEFAULT:
        data = None
    else:
        data = default_data
    if default_path is not None:
        data = data_merge(data, yaml_load(default_path))
    if source is None:
        return data
    if type(source) is not str and len(source) == 1:
        # when called from __main source is always a list, even if it contains only one item.
        # turn into a string if it contains only one item to support our different call modes
        source = source[0]
    if type(source) is list or type(source) is tuple:
        # got a list, assume to be files
        files = source
    elif os.path.isdir(source):
        # got a dir, read all *.yaml files
        files = sorted(glob.glob(os.path.join(source, "*.yaml")))
    elif os.path.isfile(source):
        # got a single file, turn it into list to use the same code
        files = [source]
    else:
        # try to use the source as a glob
        files = sorted(glob.glob(source))
    if files:
        logger.debug("Reading %s\n", ", ".join(files))
        for yaml_file in files:
            try:
                with open(yaml_file) as f:
                    new_data = safe_load_all(f)
                    for doc in new_data:
                        data = data_merge(data, doc)
                logger.debug("YAML LOAD: %s", new_data)
            except MarkedYAMLError as e:
                logger.error("YAML Error: %s", e)
                raise YamlReaderError("YAML Error: %s" % str(e))
    else:
        if default_data is NO_DEFAULT:
            logger.error("No YAML data found in %s and no default data given", source)
            raise YamlReaderError("No YAML data found in %s" % source)

    return data


def __main():
    import optparse
    parser = optparse.OptionParser(usage="%prog [options] source...",
                                   description="Merge YAML data from given files, dir or file glob",
                                   version="%" + "prog %s" % __version__,
                                   prog="yamlreader")
    parser.add_option("--debug", dest="debug", action="store_true", default=False,
                      help="Enable debug logging [%default]")
    options, args = parser.parse_args()
    if options.debug:
        logger = logging.getLogger()
        loghandler = logging.StreamHandler()
        loghandler.setFormatter(logging.Formatter('yamlreader: %(levelname)s: %(message)s'))
        logger.addHandler(loghandler)
        logger.setLevel(logging.DEBUG)

    if not args:
        parser.error("Need at least one argument")
    try:
        safe_dump(yaml_load(args, default_data={}), sys.stdout)
    except Exception as e:
        parser.error(e)

if __name__ == "__main__":
    __main()
