from random import shuffle

def contains_sublist(lst, sublst):
	# Is list sublst contained somewhere within list lst?
    n = len(sublst)
    return any((sublst == lst[i:i+n]) for i in xrange(len(lst)-n+1))
    
def contains_specific_run(lst, item, num):
	# Test whether item appears in a run of num times
	# (or more) within list lst:
	return contains_sublist(lst, [item ]* num)
	
def contains_any_run(lst, num):
	# Test whether any element of list lst appears in
	# a run of num times (or more) in a row:
	items = set(lst)
	return any(contains_specific_run(lst, item,num) for item in items)
	
def shuffle_without_runs(lst, num):
	# Shuffle list lst into an order that avoids any
	# item being repeated num times in a row:
	shuffle(lst)
	while contains_any_run(lst, num):
		shuffle(lst)
	return lst
	
def find_item_named(lst, itemname):
	# Find the Linger item with the name itemname in
	# the item list lst
	for x in lst:
		if x.itemname == itemname:
			myitem = x
			break
	return x 