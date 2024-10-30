from flask import Flask, request, render_template
import MeCab
import re
import os

app = Flask(__name__)

# Hàm xác định hình vị tự do hay hạn chế
def identify_morpheme_type(surface, features):
    # Nếu từ là động từ và không phải là đuôi ます -> hình vị hạn chế (như あり trong あります)
    if "動詞" in features and surface != "ます":
        return "Hình vị hạn chế"
    elif "動詞" in features and surface == "ます":  # Đuôi ます là hình vị hạn chế
        return "Hình vị hạn chế"
    elif "名詞" in features:  # Danh từ
        return "Hình vị tự do"
    else:
        return "Hình vị hạn chế"

# Hàm xác định loại từ (和語, 漢語, 外来語, 混種語, オノマトペ)
def identify_word_type(features):
    if "和" in features:
        return "和語 (Từ thuần Nhật)"
    elif "漢" in features:
        return "漢語 (Từ Hán Nhật)"
    elif "外" in features:
        return "外来語 (Từ ngoại lai)"
    elif "混" in features:
        return "混種語 (Từ hỗn hợp)"
    elif "オノマトペ" in features:
        return "オノマトペ (Từ tượng thanh/tượng hình)"
    else:
        return "Không xác định"

def analyze_sentence(sentence):
    # Chỉ chỉ định đường dẫn đến từ điển, không cần chỉ định mecabrc
    mecab = MeCab.Tagger("-d /usr/lib/x86_64-linux-gnu/mecab/dic/ipadic")
    
    parsed_sentence = mecab.parse(sentence).strip()

    morphemes = []
    morpheme_types = []
    for line in parsed_sentence.split('\n'):
        if line != 'EOS':
            surface, features = line.split('\t')
            features = features.split(',')
            if features[0] != '記号':
                morphemes.append(surface)
                morpheme_type = identify_morpheme_type(surface, features)
                morpheme_types.append(morpheme_type)

    total_words = len(morphemes)
    unique_words = len(set(morphemes))

    return {
        'morphemes': morphemes,
        'morpheme_types': morpheme_types,
        'total_words': total_words,
        'unique_words': unique_words
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    result_sentence = None
    if request.method == 'POST':
        # Xử lý phân tích câu
        if 'sentence' in request.form:
            sentence = request.form['sentence']
            if sentence:
                result_sentence = analyze_sentence(sentence)
    return render_template('index.html', result_sentence=result_sentence)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
