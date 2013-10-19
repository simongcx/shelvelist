shelvelist
==========

Python library for persistent lists based on shelve

Objectives
----------

Python native list like functionality without the need to hold the list in memory. Intended for large lists or low memory situations.


Alternatives
------------

Why not put a save-to-disk wrapper around the existing Python list class? This method is suggested here:

http://stackoverflow.com/questions/9449674/how-to-implement-a-persistent-python-list

But this wrapper will not prevent the list being held in memory as well, which defeats the objective of keeping a large list out of memory.
