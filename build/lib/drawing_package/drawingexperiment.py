import json
import base64
import extcolors
import pandas as pd
import numpy as np
import cv2
from colormap import rgb2hex
import os
import os.path
import os,sys
from PIL import Image
from pathlib import Path


# These functions will help parse the information from the initial drawing experiment

def path2dict(pathdrawings,img_extension):
    """
    Creates a dictionary containing a path to every individual drawing within the specified folder
    :param: pathdrawings: path to folder containing drawings
    :param: img_extension: specify the extension of the drawings (e.g., .jpg, .jpeg, .png)
    :return: drawingpath_dict: dictionary containing all paths to individual drawings

    """

    drawingpath_dict = {}

    # this prints the whole path for the image
    files = Path(pathdrawings).glob("*" + img_extension)
    for i in files:
        drawingpath_dict.update({i: {}})

    return drawingpath_dict


def extract_color_profile(input_image):
    """
    Extracts the frequency of every color in an image
    :param: input_image: image you want the color profile for
    :return: df_color: a dataframe listing every color in the image, the number of pixels with that color
    ('occurences'), and the proportion of pixels that color ('proportion')
    """
    # resize
    img = Image.open(input_image)
    (width, height) = img.size
    totalpx = (width * height) # total pixels in image

    # Create dataframe
    colors_x = extcolors.extract_from_path(input_image, tolerance=12, limit=32)
    # note: tolerance is whether you want any colors grouped together (0 = none grouped, 100 = all grouped)
    # limit is the limit of how many colors you want displayed and subsequently saved in your dataframe
    df_color = color_to_df(colors_x, totalpx)

    # Calculate proportion of the pixels that are each color
    df_color = df_color.astype({'occurence': 'int'})
    color_proportions = df_color['occurence'].div(totalpx)  # dividing by all pixels in image
    df_color['proportion'] = color_proportions  # adding to the dataframe

    return df_color


def extract_nonwhitepx(df_color):
    """
    Extracts the proportion of pixels that are not white (i.e., how many pixels were used in the drawing)
    :param: df_color: dataframe outputted from extract_color_profile function that lists the frequency of each color in
    the image
    :return: nonwhitepix_prop: the proportion of non-white pixels in the image
    """

    # Calculate proportion of non-white pixels (how many pixels are filled?)
    if '#FFFFFF' in df_color.values:
        whitepx_prop = df_color.loc[df_color.c_code == '#FFFFFF', 'proportion'].values[0]
        nonwhitepx_prop = 1 - whitepx_prop
    else:
        nonwhitepx_prop = 0

    return nonwhitepx_prop


def extract_numcolors(df_color):
    """
    Extracts how many colors were used in the drawing.
    :param df_color: dataframe outputted from extract_color_profile function that lists the frequency of each color in
    the image
    :return: numcolors: the numbers of colors used in the drawing.
    """

    numcolors = df_color.shape[0]
    return numcolors


def color_to_df(colors_x,totalpx):
    """
    Note: Function from this website: https://towardsdatascience.com/image-color-extraction-with-python-in-4-steps-8d9370d9216e
    :param: colors_x: pixel composition of drawings, outputted from extcolors.extract_from_path function
    :param: totalpx: total number of pixels in drawing (width * height of drawing)
    :return: df: dataframe containing the pixel composition of the drawing in HEX values
    """
    extrastr = ('], ' + str(totalpx) + ')') # extra string at the end of color_x that needs to be deleted
    colors_pre_list = str(colors_x).replace('([(', '').replace(extrastr,'').split(', (') # deleting strings we don't need and making colors into a list
    df_rgb = [i.split('), ')[0] + ')' for i in colors_pre_list]
    df_percent = [i.split('), ')[1].replace(')', '') for i in colors_pre_list]

    # convert RGB to HEX code
    df_color_up = [rgb2hex(int(i.split(", ")[0].replace("(", "")),
                           int(i.split(", ")[1]),
                           int(i.split(", ")[2].replace(")", ""))) for i in df_rgb]

    df = pd.DataFrame(zip(df_color_up, df_percent), columns=['c_code', 'occurence'])
    return df


def dict2resultsdf(drawingpath_dict, name_structure):
    """
    :param: drawingpath_dict: output from path2dict - dictionary containing the path to every drawing
    :param: name_structure: specifies the naming convention of the drawings, with every variable separated by underscore
    (e.g., category_timecond_participant)
    :return: df_results: dataframe containing all variables of interest and drawing analysis results
    """

    # Get name structure details
    num_underscores = (name_structure.count("_"))
    var_list = name_structure.rsplit('_')

    for k, v in drawingpath_dict.items():
        df_color = extract_color_profile(k)
        drawingpath_dict[k].update({'prop_nonwhitepx': extract_nonwhitepx(df_color)})
        drawingpath_dict[k].update({'numcolors': extract_numcolors(df_color)})
        drawingpath_dict[k].update({'drawingname': os.path.splitext(os.path.basename(k))[0]})
        drawingname = os.path.splitext(os.path.basename(k))[0]
    
        for idx, var in enumerate(var_list):
            drawingpath_dict[k].update({var: drawingname.rsplit('_')[idx]})

    # Make into dictionary
    df_results = pd.DataFrame.from_dict(drawingpath_dict).T
    return df_results


def bg2white(drawingpath):
    """
    Converts background of image to white, overwriting the original image
    Note: function inspiration from here: https://stackoverflow.com/questions/13167269/changing-pixel-color-python
    :param: drawingpath: path to drawing
    """

    im = Image.open(drawingpath)
    width, height = im.size
    data = np.array(im)
    data = data[:,:,:3] # deletes alpha channel (transparency)

    # get the background color from a corner pixel

    bg_color = im.getpixel( (width-1,height-1) )
    bg_color = bg_color[0:3] # get rid of alpha
    r1, g1, b1 = bg_color

    # set value to replace background color with (white)
    r2, g2, b2 = 255, 255, 255

    red, green, blue = data[:,:,0], data[:,:,1], data[:,:,2] 
    mask = (red == r1) & (green == g1) & (blue == b1)
    data[:,:,:3][mask] = [r2, g2, b2]

    im = Image.fromarray(data) 
    im.save(drawingpath)
