#coding=utf

import os
import re
import logging
import tkinter
import tkinter.filedialog
import threading
import time
import shutil
from argparse import ArgumentParser 

#调试标志
debug_flag=False
#debug_flag=True


if (1):
	'''
	debug配置部分
	'''
	if debug_flag:
		loggerLevel=logging.DEBUG
	else:
		loggerLevel=logging.ERROR
	
	log_path=os.path.abspath(".")
	log_file_name=log_path+os.sep+"log"+os.sep+"mylog.txt"



	# 创建一个logger
	lg = logging.getLogger('mylogger')
	lg.setLevel(loggerLevel)
	formatter = logging.Formatter('%(name)s:\t%(filename)s[line:%(lineno)d]>>>%(funcName)s:\n\t%(message)s')
	
	# 创建一个handler，用于写入日志文件
	fh = logging.FileHandler(log_file_name,"w")
	fh.setLevel(loggerLevel)
	fh.setFormatter(formatter)
	
	# 再创建一个handler，用于输出到控制台
	ch = logging.StreamHandler()
	ch.setLevel(loggerLevel)
	ch.setFormatter(formatter)
	
	# 给logger添加handler
	#lg.addHandler(ch)
	lg.addHandler(fh)


def main():
	print("convert begin:)------------------------")
	time1=time.strftime("%H:%M:%S",time.localtime(time.time()))
	print("Begin:%s"%time1)
	parser = ArgumentParser(description="Text file handle")
	'''
	parser.add_argument("i",action="store",dest="input_file")
	parser.add_argument("c",action="store",dest="config_file")
	parser.add_argument("o",action="store",dest="output_file")
	'''
	parser.add_argument("sourceFileName",help="input file")
	parser.add_argument("dictFileName",help="diction file")
	parser.add_argument("resultFileName",help="output file")
	
	args = parser.parse_args() 

	sourceFileName=args.sourceFileName
	dictFileName=args.dictFileName
	resultFileName=args.resultFileName


	
	fileHandle=FileHandle()
	fileHandle.setinput_file(sourceFileName)
	fileHandle.setoutput_file(resultFileName)
	fileHandle.setDictionFile(dictFileName)
	fileHandle.transfer()
	
	
	time1=time.strftime("%H:%M:%S",time.localtime(time.time()))
	print("End:%s"%time1)
	
	
	
		
