# -*- coding: utf-8 -*-
"""
Library for fast operations on images
"""
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os
from . import utils
from tensorflow.keras.utils import img_to_array
import basic.plots as bp

def plotImage(img, convertBGR2RGB = False, title = None):
    '''
    Shows an image in a matplotlib figure

    MATPLOTLIB wants RGB image

    Parameters
    ----------
    img : matrix height*width*N
        DESCRIPTION.
    convertBGR2RGB : bool, optional
        if conversion from BGR to RGB should be applied in order to show the 
        image with proper colors in matplotlib environment. The default is False.
    title : TYPE, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    None.

    '''
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.grid(True)
    if convertBGR2RGB:
        ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), interpolation = None)
    else:
        ax.imshow(img, interpolation = None)
    if title:
        ax.set_title(title)

    return fig, ax

def imagesDictInSubpplots(imagesDict, sharex = True, sharey = True,
                   nrows = 0, ncols = 0, mainTitle = ''):
    '''
    From dictionary of images calls basic.createSubplots and shows every image

    Parameters
    ----------
    imagesDict : TYPE
        DESCRIPTION.
    sharex : TYPE, optional
        DESCRIPTION. The default is True.
    sharey : TYPE, optional
        DESCRIPTION. The default is True.
    nrows : TYPE, optional
        DESCRIPTION. The default is 0.
    ncols : TYPE, optional
        DESCRIPTION. The default is 0.
    mainTitle : TYPE, optional
        DESCRIPTION. The default is ''.
    listOfTitles : TYPE, optional
        DESCRIPTION. The default is [''].

    Returns
    -------
    None.

    '''
    # convert to list to make reference by index possible
    listImagesDictKeys = list(imagesDict.keys())
    listImagesDictValues = list(imagesDict.values())

    fig, ax = bp.createSubPlots(len(imagesDict), sharex, sharey,
                                nrows, ncols, mainTitle)
    counter = -1
    for axes in ax:
        for this_ax in axes:
            counter += 1
            this_ax.grid()
            this_ax.set_title(listImagesDictKeys[counter])
            if listImagesDictValues[counter] is not None:
                this_ax.imshow(listImagesDictValues[counter])
    plt.tight_layout()


def cropImageTLBR(img, tl, br, showImage = False, convertBGR2RGB = False):
    '''
    Crop image from top-left to bottom-right

    Parameters
    ----------
    img : matrix width*height*N
        N can be whatever valu >= 1.
    tl : list of [x, y] coordinates
        top left coordinates.
    br : list of [x, y] coordinates
        low right coordinates.

    Returns
    -------
    img : image: matrix
        cropped image.

    '''
    assert tl[0] < br[0] and tl[1] < br[1], \
        f"not valid top-left/bottom-right coordinates. \ntl must be lower than br, got tl: {tl} and br: {br}"
    # example
    # tl = [686, 348]
    # br = [758, 388]
    try:
        img = img[tl[1]:br[1], tl[0]:br[0],:]
    except:
        img = img[tl[1]:br[1], tl[0]:br[0]]

    if showImage:
        plotImage(img, title = 'cropped image', convertBGR2RGB = convertBGR2RGB)

    return img

def cropImageNRegions(img, nrows = 2, ncols = 2, showImage = False):
    try:
        h, w, _ = img.shape
    except:
        h, w = img.shape
    imagesDict = {}
    for i in range(nrows):
        for j in range(ncols):
            try:
                imagesDict[str(i)+'-'+str(j)] = img[int(i*h/nrows):int((i+1)*h/nrows), int(j*w/ncols):int((j+1)*w/ncols),:]
            except:
                imagesDict[str(i)+'-'+str(j)] = img[int(i*h/nrows):int((i+1)*h/nrows), int(j*w/ncols):int((j+1)*w/ncols)]

    if showImage:
        # call function for image show
        imagesDictInSubpplots(imagesDict, nrows = nrows, ncols = ncols,
                              mainTitle = 'image cropped in {} row[s] * {} column[s]'.format(nrows, ncols))

    return imagesDict

