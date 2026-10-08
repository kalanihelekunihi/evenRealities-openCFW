from pathlib import Path
import sys,subprocess,json
D=Path(__file__).resolve().parent
GCC=Path(sys.argv[1]);base=Path(sys.argv[2]);src=D.parents[1]/'components/touch/config_bootstrap_offline/bootstrap.c'
mutations={
 'accept_wrong_magic':('RECORD->magic!=0x45564e55u','RECORD->magic!=0x12345678u',('wrongmagic',1000,'success',0)),
 'accept_failed_read':('if(s || RECORD->magic','if(RECORD->magic',('badhistoric',1000,'success',0)),
 'ignore_default_write_failure':('if(s){touch_bootstrap_log(0xab48','if(0){touch_bootstrap_log(0xab48',('zero',1000,'erase-base-error',0))}
results=[]
for name,(a,b,inputs) in mutations.items():
 dest=base/name;dest.mkdir(parents=True,exist_ok=True);source=dest/'bootstrap.c';source.write_text(src.read_text().replace(a,b))
 # Override one compiled object, then use the same explicitly retained entry set.
 subprocess.run([str(GCC),'-mcpu=cortex-m0plus','-mthumb','-Og','-fshort-enums','-ffreestanding','-fno-builtin','-ffunction-sections','-I'+str(src.parent),'-I'+str(src.parent.parent/'eeprom_offline'),'-I'+str(src.parent.parent/'eeprom_init_offline'),'-c',str(source),'-o',str(dest/'bootstrap.o')],check=True)
 objs=[str(dest/'bootstrap.o') if p.name=='bootstrap.o' else str(p) for p in base.glob('*.o')]
 elf=dest/'provider.elf';subprocess.run([str(GCC.with_name('arm-none-eabi-ld')),'--gc-sections','-Ttext=0x100000','-e','touch_config_bootstrap','-u','touch_factory_eeprom_configuration','-u','touch_provider_read_size','-u','touch_provider_erase_value','-u','touch_storage_zero',*objs,'-o',str(elf)],check=True)
 sys.argv=[str(D/'verify.py'),str(elf)];ns={'__file__':str(D/'verify.py')};exec((D/'verify.py').read_text().split('cases=[];coverage=set()')[0],ns)
 original,_=ns['boot'](False,*inputs);mutant,_=ns['boot'](True,*inputs);assert original!=mutant,name
 results.append({'mutant':name,'rejected':True,'inputs':inputs,'original_logs':original['logs'],'mutant_logs':mutant['logs']})
(D/'negative-results.json').write_text(json.dumps(results,indent=2)+'\n');print('PASS',len(results),'mutants rejected')
