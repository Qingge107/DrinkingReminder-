from PIL import Image

# 打开PNG图像
img = Image.open('water.png')

# 转换为ICO
img.save('water.ico', format='ICO')