def getFrameFromVideo(videoCompletePath, frameNum, showImage = False,
                      convertBGR2RGB = False):
    '''
    from a video, returns the frame 
    
    Parameters
    ----------
    videoCompletePath : string
        path to the video.
    frameNum : int
        number of the frame that wants to be retreived.
    showFrame : boolean, optional
        show the frame in an image. The default is False.
    convertBGR2RGB : see plotImage
    
    Returns
    -------
    frame : image
        present in the video at the given frame.
    
     '''
    # create the video capture element
    video = cv2.VideoCapture(videoCompletePath)
    # get the number of total frame
    total = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if total-1 < frameNum:
        frameNum = total-1
    
    # get the frame 
    video.set(1, frameNum); 
    ret, frame = video.read()

    if showImage:
        plotImage(img = frame,
                  convertBGR2RGB = convertBGR2RGB,
                  title = os.path.split(videoCompletePath)[1] +
                  ' [frame {} of {}]'.format(frameNum,total))
    return frame

def fromCoordsToTLBR(coords_tuple, returnInt = True):
    '''
    from tuples of coords of the type [(x1,y1,z1), (x2,y2,z2),...]
    to 2 lists:
        - tl: [min[x1,x2,...],min[y1,y2,...],min[z1,z2,...]]
        - br: [max[x1,x2,...],max[y1,y2,...],max[z1,z2,...]]
    

    Parameters
    ----------
    coords_tuple : TYPE
        DESCRIPTION.

    Returns
    -------
    tl : TYPE
        DESCRIPTION.
    br : TYPE
        DESCRIPTION.
    '''
    tl = []
    br = []
    for i in range(len(coords_tuple[0])):
        #all the i-th coord of each tuple
        tmp = [x[i] for x in coords_tuple]
        if returnInt:
            # get the lowest value and put in tl
            tl.append(int(np.floor(np.amin(tmp))))
            # get the greates value and put in br
            br.append(int(np.ceil(np.amax(tmp))))
        else:
            # get the lowest value and put in tl
            tl.append(np.amin(tmp))
            # get the greates value and put in br
            br.append(np.amax(tmp))

    return tl, br

def getCoords_user(img, nPoints = -1, title = ''):
    orig_img = img.copy()
    tl = [0,0]
    br = [img.shape[1],img.shape[0]]

    while True:
        fig, ax = plotImage(orig_img, title = title+'select the {} points'.format(nPoints))
        coords_tuple = plt.ginput(n=nPoints, timeout=-1, show_clicks=True)
        tl, br = fromCoordsToTLBR(coords_tuple)
        img = cropImageTLBR(orig_img, tl, br)

        imgName = 'Press Enter to confirm'
        cv2.imshow(imgName, rescaleToMaxPixel(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), 800))
        key = cv2.waitKey(0)
        if key == ord('\r'): # enter key
            plt.close(fig)
            cv2.destroyWindow(imgName)
            break
        else:
            plt.close(fig)
            cv2.destroyWindow(imgName)
            continue
    return tl, br

