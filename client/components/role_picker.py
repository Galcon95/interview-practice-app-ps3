# Component: dropdowns for IT role and seniority level.
# Used by the Q&A generator page. Returns (role, level).
# The lists come from the server (guards/input_validation.py), which also checks them.

import streamlit as st


def role_picker(roles, levels):
    """Draw two dropdowns side by side: the IT role and the seniority level.

    Args:
        roles: the roles to choose from, from api_client.get_roles_and_levels().
        levels: the levels to choose from, from api_client.get_roles_and_levels().

    Returns:
        A tuple (role, level) with the chosen values (str).
    """
    col_role, col_level = st.columns(2)
    role = col_role.selectbox("Role", roles)
    level = col_level.selectbox("Level", levels)
    return role, level
