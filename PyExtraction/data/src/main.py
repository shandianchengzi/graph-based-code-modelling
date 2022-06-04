# coding:utf-8
import re
import os
import gzip
import sys
import json

# Usage: ./main.py <INPUT_DIR> <OUTPUT_DIR>
# Usage eg: python ./main.py data/src/ data/

INPUT_DIR=sys.argv[1]
OUTPUT_DIR=sys.argv[2]


def saveResult(filepath,result):
  result['repo']=filepath[len(INPUT_DIR):]
  with open(OUTPUT_DIR+"result.jsonl","a",encoding='utf-8') as pf:
    pf.write(json.dumps(result))
    pf.write('\n')


def isDef(line):
  if "def" not in line.split(" "): # 无def时
    return False,0
  lineRmSpace=line.strip()
  if (lineRmSpace=='') or (lineRmSpace[0]=='#'): # 过滤空行和注释行
    return False,0
  return True
  

def dealFile(filepath):
  tofind = "\s*def "
  result={}
  with open(filepath,"rt",encoding='utf-8') as f: 
    allLines = f.readlines()                  
    flag = 0
    index = 0
    for line in allLines:
      # 不在函数体内时，找寻def
      if(flag==0):
        # 查找def
        if(isDef(line)==False):
          continue
        # 若有def，初始化各种参数，准备存储结果
        index = line.find("def")
        flag = 1
        result={}
        result['orginal_string']=line
        result['code']=line
      # 在函数体内时，直接将结果加到后面
      else:
        result['orginal_string']=result['orginal_string']+line
        lineRmSpace=line.strip()
        if (lineRmSpace=='') or (lineRmSpace[0]=='#'): # 过滤空行和注释行
          continue
        # 读到函数体结尾
        if(re.findall("\S",line[0:index])): # 若第index个字符前不是空白，并且该行不是空行或注释
          flag=0
          saveResult(filepath,result)  # 存储结果
          if(isDef(line)): # 若该行是新函数体的开始，则直接初始化
            index = line.find("def")
            flag = 1
            result={}
            result['orginal_string']=line
            result['code']=line
        # 并非函数体结尾
        result['code']=result['code']+line
     
    

def searchInDir(dirname):
  for root,dirs,files in os.walk(dirname):
    # 递归遍历目录
    for dir in dirs:
      searchInDir(dir)
    for filename in files:
      # 过滤.py文件
      if(os.path.splitext(filename)[1]!='.py'):
        continue
      # 处理文件
      filepath = os.path.join(root,filename)
      dealFile(filepath)
      
      
searchInDir(INPUT_DIR)