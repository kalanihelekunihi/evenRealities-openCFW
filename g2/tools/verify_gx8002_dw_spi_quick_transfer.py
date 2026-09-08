#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Aggregate reviewed transfer contracts for source integration, not hardware release."""
import hashlib
import json
import shutil
from verify_gx8002_logging import check_paths
from build_gx8002_dw_spi_quick_transfer_candidate import ROOT
from verify_gx8002_spi_transfer_lifecycle import verify as lifecycle
from verify_gx8002_spi_transfer_alignment import verify as alignment
from verify_gx8002_spi_transfer_tx import verify as tx
from verify_gx8002_spi_transfer_rx import verify as rx
from verify_gx8002_spi_transfer_message import verify as message
from verify_gx8002_spi_transfer_gate_composition import verify as gate


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    reports={name:fn() for name,fn in (('lifecycle',lifecycle),('alignment',alignment),
                                      ('tx',tx),('rx',rx),('message',message),('gate',gate))}
    candidate=reports['lifecycle']['candidate']
    if not candidate['fits'] or candidate['compiled_bytes']!=602:
        raise ValueError('Transfer placement changed')
    if any(report['candidate']!=candidate for report in reports.values()):
        raise ValueError('Candidate changed during qualification')
    names=['verify_gx8002_dw_spi_quick_transfer.py','build_gx8002_dw_spi_quick_transfer_candidate.py',
           'analyze_gx8002_dw_spi_quick_transfer.py','compare_gx8002_platform_gate.py',
           'link_gx8002_platform_gate.py']
    names.extend('verify_gx8002_spi_transfer_'+suffix+'.py' for suffix in
                 ('lifecycle','alignment','tx','rx','message','gate_composition'))
    names.extend('model_gx8002_spi_transfer_'+suffix+'.py' for suffix in
                 ('lifecycle','alignment','tx','rx','message'))
    hashes={name:hashlib.sha256((ROOT/'tools'/name).read_bytes()).hexdigest() for name in names}
    row={key:candidate[key] for key in ('symbol','section_name','compiled_bytes','compiled_sha256')}
    row['stock_occurrences']=[{'symbol':candidate['symbol'],'package_offset':0xf790,'bytes':634,
                               'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/dw-spi-quick-transfer-candidate.elf',output/'dw-spi-quick-transfer.elf')
    return {'functions':[row],'evidence':candidate,'qualification':reports,'evidence_sha256':hashes,
            'decoded_transfer_cases':sum(reports[k]['decoded_cases'] for k in ('lifecycle','alignment','tx','rx','message')),
            'source_admitted':True,'hardware_qualified':False,
            'limits':['Source admission covers recovered valid-buffer/list contracts; it is not whole-firmware or hardware qualification.',
                      'Unsupported widths, malformed/metadata-aliased lists, FIFO overrun/negative free space, concurrent mutation and non-progressing hardware remain outside finite replay.',
                      'Clock-boundary composition uses the existing modeled lookup and separate abstract helper stack; no shared nested-stack or physical timing proof.',
                      'Shared RX/TX data buffers are modeled; metadata remains distinct. No new timeout, saturation or validation behavior is introduced.']}

if __name__=='__main__':
    report=verify()
    (ROOT/'docs/research/gx8002-dw-spi-quick-transfer-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Qualified decoded transfer cases:',report['decoded_transfer_cases'])
