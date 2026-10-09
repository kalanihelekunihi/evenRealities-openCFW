from pathlib import Path
import re,subprocess,json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[2]
s=(R/'g2/analysis/source-discovery-parallel-2026-10-09/acquisitions/st-case-flash-pin/stm32g0xx_hal_flash.c').read_text();d=(O/'stm32g0b1xx.h').read_text();h=(O/'stm32g0xx_hal_flash.h').read_text();u=(O/'stm32g0xx.h').read_text();defs=(O/'stm32g0xx_hal_def.h').read_text()
reg=re.search(r'typedef struct\s*\{[^}]+\}\s*FLASH_TypeDef;',d).group();enum=re.search(r'typedef enum\s*\{[^}]*HAL_OK[^}]*\}\s*HAL_StatusTypeDef;',defs).group()
macros=[]
for text,names in [(h,['FLASH_KEY1','FLASH_KEY2','FLASH_OPTKEY1','FLASH_OPTKEY2']),(d,['FLASH_CR_OPTLOCK_Pos','FLASH_CR_OPTLOCK_Msk','FLASH_CR_OPTLOCK','FLASH_CR_LOCK_Pos','FLASH_CR_LOCK_Msk','FLASH_CR_LOCK']),(u,['READ_BIT','WRITE_REG'])]:
 for name in names:
  line=next(l for l in text.splitlines() if re.match(r'#define\s+'+name+r'(?:\s|\()',l));macros.append(line.split('/*!')[0].split('/*')[0].rstrip())
bodies=[]
for name in ['HAL_FLASH_Unlock','HAL_FLASH_OB_Unlock']:
 m=re.search(r'HAL_StatusTypeDef '+name+r'\(void\)\s*\{',s);i=m.end();depth=1
 while depth:
  depth+=(s[i]=='{')-(s[i]=='}');i+=1
 bodies.append(s[m.start():i])
# Explicit bounded environment, not a full SDK/configuration build.
unit='#include <stdint.h>\n#define __IO volatile\n'+reg+'\n'+enum+'\n'+'\n'.join(macros)+'\n#define FLASH ((FLASH_TypeDef *)0x40022000UL)\n'+'\n'.join(bodies)+'\n'
(O/'selected-public.c').write_text(unit)
flags=['--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin'];argv=['clang',*flags,'-c',str(O/'selected-public.c'),'-o',str(O/'selected-public.o')];subprocess.run(argv,check=True)
subprocess.run(['clang',*flags,'-S',str(O/'selected-public.c'),'-o',str(O/'selected-public.s')],check=True)
(O/'build-receipt.json').write_text(json.dumps({'argv':argv,'compiler':subprocess.check_output(['clang','--version'],text=True),'selected_source_sha256':hashlib.sha256(unit.encode()).hexdigest(),'object_sha256':hashlib.sha256((O/'selected-public.o').read_bytes()).hexdigest(),'profile':'single size-optimized offline Clang ARMv6-M comparator; not producing armclang','genuine_bodies_and_selected_definitions':True,'full_sdk_build':False},indent=2)+'\n')
