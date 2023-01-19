
# Perfmon
A lightweight performance monitor (client side) (rewrite for twice)

This is a client side of the perfmon project, it has a lightweight scheduler and multiprocessing workers, every worker
can active when a job activated.

Each work can be configured in a json file, the program will read the config file to setup tasks and scheduler, then
post the report of task instances to the specified server.
