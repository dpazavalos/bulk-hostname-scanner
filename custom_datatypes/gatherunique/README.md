# Gather Unique

Simple, unique list gatherer, with *args for passable blacklist check and optional list_in for 
automated sorting against blacklist/s

##  Installation

```
pip install gather_unique
```

##  Usage

```python
from gatherunique import GatherUnique as gun
gather = gun()
head = "Header to display"

# Unique list from stdin, no header
uniq1 = gather.run()

# Unique list from stdin, with provided blacklist and header
uniq2 = gather.run(list_in=['1', '2', '3', '4', '5'], header=head )

# Unique list from list_in= against provided blacklist
uniq3 = gather.run(list_in=['6', '6', '1', '2'], blacklist0=['1', '2', '3', '4', '5'])
```

Note that args are considered blacklists by default. Use 'header=' and 'list_in=' to differentiate
