import csv

WORD_HEADERS = {'lemma', 'type', 'isunattested', 'etymology', 'descendents', 'references'}
VARIANT_HEADERS = {'class', 'forms', 'definition', 'notes', 'derivatives'}
HEADERS = WORD_HEADERS | VARIANT_HEADERS
MIN_HEADERS = {'lemma', 'definition'}


def parse_csv(file, delimiter, quotechar):
    lines = (str(line, encoding='utf-8') for line in file)
    data = csv.DictReader(lines, delimiter=delimiter, quotechar=quotechar, strict=True, doublequote=False, escapechar='\\')
    if not (MIN_HEADERS <= set(data.fieldnames) <= HEADERS):
        raise csv.Error(f'Invalid headers: {data.fieldnames}')

    entries = []
    for row in data:
        row = {key: value for key, value in row.items() if value is not None}
        if not (MIN_HEADERS <= set(row)):
            raise csv.Error(f'Invalid row: {row}')
        word = {key: value for key, value in row.items() if key in WORD_HEADERS}
        variant = {key: value for key, value in row.items() if key in VARIANT_HEADERS}
        if 'class' in variant:
            variant['lexclass'] = variant.pop('class')
        if word['lemma'] == '^':
            if not entries:
                raise csv.Error('Cannot add variant when there are no words')
            entries[-1]['variants'].append(variant)
        else:
            if 'isunattested' in word:
                word['isunattested'] = bool(word['isunattested'])
            entries.append({'word': word, 'variants': [variant]})

    return entries
