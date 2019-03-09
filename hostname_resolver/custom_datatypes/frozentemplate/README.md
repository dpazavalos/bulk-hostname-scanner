# Frozen Template

Emulation of 3.7 Dataclasses frozen attribute, with soft lock for immutability
Allows immutable dataclass style objects for pre 3.7 applications. Set and forget about constants
Once init completes, builtin setattr and delattr will throw a SyntaxError on attempted use

##  Usage

```
>>> from frozentemplate import Frozen   # Assuming Frozen has had custom values written in
>>> constants1 = Frozen()
>>> constants1.val = "Can I change it?"
SyntaxError: Consider Constants obj immutable, do not modify!

>>> constants2 = Frozen(freeze_post_init=False)
>>> constants2.val = "Can I change it?"
# Yes you can
```

 * .freeze_now() - 
force freeze object, preventing any set or removing

 * .unfreeze() - 
 force unfreeze object, allowing any set or removing

 * __init__(freeze_post_init) - 
defaults to freeze object once init. Set False to diable auto-freeze, 
call .freeze_now to manually lock class attributes once desired
