from pathlib import Path
import subprocess,tempfile,json,hashlib,re
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text()
body=s[s.index('/* Native30853c..'):s.index('/* Native30b1ac tail')]
for addr,name in [('805cac','config_ptr'),('805c70','primary_base'),('805c68','link_base'),('805c40','stream_base')]:
 body=body.replace('*(volatile uint32_t *)(uintptr_t)0x'+addr+'u',name)
body=body.replace('*(volatile uint32_t *)(record+4u)','((uintptr_t)(host_state[(record-(uintptr_t)stream)/256]))')
body=re.sub(r'__asm__ volatile\("mpywhl %0,%1,%2":"=r"\(offset\):"r"\(index\),"r"\(stride\)\);','offset=index*stride;',body)
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t config[64],changed_config[64],primary[4*912],changed_primary[4*912],link[4*656],stream[4*256],host_state[4][8];
static uintptr_t config_ptr,primary_base,link_base,stream_base;static unsigned calls,log_ids[16],return_id,mutate,phase;
uintptr_t opencfw_em9305_ll_primary_take_3252dc(uintptr_t record){unsigned id=(record-primary_base)/912;assert(id<4);log_ids[calls++]=id;if(id==return_id)return 0x1234;if(mutate){primary_base=(uintptr_t)changed_primary;config_ptr=(uintptr_t)changed_config;}return 0;}
uintptr_t opencfw_em9305_ll_pending_packet_take_31ba54(uintptr_t queue){unsigned id=(queue-(uintptr_t)link-532)/656;assert(id<4);log_ids[calls++]=id;if(id==return_id)return 0x1234;if(mutate){config_ptr=(uintptr_t)changed_config;}return 0;}
uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t queue,uintptr_t handler){unsigned id=(queue-(uintptr_t)stream-48)/256;assert(id<4);log_ids[calls++]=4+id;*(uint8_t*)handler=7;if(4+id==return_id)return 0x1234;if(mutate)config_ptr=(uintptr_t)changed_config;return 0;}
'''+body+r'''
int main(void){unsigned cases=0;
for(unsigned count=1;count<=4;count++)for(unsigned mask=0;mask<16;mask++)for(return_id=0;return_id<5;return_id++)for(mutate=0;mutate<2;mutate++){
 memset(primary,0,sizeof(primary));memset(changed_primary,0,sizeof(changed_primary));memset(config,0,64);memset(changed_config,0,64);config[34]=count;
 for(unsigned i=0;i<4;i++){primary[i*912]=(mask>>i)&1;changed_primary[i*912]=1;}
 config_ptr=(uintptr_t)config;primary_base=(uintptr_t)primary;calls=0;unsigned expected[4],n=0,result=0,swapped=0;
 for(unsigned i=count;i-->0;){if(swapped||((mask>>i)&1)){expected[n++]=i;if(i==return_id){result=0x1234;break;}if(mutate)swapped=1;}}
 assert(opencfw_em9305_ll_primary_pending_30853c()==result&&calls==n);for(unsigned i=0;i<n;i++)assert(log_ids[i]==expected[i]);cases++;
}
for(unsigned mask=0;mask<256;mask++)for(return_id=0;return_id<9;return_id++)for(mutate=0;mutate<2;mutate++){
 memset(link,0,sizeof(link));memset(stream,0,sizeof(stream));memset(host_state,0,sizeof(host_state));memset(config,0,64);memset(changed_config,0,64);config[53]=4;config[58]=4;changed_config[53]=2;changed_config[58]=2;
 for(unsigned i=0;i<4;i++){link[i*656]=(mask>>i)&1;stream[i*256]=(mask>>(4+i))&1;}
 config_ptr=(uintptr_t)config;link_base=(uintptr_t)link;stream_base=(uintptr_t)stream;calls=0;unsigned expected[8],n=0,result=0,changed=0;
 for(unsigned i=0;i<(changed?2:4);i++)if((mask>>i)&1){expected[n++]=i;if(i==return_id){result=0x1234;break;}if(mutate)changed=1;}
 if(!result)for(unsigned i=0;i<(changed?2:4);i++)if((mask>>(4+i))&1){expected[n++]=4+i;if(4+i==return_id){result=0x1234;break;}if(mutate)changed=1;}
 assert(opencfw_em9305_ll_link_pending_30858c()==result&&calls==n);for(unsigned i=0;i<n;i++)assert(log_ids[i]==expected[i]);cases++;
}
for(unsigned enabled=0;enabled<256;enabled++)for(unsigned marker=0;marker<256;marker++){
 memset(stream,0,sizeof(stream));stream[108]=enabled;stream[44]=marker;calls=0;return_id=4;mutate=0;unsigned takes=enabled||marker<=1;
 assert(opencfw_em9305_ll_stream_take_317624((uintptr_t)stream)==(takes?0x1234:0)&&calls==takes);cases++;
}
printf("%u\n",cases);}
'''
h=h.replace(',phase;', ';')
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('pending-scans-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual three scan/take C bodies, normalized runtime/state pointers and MPYWHL arithmetic. Controlled queue children. Counts1..4, active masks, packet precedence, primary base reload and link/stream config reload after child mutation, exhaustive stream enabled/state bytes. Zero-count primary native underflow is outside controlled finite domain. Not native ISA/runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