def getImagesDictBasicTransform(img, imgFormat = 'BGR', showImage = False):
    '''
    Applies basic transformation on the input image and saves it in a dictionary.
    Operations are:
        - splitting in RGB
        - splitting in HSV
        - splitting in LAB
        - grayscale

    Parameters
    ----------
    img : matrix width*height*3
        assumed BRG, it's possible to specify it's RGB with imgFormat flag.
    imgFormat : TYPE, optional
        DESCRIPTION. The default is 'BGR'.
    showImage : TYPE, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    imagesDict : dictionary
        contains as keys the name of the corresponding image.

    '''
    # check image format
    validImgFormats = ['BGR', 'RGB']
    assert imgFormat in validImgFormats, \
    f"imgFormat not valid, possible values are: {validImgFormats}"

    if imgFormat == 'BGR':
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # conversion
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    img_lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)

    # create images dictionary
    imagesDict = {}
    imagesDict['RGB'] = img
    for i in range(3):
        imagesDict['RGB ch' + str(i)]=img[:,:,i]
    imagesDict['HSV'] = img_hsv
    for i in range(3):
        imagesDict['HSV ch' + str(i)]=img_hsv[:,:,i]
    imagesDict['HSV'] = img_lab
    for i in range(3):
        imagesDict['LAB ch' + str(i)]=img_lab[:,:,i]
    imagesDict['gray'] = img_gray

    # print(imagesDict.keys())
    if showImage:
        # call function for image show
        imagesDictInSubpplots(imagesDict, ncols = 4,
                              mainTitle = 'image inspection on the different channels')

    return imagesDict

def filterImage3Channels(img, ch0 = [0, 255], ch1 = [0, 255], ch2 = [0, 255], showPlot = False):
    '''
    given an image, checks which pixels have value inside the ranges specified 
    in ch0, ch1 and ch2. Returns another image with 0 (or [0,0,0]) where the 
    condition is not satisfied and 255 (or [255,255,255]) where it is

    Parameters
    ----------
    img : TYPE
        DESCRIPTION.
    ch0 : TYPE, optional
        DESCRIPTION. The default is [0, 255].
    ch1 : TYPE, optional
        DESCRIPTION. The default is [0, 255].
    ch2 : TYPE, optional
        DESCRIPTION. The default is [0, 255].
    showPlot : TYPE, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    result : TYPE
        DESCRIPTION.

    '''
    true = img*0+255

    lower = np.array([ch0[0], ch1[0], ch2[0]])
    upper = np.array([ch0[1], ch1[1], ch2[1]])

    mask = cv2.inRange(img, lower, upper)
    result = cv2.bitwise_and(true, true, mask = mask)

    if showPlot:
        imagesDict={}
        imagesDict['orig'] = img
        imagesDict['filt'] = result
        imagesDictInSubpplots(imagesDict, sharex = True, sharey = True,
                           nrows = 0, ncols = 1,
                           mainTitle = 'filt with ' + str(ch0) + ' ' + str(ch1) + ' ' + str(ch2))
    return result

def projection(img, showPlot = False):
    '''
    horizontal and vertical projection of the image
    
    Parameters
    ----------
    one_channel_img : matrix height*width*1
        

    Returns
    -------
    hProj : np.array
        mean of each row [array of height elements]
    vProj : np.array
       mean of each column [array of width elements]

    '''
    # represent each row with the mean value [array of height elements]
    hProj = np.nanmean(img, axis=1)
    # represent each column with the mean value [array of width elements]
    vProj = np.nanmean(img, axis=0)

    if showPlot:
        fig = plt.figure()
        ax1 = fig.add_subplot(221)
        ax2 = fig.add_subplot(222)
        ax3 = fig.add_subplot(224)

        ax1.plot(hProj,np.arange(0,len(hProj)),'.-')
        ax1.set_ylim(ax1.get_ylim()[::-1])
        ax1.set_title('rows [hProj]')

        ax2.imshow(img, aspect="auto")

        ax3.plot(vProj,'.-')
        ax3.set_title('cols [vProj]')

        ax1.grid(True)
        ax2.grid(True)
        ax3.grid(True)

    return hProj, vProj

def getTLBRprojection(img, discValue = 0, showPlot = False):
    '''
    

    Parameters
    ----------
    img : TYPE
        DESCRIPTION.
    discValue : int or float, depending on image, optional
        discarde value. The default is 0.
    showPlot : TYPE, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    tl : TYPE
        DESCRIPTION.
    br : TYPE
        DESCRIPTION.

    '''
    hProj, vProj = projection(img, showPlot)

    # give widest dimensions
    tl = [0, 0]
    br = img.shape[0:2]
    br = [br[1], br[0]]

    try:
        tl[0] = np.argwhere(vProj!=discValue)[0][0]
    except:
        pass
    try:
        tl[1] = np.argwhere(hProj!=discValue)[0][0]
    except:
        pass
    try:
        br[0] = np.argwhere(vProj!=discValue)[-1][0]
    except:
        pass
    try:
        br[1] = np.argwhere(hProj!=discValue)[-1][0]
    except:
        pass

    return tl, br

