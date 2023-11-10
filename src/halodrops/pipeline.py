from .helper.paths import Paths
from .sonde import Sonde
import configparser
import inspect


def get_mandatory_args(function):
    """
    Get a list of all arguments that do not have a default value for each function in the list.

    Parameters
    ----------
    list_of_functions : list
        A list of functions to inspect.

    Returns
    -------
    list
        A list of argument names that do not have a default value.

    Examples
    --------
    >>> def func1(a, b=2):
    ...     pass
    >>> def func2(c, d=4, e=5):
    ...     pass
    >>> mandatory_args([func1, func2])
    ['a', 'c']
    """
    mandatory_args = []
    sig = inspect.signature(function)
    for name, param in sig.parameters.items():
        if param.default == inspect.Parameter.empty and name != "self":
            mandatory_args.append(name)
    return mandatory_args


def get_mandatory_values_from_config(config, mandatory_args):
    """
    Extracts mandatory values from the 'MANDATORY' section of a configuration file.

    Parameters
    ----------
    config : ConfigParser
        The configuration file parser.
    mandatory_args : list
        A list of argument names that are expected to be in the 'MANDATORY' section of the config file.

    Returns
    -------
    dict
        A dictionary where the keys are the argument names and the values are the corresponding values from the config file.

    Raises
    ------
    ValueError
        If the 'MANDATORY' section is not found in the config file or if a mandatory argument is not found in the 'MANDATORY' section.

    Examples
    --------
    >>> import configparser
    >>> config = configparser.ConfigParser()
    >>> config.read_string('[MANDATORY]\\narg1=value1\\narg2=value2')
    >>> mandatory_values_from_config(config, ['arg1', 'arg2'])
    {'arg1': 'value1', 'arg2': 'value2'}
    """
    if not config.has_section("MANDATORY"):
        raise ValueError(f"MANDATORY section not found in config file")
    else:
        mandatory_dict = {}
        for arg in mandatory_args:
            if config.has_option("MANDATORY", arg):
                mandatory_dict[arg] = config.get("MANDATORY", arg)
            else:
                raise ValueError(f"Mandatory argument {arg} not found in config file")
    return mandatory_dict


def get_nondefaults_from_config(
    config: configparser.ConfigParser, obj: callable
) -> dict:
    """
    Get the non-default arguments for a given function from a ConfigParser object.

    Parameters
    ----------
    config : configparser.ConfigParser
        A ConfigParser object containing configuration settings.
    obj : callable
        The function for which to get the non-default arguments.

    Returns
    -------
    dict
        A dictionary of non-default arguments for the function.
    """

    section_name = f"{obj.__module__}.{obj.__qualname__}".split("halodrops.")[1]

    if section_name in config.sections():
        nondefault_args = config[section_name]
    else:
        nondefault_args = {}
    return nondefault_args


def get_args_for_function(config, function):
    """
    Get the arguments for a given function.

    This function first checks if the qualified name of the function exists in the nondefaults dictionary.
    If it does, it uses the corresponding value as the arguments for the function.
    Otherwise, it initializes an empty dictionary as the arguments.

    Then, it gets the list of mandatory arguments for the function.
    If there are any mandatory arguments, it gets their values from the config and updates the arguments dictionary with them.

    Parameters
    ----------
    function : function
        The function for which to get the arguments.
    nondefaults : dict
        A dictionary mapping function qualified names to dictionaries of arguments.

    Returns
    -------
    dict
        A dictionary of arguments for the function.
    """
    args = get_nondefaults_from_config(config, function)
    mandatory = get_mandatory_args(function)
    if mandatory:
        mandatory_args = get_mandatory_values_from_config(config, mandatory)
        args.update(mandatory_args)

    return args


def create_and_populate_Paths_object(config: configparser.ConfigParser) -> Paths:
    """
    Creates a Paths object and populates it with A-files.

    Parameters
    ----------
    config : configparser.ConfigParser
        A ConfigParser object containing configuration settings.

    Returns
    -------
    Paths
        A Paths object.
    """
    output = {}
    mandatory = get_mandatory_args(Paths)
    mandatory_args = get_mandatory_values_from_config(config, mandatory)
    output["paths"] = Paths(**mandatory_args)
    output["sondes"] = output["paths"].populate_sonde_instances()
    return output["paths"], output["sondes"]


