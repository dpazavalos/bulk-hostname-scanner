# Gather Unique

Gathers a list of unique entries from user, with optional blacklists and header prompt
Note: Item type depends on gathering method. If using stdin, anticipate string returns.
Otherwise, use list_in

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
uniq3 = gather.run(list_in=['6', '6', '1', '2'], 
                   blacklist0=['1', '2', '3', '4', '5'], 
                   blacklist1=['7', '8'])
```

Note: kwargs used only for flexible positioning. Your blacklist arg names literally do not matter, 
just differentiate them from the default args
