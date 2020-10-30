recognized_datasets = ["FAFB", "HEMIBRAIN"]
recognized_platforms = ["CATMAID", "NEUPRINT", "FLYWIRE", None]

def get_neurotransmitter_predictions(skids, presynaptic_locations, platform, dset):
    presynaptic_locations = get_presynaptic_locations(skids, presynaptic_locations, platform, dset)
    predictions = get_neurotransmitter_predictions_from_locations(presynaptic_locations, dset)
    return predictions

def get_neurotransmitter_predictions_from_locations(presynaptic_locations, dset):
    dset_path = get_dset_path(dset)
    predictions = [{"id": 0, "x": 0, "y": 1, "z": 2, "prediction": {"0": 0.1, "1": 0.9}}]
    return predictions

def get_presynaptic_locations(skids, presynaptic_locations, platform, dset):
    """
    skids: list of ints
    presynaptic_locations: list of tuple of ints (x,y,z)
    platform: string
    dset: string

    returns: a list of locations in the given dset
    """
    if not isinstance(skids, list):
        raise TypeError("skids must be list type")
    if not isinstance(presynaptic_locations, list):
        raise TypeError("presynaptic locations must be list type")
    if not isinstance(platform, str):
        raise TypeError("platform must be string type")
    if not isinstance(dset, str):
        raise TypeError("dset must be string type")

    skids = list(skids)
    presynaptic_locations = list(presynaptic_locations)

    get_presynaptic_locations_from_skid, transform_location = get_dset_platform_functions(dset, platform)
    
    if skids:
        for skid in skids:
            presynaptic_locations += get_presynaptic_locations_from_skid(skid)

    presynaptic_locations = [transform_location(*loc) for loc in presynaptic_locations]

    return presynaptic_locations

def get_dset_platform_functions(dset, platform):
    """
    Returns the pair (a,b) where a is a function 
    to query presynaptic locations from skid 
    from the given (platform, dset) tuple and
    b is a transformation of platform location 
    """
    if platform is None:
        # Coordinates given in dataset space - no queries available, np transform required.
        platform = dset

    function_dict = register_dset_platform_functions()
    try:
        return function_dict[(dset, platform)]
    except KeyError:
        raise ValueError(f"Combination of platform {platform} and dataset {dset} not understood")

def register_dset_platform_functions():
    function_dict = {("FAFB", "CATMAID"): (get_fafb_catmaid_presynaptic_locations_from_skid, transform_fafb_catmaid_location),
                     ("FAFB", "FLYWIRE"): (get_fafb_flywire_presynaptic_locations_from_skid, transform_fafb_flywire_location),
                     ("HEMI", "NEUPRINT"): (get_hemi_neuprint_presynaptic_locations_from_skid, transform_hemi_neuprint_location),
                     ("FAFB", "FAFB"): (get_fafb_fafb_presynaptic_locations_from_skid, transform_fafb_fafb_location),
                     ("HEMI", "HEMI"): (get_hemi_hemi_presynaptic_locations_from_skid, transform_hemi_hemi_location)}

    return function_dict

def get_dset_path(dset):
    return 0

def get_fafb_catmaid_presynaptic_locations_from_skid(skid):
    """
    Returns a list [(x,y,z), ...] of catmaid locations for the given skid.
    """
    return [(0,1,2), (3,4,5)]

def get_fafb_flywire_presynaptic_locations_from_skid(skid):
    """
    Returns a list [(x,y,z), ...] of flywire locations for the given skid,
    """
    return [(0,1,2), (3,4,5)]

def get_hemi_neuprint_presynaptic_locations_from_skid(skid):
    """
    Returns a list [(x,y,z), ...] of neuprint locations for the given skid.
    """
    return [(0,1,2), (3,4,5)]

def get_fafb_fafb_presynaptic_locations_from_skid(skid):
    raise ValueError("Cannot query from skid without platform")

def get_hemi_hemi_presynaptic_locations_from_skid(skid):
    raise ValueError("Cannot query from skid without platform")

def transform_fafb_catmaid_location(x, y, z):
    """
    Transforms catmaid coordinates to fafb_v14 space
    """
    return (x,y,z)

def transform_hemi_neuprint_location(x, y, z):
    """
    Transforms neuprint coordinates to n5 hemi space
    """
    return (x,y,z)

def transform_fafb_flywire_location(x, y, z):
    """
    Transforms fly wire coordinates to fafb_v14 space.
    """
    return (x,y,z)

def transform_fafb_fafb_location(x,y,z):
    """
    Identity function if using FAFB space directly.
    """
    return (x,y,z)

def transform_hemi_hemi_location(x,y,z):
    """
    Identity function if using hemibrain space directly
    """
    return (x,y,z)
