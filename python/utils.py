from algorithms import get_traffic_speed

def get_road_name(from_id, to_id, id_to_name):
    """
    Generates a road name from node IDs.

    Args:
        from_id: Starting node ID.
        to_id: Ending node ID.
        id_to_name (dict): ID to name mapping.

    Returns:
        str: Road name in format 'from_name-to_name'.
    """
    from_name = id_to_name.get(from_id, str(from_id))
    to_name = id_to_name.get(to_id, str(to_id))
    return f"{from_name}-{to_name}"