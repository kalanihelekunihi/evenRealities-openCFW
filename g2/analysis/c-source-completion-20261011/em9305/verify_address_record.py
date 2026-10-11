from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native303b40..303b7c'):s.index('/* Native30af30..30af98')].replace('*(volatile uint8_t *)(uintptr_t)0x801610u','host_count').replace('*(volatile uint32_t *)(uintptr_t)0x805c00u','records_pointer').replace('__asm__ volatile("mpyuw %0,%1,72":"=r"(offset):"r"(count));','offset=count*72u;')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t records[72*256],row[72],host_count;static uintptr_t records_pointer;static unsigned found,lookups,copies,original;
uintptr_t opencfw_em9305_radio_identity_find_31441c(uint32_t k,uint32_t l,uint32_t h){assert(k==1&&l==0x1234&&h==0x5678);lookups++;return found?(uintptr_t)row:0;}
void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){assert(d==row&&s==records+(original-1)*72&&n==72);copies++;host_count=99;return memcpy(d,s,n);}
'''+body+r'''
int main(void){unsigned n=0;records_pointer=(uintptr_t)records;for(unsigned i=0;i<sizeof(records);i++)records[i]=i*17;for(original=0;original<256;original++)for(found=0;found<2;found++){host_count=original;lookups=copies=0;memset(row,0xa5,72);assert(opencfw_em9305_radio_address_update_303b40(1,0x1234,0x5678)==found);assert(lookups==1&&copies==(found&&original>=2)&&host_count==(found?(uint8_t)(original-1):original));if(copies)assert(memcmp(row,records+(original-1)*72,72)==0);else for(unsigned i=0;i<72;i++)assert(row[i]==0xa5);n++;}printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('address-record-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C allcountbytes, lookupmiss/found, last72Brow replacement, capturedcount acrosscopy and wrapzero. Normalized RAM/children/MPYUW; nativeISA/hardware unproved.'},indent=2)+'\n');print('PASS',n)
