import os.path
import json
import base64


def base64todrawing(data, savepath):
    """
    This function will convert base64 data (stored as .json) into images of the drawings and name the drawings
    as (PartID_timecond.jpg)

    Inputs:
    :savepath: where you want the images of the drawings saved
    :folder: the folder containing all the base64 code you want converted
    """

    #with open(folder, 'r') as f:
        #json_data = json.load(f)
    for i in range(len(df)):
        # Get drawing info
        subject = df['participant'][i]
        #sub['participant']
        category = df['image'][i]
        condition = df['drawingtype'][i]

        # Clean up base64 code
        img_data = df['drawing'][i].replace("data:image/png;base64,", "")
        byte_data = img_data.encode()  # this converts str back into bytes

        # Now save drawing as image!
        filename = '%s_%s_%s.png' % (subject, category,condition)  # this saves the drawing with partID & delay condition
        fullfilename = os.path.join(savepath, filename)
        with open(fullfilename, "wb") as fh:
            fh.write(base64.decodebytes(byte_data))

