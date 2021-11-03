class StrOrID:
    regex = '@\d{9}|[^/@][^/]*'

    def to_python(self, value):
        if value.startswith('@'):
            return int(value.removeprefix('@'))
        else:
            return value

    def to_url(self, value):
        if isinstance(value, int):
            return f'@{value}'
        elif isinstance(value, str):
            return value
        else:
            raise ValueError
