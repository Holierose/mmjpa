import MeCab
from collections import Counter
import sys
import re

# Hàm xác định hình vị tự do hay hạn chế
def identify_morpheme_type(surface, features):
    if "名詞" in features or "動詞" in features:
        return "Hình vị tự do"
    else:
        return "Hình vị hạn chế"

# Hàm phân loại từ thành từ đơn hay từ ghép
def classify_word(grouped_morphemes, grouped_dictionary_forms):
    if len(grouped_morphemes) == 1:
        return "Từ đơn (単純語)"
    elif len(grouped_morphemes) > 1:
        for morpheme in grouped_morphemes:
            if re.match(r'.*複合.*', morpheme):
                return "Từ phức (複合語)"
            elif re.match(r'.*派生.*', morpheme):
                return "Từ phái sinh (派生語)"
            elif re.match(r'.*畳語.*', morpheme):
                return "Từ láy (畳語)"
    return "Không xác định"

# Hàm phân tích câu và đếm số lượng từ
def analyze_sentence(sentence):
    try:
        mecab = MeCab.Tagger("-r /opt/homebrew/etc/mecabrc -d /opt/homebrew/lib/mecab/dic/ipadic")
        parsed_sentence = mecab.parse(sentence).strip()

        morphemes = []
        dictionary_forms = []
        morpheme_morpheme_types = []
        for line in parsed_sentence.split('\n'):
            if line != 'EOS':
                surface, features = line.split('\t')
                features = features.split(',')
                
                if features[0] != '記号':
                    morphemes.append(surface)
                    dictionary_form = features[6] if features[6] != '*' else surface
                    dictionary_forms.append(dictionary_form)
                    morpheme_morpheme_type = identify_morpheme_type(surface, features)
                    morpheme_morpheme_types.append(f"{surface}[{morpheme_morpheme_type}]")

        grouped_morphemes = []
        grouped_dictionary_forms = []
        temp_number = ""
        for morpheme, dictionary_form in zip(morphemes, dictionary_forms):
            if re.match(r'\d+', morpheme):
                temp_number += morpheme
            else:
                if temp_number:
                    grouped_morphemes.append(temp_number)
                    grouped_dictionary_forms.append(temp_number)
                    temp_number = ""
                grouped_morphemes.append(morpheme)
                grouped_dictionary_forms.append(dictionary_form)
        if temp_number:
            grouped_morphemes.append(temp_number)
            grouped_dictionary_forms.append(temp_number)

        total_words = len(grouped_morphemes)
        unique_words = len(set(grouped_dictionary_forms))
        word_classification = classify_word(grouped_morphemes, grouped_dictionary_forms)

        return {
            "morphemes": grouped_morphemes,
            "total_words": total_words,
            "unique_words": unique_words,
            "dictionary_forms": grouped_dictionary_forms,
            "morpheme_morpheme_types": morpheme_morpheme_types,
            "word_classification": word_classification
        }
    
    except RuntimeError as e:
        print(f"MeCab Error: {e}")
        sys.exit(1)

# Hàm in kết quả phân tích
def print_analysis(result):
    # Hiển thị hình vị và phân loại tự do/hạn chế, mỗi từ trên một dòng
    print("形態素 (Morphemes):")
    for morpheme in result['morpheme_morpheme_types']:
        print(morpheme)
    print(f"延べ語数 (tổng số từ, bao gồm từ lặp lại): {result['total_words']}")
    print(f"異なり語数 (số từ khác nhau, không tính từ lặp lại, dựa trên gốc từ): {result['unique_words']}")
    print(f"Phân loại từ: {result['word_classification']}")

# Kiểm tra nếu người dùng không nhập câu
def get_sentence_from_input():
    sentence = input("Nhập câu tiếng Nhật cần phân tích (hoặc gõ 'exit' để dừng): ").strip()
    if sentence.lower() == 'exit':
        print("Chương trình kết thúc.")
        sys.exit(0)
    if not sentence:
        print("Bạn chưa nhập câu. Vui lòng thử lại.")
        return get_sentence_from_input()
    return sentence

# Chương trình chính chạy liên tục
if __name__ == "__main__":
    while True:
        sentence = get_sentence_from_input()
        analysis_result = analyze_sentence(sentence)
        print_analysis(analysis_result)
