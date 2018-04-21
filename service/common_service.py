# coding=utf-8
import random


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


def create_random_comment():
    """
    適当なコメントをランダムに作成します。
    """
    random_comments = ['なるほど', '最近よく聞く', 'あんまり', '本当', '賛否両論', 'いい', 'うん', 'どういうことだろ',
                       'そういうこと', 'すごい', '初めて聞いた', 'すてき', 'そう', 'まだあまり知られてなさそう', 'たしかに',
                       'もういい', 'む', 'ふ', '今さら', 'でしょ', 'わかる', 'なんで', 'そう', '速報', 'たしかに',
                       'そんなバカな', 'まだまだ', 'いいじゃん', 'ですね', 'そんなこともあるよね', 'なんで', 'わからない', 'えええ',
                       'や', 'そんな日もある', 'いや', '神', '仕事', 'ダメ', 'セーフ', 'アウト', '悲しみ', '嬉しみ', 'ハイ',
                       'かわいい', 'やばい', 'まじ', 'マジ', 'それな', 'かっこいい']

    random_end_of_words = ['( ^ω^ )', '( ? _ ? )', '(｡-_-｡)', '(O_O)', '(￣^￣)ゞ', '(-_-)zzz', '(・Д・)ノ', 'Σ(・□・；)',
                           '⊂((・x・))⊃', '( ´ ▽ ` )ﾉ', '(>_<)', '(´Д` )', '( *｀ω´)', 'd(￣ ￣)', '(^^)', '＼(^o^)／',
                           '(*_*)', '(OvO)', '(･_･;)' 'です', 'よね', '?', '!', '', '', '', '', '', '', '笑','...', '。',
                           '!!', '!?', '??', 'ー']
    return random.choice(random_comments) + random.choice(random_end_of_words)


def contain_dangerous_word(text):
    """
    textに公序良俗違反にみなされそうな言葉が含まれていないかチェックする
    """
    dangerous_words = ["暴力", "死", "エロ", "アダルト", "テロ", "殺", "えろ", "エッチ", "えっち", "AV"]
    for word in dangerous_words:
        if text.find(word) > 0:
            return True
    return False