class FileHandle():

	def __init__(self,input_file="",output_file="",diction_file=""):
		self.input_file=input_file
		self.output_file=output_file
		self.diction_file=diction_file
		
		self.tmp_path=os.path.abspath(".")+os.sep+"tmp"
		self.tmp_part_file_path=self.tmp_path+os.sep+"temp_part_file"
		self.after_add_dict_path=self.tmp_path+os.sep+"added_dict_file"
		
		self.line_count=200
		
	def	setinput_file(self,input_file):
		self.input_file=input_file
	
	
	def setoutput_file(self,output_file):
		self.output_file=output_file
		
		
	def setDictionFile(self,diction_file):
		self.diction_file=diction_file
		
	def transfer(self):
		self.split_file()
		self.add_diction_to_files()
		self.join_file()
	
	def split_file(self):
		if self.input_file and os.path.exists(self.input_file):
		
			try:
				if os.path.exists(self.tmp_part_file_path):
					shutil.rmtree(self.tmp_part_file_path,True)
				os.makedirs(self.tmp_part_file_path)
				
				with open(self.input_file,encoding='utf-8') as f:#使用with读取文件
					temp_count=0
					temp_content=[]
					part_num=1
					
					for line in f:
						if temp_count<self.line_count:
							temp_count+=1
						else:
							self.write_file(part_num,temp_content)
							part_num+=1
							temp_count=1
							temp_content=[]
						
						temp_content.append(line)
						
					else:
						self.write_file(part_num,temp_content)
			except IOError as err:
				print(err)
		else:
			print("%s is not a validate file"%self.input_file)
			
			
			
	def write_file(self,part_num,*line_content):
		
		write_to_file_name=self.get_part_file_name(part_num)
		
		#lognew1=logging.getLogger("new1")
		#lognew1.debug("write_to_file_name=%s"%write_to_file_name)
		
		try:
			with open(write_to_file_name,"w",encoding='utf-8') as write_to_file:
				write_to_file.writelines(line_content[0])
		except IOError as err:
			print(err)
			
	
	def get_part_file_name(self,part_num):
		part_num="%03d"%(part_num)
		output_file_name=self.tmp_part_file_path+os.sep+"temp_file_"+str(part_num)+".part"
		return output_file_name
		
		
	def add_diction_to_files(self):
		if os.path.exists(self.after_add_dict_path):
			shutil.rmtree(self.after_add_dict_path)
		os.makedirs(self.after_add_dict_path)
		
		parts=os.listdir(self.tmp_part_file_path)
		parts.sort()
		
		lg.debug("parts=%s"%parts)
		lg.debug("parts.length()=%s"%len(parts))
		
		#分成4个list，每个list中的文件使用一个线程进行处理
		from_file_name_list1=[]
		from_file_name_list2=[]
		from_file_name_list3=[]
		from_file_name_list4=[]
		
		
		thread_list=[]
		
		#如果文件数小于4，只放在第一个list中
		if len(parts)<4:
			from_file_name_list1=parts
			
			lg.debug("from_file_name_list1=%s"%from_file_name_list1)
			
			t1=threading.Thread(target=self.add_diction_by_list,args=(from_file_name_list1,))
			t1.setDaemon(True)
			t1.start()
			thread_list.append(t1)
			
		else:
			for j in range(0,len(parts)):
				
				lg.debug("len-parts=%s"%len(parts))
				
				if j%4==0:
					from_file_name_list1.append(parts[j])
				if j%4==1:
					from_file_name_list2.append(parts[j])
				if j%4==2:
					from_file_name_list3.append(parts[j])
				if j%4==3:
					from_file_name_list4.append(parts[j])
					
			t1=threading.Thread(target=self.add_diction_by_list,args=(from_file_name_list1,))
			t1.setDaemon(True)
			t1.start()
			thread_list.append(t1)
			
			t2=threading.Thread(target=self.add_diction_by_list,args=(from_file_name_list2,))
			t2.setDaemon(True)
			t2.start()
			thread_list.append(t2)
			
			t3=threading.Thread(target=self.add_diction_by_list,args=(from_file_name_list3,))
			t3.setDaemon(True)
			t3.start()
			thread_list.append(t3)
			
			
			t4=threading.Thread(target=self.add_diction_by_list,args=(from_file_name_list4,))
			t4.setDaemon(True)
			t4.start()
			thread_list.append(t4)
			
			
		for thread in thread_list:
				thread.join()
				
				
	def add_diction_by_list(self,from_file_name_list):
		for filename in from_file_name_list:
			from_file_name=os.path.join(self.tmp_part_file_path,filename)
			
			to_file_name=self.after_add_dict_path+os.sep+"ok_"+filename
			self.add_diction(from_file_name,to_file_name)
			
	def add_diction(self,from_file_name,to_file_name):
		
		f1line=""
		f2line=""
		f3lin3=""
		lineAfterRemark=""
		
		f1=open(from_file_name,'r',encoding='utf-8')
		f2=open(to_file_name,'w',encoding='utf-8')
		f3=open(self.diction_file,'r',encoding='utf-8')	
		i=0

		for f1line in f1:
			i=i+1
			
			#从待处理文件中取出一行，针对每个单词，查找是否在字典文件中
			lineAfterRemark=self.add_diction_by_line(f1line,f3)
			
			f2.write(f1line)
			f2.write(lineAfterRemark)
			
		f1.close
		f2.close
		f3.close
		
	def add_diction_by_line(self,beforeLine,dictHandler):
	
	#从待处理文件中取出一行，针对每个单词，查找是否在字典文件中，如果在，则把字典文件中的哪一行解释作为新的一行在行尾添加

		addLine=""
		newLine=""
		dictHandler.seek(0)
		
		for dictLine in dictHandler:
			aIndex=0
			
			#从字典文件中分离出第一个字符串，即需要解释的单词，放到dictWordList[0]
			dictWordList=dictLine.split()
			if dictWordList==[]:
				continue
			
			dictWord=dictWordList[0]
			
			#容错处理，如果取出的第一个单词不是字母，说明有问题，直接跳过
			if dictWord[0].isalpha is False:
				continue
			#格式化字符串，把所有的干扰字符都换成空格	
			#to_find_string=beforeLine.replace(",","").replace("."," ").replace("\""," ").replace("\'"," ").replace(";"," ").replace("-"," ").replace("*"," ").replace("\\"," ").replace("["," ").replace("]"," ").lower()
			
			p=re.compile("[^a-z]+")
			to_find_string=p.sub(" ",beforeLine.lower())
			
			dictWord=dictWord.lower()
			
			if len(dictWord)<=4:
				find_word=" "+dictWord+" "
				find_word1=dictWord+" "
			else:
				find_word=" "+dictWord
				find_word1=dictWord
				
			#to_find_string中查找前面有空格的词，如果本身单词长度太小，需要后面也是空格
			aIndex=to_find_string.find(find_word)
			if aIndex==-1:
				if to_find_string.startswith(find_word1)!=True:
					continue
									
			newLine=newLine+dictLine
			
			if len(newLine)>=2:
				addLine="--------------------------------------------\n"+newLine+"--------------------------------------------\n"
		return addLine
		
	def join_file(self):
		output=open(self.output_file,'wb')
		
		parts=os.listdir(self.after_add_dict_path)
		parts.sort()
		
		for filename_without_path in parts:
			file_name=os.path.join(self.after_add_dict_path,filename_without_path)
			fileobj=open(file_name,'rb')
			while 1:
				filebytes=fileobj.read()
				if not filebytes:
					break
				output.write(filebytes)
			fileobj.close()
		output.close()
		
			
			
if __name__=="__main__":
	main()