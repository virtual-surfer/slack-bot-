# coding=utf-8


def select_dictionary(dictionary, count):
    """
    辞書の最初のものからcountの数だけ取得する。(countが0以下の場合は空の辞書を返す)
    """
    result_dictionary = {}
    if count < 1:
        return result_dictionary
    loop_count = 0
    for key, value in dictionary:
        result_dictionary.setdefault(key, value)
        loop_count += 1
        if loop_count >= count:
            break
    return result_dictionary


def contain_dangerous_word(text):
    """
    textに公序良俗違反にみなされそうな言葉が含まれていないかチェックする
    """
    dangerous_words = ["暴力", "死", "エロ", "アダルト", "テロ", "殺", "えろ", "エッチ", "えっち"]
    for word in dangerous_words:
        if text.find(word) > 0:
            return True
    return False
