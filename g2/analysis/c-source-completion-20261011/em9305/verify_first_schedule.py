from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native31b7fc..'):s.index('/* Native31bad0..')]
body=body.replace('*(volatile uint32_t *)(descriptor+16u)','((uintptr_t)slot_data)').replace('*(volatile uint32_t *)(uintptr_t)0x8027f8u','(present?(uintptr_t)&host_callback:0)')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static _Alignas(4) uint8_t slot_data[20],desc[36],req[24];static unsigned present,result,calls,timers;
static uint32_t word(uintptr_t p){return *(uint32_t*)p;}
uint32_t opencfw_em9305_ll_test_complete_31bad0(uint32_t a,uint32_t b,uint32_t c,uintptr_t d,uint32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;assert(0);return 0;}
uint32_t opencfw_em9305_ll_test_timer_31c490(uint32_t id,uint32_t context){assert(id==0x1234&&context==0x76543210);timers++;return 99;}
static uint32_t host_callback(uint32_t id,uintptr_t f){assert(id==0x7788);calls++;assert(*(uint32_t*)(slot_data+4)==0xa5a5a5a5&&*(uint32_t*)(slot_data+8)==0xa5a5a5a5&&*(uint16_t*)(slot_data+2)==0x7788);assert(*(uint8_t*)f==0&&word(f+4)==0x11223344&&*(uint8_t*)(f+8)==req[4]&&*(uint16_t*)(f+10)==0x3456&&*(uint16_t*)(f+12)==0x789a&&*(uint8_t*)(f+16)==req[16]);assert(word(f+20)==0xaabbccdd&&word(f+24)==0x55667788&&word(f+28)==(uint32_t)(uintptr_t)&opencfw_em9305_ll_test_complete_31bad0&&word(f+32)==0x12345678&&word(f+36)==0x87654321&&word(f+40)==0x31415926&&word(f+44)==0x27182818&&*(uint8_t*)(f+48)==0);slot_data[0]=17;*(uint16_t*)desc=0x1234;return result;}
'''+body+r'''
int main(void){unsigned count=0;for(unsigned marker=0;marker<256;marker++){for(unsigned pattern=0;pattern<256;pattern++){for(present=0;present<2;present++){for(result=0;result<2;result++){
 memset(slot_data,0xa5,20);memset(desc,0,36);memset(req,0,24);slot_data[0]=marker;*(uint16_t*)desc=0x7788;*(uint32_t*)(desc+8)=0x11223344;*(uint32_t*)(desc+12)=0x55667788;*(uint32_t*)(desc+20)=0x12345678;*(uint32_t*)(desc+24)=0x87654321;*(uint32_t*)(desc+28)=0x31415926;*(uint32_t*)(desc+32)=0x27182818;req[4]=pattern;req[16]=255-pattern;*(uint16_t*)(req+6)=0x3456;*(uint16_t*)(req+8)=0x789a;*(uint32_t*)(req+20)=0xaabbccdd;calls=timers=0;
 unsigned expected=marker==0||marker==255?0:marker!=1||!present?18:result?0:13;assert(opencfw_em9305_ll_test_schedule_first_31b7fc((uintptr_t)desc,(uintptr_t)req,0x76543210)==expected&&calls==(marker==1&&present)&&timers==(marker==1&&present&&result));
 assert(slot_data[0]==(marker==1&&present?(result?17:255):marker));assert(word((uintptr_t)(slot_data+4))==0xa5a5a5a5&&word((uintptr_t)(slot_data+8))==0xa5a5a5a5);assert(slot_data[12]==0xa5);assert(*(uint16_t*)(slot_data+2)==(marker==1?0x7788:0xa5a5));count++;
}}}}printf("%u\n",count);}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('first-schedule-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C with normalized descriptor/slot and callback cell. Allmarker/type/flag bytefixtures, callback missing/failure/success, authenticated52B scratch fields ignoring unspecified padding, slot id pre-callback write, callback marker/descriptor id mutation, source-relocated completion callback and reloaded id/context timer handoff with ignored child status. Not native runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
