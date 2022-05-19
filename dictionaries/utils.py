import csv

WORD_HEADERS = {'lemma', 'type', 'isunattested', 'etymology', 'descendents', 'references'}
VARIANT_HEADERS = {'class', 'forms', 'definition', 'notes', 'derivatives'}
HEADERS = WORD_HEADERS | VARIANT_HEADERS
MIN_HEADERS = {'lemma', 'definition'}


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
            variant = {key: value for key, value in row.items() if key in VARIANT_HEADERS}
            if 'class' in variant:
                variant['lexclass'] = variant.pop('class')
            if word['lemma'] == '^':
                if not entries:
                    raise csv.Error
                entries[-1]['variants'].append(variant)
            else:
                entries.append({'word': word, 'variants': [variant]})

    return words
