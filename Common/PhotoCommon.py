import os
import sys
import re
import subprocess
import datetime
import imagehash
from PIL import Image
from PIL.ExifTags import TAGS
import PIL.ExifTags as PilTags
sys.path.append('../Common')
import Common



g_path_ffmpeg	= 'E:\\Work\\program\\ffmpeg\\ffprobe.exe'

def FormatDatetime(datetime):
	if 'T' in datetime:
		strs	= datetime.split('T')
	else:
		strs	= datetime.split(' ')
	strdt	= strs[0]
	strtm	= strs[1]

	if ':' in strdt:
		strs	= strdt.split(':')
	else:
		strs	= strdt.split('-')
	str	= strs[0] + '/' + strs[1] + '/' + strs[2]

	if ':' in strtm:
		strs	= strtm.split(':')
	str	= str + '_' + strs[0] + ':' + strs[1] + ':' + strs[2]

#	print('FormatDatetime=' + datetime + ' -> ' + str)
	return str



# https://news.mynavi.jp/article/zeropython-42/ を参考に変換
def ConvExifDeg(v):
	# Exif情報の分数を度に変換
	d = float(v[0][0]) / float(v[0][1])
	m = float(v[1][0]) / float(v[1][1])
	s = float(v[2][0]) / float(v[2][1])
	return d + (m / 60.0) + (s / 3600.0)



def ConvLatLong(gps):
	lat = ConvExifDeg(gps['GPSLatitude'])
	lat_ref = gps['GPSLatitudeRef']
	if lat_ref != 'N': lat = 0 - lat
	long = ConvExifDeg(gps['GPSLongitude'])
	lon_ref = gps['GPSLongitudeRef']
	if lon_ref != 'E': long = 0 - long
	return lat, long



def IsPhoto(file):
	base, fileext = os.path.splitext(file)
	fileext	= fileext.upper()
	if fileext == '.JPG' or fileext == '.PNG':
		return True
	else:
		return False



def IsMovie(file):
	base, fileext = os.path.splitext(file)
	fileext	= fileext.upper()
	if fileext == '.MOV' or fileext == '.MP4':
		return True
	else:
		return False



def GetExif_PhotoCommon(file, target):
	try:
		img = Image.open(file)
	except:
		return False, 'EXCEPTION(ImageOpen)'

	try:
		exif = img._getexif()
	except:
		img.close()	
		return False, 'EXCEPTION(GetExif)'
	try:
		for id,val in exif.items():
			tg = TAGS.get(id, id)
			if target == 'DEBUG':
				print(tg, ' = ', val)
			if tg == target:
				img.close()	
				return True, val
	except AttributeError:
		img.close()	
		return False, 'EXCEPTION(Attribute)'

	img.close()	
	return False, 'ExifNotFound'



def GetExif_PhotoShotDate(file):
	result, value = GetExif_PhotoCommon(file, 'DateTimeOriginal')
	if result == False:
		return result, value
	fmtval = FormatDatetime(value)
	return result, fmtval



def GetExif_PhotoLatLong(file):
	result, value = GetExif_PhotoCommon(file, 'GPSInfo')
	if result == False:
		return False, -1, -1
	gps = {
		PilTags.GPSTAGS.get(t, t): value[t]
		for t in value
	}
	lat, long = ConvLatLong(gps)
	return True, str(lat), str(long)



