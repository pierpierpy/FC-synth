"""Mock tool library for synthetic function-calling conversations.

Two parallel catalogues are provided, one per language:

- ``synthfc.tools.eng`` — English tool names, descriptions and mock results.
- ``synthfc.tools.ita`` — Italian equivalents.

Each catalogue exposes a ``TOOLS_BY_CATEGORY`` mapping and an ``execute_tool``
helper that returns plausible mock results.
"""
