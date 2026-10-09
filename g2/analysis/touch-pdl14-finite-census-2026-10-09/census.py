from pathlib import Path
import csv,json,hashlib,re
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
completed=set('Cy_MSCLP_Configure Cy_MSCLP_Capture Cy_GPIO_SetHSIOM Cy_GPIO_Write Cy_GPIO_SetDrivemode Cy_GPIO_SetInterruptEdge Cy_GPIO_Pin_Init Cy_SCB_ReadArrayNoCheck Cy_SCB_WriteArrayNoCheck Cy_SCB_WriteDefaultArrayNoCheck Cy_SCB_ReadArray Cy_SCB_WriteArray Cy_SCB_WriteDefaultArray'.split())
source_map={'Cy_SysLib_':'cy_syslib.c','Cy_Flash_':'cy_flash.c','Cy_SysClk_':'cy_sysclk.c','Cy_SysInt_':'cy_sysint.c','Cy_SysPm_':'cy_syspm.c','Cy_SysTick_':'cy_systick.c','Cy_SCB_I2C_':'cy_scb_i2c.c'}
payload=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';b=payload.read_bytes();assert sha(payload)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';rows=[]
for row in csv.reader((R/'g2/symbols/touch.tsv').open(),delimiter='\t'):
 if len(row)<8 or not row[3].startswith('Cy_') or 'mtb-pdl-cat2' not in row[4]:continue
 a=int(row[0],16);n=int(row[2]);digest=hashlib.sha256(b[32+a-0x3300:32+a-0x3300+n]).hexdigest();assert digest==row[-1],row[3]
 src=next((v for k,v in source_map.items() if row[3].startswith(k)),None)
 status='completed_selected_comparator' if row[3] in completed else 'predeclared_unchanged_source_comparison' if src else 'header_inline_provider_requires_separate_source_emission_contract'
 rows.append({'function':row[3],'address':a,'historical_code_bytes':n,'target_code_sha256':digest,'absolute_payload_offset':32+a-0x3300,'confidence':row[5],'source_unit':src,'status':status})
tasks=R/'g2/build/pseudocode-first/20260930T190500Z/tasks';overlaps=[]
for p in tasks.glob('*.json'):
 d=json.loads(p.read_text());s=d.get('scope','');s=s if isinstance(s,str) else json.dumps(s)
 for a,z in re.findall(r'\[\s*(0x[0-9a-fA-F]+)\s*,\s*(0x[0-9a-fA-F]+)\s*\)',s):
  for row in rows:
   if row['status']=='predeclared_unchanged_source_comparison' and int(a,16)<row['address']+row['historical_code_bytes'] and row['address']<int(z,16):overlaps.append({'task':str(p.relative_to(R)),'function':row['function']})
assert not overlaps,overlaps
record={'scope':'existing Cy_ PDL-attributed symbol rows only; not all firmware functions','selection_before_compilation':True,'payload_sha256':sha(payload),'symbols_sha256':sha(R/'g2/symbols/touch.tsv'),'functions':rows,'recognized_task_overlaps':overlaps,'extra_completed_control_not_named_in_symbols':'Cy_MSCLP_ConfigureScan'}
(O/'selection.json').write_text(json.dumps(record,indent=2)+'\n');print('finite candidates',len(rows),'new comparisons',sum(x['status']=='predeclared_unchanged_source_comparison' for x in rows))
