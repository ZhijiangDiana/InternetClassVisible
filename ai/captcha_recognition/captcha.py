# -*- coding: UTF-8 -*-
import numpy as np
import torch
import torch.nn as nn
from torch.autograd import Variable
from torchvision.models import resnet34
import torchvision.transforms as transforms
import base64
from PIL import Image
from io import BytesIO


# example
# base64_code = "captcha base64 code"
# print(captchaRecog(base64_code))


NUMBER = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
ALPHABET = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
ALL_CHAR_SET = NUMBER + ALPHABET
ALL_CHAR_SET_LEN = len(ALL_CHAR_SET)
MAX_CAPTCHA = 4

transform = transforms.Compose([transforms.ToTensor(),])


class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.resnet = resnet34(weights='DEFAULT')
        self.resnet.fc = nn.Sequential(
            nn.Linear(512, 1024),
            nn.Dropout(0.5),  # drop 50% of the neuron
            nn.ReLU())
        self.rfc = nn.Sequential(
            nn.Linear(1024, MAX_CAPTCHA*ALL_CHAR_SET_LEN),
        )

    def forward(self, x):
        out = self.resnet(x)
        out = self.rfc(out)
        return out


cnn = CNN()
cnn.eval()
print("loading captcha recognition model weight...")
cnn.load_state_dict(torch.load('ai/captcha_recognition/captcha_recog_model_weight.pt', map_location=torch.device('cpu')))


def captchaRecog(img_base64):
    _, context=img_base64.split(",")
    img_data = base64.b64decode(context)
    image = Image.open(BytesIO(img_data)).convert("RGBA")

    W, L = image.size
    for h in range(W):
        for i in range(L):
            if image.getpixel((h, i))[-1] == 0:
                image.putpixel((h, i), (255, 255, 255, 255))
    image = transform(image.convert("RGB")).unsqueeze(dim=0)

    vimage = Variable(image)
    predict_label = cnn(vimage)

    c0 = ALL_CHAR_SET[np.argmax(predict_label[0, 0:ALL_CHAR_SET_LEN].data.numpy())]
    c1 = ALL_CHAR_SET[np.argmax(predict_label[0, ALL_CHAR_SET_LEN:2 * ALL_CHAR_SET_LEN].data.numpy())]
    c2 = ALL_CHAR_SET[np.argmax(predict_label[0, 2 * ALL_CHAR_SET_LEN:3 * ALL_CHAR_SET_LEN].data.numpy())]
    c3 = ALL_CHAR_SET[np.argmax(predict_label[0, 3 * ALL_CHAR_SET_LEN:4 * ALL_CHAR_SET_LEN].data.numpy())]

    c = '%s%s%s%s' % (c0, c1, c2, c3)
    return c

