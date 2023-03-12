
# Perfmon
A lightweight performance monitor (client side) (rewrite for twice)

This is a client side of the perfmon project, it has a lightweight scheduler and multiprocessing workers, every worker
can active when a job activated.

Each work can be configured in a json file, the program will read the config file to setup tasks and scheduler, then
post the report of task instances to the specified server.

![](data/github/Perfmon_x3.png)

# Perfmon

A lightweight performance monitor daemon (client mode)

Client side gathering system information and report to specified server in configuration file.

# Usage

You need Python3.10 to run the program property.

Using command below to start perfmon client:

``` shell
python3 src/main.py -c CONFIG.json
```

# Configuration

Program needs a configuration file to run task, you can prepare a json file to describe every task.

## Main config

A standard configuration file struct like this:

``` json
{
    "agent_name": "AgentName",
    "submit": {},
    "process": 1,
    "perfmon": []
}
```

|       item | type   | description                                                             |
|-----------:|:-------|:------------------------------------------------------------------------|
| agent_name | string | Agent name for this instance                                            |
|     submit | dict   | Submit plan for the agent                                               |
|    process | int    | Instance will fork processes count to deal tasks, default for CPU cores |
|    perfmon | list   | The Perfmon items list                                                  |

## Submit configs

A submitting configuration struct like this:

``` json
{
    "type": "Type",
    "format": "JsonEachRow"
}
```

|   item | type | description                                                |
|-------:|:-----|:-----------------------------------------------------------|
|   type | Enum | Submit method type, support "file", "http", "print"        |
| format | Enum | Submit content format, support "JsonEachRow", "PythonRepr" |

Besides, every type has their own specific configuration items:

For `type == "file"`:

| items for type == "file" | type   | description         |
|-------------------------:|:-------|:--------------------|
|                     path | string | Path to file output |

For `type == "http"`:

| items for type == "http" | type   | description                  |
|-------------------------:|:-------|:-----------------------------|
|                      url | string | Path to file output          |
 |                   header | dict   | header dict for http request |
|                    retry | int    | http request retry times     |

For `type == "print"`

| items for type == "print" | type | description                                                       |
|--------------------------:|:-----|:------------------------------------------------------------------|
|                    device | Enum | Device for print destination device, support "stdout", "stderr"   |

## Perfmon configs
