import csv

_WORD_HEADERS = ['lemma', 'type', 'isunattested', 'etymology', 'descendents', 'references']
WORD_HEADERS = set(_WORD_HEADERS)
_VARIANT_HEADERS = ['class', 'forms', 'definition', 'notes', 'derivatives']
VARIANT_HEADERS = set(_VARIANT_HEADERS)
HEADERS_LIST = _WORD_HEADERS + _VARIANT_HEADERS
HEADERS = WORD_HEADERS | VARIANT_HEADERS
MIN_HEADERS = {'lemma', 'definition'}

class Echo:
    def write(self, value):
        return value


class Dialect(csv.Dialect):
    doublequote = True
    lineterminator = '\r\n'
    quoting = csv.QUOTE_MINIMAL
    strict = True

    def __init__(self, delimiter, quotechar):
        self.delimiter = delimiter
        self.quotechar = quotechar


def parse_csv(file, delimiter, quotechar):
    lines = (str(line, encoding='utf-8') for line in file)
    data = csv.DictReader(lines, dialect=Dialect(delimiter, quotechar))
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


def make_csv(dictionary, delimiter, quotechar):
    writer = csv.DictWriter(Echo(), fieldnames=HEADERS_LIST, dialect=Dialect(delimiter, quotechar))
    yield writer.writeheader()
    for word in dictionary.words.all():
        row = {field: getattr(word, field) for field in WORD_HEADERS}
        if not word.variants.count():
            yield writer.writerow(row)
        for variant in word.variants.all():
            var_row = {field: getattr(variant, field, '') for field in VARIANT_HEADERS}
            var_row['class'] = variant.lexclass
            yield writer.writerow(row | var_row)
            row = {'lemma': '^'}
