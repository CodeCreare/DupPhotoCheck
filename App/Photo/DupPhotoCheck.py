import os
import sys
import re
import datetime
import shutil
sys.path.append('../../Common')
import Common
import WindowsIf
import PhotoCommon




s_testmode		= False
s_dir_base		= r'E:\Work\Temp\DupPhotos'
s_dir_work		= ''
s_remain_priors	= ['.+\d{8}_\d{6}$']
s_thres_simi	= 7
s_thres_very	= 5



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



def ProcessSameFiles(files, groupidx):
	global s_dir_work
#	print('ProcessSameFiles groupidx=', groupidx)
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



def ProcessVeriSimilarGroups(dir_src, groups_very, strtag):
	grouppos		= 0
	for group_very in groups_very:
		grouppos	+= 1
		files		= []
		for fname in group_very:
			file	= dir_src + '\\' + fname
			files.append(file)

		ProcessSameFiles(files, strtag + str(grouppos))



def AllHashTypeSimilar(all1, all2):
	global s_thres_very
	verysimi = True
	for pos in range(4):
		diff = all1[pos] - all2[pos]
		if s_thres_very < diff:
			verysimi = False

	return verysimi



def PickupVerySimilarMovies(dir_src, movies):
	print('PickupVerySimilarMovies, len(movies)=', len(movies))
	hashs		= {}
	filepos		= 0
	for movie in movies:
		filepos	+= 1
		file	= dir_src + '\\' + movie
		hash	= GetMovHash(file)
		hashs[movie]	= hash
		PrintProg('.', filepos)
#		print('hash=', hash)

	groups	= []
	for fname_tgt in hashs:
		hash_tgt	= hashs[fname_tgt]
#		print('hash_tgt=', hash_tgt, type(hash_tgt))
		if type(hash_tgt) == int and hash_tgt == -1:
			continue
		group		= []
		for fname in hashs:
			hash	= hashs[fname]
			if type(hash) == int and hash == -1:
				continue
			if fname != fname_tgt and hash == hash_tgt:
#				print('diff <= s_thres_simi, ', diff, fname, fname_tgt)
				group.append(fname)
				if not fname_tgt in group:
					group.append(fname_tgt)

		if 0 < len(group):
#			print('group=', group)
			for fname_group in group:
				hashs[fname_group] = -1
			groups.append(group)

	print('')
	print('groups=', groups)
	print('[Result] PickupVerySimilarMovies', len(groups), '/', len(movies))
	return groups



def PickupVerySimilarPhotos(dir_src, groups_simi):
	print('PickupVerySimilarPhotos, len(groups_simi)=', len(groups_simi))

	groups			= []
	grouppos		= 0
	for group_simi in groups_simi:
		grouppos	+= 1
		PrintProg('.', grouppos)
		allhashs	= {}
		for fname in group_simi:
			file	= dir_src + '\\' + fname
			allhash	= PhotoCommon.GetAllHash(file)
			allhashs[fname] = allhash

		for fname_tgt in allhashs:
			allhash_tgt	= allhashs[fname_tgt]
#			print('allhash_tgt=', allhash_tgt, type(allhash_tgt))
			if type(allhash_tgt) == int and allhash_tgt == -1:
				continue
			group		= []
			for fname in allhashs:
				allhash	= allhashs[fname]
				if type(allhash) == int and allhash == -1:
					continue
				
				if fname != fname_tgt and AllHashTypeSimilar(allhash, allhash_tgt):
#					print('diff <= s_thres_simi, ', diff, fname, fname_tgt)
					group.append(fname)
					if not fname_tgt in group:
						group.append(fname_tgt)

			if 0 < len(group):
#				print('group=', group)
				for fname_group in group:
					allhashs[fname_group] = -1
				groups.append(group)
	
	print('')
#	print('groups=', groups)
	print('[Result] PickupVerySimilarPhotos', len(groups), '/', len(groups_simi))
	return groups



def PickupSimilarPhotos(dir_src, photos):
	global s_thres_simi
	print('PickupSimilarPhotos, len(photos)=', len(photos))

	hashs		= {}
	filepos		= 0
	for photo in photos:
		filepos	+= 1
		file	= dir_src + '\\' + photo
		hash	= PhotoCommon.GetAverageHash(file)
		hashs[photo]	= hash
		PrintProg('.', filepos)
#		print('hash=', hash)

	groups	= []
	for fname_tgt in hashs:
		hash_tgt	= hashs[fname_tgt]
#		print('hash_tgt=', hash_tgt, type(hash_tgt))
		if type(hash_tgt) == int and hash_tgt == -1:
			continue
		group		= []
		for fname in hashs:
			hash	= hashs[fname]
			if type(hash) == int and hash == -1:
				continue
			diff	= hash - hash_tgt
			if fname != fname_tgt and diff <= s_thres_simi:
#				print('diff <= s_thres_simi, ', diff, fname, fname_tgt)
				group.append(fname)
				if not fname_tgt in group:
					group.append(fname_tgt)

		if 0 < len(group):
#			print('group=', group)
			for fname_group in group:
				hashs[fname_group] = -1
			groups.append(group)

	print('')
#	print('groups=', groups)
	print('[Result] PickupSimilarPhotos', len(groups), '/', len(photos))
	return groups



def SeparateFiles(dir_src, fnames):
	fnames_photo	= []
	fnames_movie	= []
	for fname in fnames:
		file	= dir_src + '\\' + fname
		if PhotoCommon.IsPhoto(file):
			fnames_photo.append(fname)
		elif PhotoCommon.IsMovie(file):
			fnames_movie.append(fname)

	return fnames_photo, fnames_movie



def DupPhotoCheck():
	SetWorkDir()
	dir_src			= sys.argv[1]
	fnames			= os.listdir(dir_src)
	photos, movies	= SeparateFiles(dir_src, fnames)
	groups_simi		= PickupSimilarPhotos(dir_src, photos)
	groups_very		= PickupVerySimilarPhotos(dir_src, groups_simi)
	ProcessVeriSimilarGroups(dir_src, groups_very, 'SimilarPhotos_')
	groups_very		= PickupVerySimilarMovies(dir_src, movies)
	ProcessVeriSimilarGroups(dir_src, groups_very, 'SimilarMovies_')
	print(' - End(DupPhotoCheck)')
#	input('何かキーを押してください')



DupPhotoCheck()



