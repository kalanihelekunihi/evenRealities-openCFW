# SPDX-License-Identifier: MIT
"""Fresh-process admission and layout checks for recovered DMA replacements."""
import importlib,json
from build_gx8002_source_candidate import ROOT,IMAGE,reviewed_replacements,compose

KINDS=('bus-address','descriptors','configure','callback','select','deallocate','irq-handler','clear','initialize','transfer')

UART_ENTRIES=(('dma-burst','burst',1),('receive-complete','complete',1),('receive-control','control',2),('transmit-control','control',2),('receive-buffer','buffer',1),('transmit-buffer','buffer',1),('receive-dma','dma',1))

def verify():
    output=ROOT/'build/gx8002-dma-source-admissions';replacements=[]
    for kind in KINDS:
        module=importlib.import_module('verify_gx8002_dma_'+kind.replace('-','_')+'_source')
        directory=output/kind
        report=module.verify(output=directory)
        baseline=json.loads((ROOT/f'docs/research/gx8002-dma-{kind}-source-verification.json').read_text())
        artifact=directory/(kind.replace('-','_')+'.elf')
        replacements.extend(reviewed_replacements(report,baseline,artifact,'dma-'+kind))
    for kind,artifact_name,count in UART_ENTRIES:
        module=importlib.import_module('verify_gx8002_uart_'+kind.replace('-','_')+'_source')
        directory=output/('uart-'+kind)
        report=module.verify(output=directory)
        baseline=json.loads((ROOT/f'docs/research/gx8002-uart-{kind}-source-verification.json').read_text())
        rows=reviewed_replacements(report,baseline,directory/(artifact_name+'.elf'),'uart-'+kind)
        if len(rows)!=count:raise ValueError('UART admission count')
        replacements.extend(rows)
    firmware,ownership,totals=compose(IMAGE.read_bytes(),replacements)
    expected=sum(row['bytes'] for row in replacements)
    for row in replacements:
        offset=row['package_offset']
        if firmware[offset:offset+row['bytes']]!=row['payload']:
            raise ValueError('DMA composed payload differs from qualified ELF')
    source_spans=[entry for entry in ownership if entry['kind']=='compiled_c']
    if {entry['symbol'] for entry in source_spans}!={row['symbol'] for row in replacements}:
        raise ValueError('DMA ownership symbol coverage')
    if totals['compiled_c']!=sum(row['compiled_bytes'] for row in replacements):raise ValueError('DMA compiled ownership')
    if len(replacements)!=len(KINDS)+sum(entry[2] for entry in UART_ENTRIES):raise ValueError('DMA admission coverage')
    return {'admitted_functions':len(replacements),'replaced_envelope_bytes':expected,
        'compiled_bytes':totals['compiled_c'],'image_bytes':len(firmware),
        'source_only':False,'hardware_qualified':False,
        'limits':['Isolated DMA replacement layout and container checks only; other firmware bytes retained. Not a complete source-only firmware build.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-dma-source-admissions.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
