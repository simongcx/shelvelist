#-------------------------------------------------------------------------------
# Name:        shelvelist
# Purpose:     a persistent list class based on Shelve
#
# Author:      Simon
#
# Created:     15/10/2013
# Copyright:   (c) Simon 2013
# Licence:     GNU General Public License v3
#-------------------------------------------------------------------------------


import shelve
import random
import os
import sys

#to do (this is the list of list functions not implemented)
##__add__
##__class__
##__delattr__
##__delitem__ (for increments other than 1)
##__delslice__ (for increments other than 1)
##__eq__
##__format__
##__ge__
##__getattribute__
##__getitem__ (for increments other than 1)
##__getslice__ (for increments other than 1)
##__gt__
##__hash__
##__iadd__
##__imul__
##__le__
##__lt__
##__mul__
##__ne__
##__new__
##__reduce__
##__reduce_ex__
##__repr__
##__reversed__
##__rmul__
##__setattr__
##__setitem__ (for increments other than 1)
##__setslice__ (for increments other than 1)
##__sizeof__
##__subclasshook__
##remove
##reverse
##sort

# Don't expect to be able to do Python literal list creation
# mylist = shelvelist(filename)
# mylist = [1,2,3]
# Now mylist is just a list!


class shelvelist():
    """Persistent list based on shelve
Does not implement all list functionality
Please read the documentation"""

    def __init__(self,filenameandpath):
        if os.path.exists(filenameandpath):
            new = False
        else:
            new = True
        self.shelf = shelve.open(filenameandpath)
        if new:
            self.shelf['last'] = -1

    def pop(self,index=None):
        if index is None:
            returnvalue = self.shelf[str(self.shelf['last'])]
            self.shelf['last'] = self.shelf['last'] - 1
            return returnvalue
        elif isinstance(index,int):
            returnvalue = self.shelf[str(index)]
            self.__delitem__(index)
            return returnvalue
        else:
            raise Exception
        self.shelf.sync()

    def append(self,value):
        self.shelf['last'] = self.shelf['last'] + 1
        self.shelf[str(self.shelf['last'])] = value
        self.shelf.sync()

    def __getitem__(self, arg):
        if isinstance(arg, slice):
            stop = arg.stop
            if stop == 2147483647:
                stop = self.shelf['last'] + 1
            return [self.__getitem__(i) for i in range(arg.start,stop)]
        elif isinstance(arg,int):
            return self.shelf[str(arg)]
        else:
            raise TypeError('shelvelist indices must be integers, not ' + type(arg).__name__)

    def __str__(self):
        return str([self.__getitem__(i) for i in range(0,self.shelf['last']+1)])

    def __len__(self):
        return self.shelf['last'] + 1

    def __delitem__(self,arg):
        if isinstance(arg, slice):
            start = arg.start
            stop = min(arg.stop, self.shelf['last'] + 1)
            slicelength = stop - start
            starttoend = (self.shelf['last'] + 1) - start
            listremainder = starttoend - slicelength

            for i in range(0, listremainder): #loop through everything remaining to the right after a delete, and move left
                self.shelf[str(i + start)] = self.shelf.pop(str(i + stop))

            for i in range(start + listremainder, stop): #clear up any remaining deletes required (in order to keep file size under control)
                del self.shelf[str(i)]

            self.shelf['last'] = self.shelf['last'] - slicelength
        elif isinstance(arg, int):
            leftlift = 1
            start = arg
            for i in range(start,self.shelf['last']):
                self.shelf[str(i)] = self.shelf[str(i + 1)]
            self.shelf['last'] = self.shelf['last'] - 1
        else:
            raise Exception

        self.shelf.sync()

    def count(self,value):
        if self.shelf['last'] == value:
            meta = 1
        else:
            meta = 0
        return self.shelf.values().count(value) - meta


    def index(self,value):
        for i in range(0,self.shelf['last'] + 1):
            if self.shelf[str(i)] == value:
                return i
        raise Exception


    def __contains__(self,value):
        for i in range(0,self.shelf['last'] + 1):
            if self.shelf[str(i)] == value:
                return True
        return False

    def __setitem__(self, arg, value):
        if isinstance(arg, slice):

            #scenarios:
            #the range defined in the slice is larger that the number of values in the provided iterable
            # -> need to delete the records
            #the range defined in the slice is less than the number of value in the provided iterable
            # -> need to shift forward everything else


            # __setitem__ can be thought of as combination of two operations:
            #    deletion the slice records from the list
            #    then add the addition of the new records from the beginning of the slice
            # however, deletes and insertions are expensive, so not efficient to run all the deletes, then all the inserts
            start = arg.start
            stop = min(arg.stop, self.shelf['last'] + 1)
            slicelength = stop - start
            starttoend = (self.shelf['last'] + 1) - start
            listremainder = starttoend - slicelength

            if len(value) == slicelength:
                for i, item in enumerate(value):
                    self.shelf[str(start + i)] = item


            if len(value) > slicelength:
                rightshift = len(value) - slicelength
                for i in range(self.shelf['last'], stop - 1, -1):
                    self.shelf[str(i + rightshift)] = self.shelf.pop(str(i))
                for i, item in enumerate(value):
                    self.shelf[str(start + i)] = item
                self.shelf['last'] = self.shelf['last'] + len(value) - slicelength

            if len(value) < slicelength:
                for i, item in enumerate(value):
                    self.shelf[str(start + i)] = item
                self.__delitem__(slice(start + len(value), stop))

        elif isinstance(arg,int):
            self.shelf[str(arg)] = value
        else:
            raise Exception
        self.shelf.sync()

    def insert(self, index, value):
        # list behaviour is that if index > len(list) then value is appended
        if index > self.shelf['last']:
            self.shelf.append(value)
        else:
            for i in range(self.shelf['last'], index - 1, -1):
                self.shelf[str(i + 1)] = self.shelf.pop(str(i))
            self.shelf[str(index)] = value
        self.shelf.sync()


    def __iter__(self):
        return (self.shelf[str(i)] for i in range(0,self.shelf['last'] + 1))

    def extend(self, extlist):
        for item in extlist:
            self.append(item)

    def remove(self, item):
        for i in range(self.shelf['last'], -1, -1):
            if self.shelf[str(i)] == item:
                self.__delitem__(i)
                return
        raise ValueError('shelvelist.remove(x): x not in shelvelist')
        self.shelf.sync()

    def __add__(self, other):
        if isinstance(other, list):
            return [self.__getitem__(i) for i in range(0,self.shelf['last']+1)] + other
        else:
            raise TypeError('can only concatenate list (not "' + type(other).__name__ + '") to shelvelist')

    def __iadd__(self,other):
        if hasattr(other, '__iter__'):
            for item in other:
                self.append(item)
            return self
        else:
            raise TypeError("'" + type(other).__name__ + "' object is not iterable")


