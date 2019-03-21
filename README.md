# hostname-resolver

A bulk hostname resolver, designed to get info on a large number of internal hostnames against 
internal TLDs.

Given a list of hostnames, finds their FQDN using an inbuilt list of top level domains. Designed 
for environments where user needs full names of internal servers, but has only hostnames.

In addition, provides limited formatting and reporting functionality (simple text or csv)


## Installation

```
pip install hostname-resolver  
```

Usage

```python
import hostname_resolver
resolver = hostname_resolver.HostnameResolver()
resolver.run()
```

or:

```
python3 ./hostname_resolver/__init__.py
```

On default runs, hostname_resolver will prompt you for hostnames (recommend copy/pasting a column) 
hostname_resolver strips any duplicates and attempts to resolve hostnames as is or iterates each 
against its known TLDs. As it resolves it displays what was given, how it resolved the hostname, 
and the found IP. Once a full list is run, hostname_resolver then prompts you to run a new list, 
add to the previous list, build a report (text file or csv), or quit

## Features

 - Adhoc functionality, most functionality modules are loaded only as needed to reduce startup time

 - versatility, hostnames to check can be passed through run, stdin, or the file can be called 
 directly with hostnames in as command line arguments (single items, passable arrays, or path names
 to files containing hostnames)

 - Modularity. It's all horizontal as heck
