scarper for apkmirror

Note: this was written with python3.8, other versions may be unstable.
Note: apkmirror.com may change its interface causing this code to break. This code works on the site as of 7 Feb 2020.

to run: python crawler.py <textfile>

textfile contains the app ids of each android application.
if found it returns info(version, size in byte, date published, and others) in a .csv format.
else it would report it not found in the notFound log file. 
 