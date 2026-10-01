/* Manual behavioral recovery, not original firmware source or a patch.
 * Native structures/pointers conceptual; stock queue record has 8-byte header.
 * Provider behavior, scheduler timing and physical angle calibration excluded.
 */
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdbool.h>
extern void *tx_queue,*tx_thread;
extern bool fast_mode_selected(void);
extern void request_fast_mode(void),*file_heap_allocate(unsigned),file_heap_free(void *);
extern unsigned queue_count(void *),queue_capacity(void *);
extern int queue_put(void *,void *const *,unsigned,unsigned),queue_get(void *,void **,unsigned,unsigned);
extern void set_thread_flags(void *,unsigned);
/* 0x0047564E, focused transport=1 path. Subtype is not serialized here. */
int enqueue_audio_body(const void *body,uint16_t bytes) {
 if(!body || !tx_queue)return -1;
 if(!fast_mode_selected())request_fast_mode(); /* does not reject the body */
 uint8_t *record=file_heap_allocate((bytes+14u)&~3u);
 if(!record)return -1;
 uint32_t type=2,length=bytes;
 memcpy(record,&type,4);memcpy(record+4,&length,4);memcpy(record+8,body,bytes);
 if(queue_count(tx_queue)>=queue_capacity(tx_queue)/2) {
  file_heap_free(record);return 0; /* deliberate stream drop, still success */
 }
 if(queue_put(tx_queue,(void *const *)&record,0,500)) {
  file_heap_free(record);return -1;
 }
 set_thread_flags(tx_thread,0x400000);return 0;
}
extern bool take_tx_token(unsigned);
extern void ess_send_borrowed(const void *,uint16_t);
/* 0x0047538C, focused queue type 2. Other types use other protocol encoders. */
void drain_audio_queue_excerpt(void) {
 uint8_t *record;
 while(queue_get(tx_queue,(void **)&record,0,0)==0 && record) {
  uint32_t type,length;memcpy(&type,record,4);memcpy(&length,record+4,4);
  if(type==2 && take_tx_token(50))ess_send_borrowed(record+8,(uint16_t)length);
  file_heap_free(record); /* may precede later WSF consumption */
 }
}
/* 0x004BE2F6: record layout public offsets +0 conn u16, +2 event u8,
 * +4 pointer32, +8 length u16. ATT copy happens later, not here. */
extern uint8_t ess_connection,ess_handler,ess_ccc_enabled;
extern bool ota_active(void);
extern void tx_complete(void),*WsfMsgAlloc(unsigned),WsfMsgSend(unsigned,void *);
extern void fill_ess_message(void *,uint16_t,uint8_t,const void *,uint16_t);
void ess_send_borrowed(const void *data,uint16_t bytes) {
 if(ota_active() || !ess_connection || ess_ccc_enabled!=1){tx_complete();return;}
 void *msg=WsfMsgAlloc(12);if(!msg){tx_complete();return;}
 fill_ess_message(msg,ess_connection,0xa9,data,bytes);WsfMsgSend(ess_handler,msg);
}
/* 0x004BE24E -> 0x00533ED8 -> 0x00533C6C:
 * Event A9 calls AttsHandleValueNtf(conn,0x0864,length,pointer).
 * With eligible connection, change-aware client, MTU >= length+3 and successful
 * allocation: owned ATT packet holds [1B,64,08,payload...]. memcpy copies the
 * exact value; no AA transport prefix, extra length or CRC is added.
 * Too-small MTU calls attsExecCallback(conn,0x0864,0x77); no fragmentation here.
 */

/* 0x005915EA: full normal stereo input only, 800 pairs of signed 16-bit PCM.
 * Stock validates divisible-by-four and <=3200 bytes but loops over 800 pairs
 * regardless; callers must actually provide the full readable buffer.
 */
void preprocess_normal_frame(const int16_t stereo[1600],int16_t mono[800],
                              uint64_t *left_mean,uint64_t *right_mean) {
 uint64_t left=0,right=0;
 for(unsigned i=0;i<800;i++) {
  int l=stereo[2*i],r=stereo[2*i+1];
  mono[i]=(int16_t)(l/2+r/2);left+=(uint64_t)(l*l);right+=(uint64_t)(r*r);
 }
 *left_mean=left/800;*right_mean=right/800;
}
/* 0x0059173A: param pointer/length gate omitted from scalar representation.
 * No log10, scaling to dB, or saturating clamp appears in this body. */
uint16_t energy_ratio(uint64_t left,uint64_t right,const uint64_t window[10]) {
 if(!left || !right)return 0;
 uint64_t sum=0;for(unsigned i=0;i<10;i++)sum+=window[i];
 return (uint16_t)(((left+right)/2+1)/(sum/10+1));
}
/* 0x00591C26: rolling mean-square window; input validity check omitted. */
void update_energy_window(const int16_t *pcm,unsigned samples,uint64_t window[10],unsigned *index) {
 uint64_t sum=0;for(unsigned i=0;i<samples;i++){int v=pcm[i];sum+=(uint64_t)(v*v);}
 window[*index]=sum/samples;*index=(*index+1)%10;
}
/* 0x00591BA4: finite valid correlation result. Invalid/NaN semantics and physical
 * orientation are not reconstructed. Original VFP instructions tested with
 * controlled radians; conversion truncates toward zero, then narrows to i16. */
int16_t angle_to_metadata(double radians) {
 return (int16_t)(int32_t)(radians*180.0/3.141592653589793);
}
