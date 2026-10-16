#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Print strict coverage percentages from a verified hybrid build report."""
import json
from pathlib import Path
import sys

LABELS={
 'c_compiled_executable':'Compiled C executable',
 'assembly_source_executable':'Source assembly executable',
 'compiled_non_executable_data':'Compiled non-executable data',
 'compiled_unclassified':'Compiled, classification unresolved',
 'pulled_executable_confirmed':'Confirmed executable pull-through',
 'pulled_non_executable_confirmed':'Confirmed non-executable pull-through',
 'pulled_compressed_initializers':'Compressed initializer pull-through',
 'pulled_unclassified':'Unclassified pull-through',
 'generated_non_executable_container':'Generated container metadata',
}


def markdown(value):
    summaries=value['summaries'];lines=['# Stored firmware byte accounting','',value['denominator_policy'],'',
        '| Category | '+' | '.join(s['scope'].upper() for s in summaries)+' |',
        '| --- | '+' | '.join('---:' for s in summaries)+' |']
    for key,label in LABELS.items():
        lines.append('| '+label+' | '+' | '.join(f"{s['bytes'][key]:,} B ({s['percent_of_stored_firmware'][key]:.5f}%)" for s in summaries)+' |')
    lines+=['| Total | '+' | '.join(f"{s['denominator_bytes']:,} B (100%)" for s in summaries)+' |','',
        'Executable and non-executable pull-through are confirmed lower bounds. Unclassified bytes are not assigned to either class. The function-envelope estimate is not instruction-level proof.',
        'C means emitted executable bytes from C translation units, excluding identified wholly handwritten assembly providers. C translation units may contain compiler intrinsics or inline assembly.',
        'Compiled literal-pool data is counted as non-executable data, not C executable instructions. Compressed initializers are separate because their expanded RAM contents can include code and data. Expanded RAM images and absent resident firmware are excluded.','',
        'This report does not establish complete source implementation, complete source integration, or hardware behavior.','']
    bounds=summaries[-1].get('compiled_c_share_of_stored_executable_bounds_percent')
    if bounds and all(b is not None for b in bounds):
        lines += [f'The compiled C share of stored executable bytes is bounded by {bounds[0]:.5f}% to {bounds[1]:.5f}%; its exact denominator is unresolved. This is not a source-completeness percentage.', '']
    if value.get('remaining_classification'):
        lines += ['## Refinement of unclassified pull-through', '', 'These evidence classes partition the remaining bytes; they do not establish executable status.', '', '| Evidence class | Bytes | % of stored firmware |', '| --- | ---: | ---: |']
        for key,count in value['remaining_classification']['totals'].items():
            lines.append(f'| {key.replace("_"," ")} | {count:,} | {100*count/summaries[-1]['denominator_bytes']:.5f}% |')
        lines += ['', 'See remaining-classification.csv for exclusive payload offsets and remaining-classification.json for hashed evidence.', '']
    return '\n'.join(lines)


def main():
    if len(sys.argv)!=2:raise SystemExit('usage: report_coverage.py path/to/coverage.json')
    value=json.loads(Path(sys.argv[1]).read_text());print(markdown(value))

if __name__=='__main__':main()
