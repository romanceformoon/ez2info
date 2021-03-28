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
nick = (245, 47, 445, 94)
combo = (1178, 655, 1264, 695)
key = (35, 136, 144, 243)
notes = (1180, 317, 1270, 352)


def cleanText(readData):
    # 스팸 메세지에 포함되어 있는 특수 문자 제거
    text = re.sub(
        '[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', readData)
    # 양쪽(위,아래)줄바꿈 제거
    text = text.strip('\n')
    text = text.rstrip()
    text = text.split('\n')[0]
    return text


def preProcessJudge(image):
    img = cv2.imread(image, cv2.IMREAD_COLOR)
    canny = cv2.Canny(img, 100, 200)
    # out = canny.copy()
    # out = 255 - out

    return canny


def image2Text(param, param2, config, judge, image, lang=None):
    i = 1
    result = pytesseract.image_to_string(param, config=config, lang=lang)
    if len(cleanText(result)) == 0:
        result = pytesseract.image_to_string(param2, config=config, lang=lang)

    while len(cleanText(result)) == 0 and i < 250:
        if judge == "kool":
            coord = ((kool[0] - i), (kool[1] - i),
                     (kool[2] + i), (kool[3] + i))
            temp = image.crop(coord)
            result = pytesseract.image_to_string(
                temp, config=config, lang=lang)
            i += 1

        elif judge == "cool":
            coord = ((cool[0] - i), (cool[1] - i),
                     (cool[2] + i), (cool[3] + i))
            temp = image.crop(coord)
            result = pytesseract.image_to_string(
                temp, config=config, lang=lang)
            i += 1

        elif judge == "good":
            coord = ((good[0] - i), (good[1] - i),
                     (good[2] + i), (good[3] + i))
            temp = image.crop(coord)
            result = pytesseract.image_to_string(
                temp, config=config, lang=lang)
            i += 1
            # print(i)

        elif judge == "miss":
            coord = ((miss[0] - i), (miss[1] - i),
                     (miss[2] + i), (miss[3] + i))
            temp = image.crop(coord)
            result = pytesseract.image_to_string(
                temp, config=config, lang=lang)
            i += 1

        elif judge == "fail":
            coord = ((fail[0] - i), (fail[1] - i),
                     (fail[2] + i), (fail[3] + i))
            temp = image.crop(coord)
            result = pytesseract.image_to_string(
                temp, config=config, lang=lang)
            i += 1

    return cleanText(result)


def work(filename):
    # filelist = os.listdir('static/upload/')
    # print(filelist)

    initialCheck = Image.open(filename)
    # resize = (0, 50, 1680, 1000)
    i, a, b = 0, 0, 0
    # print(initialCheck.size)
    if not (initialCheck.size[0] // 16 == initialCheck.size[1] // 9):
        height = initialCheck.size[1]
        while (height / 9 != initialCheck.size[0] / 16):
            height -= 1
        print(height)
        crop_letter_box = (initialCheck.size[1] - height) // 2
        resize = (0, crop_letter_box,
                  initialCheck.size[0], initialCheck.size[1] - crop_letter_box)
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
        croppedCombo = image1.crop(combo)
        croppedNotes = image1.crop(notes)

    croppedSongName.save('static/upload/crop/name.png')
    croppedKool.save('static/upload/crop/kool.png')
    croppedCool.save('static/upload/crop/cool.png')
    croppedGood.save('static/upload/crop/good.png')
    croppedMiss.save('static/upload/crop/miss.png')
    croppedFail.save('static/upload/crop/fail.png')
    croppedNickname.save('static/upload/crop/nick.png')
    croppedCombo.save('static/upload/crop/combo.png')
    croppedNotes.save('static/upload/crop/notes.png')

    ret = {}
    print(filename)
    result = pytesseract.image_to_string(
        croppedSongName, lang='kor+eng', config='--psm 11 -c preserve_interword_spaces=1')
    print("songName 인식결과: ", cleanText(result))
    ret['song'] = cleanText(result)

    result = pytesseract.image_to_string(
        croppedNickname, lang='kor+eng', config='--oem 3 --psm 11 -c preserve_interword_spaces=1')
    print("Nickname 인식결과: ", cleanText(result))
    ret['nickname'] = cleanText(result)

    result = image2Text(croppedKool, preProcessJudge('static/upload/crop/kool.png'),
                        '--psm 6 -c tessedit_char_whitelist=0123456789', judge="kool", image=image1)
    print("Kool 인식결과: ", cleanText(result))
    ret['kool'] = cleanText(result)

    result = image2Text(croppedCool, preProcessJudge('static/upload/crop/cool.png'),
                        '--psm 6 -c tessedit_char_whitelist=0123456789', judge="cool", image=image1)
    print("Cool 인식결과: ", cleanText(result))
    ret['cool'] = cleanText(result)

    result = image2Text(croppedGood, preProcessJudge('static/upload/crop/good.png'),
                        '--psm 6 -c tessedit_char_whitelist=0123456789', judge="good", image=image1)
    print("Good 인식결과: ", cleanText(result))
    ret['good'] = cleanText(result)

    result = image2Text(croppedMiss, preProcessJudge('static/upload/crop/miss.png'),
                        '--psm 6 -c tessedit_char_whitelist=0123456789', judge="miss", image=image1)
    print("Miss 인식결과: ", cleanText(result))
    ret['miss'] = cleanText(result)

    result = image2Text(croppedFail, preProcessJudge('static/upload/crop/fail.png'),
                        '--psm 6 -c tessedit_char_whitelist=0123456789', judge="fail", image=image1)
    print("Fail 인식결과: ", cleanText(result))
    ret['fail'] = cleanText(result)

    result = pytesseract.image_to_string(
        croppedScore, config='--psm 6 -c tessedit_char_whitelist=0123456789')
    print("Score 인식결과: ", cleanText(result))
    ret['score'] = cleanText(result)

    result = pytesseract.image_to_string(
        croppedCombo, config='--psm 6 -c tessedit_char_whitelist=0123456789')
    print("MaxCombo 인식결과: ", cleanText(result))
    ret['combo'] = cleanText(result)

    result = pytesseract.image_to_string(
        croppedNotes, config='--psm 6 -c tessedit_char_whitelist=0123456789')
    print("Total Notes 인식결과: ", cleanText(result))
    ret['notes'] = cleanText(result)
    print('--------------------------------')

    return ret
