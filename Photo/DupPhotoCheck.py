import os
import sys
import re
import glob
import datetime
import filecmp
import shutil
from PIL import Image
sys.path.append('../Common')
import Common
import WindowsIf
import PhotoCommon




s_testmode		= False
s_dir_base		= r'E:\Work\Temp\DupPhotos'
s_dir_work		= ''
s_remain_priors	= ['.+\d{8}_\d{6}$']



def SetWorkDir():
	global s_dir_base
	global s_dir_work
	dt_now	= datetime.datetime.now()
	str_now	= dt_now.strftime('DP_%Y%m%d_%H%M%S')
	s_dir_work	= s_dir_base + '\\' + str_now + '\\'
	Common.MakeFolderIfNotExist(s_dir_base)
	Common.MakeFolderIfNotExist(s_dir_work)



def Move1File(file_src, path_dst):
	fname	= os.path.basename(file_src)
	file_dst	= path_dst + fname
	print('[Move] ' + file_src + ' -> ' + file_dst)
	if s_testmode == False:
		shutil.move(file_src, file_dst)
	return file_dst



def Remove1File(file):
	print('[Remove] ' + file)
	if s_testmode == False:
		os.remove(file)



def GetMovHash(file):
	size			= os.path.getsize(file)
	success, date	= PhotoCommon.GetExif_ImageShotDate(file)
	return success, date + '_' + str(size)



def PrintProg(mark, filepos):
	print(mark, end='', flush=True)

	if filepos % 10 == 0:
		print('{:4}'.format(filepos), end='', flush=True)

	if filepos % 50 == 0:
		print('')



def RemoveSingleKeys(dict):
	deltgthashs	= []
	for hash in dict:
		files = dict[hash]
		if len(files) == 1:
			deltgthashs.append(hash)

	for hash in deltgthashs:
		del dict[hash]

	return dict



def ProcessSameFiles(files, groupidx):
	global s_dir_work
	print('ProcessSameFiles groupidx=', groupidx)
	file_remain	= files[0]
	for remain_prior in s_remain_priors:
		for file in files:
			fname	= os.path.basename(file)
			top,ext	= os.path.splitext(fname)
			if re.match(remain_prior, top):
				file_remain	= file
				break

	dir_workidx	= s_dir_work + str(groupidx) + '\\'
	Common.MakeFolderIfNotExist(dir_workidx)
	for file in files:
		fname	= os.path.basename(file)
		if file == file_remain:
			WindowsIf.CreateShortcut(file, dir_workidx + fname + '.lnk')
		else:
			Move1File(file, dir_workidx)



def Dummy():
	path_src	= os.path.dirname(files[0])
	path_dst	= path_src + '\\Same' + str(groupidx) + '\\'
	Common.MakeFolderIfNotExist(path_dst)

	newfiles	= []
	print(' - fnames = ', end='')
	for file in files:
		fname	= os.path.basename(file)
		print(fname, ', ', end='')
		file_new	= Move1File(file, path_dst)
		newfiles.append(file_new)

	print(' ')
	file_onlyone	= 'NONE'
	for file_new in newfiles:
		fname	= os.path.basename(file_new)
		top,ext	= os.path.splitext(fname)
		if (fname.startswith('Photo_') or fname.startswith('Movie_')) and re.match('.+\d{6}$', top):
			file_onlyone	= file_new
			break

	if file_onlyone	== 'NONE':
		return

	for file_new in newfiles:
		if file_new != file_onlyone:
			Remove1File(file_new)



def ProcessSameFileGroups(dict_same):
	print('ProcessSameFileGroups, len(dict_same)=', len(dict_same))
	groupidx	= 1
	for hash_same in dict_same:
		ssamefiles = dict_same[hash_same]
		ProcessSameFiles(ssamefiles, groupidx)
		groupidx += 1



def CheckSameFiles(dict_simi):
	print('CheckSameFiles len(dict_simi)=', len(dict_simi))
	dict_same	= {}
	hashpos		= 0
	for hash_simi in dict_simi:
		hashpos += 1
		similarfiles = dict_simi[hash_simi]
		print(' - fnames = ', end='')
		for file in similarfiles:
			fname	= os.path.basename(file)
			print(fname, ', ', end='')
			if PhotoCommon.IsMovie(file):
				hash_same = hash_simi
			else:
				hash_same = PhotoCommon.GetTotalHash(file)

			strhash	= str(hash_same)
			if strhash in dict_same:
				samefiles = dict_same[strhash]
				samefiles.append(file)
			else:
#				print('total hash new, file=', file, ', strhash=', strhash)
				dict_same[strhash] = [file]

		print('')
	dict_same = RemoveSingleKeys(dict_same)
	print('')
	return dict_same



def CheckSimilarFiles():
	path_src	= sys.argv[1]
	files		= os.listdir(path_src)
	print('CheckSimilarFiles, len(files)=', len(files))

	dict_simi	= {}
	fails		= []
	filepos		= 0
	for fname in files:
		filepos += 1
		file	= path_src + '\\' + fname
		if PhotoCommon.IsMovie(file):
			success, hash	= GetMovHash(file)
			if not success:
				PrintProg('x', filepos)
				fails.append(file)
				continue
		else:
			hash	= PhotoCommon.GetAverageHash(file)
		strhash	= str(hash)
		if strhash in dict_simi:
			similarfiles = dict_simi[strhash]
			PrintProg('!', filepos)
			similarfiles.append(file)
		else:
			dict_simi[strhash] = [file]
			PrintProg('.', filepos)

	print('')
	dict_simi = RemoveSingleKeys(dict_simi)
	return dict_simi



def MoveSingleFilesToParentFolder():
	path_src	= sys.argv[1]
	files		= os.listdir(path_src)
	for fname in files:
		file	= path_src + '\\' + fname
		if os.path.isdir(file):
			pics	= os.listdir(file)
			if len(pics) == 1:
				src_file	= file + '\\' + pics[0]
				dst_file	= path_src + '\\' + pics[0]
				print('[Move Single File] ' + src_file + ' -> ' + dst_file)
				shutil.move(src_file, dst_file)



def RemoveEmptyDirs():
	path_src	= sys.argv[1]
	files		= os.listdir(path_src)
	for fname in files:
		file	= path_src + '\\' + fname
		if os.path.isdir(file):
			pics	= os.listdir(file)
			if len(pics) == 0:
				os.rmdir(file)
				print('[Remove Empty Dir] ' + file)



def DupPhotoCheck():
	SetWorkDir()
	dict_simi = CheckSimilarFiles()
	dict_same = CheckSameFiles(dict_simi)
	ProcessSameFileGroups(dict_same)
	MoveSingleFilesToParentFolder()
	RemoveEmptyDirs()
	print(' - End(DupPhotoCheck)')
#	input('何かキーを押してください')



DupPhotoCheck()



