

import os, os.path, urllib
import pwd


def getFullName():
	try:
		# Try to get the full name if it exists
		fullname = pwd.getpwuid(os.getuid())[4].split(",")[0]
		if fullname == "":
			fullname = pwd.getpwuid(os.getuid())[0]
		return fullname
	except:
		# If we can't get the fullname, then just use the login
		return pwd.getpwuid(os.getuid())[0]

def samefile(path1, path2):
	return os.path.samefile(path1, path2)


def url2pathname(url):
	return urllib.url2pathname(url)

def pathname2url(path):
	return "file://%s" % urllib.pathname2url(path)

def GetRecordingDefaults():
	return dict()

def GetPlaybackDefaults():
	return dict()
