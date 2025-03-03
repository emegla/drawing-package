import os.path
import json
import base64


def base64todrawing(savepath, folder):
    """
    This function will convert base64 data (stored as .json) into images of the drawings and name the drawings
    with as (PartID_timecond.jpg)

    Inputs:
    :savepath: where you want the images of the drawings saved
    :folder: the folder containing all the base64 code you want converted
    """

    with open(folder, 'r') as f:
        json_data = json.load(f)
    for sub in json_data['data']:
        # Get drawing info
        participant = sub['participantid']
        delaycond = sub['timecond']

        # Clean up base64 code
        img_data = sub['drawing'].replace("data:image/png;base64,", "")
        byte_data = img_data.encode()  # this converts str back into bytes

        # Now save drawing as image!
        filename = '%s_%s.png' % (participant, delaycond)  # this saves the drawing with partID & delay condition
        fullfilename = os.path.join(savepath, filename)
        with open(fullfilename, "wb") as fh:
            fh.write(base64.decodebytes(byte_data))