def iterate_Sonde_method_over_dict_of_Sondes_objects(
    obj: dict, functions: list, config: configparser.ConfigParser
) -> dict:
    """
    Iterates over a dictionary of Sonde objects and applies a list of methods to each Sonde.

    For each Sonde object in the dictionary, this function applies each method listed in the 'functions' key of the substep dictionary.
    The arguments for each method are determined by the `get_args_for_function` function, which uses the nondefaults dictionary and the config object.

    Parameters
    ----------
    obj : dict
        A dictionary of Sonde objects.
    functions : list
        a list of method names.
    nondefaults : dict
        A dictionary mapping function qualified names to dictionaries of arguments.
    config : configparser.ConfigParser
        A ConfigParser object containing configuration settings.

    Returns
    -------
    dict
        The original dictionary of Sonde objects, but with each Sonde modified by the applied methods.
    """
    my_dict = obj
    new_dict = {}

    for function_name in functions:
        for key, value in my_dict.items():
            function = getattr(Sonde, function_name)
            new_dict[key] = function(value, **get_args_for_function(config, function))
        my_dict = new_dict

    return my_dict


def run_substep(
    previous_substep_output, substep: dict, config: configparser.ConfigParser
):
    """
    This function applies a specified function to the input data and stores the output for use in subsequent steps.

    Parameters
    ----------
    previous_substep_output : dict
        A dictionary storing the output data from previous steps. The input data for this step is retrieved from this dictionary using the key specified in substep['intake'], and the output of this step is stored in this dictionary under the key(s) specified in substep['output'].
    substep : dict
        A dictionary containing information about the current processing step. It should have the following keys:
        - 'apply': a function to apply to the input data.
        - 'intake': the key in the previous_substep_output dictionary that corresponds to the input data for this step.
        - 'output': the key(s) under which to store the output of this step in the previous_substep_output dictionary. If this is a list, the function should return a list of outputs of the same length.
        - 'functions' (optional): a list of functions to apply to the input data. If this key is present, the 'apply' function should take this list as an additional argument.
    config : object
        A configuration object used by the function.

    Returns
    -------
    dict
        The updated dictionary with the output data from the current step. The output data is stored under the key(s) specified in substep['output'].

    Notes
    -----
    This function assumes that the 'apply' function returns a list of outputs if substep['output'] is a list, and a single output otherwise. If substep['output'] is a list but the 'apply' function does not return a list of outputs, or if the lengths of the two lists do not match, this function will raise an exception.
    """
    function = substep["apply"]
    intake = substep["intake"]
    if "functions" not in substep:
        if intake is None:
            previous_substep_output = {}
            output = function(config)
        else:
            output = function(previous_substep_output[intake], config)
    else:
        output = function(previous_substep_output[intake], substep["functions"], config)

    if isinstance(substep["output"], list):
        for i, key in enumerate(substep["output"]):
            previous_substep_output[key] = output[i]
    else:
        previous_substep_output[substep["output"]] = output

    return previous_substep_output


def run_pipeline(pipeline: dict, config: configparser.ConfigParser):
    """
    Executes a pipeline of processing steps.

    Parameters:
    ----------
    pipeline : dict
        A dictionary representing the pipeline
        where each key is a substep and the value is a dictionary with the configurations of that substep.
    config : configparser.ConfigParser
        Configuration settings for the package.

    Returns:
    ----------
    dict:
        The output of the last substep in the pipeline.
    """
    previous_substep_output = None
    for step in pipeline:
        print(f"Running {step}...")
        substep = pipeline[step]
        if previous_substep_output is None:
            previous_substep_output = run_substep(None, substep, config)
        else:
            previous_substep_output = run_substep(
                previous_substep_output, substep, config
            )
    return previous_substep_output


pipeline = {
    "create_paths": {
        "intake": None,
        "apply": create_and_populate_Paths_object,
        "output": ["paths", "sondes"],
    },
    "qc": {
        "intake": "sondes",
        "apply": iterate_Sonde_method_over_dict_of_Sondes_objects,
        "functions": ["add_postaspenfile", "add_aspen_ds"],
        "output": "sondes",
    },
}
