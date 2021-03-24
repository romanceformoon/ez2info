from PIL import Image
import pytesseract
import cv2
import re
import os

songName = (849, 175, 1176, 217)
kool = (1180, 372, 1270, 402)
cool = (1180, 402, 1270, 452)
good = (1180, 452, 1270, 492)
miss = (1180, 492, 1270, 532)
fail = (1180, 532, 1257, 572)
score = (1445, 640, 1650, 690)
resize = (0, 50, 1680, 1000)
nick = (245, 47, 445, 94)


def cleanText(readData):
    # 스팸 메세지에 포함되어 있는 특수 문자 제거
    text = re.sub(
        '[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', readData)
    # 양쪽(위,아래)줄바꿈 제거
    text = text.strip('\n')
    text = text.rstrip()
    text = text.split('\n')[0]
    return text


def recalc_coord(x):
    return (int(x[0] / 1.5), int(x[1] / 1.5), int(x[2] / 1.5), int(x[3] / 1.5))


def preProcessJudge(image):
    img = cv2.imread(image, cv2.IMREAD_COLOR)
    canny = cv2.Canny(img, 100, 200)
    out = canny.copy()
    out = 255 - out

    return canny


def image2Text(param, param2, config, lang=None):
    i = 1
    result = pytesseract.image_to_string(param, config=config, lang=lang)
    if len(cleanText(result)) == 0:
        result = pytesseract.image_to_string(param2, config=config, lang=lang)

    while len(cleanText(result)) == 0 and i < 50:
        if param == croppedKool:
            coord = ((kool[0] - i), (kool[1] - i),
                     (kool[2] + i), (kool[3] + i))
            temp = image1.crop(coord)
            result = pytesseract.image_to_string(
                temp, config=config, lang=lang)
            i += 1

        elif param == croppedCool:
            coord = ((cool[0] - i), (cool[1] - i),
                     (cool[2] + i), (cool[3] + i))
            temp = image1.crop(coord)
            result = pytesseract.image_to_string(
                temp, config=config, lang=lang)
            i += 1

        elif param == croppedGood:
            coord = ((good[0] - i), (good[1] - i),
                     (good[2] + i), (good[3] + i))
            temp = image1.crop(coord)
            result = pytesseract.image_to_string(
                temp, config=config, lang=lang)
            i += 1
            # print(i)

        elif param == croppedMiss:
            coord = ((miss[0] - i), (miss[1] - i),
                     (miss[2] + i), (miss[3] + i))
            temp = image1.crop(coord)
            result = pytesseract.image_to_string(
                temp, config=config, lang=lang)
            i += 1

        elif param == croppedFail:
            coord = ((fail[0] - i), (fail[1] - i),
                     (fail[2] + i), (fail[3] + i))
            temp = image1.crop(coord)
            result = pytesseract.image_to_string(
                temp, config=config, lang=lang)
            i += 1

    return cleanText(result)


def work(filename):
    # filelist = os.listdir('static/upload/')
    # print(filelist)

    initialCheck = Image.open(filename)
    # print(initialCheck.size)
    if initialCheck.size[1] == 1050:
        print("Resolution Checkpoint.")
        print("Image Crop Start.")
        resizeImage = initialCheck.crop(resize)
        resizeImage.save(filename)

    img = cv2.imread(filename, cv2.IMREAD_COLOR)
    dst = cv2.resize(img, dsize=(1920, 1080), interpolation=cv2.INTER_LINEAR)
    img2 = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(img2, (3, 3), 0)
    out = blur.copy()
    out = 255 - out
    cv2.imwrite('static/upload/crop/blur.jpg', out)

    image1 = Image.open('static/upload/crop/blur.jpg')

    # 이미지의 크기 출력
    # print(image1.size)
    if image1.size[0] == 1920:
        croppedSongName = image1.crop(songName)
        croppedKool = image1.crop(kool)
        croppedCool = image1.crop(cool)
        croppedGood = image1.crop(good)
        croppedMiss = image1.crop(miss)
        croppedFail = image1.crop(fail)
        croppedScore = image1.crop(score)
        croppedNickname = image1.crop(nick)

    croppedSongName.save('static/upload/crop/name.png')
    croppedKool.save('static/upload/crop/kool.png')
    croppedCool.save('static/upload/crop/cool.png')
    croppedGood.save('static/upload/crop/good.png')
    croppedMiss.save('static/upload/crop/miss.png')
    croppedFail.save('static/upload/crop/fail.png')
    croppedNickname.save('static/upload/crop/nick.png')

    ret = {}
    print(filename)
    result = pytesseract.image_to_string(
        croppedSongName, lang='kor+eng', config='--psm 11 -c preserve_interword_spaces=1')
    print("songName 인식결과: ", cleanText(result))
    ret['song'] = cleanText(result)

    result = pytesseract.image_to_string(
        croppedNickname, lang='kor+eng', config='--oem 3 --psm 11 -c preserve_interword_spaces=1')
    print("Nickname 인식결과: ", cleanText(result))

    result = image2Text(croppedKool, preProcessJudge('static/upload/crop/kool.png'),
                        '--psm 6 -c tessedit_char_whitelist=0123456789')
    print("Kool 인식결과: ", cleanText(result))
    ret['kool'] = cleanText(result)

    result = image2Text(croppedCool, preProcessJudge('static/upload/crop/cool.png'),
                        '--psm 6 -c tessedit_char_whitelist=0123456789')
    print("Cool 인식결과: ", cleanText(result))
    ret['cool'] = cleanText(result)

    result = image2Text(croppedGood, preProcessJudge('static/upload/crop/good.png'),
                        '--psm 6 -c tessedit_char_whitelist=0123456789')
    print("Good 인식결과: ", cleanText(result))
    ret['good'] = cleanText(result)

    result = image2Text(croppedMiss, preProcessJudge('static/upload/crop/miss.png'),
                        '--psm 6 -c tessedit_char_whitelist=0123456789')
    print("Miss 인식결과: ", cleanText(result))
    ret['miss'] = cleanText(result)

    result = image2Text(croppedFail, preProcessJudge('static/upload/crop/fail.png'),
                        '--psm 6 -c tessedit_char_whitelist=0123456789')
    print("Fail 인식결과: ", cleanText(result))
    ret['fail'] = cleanText(result)

    result = pytesseract.image_to_string(
        croppedScore, config='--psm 6 -c tessedit_char_whitelist=0123456789')
    print("Score 인식결과: ", cleanText(result))
    print('--------------------------------')
    ret['score'] = cleanText(result)

    return ret
