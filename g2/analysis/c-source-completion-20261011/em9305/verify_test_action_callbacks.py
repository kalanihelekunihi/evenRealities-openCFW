from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native31b7e4..'):s.index('/* Native32385c..')]
body=body.replace('*(volatile uint32_t *)(request+16u)','*(uintptr_t *)request').replace('*(volatile uint32_t *)(uintptr_t)0x8027fcu','((uintptr_t)&host_callback)').replace('*(volatile uint8_t *)(uintptr_t)0x805addu','released_count')
h=r'''
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static _Alignas(4) uint8_t slot[32];static uint8_t released_count;static unsigned kind,marker,queued,removes,releases,enters,exits,callbacks,stage,mutate,critical_mutate;
static uint32_t host_callback(uint32_t id,uint32_t mode){assert(id==0x7d38&&mode==kind);callbacks++;if(mutate)slot[kind?4:0]=255;return 0xcafebabe;}
uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t queue,uintptr_t handler){assert(queue==(uintptr_t)(slot+4)&&stage==0);removes++;if(releases==queued)return 0;*(uint8_t*)handler=17;stage=1;return 0x1000+16*releases;}
uint32_t opencfw_em9305_wsf_event_release(uintptr_t event){assert(stage==1&&event==0x1000+16*releases);stage=2;releases++;return 99;}
uint32_t opencfw_em9305_wsf_critical_enter(void){assert(stage==2);stage=3;enters++;if(critical_mutate)released_count=127;return 99;}
uint32_t opencfw_em9305_wsf_critical_exit(void){assert(stage==3);stage=0;exits++;return 99;}
'''+body+r'''
int main(void){unsigned count=0;for(kind=0;kind<2;kind++){for(marker=0;marker<256;marker++){for(unsigned initial=0;initial<256;initial++){for(queued=0;queued<9;queued++){for(mutate=0;mutate<2;mutate++){for(critical_mutate=0;critical_mutate<2;critical_mutate++){
 memset(slot,0xa5,32);slot[kind?4:0]=marker;*(uint16_t*)(slot+(kind?14:2))=0x7d38;released_count=initial;removes=releases=enters=exits=callbacks=stage=0;
 uintptr_t request=(uintptr_t)slot;uint32_t result=kind?opencfw_em9305_ll_test_action_31b8a8((uintptr_t)&request):opencfw_em9305_ll_test_action_31b7e4((uintptr_t)&request);unsigned drain=kind&&marker<=1;unsigned expected_count=drain&&queued?(critical_mutate?128:(initial+queued)&255):initial;
 assert(result==(kind?(marker<=1?0:marker):(marker==1?0xcafebabe:marker))&&callbacks==(marker==1));assert(released_count==expected_count&&removes==(drain?queued+1:0)&&releases==(drain?queued:0)&&enters==releases&&exits==releases&&stage==0);assert(slot[kind?4:0]==(mutate&&marker==1?255:marker));count++;
}}}}}}printf("%u\n",count);}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('test-action-callbacks-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual two C bodies, normalized runtime pointer/callback/counter cells, controlled selected WSF children. Exhaustive marker/counter bytes, queue lengths0..8, exact release/critical order, callback/counter mutation, nonboolean returns. Native-required callback remains unguarded. Not native runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
