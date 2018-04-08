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
