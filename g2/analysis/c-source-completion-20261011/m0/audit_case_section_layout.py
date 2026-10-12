#!/usr/bin/env python3
"""Measure CASE sectioning, GC probe, and fixed reset placement limits."""
from pathlib import Path
import hashlib
import json
import re
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent
R=H.parents[3]
stock=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
assert hashlib.sha256(stock).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
def info(name):
    path=H/name
    with path.open('rb') as f:
        elf=ELFFile(f)
        seg=[s for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
        assert len(seg)==1
        sym={x.name:x['st_value'] for x in elf.get_section_by_name('.symtab').iter_symbols()}
        vector=elf.get_section_by_name('.isr_vector').data()
        return {'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'load_bytes':seg[0]['p_filesz'],'entry':hex(elf.header['e_entry']),
                'reset_symbol':hex(sym['case_reset_entry_0144']),
                'vector_bytes':len(vector),'vector_first_two_stock_equal':vector[:8]==stock[32:40],
                'vector_full_stock_equal':vector==stock[32:32+len(vector)]}
plain=info('case_sectioned_round.elf')
fixed=info('case_reset_placement_probe.elf')
gc=info('case_gc_probe.elf')
discarded=re.findall(r"removing unused section '([^']+)'",(H/'case_gc_probe.log').read_text())
code_discarded=[x for x in discarded if x.startswith('.text.')]
result={'status':'CASE_SECTION_LAYOUT_PROBE','stock_payload_bytes':len(stock)-32,
        'sectioned_all':plain,'fixed_reset_all':fixed,'gc_vector_reachable_only':gc,
        'gc_removed_code_section_count':len(code_discarded),
        'gc_removed_code_section_names':code_discarded,
        'gc_savings_vs_sectioned_bytes':plain['load_bytes']-gc['load_bytes'],
        'fixed_reset_overflow_bytes':fixed['load_bytes']-(len(stock)-32),
        'gc_overflow_bytes':gc['load_bytes']-(len(stock)-32),
        'limits':['GC roots include explicit source vectors and relocations only; native indirect registrations, callbacks and raw function-address roots have not all been authenticated.',
                  'GC removes case_event_post and HAL_UART_ErrorCallback among other source providers, so the vector-only GC image is a diagnostic lower bound, not a qualified final selection.',
                  'Reset symbol and first two vector words match native in the fixed placement; other vector entries and executable bytes do not.',
                  'Gap fill, complete memory layout, source data ownership and physical behavior remain open.']}
assert fixed['reset_symbol']=='0x8000145' and fixed['entry']=='0x8000145'
assert fixed['vector_bytes']==184 and fixed['vector_first_two_stock_equal']
assert result['fixed_reset_overflow_bytes']>0 and result['gc_overflow_bytes']>0
(H/'case-section-layout-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ('status','fixed_reset_overflow_bytes','gc_overflow_bytes','gc_savings_vs_sectioned_bytes','gc_removed_code_section_count')}))
