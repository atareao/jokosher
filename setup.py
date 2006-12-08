#!/usr/bin/env python

from distutils.core import setup
import os
import glob

I18NFILES = []
for filepath in glob.glob("locale/*/LC_MESSAGES/*.mo"):
	targetpath = os.path.dirname(os.path.join("share/", filepath))
	I18NFILES.append((targetpath, [filepath]))


setup(name='jokosher',
	version='0.3',
	author='Jokosher Project',
	author_email='email@jokosher.org',
	maintainer='David Corrales',
	maintainer_email='corrales.david@gmail.com',
	description='Multi-track non-linear audio editing.',
	long_description='Jokosher is a simple yet powerful multi-track studio. With it you can create and record music, podcasts and more, all from an integrated simple environment.',
	url='http://www.jokosher.org/',
	download_url='http://www.jokosher.org/download',
	license='GNU GPL',
	platforms='linux-x86',
	scripts=['jokosher'],
	packages=['Jokosher'],
	data_files=[('share/jokosher/',
		glob.glob("Jokosher/*.glade")
		),
		('share/jokosher/',
		["Jokosher/jokosher-logo.png"]
		),
		('share/jokosher/Instruments',
		glob.glob("Instruments/*.instr")
		),
		('share/jokosher/Instruments/images',
		glob.glob('Instruments/images/*')
		),
		('share/icons/hicolor/48x48/apps',
		['images/jokosher-icon.png']
		),
		('share/pixmaps',
		['images/jokosher-icon.png']
		),
		('share/jokosher/pixmaps',
		glob.glob("images/*.png")
		),
		('share/applications',
		['jokosher.desktop'],
		),
		('share/jokosher/extensions',
		glob.glob("extensions/*")
		)
		]+I18NFILES
)

## To uninstall manually delete these files/folders:
## /usr/share/jokosher/
## /usr/icons/hicolor/48x48/apps/jokosher-icon.png
## /usr/share/locale/*/LC_MESSAGES/jokosher.mo
## /usr/share/pixmaps/jokosher-icon.png
## /usr/share/applications/jokosher.desktop
