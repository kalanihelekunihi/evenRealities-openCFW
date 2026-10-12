/* Native Thread_BleMsgrxQueueClear 0x48f018 and Msgtx 0x475524.
 * Both drain queued heap-owned pointers until get fails or returns NULL. */
#include <stdint.h>
#include <stddef.h>
extern uint8_t audio_ble_rx_thread_state[]; /* 0x20003ffc */
extern uint8_t audio_ble_tx_thread_state[]; /* 0x20004020 */
extern uint32_t audio_cmsis_queue_get_count(void *); /* selected 0x449bc8 */
extern int32_t audio_uart_queue_receive(void *,void *,uint32_t,uint32_t); /* selected 0x449b3c */
extern void audio_file_heap_free(void *); /* selected native 0x474d16 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char*,const char*,const char*,uint32_t,const char*,...);
extern uint32_t compressed_log_output(uint32_t,const char*,const char*,...);

static const char rx_module[]="ble.msgrx",tx_module[]="ble.msgtx";
static const char rx_source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_ble_msgrx.c";
static const char tx_source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_ble_msgtx.c";
static const char rx_func[]="Thread_BleMsgrxQueueClear",tx_func[]="Thread_BleMsgtxQueueClear";
static const char *const extended[2][3]={
 {"Thread_BleMsgrxQueueClear: queue is NULL",
  "Thread_BleMsgrxQueueClear: clearing queue, msg_count=%d",
  "Thread_BleMsgrxQueueClear: cleared %d messages, remaining=%d"},
 {"Thread_BleMsgtxQueueClear: queue is NULL",
  "Thread_BleMsgtxQueueClear: clearing queue, msg_count=%d",
  "Thread_BleMsgtxQueueClear: cleared %d messages, remaining=%d"}};
static const char *const compact[2][3]={
 {"[ble.msgrx]Thread_BleMsgrxQueueClear: queue is NULL",
  "[ble.msgrx]Thread_BleMsgrxQueueClear: clearing queue, msg_count=%d",
  "[ble.msgrx]Thread_BleMsgrxQueueClear: cleared %d messages, remaining=%d"},
 {"[ble.msgtx]Thread_BleMsgtxQueueClear: queue is NULL",
  "[ble.msgtx]Thread_BleMsgtxQueueClear: clearing queue, msg_count=%d",
  "[ble.msgtx]Thread_BleMsgtxQueueClear: cleared %d messages, remaining=%d"}};

static void diagnostic(uint32_t side,uint32_t kind,uint32_t a,uint32_t b) {
    const char *module=side?tx_module:rx_module;
    const char *source=side?tx_source:rx_source;
    const char *func=side?tx_func:rx_func;
    uint32_t line=kind==0u?(side?0x10fu:0x11cu):kind==1u?(side?0x114u:0x121u):(side?0x123u:0x130u);
    if(audio_log_flags()&2u) {
        if(kind==0u) audio_log_extended(2u,module,source,func,line,extended[side][kind]);
        else if(kind==1u) audio_log_extended(4u,module,source,func,line,extended[side][kind],a);
        else audio_log_extended(4u,module,source,func,line,extended[side][kind],a,b);
    }
    if((audio_log_flags()&1u)||(audio_log_flags()&4u)) {
        uint32_t flags=kind==0u?0x8000000u:kind==1u?0x10400000u:0x10800000u;
        if(kind==0u) (void)compressed_log_output(flags,compact[side][kind],compact[side][kind]);
        else if(kind==1u) (void)compressed_log_output(flags,compact[side][kind],compact[side][kind],a);
        else (void)compressed_log_output(flags,compact[side][kind],compact[side][kind],a,b);
    }
}
static int32_t clear(uint8_t *state,uint32_t side) {
    void *queue=*(void **)(void *)(state+12u);
    if(queue==0) {diagnostic(side,0u,0u,0u);return 0;}
    uint32_t initial=audio_cmsis_queue_get_count(queue);
    diagnostic(side,1u,initial,0u);
    int32_t removed=0;
    for(;;) {
        void *message=0;
        if(audio_uart_queue_receive(queue,&message,0u,0u)!=0||message==0) break;
        audio_file_heap_free(message);
        removed++;
    }
    diagnostic(side,2u,(uint32_t)removed,audio_cmsis_queue_get_count(queue));
    return removed;
}
int32_t Thread_BleMsgrxQueueClear(void) {return clear(audio_ble_rx_thread_state,0u);}
int32_t Thread_BleMsgtxQueueClear(void) {return clear(audio_ble_tx_thread_state,1u);}
