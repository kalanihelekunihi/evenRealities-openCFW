/* Manual behavioral recovery tied to disassembly.txt and validation.json.
 * NOT original source, NOT byte-matched, NOT a firmware patch. Logging omitted.
 * Native structs below are conceptual; explicit serialized offsets are stock.
 * Partial display/dashboard branches are labeled as such. */
#include "ring_actions.h"
#include <stddef.h>
#include <string.h>
extern int sync_publish(uint16_t id,const void *,uint16_t length,unsigned mode);
extern unsigned device_role(void),kernel_ticks(void);
extern void dual_hold_track(uint16_t,uint32_t,uint32_t),usage_track(uint16_t,uint32_t,uint32_t);
extern bool dual_hold_active(void),input_allowed(void);
extern void system_command(unsigned,unsigned,unsigned,unsigned);
extern int forward_app_input(uint16_t,uint32_t,uint32_t,unsigned);
extern void *heap_alloc(unsigned),*queue_local,*queue_role1,*event_flags;
extern void heap_free(void *),signal_flags(void *,unsigned);
extern int queue_put(void *,void *const *,unsigned priority,unsigned timeout_ticks);
extern void fatal_queue_failure(void); /* original invokes assert then faults/spins */
static uint32_t active_source=0xffff,last_input_tick; /* 0x200036F8 / 0x20074984 */
typedef struct {uint16_t source,padding;uint32_t event;uint8_t first,second,pad[2];} Input;

/* 0x004C5886 */
uint32_t pack_extra(uint8_t first,uint8_t second) {return g2_input_extra(first,second);}
/* 0x004C5892: names pinned to retained strings, not inferred gesture names. */
const char *input_event_name(uint32_t event) {
 switch(event) {
 case 0:return "SINGLE_CLICK";case 1:return "DOUBLE_CLICK";case 3:return "LONG_PRESS";
 case 4:return "UPROLL";case 5:return "DOWNROLL";case 13:return "PRESS";
 case 14:return "RELEASE";case 0x1010:return "DECA_CLICK";default:return "UNKNOWN";
 }
}
/* 0x004C5916. Stock writes only source/event/first/second into the stack record;
 * padding bytes are not initialized here. Do not use them as protocol fields. */
void ring_input_publish(uint16_t source,uint32_t event,uint8_t first,uint8_t second) {
 Input record;record.source=source;record.event=event;record.first=first;record.second=second;
 sync_publish(0x108,&record,12,0);
}
/* 0x004C5DBC: caller-supplied length is copied into 12 local bytes without a
 * local upper-bound check. This pseudocode assumes the genuine 12-byte record. */
int input_manager(unsigned unused,const Input *record,unsigned length,unsigned extra) {
 (void)unused;(void)extra;
 if(device_role()==2)return 0;
 Input local={0};memcpy(&local,record,length);
 uint32_t now=kernel_ticks();
 dual_hold_track(local.source,local.event,now);usage_track(local.source,local.event,now);
 if(active_source!=0xffff && active_source!=local.source && (uint32_t)(now-last_input_tick)<1001)return 0;
 last_input_tick=now;active_source=(local.event==14)?0xffff:local.source;
 if(dual_hold_active() || !input_allowed())return 0;
 if(local.event==0x1010)system_command(0x109,0,0,0);
 else forward_app_input(local.source,local.event,pack_extra(local.first,local.second),0);
 return 0;
}
/* 0x00465748: raw Ghidra export failed for this function. Recovered manually
 * from 962 bytes and tested in original code, including allocation failures.
 * Stock envelope: +0 u32 mode, +4 u16 route, +6 u16 length, +8 32-bit pointer. */
typedef struct {uint32_t mode;uint16_t route,length;uint8_t *body;} Envelope;
int forward_app_input(uint16_t source,uint32_t event,uint32_t packed,unsigned mode) {
 if(!queue_local)return -1;
 Envelope *m=heap_alloc(12);if(!m)return -1;
 memset(m,0,12);m->body=heap_alloc(12);
 if(!m->body){heap_free(m);return -1;}
 m->mode=mode;m->length=12;
 m->body[0]=3;m->body[1]=7;m->body[2]=(uint8_t)source;m->body[3]=(uint8_t)(source>>8);
 for(unsigned i=0;i<4;i++){m->body[4+i]=(uint8_t)(event>>(i*8));m->body[8+i]=(uint8_t)(packed>>(i*8));}
 unsigned role=device_role();void *queue;
 if(role==1){m->route=3;queue=queue_role1;}
 else if(role==2){m->route=0;queue=queue_local;}
 else {heap_free(m->body);heap_free(m);return -1;}
 if(queue_put(queue,(void *const *)&m,0,2000)!=0) {
  heap_free(m->body);heap_free(m);fatal_queue_failure(); /* not a normal return in stock */
 }
 if(role==2)signal_flags(event_flags,2);
 return 0;
}

/* 0x00442D86: focused ring-relevant branches only. Input pointer is a packed
 * ten-byte suffix: u16 source at +0, u32 event at +2, u32 extra at +6.
 * Consumer dispatch into a particular application remains page/state dependent. */
extern bool current_page_exists(void),page_longpress_mode(void),transition_busy(void);
extern unsigned current_page_id(void),current_page_kind(void);
extern void ui_event(unsigned,const void *),factory_close(unsigned,unsigned);
extern void menu_stack_transition(void); /* several branches not expanded here */
void display_ring_input_excerpt(uint16_t source,uint32_t event,uint32_t packed) {
 if(!current_page_exists())return;
 uint32_t source_word=source;
 int32_t roll[2]={(int16_t)packed,(int16_t)(packed>>16)};
 switch(event) {
 case 0:ui_event(10,&source_word);break;
 case 1:ui_event(0x48,&source_word);break;
 case 4:ui_event(0x44,roll);break;
 case 5:ui_event(0x45,roll);break;
 case 14:ui_event(0x4a,roll);break;
 case 3:
  if(page_longpress_mode())ui_event(8,&packed);
  else if(transition_busy()) {if(current_page_id()==0x30)ui_event(8,&packed);}
  else if(current_page_kind()==0) {
   if(current_page_id()==0xe0)factory_close(1,0xe0);
   else if(device_role()==1)system_command(3,0,0,0);
  } else if(current_page_kind()==1)menu_stack_transition();
  break;
 default:break; /* unrelated input types omitted from this excerpt */
 }
}
/* 0x004E8BCC + 0x004E7D20: dashboard roll branches, GUI primitives abstract.
 * Other click/animation/release paths are not reconstructed in this excerpt. */
extern bool dashboard_blocked(void),dashboard_object_valid(void),dashboard_animating(void);
extern int dashboard_index,dashboard_count;
extern int dashboard_scroll_position(void);
extern void animate_dashboard_scroll(int),dashboard_index_changed(int),dashboard_boundary(int,int,int);
void dashboard_roll_excerpt(unsigned ui_event_id) {
 if(dashboard_blocked())return;
 int direction=ui_event_id==0x44?1:ui_event_id==0x45?-1:0;
 if(!direction || !dashboard_object_valid() || dashboard_animating())return;
 int pos=dashboard_scroll_position();
 if(direction==1 && dashboard_index<dashboard_count-1) {
  ++dashboard_index;animate_dashboard_scroll(pos+304);dashboard_index_changed(dashboard_index);
 } else if(direction==-1 && dashboard_index>0) {
  --dashboard_index;animate_dashboard_scroll(pos-304);dashboard_index_changed(dashboard_index);
 } else dashboard_boundary(direction,pos,dashboard_index);
}

/* ATT ownership boundary. Names correspond to seeded Cordio functions. */
extern uint8_t *WsfMsgDataAlloc(uint16_t,unsigned),*WsfMsgAlloc(unsigned);
extern void WsfMsgFree(void *),WsfMsgSend(uint8_t,void *),WsfTaskLock(void),WsfTaskUnlock(void);
extern void attcSendMsg(uint8_t,uint16_t,uint8_t,uint8_t *,uint8_t);
/* 0x004B50AE */
uint8_t *attMsgAlloc(uint16_t n) {return WsfMsgDataAlloc(n,0);}
/* 0x00539DEA: normal BLE lengths only; truncation/overflow not modeled away.
 * Return registers are not presented as a reliable success/delivery API. */
void AttcWriteCmd(uint8_t conn,uint16_t handle,uint16_t n,const uint8_t *caller_data) {
 uint8_t *p=attMsgAlloc((uint16_t)(n+11));if(!p)return;
 uint16_t pdu_len=(uint16_t)(n+3);p[0]=(uint8_t)pdu_len;p[1]=(uint8_t)(pdu_len>>8);
 p[8]=0x52;p[9]=(uint8_t)handle;p[10]=(uint8_t)(handle>>8);
 memcpy(p+11,caller_data,n); /* caller data no longer referenced after this call */
 attcSendMsg(conn,handle,10,p,0);
}
/* 0x004B5640: focused op=10 path reached from AttcWriteCmd. */
extern bool connection_present(uint8_t);
extern uint16_t connection_mtu(uint8_t);
extern bool connection_blocked(uint8_t);
extern void attcExecCallback(uint8_t,uint8_t,uint16_t,uint8_t);
extern uint8_t att_handler_id;
void attcSendMsg(uint8_t conn,uint16_t handle,uint8_t op,uint8_t *packet,uint8_t flag) {
 WsfTaskLock();bool present=connection_present(conn);
 uint16_t mtu=present?connection_mtu(conn):0;
 bool blocked=present&&connection_blocked(conn);WsfTaskUnlock();
 if(mtu) {
  if(blocked)attcExecCallback(conn,op,handle,0x71);
  else if(mtu<(uint16_t)(packet[0]|(packet[1]<<8)))attcExecCallback(conn,op,handle,0x77);
  else {
   uint8_t *msg=WsfMsgAlloc(12);
   if(msg) {
    /* Stock stores conn u16 +0, op u8 +2, flag u8 +3,
     * packet pointer +4, handle u16 +8, zero byte +10. */
    extern void fill_att_envelope(uint8_t *,uint8_t,uint8_t,uint8_t,uint8_t *,uint16_t);
    fill_att_envelope(msg,conn,op,flag,packet,handle);
    WsfMsgSend(att_handler_id,msg);return; /* ownership retained by ATT */
   }
  }
 }
 if(packet)WsfMsgFree(packet); /* rejected path owns and frees its copy */
}
/* 0x00530E30: send-simple, focused write-command path (op at CCB+6 is 10):
 *   packet = ccb.pending_packet_at_8;
 *   ccb.pending_packet_at_8 = NULL;
 *   attL2cDataReq(ccb.connection, ccb.bearer, packet.u16_length, packet);
 * Other opcodes also start a response timer. Lower L2CAP lifetime is not proven.
 * 0x00531AC0 separate packet cleanup helper:
 *   if (message.pointer_at_4) { WsfMsgFree(pointer); pointer_at_4=NULL; }
 */
