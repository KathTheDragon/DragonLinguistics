import csv

WORD_HEADERS = {'lemma', 'type', 'notes', 'etymology'}
SENSE_HEADERS = {'gloss', 'defin', 'pos', 'grammclass', 'notes'}
HEADERS = WORD_HEADERS | SENSE_HEADERS
MIN_HEADERS = {'lemma', 'gloss'}


def parse_csv(file, delimiter, quotechar):
    with open(file, mode='r') as f:
        data = csv.DictReader(f, delimiter=delimiter, quotechar=quotechar, strict=True, doublequote=False, escapechar='\\')
        if not (MIN_HEADERS <= set(data.fieldnames) <= HEADERS):
            raise csv.Error

        entries = []
        for row in data:
            row = {key: value for key, value in row.items() if value is not None}
            if not (MIN_HEADERS <= set(row)):
                raise csv.Error
            word = {key: value for key, value in row.items() if key in WORD_HEADERS}
            sense = {key: value for key, value in row.items() if key in SENSE_HEADERS}
            if word['lemma'] == '^':
                if not entries:
                    raise csv.Error
                entries[-1]['senses'].append(sense)
            else:
                entries.append({'word': word, 'senses': [sense]})

    return words
