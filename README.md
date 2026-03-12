# Project
Shared virtual notebook. a multi-client client-server system that supports concurrent editing of a shared virtual notebook over an IP network (or Internet).

# Architecture
The system is based on a server that maintains and manages all the notebooks and users data and light clients that enable each user to easily create, edit and share their notebooks.
The communication between the clients and server is encrypted and based on user login and authentication.
The system enables access control for each notebook and allows the owner to determine who can view or edit each of his notebooks.

# Notebooks
Each notebook can have multiple pages with text, drawings and marker strokes as well as fine control of colors and line widths. The page background can also be changed (blank, ruled, or grid).

# Sharing
The system allows each client to independantly edit and change a shared notebook and the server algorithms maintain the integrity of the notebook and enable simultaneus editing of multiple clients on the same page.

The notebooks are managed on the server and the client has a cached copy to enable quick system response and avoid conflicts between clients that perform simultaneus edits.