def appendpoplentest():
    testfilename = 'testfilename'
    if os.path.exists(testfilename):
        os.remove(testfilename)
    l = shelvelist(testfilename)
    l.append('hello world')
    assert l.pop() == 'hello world'
    assert len(l) == 0
    os.remove(testfilename)


def containstest():
    testfilename = 'testfilename'
    if os.path.exists(testfilename):
        os.remove(testfilename)
    l = shelvelist(testfilename)
    for i in range(0,10):
        l.append(i)
    for i in range(0,10):
        assert i in l
    os.remove(testfilename)


def deltest():
    testfilename = 'testfilename'
    if os.path.exists(testfilename):
        os.remove(testfilename)
    l = shelvelist(testfilename)
    mylist = []
    for i in range(0, 10):
        l.append(i)
        mylist.append(i)
    del l[:3]
    del mylist[:3]
    assert l[:] == mylist
    del l[1:3]
    del mylist[1:3]
    assert l[:] == mylist
    del l[2:-1]
    del mylist[2:-1]
    assert l[:] == mylist
    del l[0:]
    del mylist[0:]
    assert l[:] == mylist
    os.remove(testfilename)

def counttest():
    testfilename = 'testfilename'
    if os.path.exists(testfilename):
        os.remove(testfilename)
    l = shelvelist(testfilename)
    for i in range(0, 10):
        for j in range(0, i):
            l.append(i)
    for i in range(0, 10):
        assert l.count(i) == i
    os.remove(testfilename)

def indextest():
    testfilename = 'testfilename'
    if os.path.exists(testfilename):
        os.remove(testfilename)
    l = shelvelist(testfilename)
    for i in range(0, 10):
        l.append(i)
    for i in range(0, 10):
        assert l.index(i) == i
    os.remove(testfilename)