def findStartStopValues(array, discValue = 0, maxIntervals = 100):
    start = []
    stop = []

    for i in np.arange(1, len(array)-1, 1):
        if array[i-1] == discValue and array[i] != discValue:
            start.append(i)
        if array[i] != discValue and array[i+1] == discValue:
            stop.append(i)

    # in case the array starts or ends without discarded values,
    # it's necessary to add them
    if len(start) == 0 or len(stop) == 0:
        if len(start) == 0:
            start.insert(0, 0)
        if len(stop) == 0:
            stop.append(len(array))
    else:
        if start[0] > stop[0]:
            start.insert(0, 0)
        if start[-1] > stop[-1]:
            stop.append(len(array))
        # might give problems
        # todo check this

    start, stop = checkMaxIntervalsStartStop(start, stop, maxIntervals)

    return start, stop

def checkMaxIntervalsStartStop(start, stop, maxIntervals = 100):
    assert len(start) == len(stop), f"start and stop should be of the same lenght, got {len(start)} and {len(stop)}"
    start = np.array(start)
    stop = np.array(stop)
    while len(start) > maxIntervals:
        closestIndexBetweenStartStop = np.argmin(start[1:]-stop[0:-1])
        start = np.delete(start, closestIndexBetweenStartStop+1)
        stop = np.delete(stop, closestIndexBetweenStartStop)

    return start, stop
# todo finish this
def getTLBRprojectionInside(img, discValue = 0, showPlot = False, maxIntH = 1, maxIntV = 3):
    hProj, vProj = projection(img, showPlot)

    starth, stoph = findStartStopValues(hProj[:,0], discValue, maxIntervals = maxIntH)
    startv, stopv = findStartStopValues(vProj[:,0], discValue, maxIntervals = maxIntV)
    tl_list = []
    br_list = []
    for tly, bry in zip(starth, stoph):
        for tlx, brx in zip(startv, stopv):
            tl_list.append([tlx, tly])
            br_list.append([brx, bry])

    return tl_list, br_list

def subValues(img, trueValueIni = [255,255,255], trueValueFin = 1, falseValueFin = 0):
    '''
    Given an image, checks which pixels are meeting the condition of trueValueIni
    and substitues them with trueValueFin. Where the condition is not verified,
    falseValueFin is given (if specified) or the original value is kept.

    Parameters
    ----------
    img : TYPE
        DESCRIPTION.
    trueValueIni : TYPE, optional
        DESCRIPTION. The default is [255,255,255].
    trueValueFin : TYPE, optional
        DESCRIPTION. The default is 1.
    falseValueFin : TYPE, optional
        DESCRIPTION. The default is 0.

    Returns
    -------
    out : TYPE
        DESCRIPTION.

    '''
    trueValueIni_len = utils.checkLength(trueValueIni)
    trueValueFin_len = utils.checkLength(trueValueFin)

    if len(img.shape)==2:
        img = np.expand_dims(img, axis = -1)
        imgPixel_len = 0
    else:
        imgPixel_len = img.shape[-1]

    assert imgPixel_len == trueValueIni_len, \
        f"elements in axis -1 of img should be of same dimension of \
trueValueIni, got {img.shape[-1]} and {trueValueIni_len}"
    if falseValueFin is not None:
        falseValueFin_len = utils.checkLength(falseValueFin)
        assert trueValueFin_len == falseValueFin_len, \
        f"trueValueFin and falseValueFin should have same dimension, \
got {trueValueFin_len} and {falseValueFin_len}"
    if falseValueFin is None:
        assert imgPixel_len == trueValueFin_len, \
            f"elements in axis -1 of img should be of same dimension of \
trueValueIni, got {img.shape[-1]} and {trueValueFin_len}"

    # check where all the values of each pixel are equals to trueValueIni
    # whereSub is a 2D matrix
    whereSub = np.all([img == trueValueIni], axis = -1).reshape(img.shape[0:2])

    # extend whereSub on the third axis with the given depth, as specified with
    # trueValueFin. If depth is 0, a 2D array is fine
    if trueValueFin_len > 0:
        whereSub = np.stack([whereSub]*trueValueFin_len, axis = -1)

    # trueValueFin and falseValueFin substitution
    if falseValueFin is not None:
        out = np.where(whereSub, trueValueFin, falseValueFin)
    else:
        out = np.where(whereSub, trueValueFin, img)
    return out

