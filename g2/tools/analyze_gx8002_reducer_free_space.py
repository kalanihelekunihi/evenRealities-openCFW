# SPDX-License-Identifier: MIT
"""Audit existing generated fill without treating retained bytes as free space."""
import json
from collections import Counter
from build_gx8002_backup_cfft import ROOT, sha


def analyze():
    directory = ROOT / 'build/gx8002-fft-q15-cosine-integration-experiment'
    report_path = directory / 'build-report.json'
    report = json.loads(report_path.read_text())
    firmware = (directory / 'firmware_codec.unadmitted.bin').read_bytes()
    assert sha(firmware) == report['firmware_sha256']
    assert len(firmware) == report['firmware_size'] == 326092
    cursor = 0
    totals = Counter()
    fill = []
    for row in report['ownership']:
        start, size = row['offset'], row['size']
        assert start == cursor and size > 0
        cursor += size
        assert cursor <= len(firmware)
        totals[row['kind']] += size
        if 'sha256' in row:
            assert sha(firmware[start:cursor]) == row['sha256']
        if row['kind'] == 'generated_unreachable_fill':
            fill.append(dict(row))
    assert cursor == len(firmware)
    assert dict(totals) == report['byte_ownership']
    backup_start, backup_end = 0x3b940, 0x4f9cc
    backup = []
    for row in fill:
        start, end = row['offset'], row['offset'] + row['size']
        if start < backup_end and end > backup_start:
            assert backup_start <= start < end <= backup_end
            backup.append(row)
    # Merge adjacent ownership rows before measuring contiguous capacity.
    spans = []
    for row in backup:
        start, end = row['offset'], row['offset'] + row['size']
        if spans and spans[-1][1] == start:
            spans[-1][1] = end
        else:
            spans.append([start, end])
    largest = max((end - start for start, end in spans), default=0)
    probes = []
    for name in ('gx8002-reduction-probe', 'gx8002-reduction-helpers-probe'):
        path = ROOT / 'docs/research' / (name + '.json')
        evidence = json.loads(path.read_text())
        for row in evidence['objects']:
            obj = ROOT / 'build' / name / (row['source']['path'].split('/')[-1] + '.o')
            assert sha(obj.read_bytes()) == row['object_sha256']
            code = sum(size for section, size in row['allocated'] if section.startswith('.text'))
            probes.append({'source': row['source'], 'object_sha256': row['object_sha256'],
                           'allocated': row['allocated'], 'code_bytes': code,
                           'code_fits_largest_existing_backup_fill': code <= largest})
    result = {
        'firmware_sha256': sha(firmware), 'ownership_report_sha256': sha(report_path.read_bytes()),
        'all_image_fill_bytes': totals['generated_unreachable_fill'],
        'backup_bounds': [backup_start, backup_end], 'backup_fill': backup,
        'backup_fill_bytes': sum(row['size'] for row in backup),
        'backup_contiguous_fill_spans': spans, 'largest_backup_fill_bytes': largest,
        'upstream_objects': probes, 'source_admitted': False,
        'limits': [
            'Inventory authenticates existing ownership; it does not independently prove that fill is unreachable.',
            'Fill outside the backup payload belongs to other images and is not available for backup placement.',
            'Retained stock tails and literal pools are not free space without additional reference and reachability evidence.',
            'Fit compares code sizes only; alignment, data, dependencies, and branch ranges also require qualification.',
            'No firmware bytes were changed. Larger complete functions require a new placement or relinking strategy.',
        ],
    }
    (ROOT / 'docs/research/gx8002-reducer-free-space.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    r = analyze()
    print({key: r[key] for key in ('all_image_fill_bytes', 'backup_fill_bytes', 'largest_backup_fill_bytes')})
