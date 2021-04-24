# coding: UTF-8
import io
import re
import os
import sys
import subprocess
import traceback
import pathlib
from pytz import timezone
import datetime
print('imported Common.py')




def GetRunPath():
	run_path = os.getcwd() + '/'
#	run_path = 'E:/Work/ReSkill/1_SoftwareLanguage/Python/'		# DEBUG
	return run_path



def GetSetting(file, path=''):
	if path == '':
		path = GetRunPath()

#	print('path=' + path)
	file	= path + file
	lines	= ReadLinesExCr(file)
	settings	= {}
	for line in lines:
		m_setting = re.match(r'([^\s]+)\s+([^\s]+)\s*' , line)
		if m_setting:
			key = m_setting.group(1)
			val = m_setting.group(2)
#			print('key=', key, 'val=', val)
			settings[key]	= val
#	print('settings=', settings)
	return settings



def ReadLinesExCr(file, enc='utf-8'):
	with open(file, 'r', encoding=enc) as fh:
		lines = fh.readlines()
	fh.close()
	for pos in range(len(lines)):
		lines[pos] = lines[pos].replace('\n', '')
	return lines



def MakeFolderIfNotExist(folder):
	if False == os.path.exists(folder):
		os.mkdir(folder)



s_print_on = False
def LogSetPrint(print_on):
	global s_print_on
	s_print_on = print_on



s_logs = []
def Log(str):
	global s_print_on
	s_logs.append(str)
	if s_print_on:
		print(str)



def LogSave(file):
	fh = io.open(file, 'w', encoding='cp932')
	for log in s_logs:
		fh.write(log + u'\n')
	fh.close()


s_cache_file = {}
def ReadFile_WithCache(file):
	key = re.sub('[:,/,\.]','_', file)
	if key in s_cache_file:
		Log('Cache exists=' + key)
	else:
		Log('Reading file=' + file, True)
		with io.open(file, 'r', encoding='cp932') as fh:
			lines = fh.readlines()
			lines = TrimLines(lines)
			fh.close()
			s_cache_file[key] = lines
	return s_cache_file[key]



def ReadFile_Decode(file):
	fh = io.open(file, 'r')
	lines = []
	exist = True
	while exist:
		try:
			line = fh.readline()
			if line == '':
				exist = False
		except UnicodeDecodeError:
			line = 'SKIP'
		lines.append(line)
#		print('line=' + line)
	fh.close()
	return lines



def WriteLines2File(file, lines, enc='UTF8'):
	fh_out = io.open(file, 'w', encoding=enc)
	for line in lines:
		fh_out.write(line + '\n')



def PrintAndExit(str):
	print (str)
	Log(str)
	jst_now = datetime.datetime.now(timezone('Asia/Tokyo'))
	str_jst = jst_now.strftime('%Y%m%d_%H%M%S')
	LogSave(GetRunPath() + 'PrintAndExit_' + str_jst + '.txt')
	input('PrintAndExit')
	sys.exit()



def WriteAndPrint(line, fh):
	fh.write(line + '\n')
	print (line)



def GetCurrentTimeStr():
	jst_now = datetime.datetime.now(timezone('Asia/Tokyo'))
	str_jst = jst_now.strftime('%Y%m%d_%H%M%S')
	return str_jst



def RoundDatetime2Day(dt):
	dtd	= datetime.date(dt.year, dt.month, dt.day)
	return dtd



def GetToday():
	dt_now		= datetime.datetime.now()
	dtd_now		= RoundDatetime2Day(dt_now)
	return dtd_now



def GetNearMonday(dtd = None):
	if dtd == None:
		dtd	= GetToday()
	
	
	week		= dtd_today.weekday()



def ConvDt2Ut(dt):
#	print('type=', type(dt))
	if type(dt) is datetime.date:
		dt	= datetime.datetime(dt.year, dt.month, dt.day, 0 ,0, 0)
	ut	= dt.timestamp()
	ut	= int(ut)
	return ut



def ConvMin2Time(min):
	if min < 0 or 59 < min:
		return '-'
	m		= min % 60
	h		= int(min / 60)
	dt		= datetime.datetime(2021, 1, 1, h, m)
	strtime	= str(dt.strftime('%H:%M'))
	return strtime



def ConvTime2Min(timedata):
	dt_time	= timedata
	if type(timedata) is str:
		dt_time	= datetime.datetime.strptime(timedata, '%H:%M')

	dt_dawn		= datetime.datetime(dt_time.year, dt_time.month, dt_time.day, 0, 0)
	delta		= dt_time - dt_dawn
	secs		= delta.total_seconds()
	mins		= secs / 60
	mins		= int(mins)
#	print('mins=', mins)
	return mins



def GetUpdatedDate(file):
	if not os.path.exists(file):
		mtime	= 0
	else:
		p		= pathlib.Path(file)
		stat	= p.stat()
		mtime	= stat.st_mtime
	dt		= datetime.datetime.fromtimestamp(mtime)
	return dt



def OpenFiles(files):
	for file in files:
		if re.match('.+xlsx*', file):
			OpenWithExcel(file)
		elif re.match('http', file):
			OpenWithChrome(file)
		elif file != '' and file != '-':
			subprocess.run('explorer {}'.format(file))



def OpenWithChrome(file):
	exes = [
		r'C:\Program Files\Google\Chrome\Application\chrome.exe',
	]
	for exe in exes:
		if os.path.exists(exe):
			str_exe	= exe + ' "' + file + '"'
#			print('str_exe=', str_exe)
			subprocess.Popen(str_exe)



def OpenWithExcel(file):
	exes = [
		r'C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE',
		r'C:\Program Files (x86)\Microsoft Office\Office14\EXCEL.EXE',
	]
	file	= file.replace('/', '\\')
	for exe in exes:
		if os.path.exists(exe):
			str_exe	= exe + ' "' + file + '"'
#			print('str_exe=', str_exe)
			subprocess.Popen(str_exe)



def PrintOrd(str_in):
	print('str_in=\n' + str_in)
	str_out	= ''
	for pos in range(len(str_in)):
		c	= str_in[pos]
		o	= ord(c)
		str_out	= str_out + hex(o) + ','
	print('[ord]=' + str_out)



def TrimLines(lines):
	lines_new = []
	for line in lines:
		if not re.match('^#', line):
			line = re.sub('\n', '', line)
			if not re.match('^\s*\Z', line):
				lines_new.append(line)
	return lines_new



def StrIfNotEmpty(str, stradd):
	if str == '':
		return str
	else:
		return str + stradd;



def SubStrBetween(str, start, end):
	retstr	= str
	if start != '':
		pos	= retstr.find(start)
		if pos == -1:
			return ''
		retstr	= retstr[pos + len(start):]

	if end != '':
		pos	= retstr.find(end)
		if pos == -1:
			return ''
		retstr	= retstr[0: pos]

	return retstr



if __name__ == '__main__':
	dt	= GetToday()
#	dt	= datetime.datetime.now()
#	ConvDt2Ut(dt)
	GetUpdatedDate('C:/work/Sky/1_情報共有(CSD)/1_日報/Others/Kanso.txt')



