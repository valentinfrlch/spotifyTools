# get image from unsplash
from ctypes import resize
import datetime

from matplotlib import image
from psutil import net_connections
import requests
# get current month name
month = datetime.datetime.now().strftime("%B")

# search unsplash for image of month
# get image url
# save image to file
# return image url
def synthesize():
    import os, random
    from PIL import Image, ImageDraw, ImageFont
    import base64
    from io import BytesIO
    # get image url
    image_url = "https://source.unsplash.com/random/1920x1080?{}".format(month + " nature")
    # save image to file
    # return image url
    #save image to file
    with open("image.jpg", "wb") as f:
        f.write(requests.get(image_url).content)
    # get random font from /dataset/fonts
    font = ImageFont.truetype("dataset/fonts/" + random.choice(os.listdir("dataset/fonts/")), 150, encoding="unic")
    # get image
    img = Image.open("image.jpg")
    # crop image 300x300
    img = img.crop((0, 0, 300, 300))
    # get draw
    draw = ImageDraw.Draw(img)
    # get text size
    text_size = draw.textsize(month, font=font)
    # get text position
    text_x = (img.width - text_size[0]) / 2
    text_y = (img.height - text_size[1]) / 2
    # draw text
    draw.text((text_x, text_y), month, font=font, fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    # save image
    # img.save("image.jpg")
    buffered = BytesIO()
    return base64.b64encode(buffered.getvalue())
synthesize()