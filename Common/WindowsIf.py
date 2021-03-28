# UTF8
import os, winshell
from win32com.client import Dispatch



def CreateShortcut(path_target, path_shortcut):
	shell = Dispatch('WScript.Shell')
	shortcut = shell.CreateShortCut(path_shortcut)
	shortcut.Targetpath = path_target
#	shortcut.WorkingDirectory = r'E:\Work\Temp'
	shortcut.save()



if __name__ == '__main__':
#	Debug()
	CreateShortcut(r'E:\Work\Temp\202008\Photo_20200801_123951.JPG', r'E:\Work\Temp\Photo.lnk')



