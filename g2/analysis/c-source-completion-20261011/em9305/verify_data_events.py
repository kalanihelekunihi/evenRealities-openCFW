from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native331b3c..'):s.index('/* Native331c20..')]
for addr,name in [('8056f8','feature19'),('8056f9','feature20'),('8056ef','enabled')]:body=body.replace('*(volatile uint8_t *)(uintptr_t)0x'+addr+'u',name)
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t request[80],storage[80],feature19,feature20,enabled;static unsigned type,alloc_ok,mutate,allocations,copies,sends;
uintptr_t opencfw_em9305_ll_event_allocate(uint32_t code,uint32_t length){assert(code==62&&length==(type==19?66:34));allocations++;if(mutate)request[4]=85;return alloc_ok?(uintptr_t)(storage+2):0;}
void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){assert(n==32&&d==storage+(copies?36:4)&&s==request+(copies?37:5));if(type==19)assert(storage[3]==0&&(copies?storage[2]==8:storage[2]==0xa5));else assert(storage[2]==9&&storage[3]==(mutate?85:42));memcpy(d,s,n);copies++;if(mutate&&type==19&&copies==1)for(unsigned i=37;i<69;i++)request[i]^=255;return d;}
uint32_t opencfw_em9305_ll_event_send(uintptr_t event){assert(event==(uintptr_t)storage&&copies==(type==19?2:1));sends++;return 99;}
'''+body+r'''
int main(void){unsigned count=0;for(type=19;type<=20;type++){for(unsigned feature=0;feature<256;feature++){for(unsigned enable=0;enable<256;enable++){for(alloc_ok=0;alloc_ok<2;alloc_ok++){for(mutate=0;mutate<2;mutate++){
 for(unsigned i=0;i<80;i++)request[i]=(uint8_t)(feature+i*13);request[2]=type;request[4]=42;memset(storage,0xa5,80);feature19=feature20=feature;enabled=enable;allocations=copies=sends=0;unsigned gated=(feature&(type==19?128:1))&&(enable&32),success=gated&&alloc_ok;
 assert(opencfw_em9305_dispatch_331b3c((uintptr_t)request)==success&&allocations==gated&&copies==(success?(type==19?2:1):0)&&sends==success);
 if(success){assert(storage[2]==(type==19?8:9)&&storage[3]==(type==19?0:mutate?85:42));for(unsigned i=0;i<32;i++){assert(storage[4+i]==(uint8_t)(feature+(i+5)*13));if(type==19)assert(storage[36+i]==(uint8_t)((feature+(i+37)*13)^(mutate?255:0)));}for(unsigned i=type==19?68:36;i<80;i++)assert(storage[i]==0xa5);}else for(unsigned i=0;i<80;i++)assert(storage[i]==0xa5);count++;
}}}}}for(type=0;type<256;type++)if(type!=19&&type!=20){request[2]=type;allocations=copies=sends=0;assert(opencfw_em9305_dispatch_331b3c((uintptr_t)request)==0&&allocations==0&&copies==0&&sends==0);count++;}printf("%u\n",count);}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('data-events-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C event builder normalized feature/enable cells; fullbyte mask fixtures, allocation failure/success, exactheader/copy/send order and input mutation byallocator/firstcopy, handled return despite nonzero sendchild return. Controlled children; not native runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
