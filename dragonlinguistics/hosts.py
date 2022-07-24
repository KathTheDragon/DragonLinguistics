from django_hosts import patterns, host

host_patterns = patterns('dragonlinguistics.domains',
    host('www', 'www.urls', name='www'),
    host('conlang', 'conlang.urls', name='conlang'),
    host('hist', 'hist.urls', name='hist'),
    # Not yet implemented
    # host('dni', 'dni.urls', name='dni'),
    # host('api', 'api.urls', name='api'),
)