def resize(img, nrows = 20, ncols = 20):
    assert len(img.shape) == 2, f"only accepting 2D images (gray scale or binary)"
    img = cv2.resize(img.astype(float), (ncols, nrows))
    img = img_to_array(img).astype(np.uint8)
    img = img.reshape(1, ncols, nrows, 1)
    return img

def rescale(img, scale_percent = 300):
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    # rescale image
    return cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

def rescaleToMaxPixel(img, maxPixels = 1000):
    return rescale(img, int(100*maxPixels/np.max(img.shape[0:2])))



#%% dismissed code

# def fromTwoCornersToTLBR(corner1, corner2):
#     '''
#     Given two couples of [x,y] coordinates, finds top left [min x, min y] and
#     bottom right [max x, max y]

#     Parameters
#     ----------
#     corner1 : TYPE
#         DESCRIPTION.
#     corner2 : TYPE
#         DESCRIPTION.

#     Returns
#     -------
#     tl : TYPE
#         DESCRIPTION.
#     br : TYPE
#         DESCRIPTION.

#     '''
#     tl = [0,0]
#     br = [0,0]

#     tl[0] = int(np.floor(np.minimum(corner1[0], corner2[0])))
#     tl[1] = int(np.floor(np.minimum(corner1[1], corner2[1])))
#     br[0] = int(np.ceil(np.maximum(corner1[0], corner2[0])))
#     br[1] = int(np.ceil(np.maximum(corner1[1], corner2[1])))
#     return tl, br


# def getTLBR_user(img):
#     '''
#     Shows image to user and asks him to press on two corners to crop it. 
#     Afterwards prints a new figure. 
#     The user can press: 
#         - in the centre of the figure to confirm the crop
#         - in one corner to redo the crop

#     Parameters
#     ----------
#     img : TYPE
#         DESCRIPTION.

#     Returns
#     -------
#     tl : [top left x, top left y] coordinates int
#         DESCRIPTION.
#     br : [bottom right x, bottom right y] coordinates int
#         DESCRIPTION.

#     '''
#     orig_img = img.copy()
#     tl = [0,0]
#     br = [img.shape[1],img.shape[0]]

#     while True:
#         fig, ax = plotImage(orig_img, title = 'select two corners')
#         corner1, corner2 = plt.ginput(n=2, timeout=-1, show_clicks=True)
#         tl, br = fromTwoCornersToTLBR(corner1, corner2)
#         img = cropImageTLBR(orig_img, tl, br)

#         imgName = 'Press Enter to confirm'
#         cv2.imshow(imgName, rescaleToMaxPixel(img, 800))
#         # if (cv2.waitKey(0) and (0xFF == ord('y') or 0xFF == ord('Y') or 0xFF == ord('\n'))):
#         key = cv2.waitKey(0)
#         if key == ord('\r'): # enter key
#             plt.close(fig)
#             cv2.destroyWindow(imgName)
#             break
#         else:
#             plt.close(fig)
#             cv2.destroyWindow(imgName)
#             continue
#     return tl, br
#%% 
"""
date: 2022-12-22 14:42:55
note: when putting order in utils
"""
# def depImgToThreeCol(image):
#     '''
#     From a dep image, containing only 1 value per pixel: 