def GetExif_MovieCommon(file, target):
	ffprob_prm	= [g_path_ffmpeg, '-show_chapters', '-hide_banner', file]
	proc		= subprocess.run(ffprob_prm, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	response	= proc.stdout.decode('utf8') + '\n' + (proc.stderr.decode('utf8'))
	for line in response.splitlines():
		if target == 'DEBUG':
			print(line)
		if target in line:
			str		= Common.SubStrBetween(line, target, '')
			str		= Common.SubStrBetween(str, ':', '')
			str		= str.strip()
			return True, str
	return False, 'ExifNotFound'



def GetExif_MovieLength(file):
	base, fileext = os.path.splitext(file)
	fileext	= fileext.upper()
	if fileext == '.MOV':
		result, value = GetExif_MovieCommon(file, 'Duration')
	else:
		result, value = GetExif_MovieCommon(file, 'Duration')
	value	= Common.SubStrBetween(value, '', ',')
	return result, value



def GetExif_MovieShotDate(file):
	base, fileext = os.path.splitext(file)
	fileext	= fileext.upper()
	if fileext == '.MOV':
		result, value = GetExif_MovieCommon(file, 'quicktime.creationdate')
	else:
		result, value = GetExif_MovieCommon(file, 'creation_time')
	if result == False:
		return result, value
	value	= value.replace('+0900', '')
	value	= value.replace('.000000Z', '')
	value	= FormatDatetime(value)
	return result, value



def GetExif_MovieLatLong(file):
	result, value = GetExif_MovieCommon(file, 'quicktime.location')
	if result == False:
		return False, -1, -1

	m = re.match(r'([\+,\-][\d,\.]+)([\+,\-][\d,\.]+)', value)
	if m:
		lat		= m.group(1)
		long	= m.group(2)
		lat		= lat.replace('+', '');
		long	= long.replace('+', '');
		return True, lat, long

	return False, -1, -1



def GetExif_ImageShotDate(file):
	if IsMovie(file):
		return GetExif_MovieShotDate(file)
	elif IsPhoto(file):
		return GetExif_PhotoShotDate(file)
	else:
		return False, 'NotImage'



def GetExif_ImageLatLong(file):
	if IsMovie(file):
		return GetExif_MovieLatLong(file)
	elif IsPhoto(file):
		return GetExif_PhotoLatLong(file)
	else:
		return False, -1, -1



def GetAverageHash(file):
	if IsMovie(file):
		print('IsMovie!, file=' + file)
		raise Exception

	if os.path.isdir(file):
		print('isdir!, file=' + file)
		raise Exception

	hash = imagehash.average_hash(Image.open(file))
	return hash



def GetAllHash(file):
	img	= Image.open(file)
	hasha = 0
	hashp = 0
	hashw = 0
	hashd = 0
	hasha = imagehash.average_hash(img)
	hashp = imagehash.phash(img)
	hashw = imagehash.whash(img)
	hashd = imagehash.dhash(img)
	return [hasha, hashp, hashw, hashd]



def GetTotalHash(file):
	img	= Image.open(file)
	hasha = imagehash.average_hash(img)
	hashp = imagehash.phash(img)
	hashw = imagehash.whash(img)
	hashd = imagehash.dhash(img)
	return str(hasha) + '_' + str(hashp) + '_' + str(hashw) + '_' + str(hashd)



def IsContentsSame(file_src, file_dst):
	if IsMovie(file_src):
		result1, shot_src	= GetExif_MovieShotDate(file_src)
		result2, len_src	= GetExif_MovieLength(file_src)
		result3, shot_dst	= GetExif_MovieShotDate(file_dst)
		result4, len_dst	= GetExif_MovieLength(file_dst)
		if result1 and result2 and result3 and result4 and shot_src == shot_dst and len_src == len_dst:
			return True
		else:
			return False
	else:
		val_src = GetTotalHash(file_src)
		val_dst = GetTotalHash(file_dst)
		if val_src == val_dst:
			return True
		else:
			return False



def TestSimilarity(dir, files):
	hash_tgt	= None
	for file in files:
		hash = GetAllHash(dir + file)
		if hash_tgt == None:
			hash_tgt = hash
			print('compare to ' + file)
		else:
			print(hash[0] - hash_tgt[0], hash[1] - hash_tgt[1], hash[2] - hash_tgt[2], hash[3] - hash_tgt[3])



def Debug():
#	result, lat, long = GetExif_ImageLatLong(path + 'Photo_20190101_102901.JPG')
#	print(lat, long)
#	result, lat, long = GetExif_ImageLatLong(path + 'Image_20190915_050934_iPhone7.MOV')
#	print(lat, long)
#	file	= 'E:\\Work\\Private\\Photo\\Data\\201908\\WSDR7063.MP4'
#	GetExif_MovieCommon(file, 'DEBUG')
#	result, value	= GetExif_MovieShotDate(file)
#	print('value=', value)

#	file	= 'E:\\Work\\Private\\Photo\\Data\\201412\\Movie_20141205_142549+0900.MOV'
#	GetExif_MovieCommon(file, 'DEBUG')
#	result, value	= GetExif_MovieShotDate(file)
#	print('value=', value)

#	tm_before	= datetime.datetime.now()
#	dir	= r'E:\Work\Temp\202008\\'
#	TestSimilarity(dir, ['IMG_2610.jpg', 'IMG_2611.jpg', 'IMG_2612.jpg'])
#	TestSimilarity(dir, ['IMG_2591.jpg', 'IMG_2592.jpg', 'IMG_2612.jpg'])
#	TestSimilarity(dir, ['Photo_20180508_210225.jpg', 'Photo_20180508_210227.jpg', 'IMG_2612.jpg'])
#	TestSimilarity(dir, ['IMG_5509.jpg', 'IMG_5511.jpg', 'IMG_5513.jpg'])
#	TestSimilarity(dir, ['tissue.jpg', 'IMG_6162.jpg', 'IMG_6165.jpg'])
#	TestSimilarity(dir, ['Photo_20180520_134110.jpg', 'Photo_20180520_134110_2.jpg'])
#	print(datetime.datetime.now() - tm_before)

	file	= r'E:\Work\Private\Photo\Data\201706\Image_20150802_102722_.MOV'
	file	= 'E:\\Work\\Private\\Photo\\Data\\201908\\WSDR7063.MP4'
	GetExif_MovieCommon(file, 'DEBUG')
#	result, value	= GetExif_MovieShotDate(file)
#	print('value=', value)
	result, value	= GetExif_MovieLength(file)
	print('value=', value)


if __name__ == '__main__':
	Debug()



