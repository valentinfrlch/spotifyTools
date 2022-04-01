# get image from unsplash
import datetime

from matplotlib import image
import requests
# get current month name
month = datetime.datetime.now().strftime("%B")

# search unsplash for image of month
# get image url
# save image to file
# return image url
def get_image(month):
    # get image url
    image_url = "https://source.unsplash.com/random/1920x1080?{}".format(month)
    # save image to file
    # return image url
    #save image to file
    with open("image.jpg", "wb") as f:
        f.write(requests.get(image_url).content)
    # return image path
    return "image.jpg"

def synthesize(image):
    """draw text on image"""
    import os, random
    from PIL import Image, ImageDraw, ImageFont
    # get random font from /dataset/fonts
    font = ImageFont.truetype("dataset/fonts/" + random.choice(os.listdir("dataset/fonts/")), 150, encoding="unic")
    # get image
    img = Image.open(image)
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
    # crop image to square
    img = img.crop((1, 1, img.width, img.width))
    img.save("image.jpg")

def resize_as_base64(img):
    from PIL import Image
    from io import BytesIO
    image = Image.open(img)
    new_image = image.resize((300, 300))
    buffered = BytesIO()
    new_image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue())