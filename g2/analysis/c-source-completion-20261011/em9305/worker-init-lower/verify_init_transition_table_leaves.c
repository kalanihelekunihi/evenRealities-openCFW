#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_init_transition_3249ac(uintptr_t);
extern uint32_t opencfw_em9305_init_transition_3249b8(uintptr_t);
extern uint32_t opencfw_em9305_init_transition_3249bc(uintptr_t);
extern uint32_t opencfw_em9305_init_transition_32d0f4(uintptr_t);
extern uint32_t opencfw_em9305_init_transition_32d108(uint32_t);
extern uint32_t opencfw_em9305_init_transition_32d10c(uintptr_t);
extern uint32_t opencfw_em9305_init_transition_32d2dc(uintptr_t);
extern uint32_t opencfw_em9305_init_transition_31a408(uintptr_t);
extern uint32_t opencfw_em9305_init_transition_31a538(uintptr_t);
extern uint32_t opencfw_em9305_init_transition_31a554(uintptr_t);
extern uint32_t opencfw_em9305_init_transition_31a58c(uintptr_t);
extern uint32_t opencfw_em9305_init_transition_316698(uintptr_t);
extern uint32_t opencfw_em9305_init_transition_3166a0(uintptr_t);
extern uint32_t opencfw_em9305_init_transition_3166bc(uintptr_t);
extern uint32_t opencfw_em9305_init_transition_3166c4(uintptr_t);
extern uint32_t opencfw_em9305_init_transition_3166d8(uintptr_t);
extern uint32_t opencfw_em9305_init_transition_gate_3168e4(void);
extern uint32_t opencfw_em9305_init_transition_316894(uintptr_t);
extern uint32_t opencfw_em9305_init_transition_3168b0(uintptr_t);
static unsigned notify_calls,cleanup_calls,mutate_on_notify,event_calls,timer_calls,callback_calls;
static uintptr_t expected_notify=0x810030u;
static char trace[32];static unsigned trace_pos,track;
static void mark(char c){if(track)trace[trace_pos++]=c;}
uint32_t opencfw_em9305_command_advertising_error_30e758(uint32_t status)
{ assert(status==0u||status==12u);mark('e');return 0x700u+status; }
uint32_t opencfw_em9305_init_state_count_down_30e49c(void)
{ mark('h');return 0x987u; }
uint32_t opencfw_em9305_init_transition_refresh_327dbc(void)
{ mark('f');return 0x34u; }
uint32_t opencfw_em9305_common_request_30455c(uint32_t mode)
{ assert(mode==1u);mark('q');return 0u; }
uint32_t opencfw_em9305_command_count_30e4bc(void)
{ mark('c');return 0u; }
uint32_t opencfw_em9305_init_secondary_count_up_30e4cc(void)
{ mark('u');return 0u; }
uint32_t opencfw_em9305_init_transition_start_327b60(void)
{ mark('s');return 0x56u; }
static unsigned release_calls,down_calls,terminate_calls;
static unsigned report_calls,prepare_calls;
static uint32_t prepared_result,prepare_mutates;
uint32_t opencfw_em9305_init_transition_report_316908(
    uint32_t id,uint32_t kind,uint32_t r2,uint32_t r3,uint32_t r4)
{ assert(id==7u);
  if(kind==12u)assert(r2==9u&&r3==0x3333u&&r4==0x4444u);
  else assert(kind==2u&&r2==4u&&r3==0x1111u&&r4==0x2222u);
  ++report_calls;return 0x4a4au; }
uint32_t opencfw_em9305_init_transition_prepare_31a700(
    uintptr_t record,uint32_t r1,uint32_t r2,uint32_t r3,uint32_t r4,uint32_t r5)
{ assert(record==0x812000u&&r1==6u&&r2==0x1111u&&r3==0x2222u);
  assert(r4==4u&&r5==5u);++prepare_calls;
  if(prepare_mutates) {
      *(uint32_t *)(uintptr_t)0x815008u=0xaabbu;
      *(uint32_t *)(uintptr_t)0x81500cu=0xccddu;
      *(uint8_t *)(uintptr_t)0x815006u=8u;
  }
  return prepared_result; }
uint32_t opencfw_em9305_common_release_304588(uint32_t mode)
{ assert(mode==1u);++release_calls;mark('r');return 0u; }
uint32_t opencfw_em9305_command_count_down_30e48c(void)
{ assert(*(uint8_t *)(uintptr_t)0x805a74u==254u);
  ++down_calls;mark('g');return 0xabcu; }
uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t source,uint32_t reason)
{ assert(source==0x814720u&&reason==77u);
  ++terminate_calls;return 0u; }
uint32_t opencfw_em9305_ll_schedule_notify_313354(uintptr_t object)
{ assert(object==expected_notify);++notify_calls;
  if(mutate_on_notify)*(uint32_t *)(uintptr_t)0x8051d0u=0x811000u;
  return 0x1234u; }
uint32_t opencfw_em9305_init_secondary_cleanup_321450(uintptr_t record)
{ assert(record==0x810000u);++cleanup_calls;return 0x5678u; }
uint32_t opencfw_em9305_init_transition_event_308664(uint32_t kind,
                                                       uintptr_t record,uint32_t index)
{ assert(kind==62u&&record==0x811000u&&index==0x5au);
  ++event_calls;return 0x1357u; }
uint32_t opencfw_em9305_wsf_timer_stop(uintptr_t timer)
{ assert(timer==0x804398u+700u);++timer_calls;return 0xbeefu; }
uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event)
{ const uint8_t *p=(const uint8_t *)event;
  assert(p[0]==0u&&p[1]==0u&&p[2]==31u&&p[3]==0u);
  assert(p[4]==2u&&p[5]==0u);++callback_calls;return 0x2468u; }
int main(void)
{
    assert(mmap((void *)0x802000u,4096u,PROT_READ|PROT_WRITE,
                MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x802000u);
    assert(mmap((void *)0x804000u,4096u,PROT_READ|PROT_WRITE,
                MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x804000u);
    assert(mmap((void *)0x805000u,4096u,PROT_READ|PROT_WRITE,
                MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x805000u);
    assert(mmap((void *)0x810000u,4096u,PROT_READ|PROT_WRITE,
                MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x810000u);
    assert(mmap((void *)0x811000u,4096u,PROT_READ|PROT_WRITE,
                MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x811000u);
    for(uintptr_t base=0x812000u;base<=0x814000u;base+=0x1000u)
        assert(mmap((void *)base,4096u,PROT_READ|PROT_WRITE,
                    MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)base);
    assert(mmap((void *)0x815000u,4096u,PROT_READ|PROT_WRITE,
                MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x815000u);
    uint8_t *record=(uint8_t *)(uintptr_t)0x810000u;
    *(uint32_t *)(uintptr_t)0x8051d0u=0x810000u;
    assert(opencfw_em9305_init_transition_3249ac((uintptr_t)record)==0x1234u);
    assert(record[2]==1u&&notify_calls==1u);
    assert(opencfw_em9305_init_transition_3249b8((uintptr_t)record)==0x5678u);
    assert(cleanup_calls==1u);
    expected_notify=0x804398u+48u;
    assert(opencfw_em9305_init_transition_3249bc(0x804398u)==0x2468u);
    assert(*(uint8_t *)(uintptr_t)0x80439au==1u);
    assert(timer_calls==1u&&callback_calls==1u);
    expected_notify=0x810030u;
    assert(opencfw_em9305_init_transition_32d0f4(0x777u)==0x1234u);
    assert(record[3]==1u&&notify_calls==3u);
    assert(opencfw_em9305_init_transition_32d108(0xdeadbeefu)==0xdeadbeefu);
    *(uint8_t *)(uintptr_t)0x811309u=0x5au;
    mutate_on_notify=1u;
    assert(opencfw_em9305_init_transition_32d10c(0x111u)==0x1357u);
    assert(event_calls==1u&&*(uint32_t *)(uintptr_t)0x8051d0u==0x811000u);
    assert(record[3]==1u);
    mutate_on_notify=0u;
    *(uint32_t *)(uintptr_t)0x8051d0u=0x810000u;
    assert(opencfw_em9305_init_transition_32d2dc(0x888u)==0x5678u);
    assert(record[3]==0u&&cleanup_calls==2u);
    assert(opencfw_em9305_init_transition_32d2dc(0x999u)==0x5678u);
    assert(record[3]==0u&&cleanup_calls==3u);
    *(uint32_t *)(uintptr_t)0x812afcu=0x813000u;
    *(uint16_t *)(uintptr_t)0x81305eu=2u;
    *(uint32_t *)(uintptr_t)0x805c70u=0x814000u;
    *(uint8_t *)(uintptr_t)0x805a74u=255u;
    assert(opencfw_em9305_init_transition_31a408(0x812000u)==0xabcu);
    assert(release_calls==1u&&down_calls==1u&&terminate_calls==1u);
    *(uint32_t *)(uintptr_t)0x805c78u=0x815000u;
    *(uint8_t *)(uintptr_t)0x812001u=7u;
    *(uint8_t *)(uintptr_t)0x815020u=9u;
    *(uint32_t *)(uintptr_t)0x815018u=0x3333u;
    *(uint32_t *)(uintptr_t)0x81501cu=0x4444u;
    assert(opencfw_em9305_init_transition_31a538(0x812000u)==0x4a4au);
    assert(report_calls==1u);
    *(uint32_t *)(uintptr_t)0x815008u=0x1111u;
    *(uint32_t *)(uintptr_t)0x81500cu=0x2222u;
    *(uint8_t *)(uintptr_t)0x815004u=4u;
    *(uint8_t *)(uintptr_t)0x815005u=5u;
    *(uint8_t *)(uintptr_t)0x815006u=6u;
    prepared_result=0x1357u;
    assert(opencfw_em9305_init_transition_31a554(0x812000u)==0x1357u);
    assert(prepare_calls==1u);
    prepared_result=0u;prepare_mutates=1u;
    assert(opencfw_em9305_init_transition_31a554(0x812000u)==0x802a54u);
    assert(*(uint32_t *)(uintptr_t)0x802a54u==0xaabbu);
    assert(*(uint32_t *)(uintptr_t)0x802a58u==0xccddu);
    assert(*(uint8_t *)(uintptr_t)0x802a5cu==8u);
    assert(*(uint8_t *)(uintptr_t)0x802a5du==0u);
    *(uint8_t *)(uintptr_t)0x813050u=3u;
    *(uint8_t *)(uintptr_t)0x805a74u=255u;
    assert(opencfw_em9305_init_transition_31a58c(0x812000u)==0xabcu);
    assert(report_calls==1u);
    *(uint8_t *)(uintptr_t)0x813050u=2u;
    *(uint8_t *)(uintptr_t)0x802a5cu=4u;
    *(uint32_t *)(uintptr_t)0x802a54u=0x1111u;
    *(uint32_t *)(uintptr_t)0x802a58u=0x2222u;
    *(uint8_t *)(uintptr_t)0x805a74u=255u;
    assert(opencfw_em9305_init_transition_31a58c(0x812000u)==0xabcu);
    assert(report_calls==2u);
    track=1u;trace_pos=0u;
    assert(opencfw_em9305_init_transition_316698(0x99u)==0x700u);
    assert(trace_pos==1u&&trace[0]=='e');
    trace_pos=0u;
    assert(opencfw_em9305_init_transition_3166a0(0x99u)==0x700u);
    assert(trace_pos==4u&&trace[0]=='r'&&trace[1]=='g'&&trace[2]=='f'&&trace[3]=='e');
    trace_pos=0u;
    assert(opencfw_em9305_init_transition_3166bc(0x99u)==0x70cu);
    assert(trace_pos==1u&&trace[0]=='e');
    trace_pos=0u;
    assert(opencfw_em9305_init_transition_3166c4(0x99u)==0x34u);
    assert(trace_pos==3u&&trace[0]=='r'&&trace[1]=='g'&&trace[2]=='f');
    trace_pos=0u;*(uint8_t *)(uintptr_t)0x805b9du=0u;
    assert(opencfw_em9305_init_transition_3166d8(0x99u)==0x56u);
    assert(*(uint8_t *)(uintptr_t)0x805a71u==1u);
    assert(trace_pos==3u&&trace[0]=='q'&&trace[1]=='c'&&trace[2]=='s');
    trace_pos=0u;*(uint8_t *)(uintptr_t)0x805b9du=1u;
    assert(opencfw_em9305_init_transition_3166d8(0x99u)==0x56u);
    assert(trace_pos==4u&&trace[0]=='q'&&trace[1]=='c'&&trace[2]=='u'&&trace[3]=='s');
    trace_pos=0u;*(uint8_t *)(uintptr_t)0x805b9du=0u;
    assert(opencfw_em9305_init_transition_gate_3168e4()==0u);
    assert(*(uint8_t *)(uintptr_t)0x805a71u==0u);
    assert(trace_pos==1u&&trace[0]=='g');
    trace_pos=0u;*(uint8_t *)(uintptr_t)0x805b9du=1u;
    assert(opencfw_em9305_init_transition_gate_3168e4()==0x987u);
    assert(trace_pos==2u&&trace[0]=='g'&&trace[1]=='h');
    trace_pos=0u;
    assert(opencfw_em9305_init_transition_316894(0x99u)==0u);
    assert(notify_calls==4u);
    *(uint8_t *)(uintptr_t)0x805a71u=1u;
    *(uint8_t *)(uintptr_t)0x8052fdu=0x44u;
    *(uint8_t *)(uintptr_t)0x805300u=0x7bu;
    expected_notify=0x805300u;
    assert(opencfw_em9305_init_transition_316894(0x99u)==0x1234u);
    assert(*(uint8_t *)(uintptr_t)0x8052fdu==1u&&
        *(uint8_t *)(uintptr_t)0x805300u==0x7bu&&notify_calls==5u);
    expected_notify=0x810030u;
    trace_pos=0u;
    assert(opencfw_em9305_init_transition_3168b0(0x99u)==0x700u);
    assert(trace_pos==5u&&trace[0]=='q'&&trace[1]=='c'&&trace[2]=='u'&&trace[3]=='s'&&trace[4]=='e');
    return 0;
}
