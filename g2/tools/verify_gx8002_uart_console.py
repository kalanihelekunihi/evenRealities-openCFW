#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Qualify recovered console functions for the experimental hybrid image."""
import json
from compare_gx8002_uart_putc import verify as compare


def verify(prefix=None, sdk=None, output=None):
    evidence = compare(prefix, sdk, output)
    placement = evidence['transmit']['placement']
    entry = next(r for r in placement['sections'] if r['symbol'].endswith('console_putc'))
    if not entry['exact_stock_match']:
        raise ValueError('console entry changed from byte-exact implementation')
    functions = []
    for row in placement['sections']:
        functions.append({'symbol': row['symbol'], 'compiled_bytes': row['bytes'],
                          'compiled_sha256': row['sha256'], 'stock_occurrences': [{
                              'symbol': row['symbol'], 'package_offset': row['package_offset'],
                              'bytes': row['stock_envelope_bytes'], 'sha256': row['stock_sha256'],
                              'region': 'image_a_xip_text'}]})
    return {'functions': functions, 'source_sha256': placement['source_sha256'],
            'compile_flags': placement['flags'], 'evidence': evidence,
            'source_admitted': True, 'hardware_qualified': False,
            'limits': ['Experimental same-entry replacement; existing descriptors and port global remain retained.',
                       'Finite restricted execution comparison does not qualify timing or hardware.']}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
