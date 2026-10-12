/* Full native Thread_MsgRxFromBle 0x48f12c. Manager RAM0x20003ffc is a
 * direct object, with thread at +8 and CMSIS queue at +12. */
#include <stdint.h>
#include <stddef.h>
extern uint8_t audio_ble_rx_thread_state[]; /* selected RAM0x20003ffc */
extern void *file_heap_allocate(uint32_t);
extern void audio_file_heap_free(void *);
extern void *memset(void *,int,size_t);
extern void *memcpy(void *,const void *,size_t);
extern uint32_t audio_cmsis_queue_get_count(void *);
extern uint32_t audio_cmsis_queue_get_capacity(const void *);
extern int32_t audio_cmsis_queue_put(void *,const void *,uint8_t,uint32_t);
extern uint32_t audio_thread_flags_set(void *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="ble.msgrx";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_ble_msgrx.c";
static const char function[]="Thread_MsgRxFromBle";
static const char no_buffer[]="ble msg msg buffer is null";
static const char no_queue[]="Thread_MsgRxFromBle queue null";
static const char no_memory[]="Thread_MsgRxFromBle alloc length = %d fail";
static const char occupancy[]="rx msg_count = %d, msg_capacity = %d";
static const char put_failed[]="ble msg send msg fail, status = %d";
static const char no_buffer_short[]="[ble.msgrx]ble msg msg buffer is null";
static const char no_queue_short[]="[ble.msgrx]Thread_MsgRxFromBle queue null";
static const char no_memory_short[]="[ble.msgrx]Thread_MsgRxFromBle alloc length = %d fail";
static const char occupancy_short[]="[ble.msgrx]rx msg_count = %d, msg_capacity = %d";
static const char put_failed_short[]="[ble.msgrx]ble msg send msg fail, status = %d";

static void log_error(uint32_t line,const char *message,const char *short_message,int32_t value,uint32_t has_value)
{
    if ((audio_log_flags()&2u)!=0u) {
        if (has_value) audio_log_extended(1u,module,source,function,line,message,value);
        else audio_log_extended(1u,module,source,function,line,message);
    }
    if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u) {
        if (has_value) (void)compressed_log_output(has_value?0x04400000u:0x04000000u,
                                                     short_message,short_message,value);
        else (void)compressed_log_output(0x04000000u,short_message,short_message);
    }
}

int32_t audio_uart_thread_msg_rx_from_ble_48f12c(uint32_t id,const void *bytes,uint32_t length)
{
    uint16_t size=(uint16_t)length;
    uint8_t *manager=audio_ble_rx_thread_state;
    if (bytes==0) {
        log_error(0x13eu,no_buffer,no_buffer_short,0,0u);
        return -1;
    }
    void *queue=*(void **)(void *)(manager+12u);
    if (queue==0) {
        log_error(0x143u,no_queue,no_queue_short,0,0u);
        return -1;
    }
    uint8_t *node=file_heap_allocate(((uint32_t)size+11u)&~3u);
    if (node==0) {
        log_error(0x14du,no_memory,no_memory_short,(int32_t)size,1u);
        return -1;
    }
    (void)memset(node+8u,0,size);
    *(uint32_t *)(void *)node=id;
    *(uint32_t *)(void *)(node+4u)=size;
    (void)memcpy(node+8u,bytes,size);
    uint32_t count=audio_cmsis_queue_get_count(queue);
    uint32_t capacity=audio_cmsis_queue_get_capacity(queue);
    if ((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,source,function,0x15du,occupancy,count,capacity);
    if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10800000u,occupancy_short,occupancy_short,count,capacity);
    int32_t status=audio_cmsis_queue_put(queue,&node,0u,500u);
    if (status==0) {
        (void)audio_thread_flags_set(*(void **)(void *)(manager+8u),0x400000u);
        return 0;
    }
    log_error(0x160u,put_failed,put_failed_short,status,1u);
    audio_file_heap_free(node);
    return -1;
}
