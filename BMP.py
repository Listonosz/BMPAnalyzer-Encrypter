from PIL import Image
import numpy as np
import math
import matplotlib.pyplot as plt
import cv2

def loadnbitsmOffset(file_handler, n, m):
    file_handler.seek(m, 0)
    rawData = file_handler.read(n)
    return rawData

def loadHeader(open_bmp):
    header = {}
    header["Signature"] = loadnbitsmOffset(open_bmp, 2, 0)
    header["FileSize"] = loadnbitsmOffset(open_bmp, 4, 2)
    header["reserved"] = loadnbitsmOffset(open_bmp, 4, 6)
    header["DataOffset"] = loadnbitsmOffset(open_bmp, 4, 10)
    return header

def loadInfoHeader(open_bmp):
    infoHeader = {}
    infoHeader["Size"] = loadnbitsmOffset(open_bmp, 4, 14)
    infoHeader["Width"] = loadnbitsmOffset(open_bmp, 4, 18)
    infoHeader["Height"] = loadnbitsmOffset(open_bmp, 4, 22)
    infoHeader["Planes"] = loadnbitsmOffset(open_bmp, 2, 26)
    infoHeader["BitCount"] = loadnbitsmOffset(open_bmp, 2, 28)
    infoHeader["Compression"] = loadnbitsmOffset(open_bmp, 4, 30)
    infoHeader["ImageSize"] = loadnbitsmOffset(open_bmp, 4, 34)
    infoHeader["XpixelsPerM"] = loadnbitsmOffset(open_bmp, 4, 38)
    infoHeader["YpixelsPerM"] = loadnbitsmOffset(open_bmp, 4, 42)
    infoHeader["ColorsUsed"] = loadnbitsmOffset(open_bmp, 4, 46)
    infoHeader["ColorsImportant"] = loadnbitsmOffset(open_bmp, 4, 50)
    return infoHeader

def loadPixels(open_bmp):
    header = loadMeta(open_bmp)
    DIB = header["Size"]
    offset = header["DataOffset"]
    bpp = header["BitCount"]
    numofColors = pow(2,bpp)
    size = header["ImageSize"]
    if(bpp <= 8):
        colortable = []
        #Load Color Table
        for i in range(numofColors):
            c1 = int.from_bytes(loadnbitsmOffset(open_bmp, 1, 14+DIB), byteorder='big')
            DIB += 1
            c2 = int.from_bytes(loadnbitsmOffset(open_bmp, 1, 14+DIB), byteorder='big')
            DIB += 1
            c3 = int.from_bytes(loadnbitsmOffset(open_bmp, 1, 14+DIB), byteorder='big')
            DIB += 1
            cr = int.from_bytes(loadnbitsmOffset(open_bmp, 1, 14+DIB), byteorder='big')
            DIB += 1
            colortable.append([c3,c2,c1,cr])

        #Load indexs of colors in pallete
        pixels_wp = []
        for i in range(size):
            pix = int.from_bytes(loadnbitsmOffset(open_bmp, 1, offset+i), byteorder='big')
            pixels_wp.append(pix)

        #Assing a correct color to pixel from color table
        pixels = []
        for i in range(len(pixels_wp)):
            color_num = pixels_wp[i]
            real_value = colortable[color_num]
            pixels.append(real_value)
        return [pixels, colortable]

    elif(bpp > 8):
        size = size/(bpp/8)
        pixels = []
        i = 1
        while i <= size:
            blue = loadnbitsmOffset(open_bmp, 1, offset)
            offset += 1
            green = loadnbitsmOffset(open_bmp, 1, offset)
            offset += 1
            red = loadnbitsmOffset(open_bmp, 1, offset)
            offset += 1
            blue = int.from_bytes(blue, byteorder='big')
            green = int.from_bytes(green, byteorder='big')
            red = int.from_bytes(red, byteorder='big')
            pixels.append([red, green, blue])
            i = i + 1
        return [pixels, list()]

def makeReadable(bmp):
    readable_bmp = {}
    for props in bmp:
        if (props == "Signature"):
            readable_bmp[props] = bmp[props].decode()
            continue
        readable_bmp[props] = int.from_bytes(bmp[props], byteorder="little")
    return readable_bmp


def loadMeta(open_bmp):
    filemeta = loadHeader(open_bmp)
    imagemeta = loadInfoHeader(open_bmp)
    filemeta.update(imagemeta)
    readable = makeReadable(filemeta)
    return readable

def getRowSize(meta):
    bpp = meta["BitCount"]
    width = meta["Width"]
    row = math.ceil(bpp*width/32)
    return row*4

def makeimagefromPixels(meta, pixels):
    w, h = meta["Width"], meta["Height"]
    if( len(pixels[0]) == 3):
        data = np.zeros((h, w, 3), dtype=np.uint8)
    else: return "ERROR, bad pixel format"
    i = int(h)-1
    while i > 0:
        for j in range(w):
            data[i][j] = pixels[j]
        i = i - 1
        pixels = pixels[w:]
    return data

def writeImagetoFile(name, meta, pixels, colorpallete=list()):
    fOut = open(name, "wb")
    metaVal = list(meta.values())
    SIG = metaVal.pop(0).encode('utf-8')
    fOut.write(SIG)
    for i in range(len(metaVal)):
        if( i == 6 or i == 7 ):
            byte = metaVal[i].to_bytes(2, byteorder='little', signed=True)
            fOut.write(byte)
            continue
        byte = metaVal[i].to_bytes(4, byteorder='little', signed=True)
        fOut.write(byte)

    if (len(colorpallete) != 0):
        for color in colorpallete:
            byte = bytes(color)
            fOut.write(byte)
    for pixel in pixels:
        byte = bytes(pixel)
        fOut.write(byte)
    fOut.close()

def anonimize_ask(meta):
    for items in meta:
        print("Czy wyzerowac :", items)
        x = input()
        if x == 't':
            meta[items] = 0
        else:
            continue
    return meta

def anonimize(meta):
    required = ['Signature', 'DataOffset', 'Size', 'Width', 'Height', 'Planes', 'BitCount']
    for items in meta:
        if items in required:
            continue
        else:
            meta[items] = 0
    return meta


file_han = open('TestData/fft.bmp', 'rb')
meta = loadMeta(file_han)
[obraz, paleta] = loadPixels(file_han)
print(meta)
meta = anonimize(meta)
writeImagetoFile("OWN.bmp", meta, obraz, paleta)

data = makeimagefromPixels(meta,obraz)
img = Image.fromarray(data)
img.save('LIB.bmp')

file_han.close()

plt.figure(figsize=(6.4*5, 4.8*5), constrained_layout=False)

img2 = cv2.imread("TestData/fft.bmp", 0)
original = np.fft.fft2(img2)
fshift = np.fft.fftshift(original)
magnitude_spectrum = 20*np.log(np.abs(fshift))

plt.subplot(121), plt.imshow(magnitude_spectrum, "gray"), plt.title("Spectrum")

plt.subplot(122), plt.imshow(np.angle(original), "gray"), plt.title("Phase Angle")
plt.show()