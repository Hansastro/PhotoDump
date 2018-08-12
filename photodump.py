import os
import re
import piexif

base10='0123456789'
base16='0123456789ABCDEF'
base2 ='01'
base23 = 'ABCDEFGHJKLMNPRSTUVWXYZ'
base31='23456789ABCDEFGHJKLMNPRSTUVWXYZ'
base31 = 'TE8CA6ZNFGXBLWU79YHV3R4KS5MPJ2D'

def _checkTrailingSlash(path='./'):
    '''
    Check if a slash is presen tat the end of o path.
    If not add it.
    
    parameters:
    path as a string
    
    return value:
    path with  a trailing slash
    '''
    if path[-1] != '/':
        return path + '/'
    else:
        return path

def _isTargetedFile(filename='', targetFiles=['CR2']):
    '''
    Check if a file name has the correct extension
    
    parameters:
    filename as a string (with complete path or not
    targetFiles as an array of all valid extention.
    
    return value:
    True if the filename is correct.
    False otherwise.
    '''
    targetFilePattern = targetFiles[0]
    for t in targetFiles[1:]:
        targetFilePattern += '|' + t
    #print(os.path.basename(filename))
    regexPattern = '^.*\.({})$'.format(targetFilePattern)
    #print(regexPattern)
    filePattern = re.compile(regexPattern, re.IGNORECASE)
    if filePattern.match(filename):
        return True
        #print('OK')
    else:
        return False
        #print('KO')
    
def listFiles(srcPath='.'):
    '''
    list all image files with their path
    
    parameters:
    source path to begin
    
    return value
    a list of all files with their path
    '''
    filesList = []
    filesInDir = os.listdir(srcPath)
    for f in filesInDir:
        fileWithPath = _checkTrailingSlash(srcPath) + f
        if os.path.isfile(fileWithPath):
            #print('{} is  a file'.format(fileWithPath))
            if _isTargetedFile(fileWithPath, targetFiles = ['CR2']):
                filesList.append(fileWithPath)
        elif os.path.isdir(fileWithPath):
            #print('{} is a directory'.format(fileWithPath))
            filesList += listFiles(fileWithPath)
        else:
            print('file {} not found'.format(fileWithPath))
    return filesList

def getImageParameters(imagePath):
    '''
    Get parameters of the image (in Exif)
    
    Parameters:
    path of the image as string
    
    return value:
    A dictionary with image parameters
       number of the image file
       camera model
       ISO
       Aperture
       Exposition
       Focal length
       Date and time
    '''
    imageParameters = {}
    #Load exif information from the file
    exifData = piexif.load(imagePath)
    #Get the image number
    imageNumberRe = re.compile('[0-9]+')
    imageNumber = imageNumberRe.search(os.path.basename(imagePath)).group()
    imageNumber = int(imageNumber)
    imageParameters['Image Number'] = '{:04d}'.format(imageNumber)
    
    imageParameters['Camera'] = exifData['0th'][0x110].decode("utf-8")
    imageParameters['ISO'] = exifData['Exif'][0x8827]
    aperture = exifData['Exif'][0x829d]
    imageParameters['Aperture'] = aperture[0] / aperture[1]
    exposureTime = exifData['Exif'][0x829a]
    imageParameters['Exposure Time'] = exposureTime[0] / exposureTime[1]
    focalLength = exifData['Exif'][0x920a]
    imageParameters['Focal Length'] = focalLength[0] / focalLength[1]
    imageParameters['Date Time Original'] = exifData['Exif'][0x9003].decode("utf-8")
    
    return imageParameters

def convertBaseNtoM(number, baseN, baseM):
    '''
    Convert a number in a base n to a base m
    
    parameters:
    number as a string
    baseN as a string 
    baseM as a string
    
    return value:
    the converted number in base m as a string
    '''
    result = ''
    
    # Convert the number in an integer
    sum = 0
    for i in range(len(number)):
        sum += baseN.index(number[i]) * len(baseN)**(len(number) - i - 1)
    
    # Convert the integer into baseM
    exponent = 1
    while sum - len(baseM)**exponent >= 0:
        exponent += 1
    
    for i in range(exponent - 1, -1, -1):
        digit = int(sum // len(baseM)**(i))
        result += baseM[digit]
        sum -= digit * len(baseM)**(i)
    
    return result
