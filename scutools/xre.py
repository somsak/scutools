"""
Extended regex

support numbering format
<1-10> = 1,2,3,4,5,6,7,8,9,10
"""

import re, string

def genrerange(pattern) :
	"Generate or'ed normal regular expression"
	try :
		a, b = string.split(pattern, '-', 2)
		return '(' + string.join( map(str, range(int(a), int(b) + 1)), '|') + ')'
	except :
		raise re.error

def compile(pattern) :
	"compile the pattern with numbering extension"

	idx = 0
	newpat = ''
	while 1 :
		l_idx = string.find(pattern, '<', idx)
		if (l_idx == -1) or ((l_idx != 0) and (pattern[l_idx - 1] == '\\')) :
			newpat = newpat + pattern[idx:] 
			break
		else :
			# Find the '>'
			r_idx = string.find(pattern, '>', l_idx)
			if (r_idx != -1) and (pattern[r_idx - 1] != '\\') :
				r = genrerange(pattern[l_idx + 1:r_idx])
				newpat = newpat + pattern[idx:l_idx] + r
				idx = r_idx + 1
				if idx >= len(pattern) :
					break
			else :
				# unmatch '<'
				raise re.error
	return re.compile(newpat)

if __name__ == '__main__' :
	import re

	print genrerange('1-1024')
	try :
		print genrerange('1-')
	except re.error, e:
		print 'OK'
	try :
		print genrerange('1024-')
	except re.error, e:
		print 'OK'
	try :
		print genrerange('1-2-3')
	except re.error, e:
		print 'OK'
	r = compile('^<3-10>$')
	for i in range(10) :
		print str(i) + ':',
		print r.match(str(i))
	r = compile('^compute<3-10>$')
	for i in range(10) :
		print str(i) + ':',
		print r.match('compute' + str(i))
	r = compile('^compute<3-7>xxx$')
	for i in range(10) :
		print str(i) + ':',
		print r.match('compute' + str(i) + 'xxx')
	r = compile('^compute<3-7>xxx<1024-2048>$')
	for i in range(10) :
		print str(i) + ':',
		print r.match('compute' + str(i) + 'xxx' + str(1290) )