def persistencetest():
    testfilename = 'testfilename'
    if os.path.exists(testfilename):
        os.remove(testfilename)
    def innerfuncction(): #by creating the shelvelist in an inner function, it goes out of scope when that function finishes
        l = shelvelist(testfilename)
        l.append('hello world')
    innerfuncction()
    l = shelvelist(testfilename)
    assert l.pop() == 'hello world'
    os.remove(testfilename)

def getitemtest():
    testfilename = 'testfilename'
    if os.path.exists(testfilename):
        os.remove(testfilename)
    l = shelvelist(testfilename)
    for i in range(0, 10):
        l.append(i)
    for i in range(0, 10):
        assert l[i] == i
    assert l[0:5] == [0,1,2,3,4]
    assert l[1:5] == [1,2,3,4]
    assert l[0:] == [0,1,2,3,4,5,6,7,8,9]
    assert l[:5] == [0,1,2,3,4]
    assert l[0:-1] == [0,1,2,3,4,5,6,7,8]
    assert l[1:-2] == [1,2,3,4,5,6,7]
    os.remove(testfilename)

def inserttest():
    testfilename = 'testfilename'
    if os.path.exists(testfilename):
        os.remove(testfilename)
    l = shelvelist(testfilename)
    mylist = []
    for i in range(0, 10):
        l.append(i)
        mylist.append(i)
    for i in range(0, 10):
        l.insert(i, i * 2)
        mylist.insert(i, i * 2)
        assert l[:] == mylist
    l.insert(500,'a')
    mylist.insert(500,'a')
    assert l[:] == mylist
    os.remove(testfilename)

def iterationtest():
    testfilename = 'testfilename'
    if os.path.exists(testfilename):
        os.remove(testfilename)
    l = shelvelist(testfilename)
    for i in range(0,10):
        l.append(i)
    x = 0
    for i in l:
        assert i == x
        x += 1
    print 'Size of iterable with 10 records:', sys.getsizeof(l.__iter__())
    for i in range(0,10000):
        l.append(i)
    print 'Size of iterable with 10,000 records:', sys.getsizeof(l.__iter__())
    os.remove(testfilename)

def extendtest():
    testfilename = 'testfilename'
    if os.path.exists(testfilename):
        os.remove(testfilename)
    l = shelvelist(testfilename)
    for i in range(0,5):
        l.extend([i] * i)
    assert l[:] == [1,2,2,3,3,3,4,4,4,4]
    os.remove(testfilename)


def setitemtest():
    testfilename = 'testfilename'
    if os.path.exists(testfilename):
        os.remove(testfilename)
    l = shelvelist(testfilename)
    mylist = []
    for i in range(0,5):
        l.append(i)
        mylist.append(i)
    # insertion longer than deletion
    l[1:2] = ['a', 'b']
    mylist[1:2] = ['a', 'b']
    assert l[:] == mylist
    # insertion, no deletion
    l[1:1] = ['c']
    mylist[1:1] = ['c']
    assert l[:] == mylist
    # insertion shorter than deletion
    l[1:4] = ['d']
    mylist[1:4] = ['d']
    assert l[:] == mylist
    os.remove(testfilename)


def removetest():
    testfilename = 'testfilename'
    if os.path.exists(testfilename):
        os.remove(testfilename)
    l = shelvelist(testfilename)
    mylist = []
    for i in range(0,10):
        l.extend([i] * i)
        mylist.extend([i] * i)
    for i in range(1,10):
        l.remove(i)
        mylist.remove(i)
        print l[:]
        print mylist
        assert l[:] == mylist
    os.remove(testfilename)


def addandiaddtest():
    testfilename = 'testfilename'
    if os.path.exists(testfilename):
        os.remove(testfilename)
    l = shelvelist(testfilename)
    for i in range(0,10):
        l.append(i)
    assert l + [10] == [0,1,2,3,4,5,6,7,8,9,10]
    print l
    l += [10,11]
    print l
    assert l[:] == [0,1,2,3,4,5,6,7,8,9,10,11]
    try:
        p = l + 5
    except Exception as e:
        print type(e).__name__ + ": " + str(e)
    try:
        l += 5
    except Exception as e:
        print type(e).__name__ + ": " + str(e)
    os.remove(testfilename)

def main():
##    appendpoplentest()
##    persistencetest()
##    containstest()
##    counttest()
##    indextest()
##    getitemtest()
##    deltest()
##    iterationtest()
##    extendtest()
##    setitemtest()
##    removetest()
    addandiaddtest()

if __name__ == '__main__':
    main()


