# 实验一：代换密码和频率分析攻击

from io import BufferedWriter
import string


# 对文件的字母进行计数
def countingLetters(file: BufferedWriter) -> dict:

    myLetterDictionary = {}

    # 将a-z的字母从0开始计数
    for lower in string.ascii_lowercase:
        myLetterDictionary.update({lower: 0})
    # 将A-z的字母从0开始计数
    for upper in string.ascii_uppercase:
        myLetterDictionary.update({upper: 0})

    # 开始遍历文件
    for line in file:
        for letter in line:
            # 如果是字母：
            if letter in string.ascii_letters:
                myLetterDictionary.update(
                    {letter: myLetterDictionary.get(letter) + 1})
    # print(myLetterDictionary)
    return myLetterDictionary


def getProportion(myLetterDictionary: dict) -> dict:
    # 各字母占比
    letterProportion = {}
    for key in myLetterDictionary.keys():
        # 将每个字母与a的比值放入数组
        letterProportion.update(
            {key: myLetterDictionary.get(key) / myLetterDictionary.get('a')})
    # print(letterProportion)
    return letterProportion


if __name__ == "__main__":
    file = open("./novelEncrypted.txt", "r", encoding='utf-8')
    letterDictionary = countingLetters(file)
    proportionDic = getProportion(letterDictionary)
    # 按照字典的值进行排序
    orderedLetterDic = dict(
        sorted(proportionDic.items(), key=lambda x: x[1], reverse=True))
    print(orderedLetterDic)