#         |----------------------------...------> x
#         |0.0       1.0       2.0     ...  img_w.0    
#         |0.1       1.1       2.1     ...  img_w.1 
#         |0.2       1.2       2.2     ...  img_w.2 
#         |0.3       1.3       2.3     ...  img_w.3 
#         ...        ...       ...     ...  ...
#         |0.img_h   1.img_h   2.img_h ...  img_w.img_h
#         v y

#     returns an 2D array with 3 columns (pointCloud):
#         x         y       dep
#         0         0       0.0
#         1         0       1.0
#         2         0       2.0
#         ...       ...     ...
#         img_w     0       img_w.0
#         --------------------------- first row of the image
#         0         1       0.1
#         1         1       1.1
#         2         1       2.1
#         ...       ...     ...
#         img_w     1       img_w.1
#         --------------------------- second row of the image
#         ...
#         ...
#         0         img_h   0.img_h
#         1         img_h   1.img_h
#         2         img_h   2.img_h
#         ...       ...     ...
#         img_w     img_h   img_w.img_h
#         --------------------------- last row of the image

#     Parameters
#     ----------
#     image : matrix
#         contains z values.

#     Returns
#     -------
#     data : array
#         contains x y z values.

#     '''
#     image_h, image_w = image.shape

#     hline = np.arange(0, image_w, 1)
#     xmask = np.repeat([hline], image_h, axis = 0)

#     vline = np.expand_dims(np.arange(0, image_h, 1), axis = 1)
#     ymask = np.repeat(vline, image_w, axis = 1)
    
#     # create a matrix x y z
#     data = np.zeros([image_h*image_w,3])
#     data[:,0] = xmask.flatten()
#     data[:,1] = ymask.flatten()
#     data[:,2] = image.flatten()

#     return data

# def threeColToDepImg(data, x_col_index = 0, y_col_index = 1, z_col_index = 2):
#     '''
#     From an 2D array with 3 columns:
#         x         y       dep
#         0         0       0.0
#         1         0       1.0
#         2         0       2.0
#         ...       ...     ...
#         img_w     0       img_w.0
#         --------------------------- first row of the image
#         0         1       0.1
#         1         1       1.1
#         2         1       2.1
#         ...       ...     ...
#         img_w     1       img_w.1
#         --------------------------- second row of the image
#         ...
#         ...
#         0         img_h   0.img_h
#         1         img_h   1.img_h
#         2         img_h   2.img_h
#         ...       ...     ...
#         img_w     img_h   img_w.img_h
#         --------------------------- last row of the image

#     returns a dep image, containing only 1 value per pixel: 

#         |----------------------------...------> x
#         |0.0       1.0       2.0     ...  img_w.0    
#         |0.1       1.1       2.1     ...  img_w.1 
#         |0.2       1.2       2.2     ...  img_w.2 
#         |0.3       1.3       2.3     ...  img_w.3 
#         ...        ...       ...     ...  ...
#         |0.img_h   1.img_h   2.img_h ...  img_w.img_h
#         v y

#      Parameters
#      ----------
#      data : array
#          contains x y z values.
#     x_col_index : int, optional
#         column of the x values. The default is 0.
#     y_col_index : int, optional
#         column of the y values. The default is 1.
#     z_col_index : int, optional
#         column of the z values. The default is 2.

#     Returns
#     -------
#     image : matrix
#         contains z values.

#     '''
#     # # removing nan values
#     # data = data[~np.isnan(data).any(axis=1), :]

#     image = np.reshape(data[:,z_col_index], [int(round(data[-1,y_col_index])+1),int(round(data[-1,x_col_index])+1)],'C')
#     return image