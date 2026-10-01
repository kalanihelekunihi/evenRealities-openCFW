/* Human recovery from original instructions; not original C or a replacement
 * firmware. Named functions below map to listed addresses. Logging omitted.
 * External providers remain declarations. Host structures are conceptual;
 * native pointer widths need not match the stock 32-bit layouts. */
#include "ring_protocol.h"
#include <stdlib.h>
#include <string.h>
extern int APP_BleRingSendDataMsg(const void *,uint16_t);
extern void input_event(unsigned source,unsigned event,unsigned a,unsigned b);
extern void device_mgr_battery_record(const uint8_t record[8]);
extern void telemetry(unsigned key,unsigned count,const void *value);
extern uint32_t osKernelGetTickCount(void);
extern void remove_delayed(uint32_t callback);
extern void push_delayed(uint32_t callback,uint32_t arg,uint32_t ticks);
extern int central_is_ring_owner_side(void);
extern void publish_ring_link_ready(void),phone_ring_connect_info(unsigned);
extern void copy_current_ring_mac(uint8_t out[6],unsigned),cleanup_ring_unpair(const uint8_t mac[6]);
extern void *file_heap_allocate(size_t);
extern void file_heap_free(void *);
extern int queue_put_pointer(void *queue,void *const *p,unsigned priority,unsigned timeout);
extern int queue_get_pointer(void *queue,void **p,unsigned priority,unsigned timeout);
extern void set_thread_flags(void *thread,unsigned flags);
extern void *ring_queue,*ring_thread,*tx_ready_sem;
extern int sem_acquire(void *,unsigned),sem_count(void *),sem_release(void *);
extern void osDelay(unsigned ticks);
extern void battery_record_template(uint8_t out[8]); /* stock flash 0x0078E464 */

/* 0x00472244..0x004722CC (raw export's body; seed end included literals). */
int RING_GlassesHeartbeatProcess(void) {
    uint8_t local[254]={0};g2_ring_heartbeat(local);
    APP_BleRingSendDataMsg(local,4);return 0;
}
/* 0x004722D8: this LOW-LEVEL process helper writes little-endian. */
int RING_TouchAlgoReportTimeProcess(uint16_t value) {
    uint8_t local[254]={0,0x1a,0x8a,1};
    local[4]=(uint8_t)value;local[5]=(uint8_t)(value>>8);
    APP_BleRingSendDataMsg(local,6);return 0;
}
/* 0x00472378: zero disables, any nonzero argument enables. */
int ring_touch_enable_process(uint8_t enable) {
    uint8_t local[254]={0};g2_ring_touch_enable(local,enable!=0);
    APP_BleRingSendDataMsg(local,8);return 0;
}
/* 0x004723D6: stock shifts raw bytes; no Boolean normalization. */
int ring_glasses_status_process(uint8_t a,uint8_t b) {
    uint8_t local[254]={0,0x1a,0x89,1};
    local[4]=(uint8_t)((a<<7)|(b<<6));
    APP_BleRingSendDataMsg(local,8);return 0;
}
/* 0x00472546. */
int ring_command88_process(void) {
    uint8_t local[254]={0};g2_ring_command_88(local);
    APP_BleRingSendDataMsg(local,4);return 0;
}

static uint32_t last_touch_tick; /* 0x20074900 */
static bool ring_worn;           /* 0x2007500C */
static uint32_t wear_started;    /* 0x20074904 */
/* 0x0047263C: only logs success if p[3]==1 && p[4]==1; no state transition. */
int RING_CmdHID(const uint8_t *p) { return p?0:-1; }
/* 0x0047269E. Stock checks n>7, yet loads FOUR bytes starting at offset 7.
 * Pseudocode preserves this discrepancy; do not reuse as a safe parser. */
int RING_CmdTouchUpdate(const uint8_t *p,uint16_t n) {
    if(!p)return -1;
    if(n>7) {
        uint32_t tick=g2_ring_touch_tick_le(p);
        if(p[4]!=8 && last_touch_tick && (uint32_t)(tick-last_touch_tick)<100)return 0;
        last_touch_tick=tick; /* occurs even when status p[3] is nonzero */
    }
    if(p[3]==0) switch(p[4]) {
    case 0:input_event(4,3,0,0);break;
    case 1:input_event(4,0,0,0);break;
    case 2:input_event(4,1,0,0);break;
    case 4:input_event(4,5,p[5],p[6]);break;
    case 5:input_event(4,4,p[5],p[6]);break;
    case 8:input_event(4,14,0,0);break;
    default:break;
    }
    return 0;
}
/* 0x004727AA: unlike other handlers, checks the six-byte minimum. */
int RING_CmdBatteryReport(const uint8_t *p,uint16_t n) {
    if(!p || n<6)return -1;
    uint8_t record[8];battery_record_template(record);
    record[0]=4;record[1]=0;record[2]=2;record[3]=0;
    record[4]=p[4];record[5]=p[5]; /* level and charging byte per diagnostic */
    device_mgr_battery_record(record);return 0;
}
/* 0x004728A0. */
void ring_reset_wear_tracking(void) {ring_worn=false;wear_started=0;}
/* 0x004728B2. A start at tick zero is not subsequently reported. */
void RING_CmdWearStatus(const uint8_t *p) {
    bool now=p[4]!=0;
    if(now==ring_worn)return;
    ring_worn=now;
    if(now)wear_started=osKernelGetTickCount();
    else if(wear_started) {
        uint32_t duration=osKernelGetTickCount()-wear_started;
        telemetry(0x60102,1,&duration);wear_started=0;
    }
}
/* 0x00472988: no generic prefix/null/minimum-length check in this body. */
void RING_CmdPackageParse(const uint8_t *p,uint16_t n) {
    switch(p[2]) {
    case 0x61:RING_CmdTouchUpdate(p,n);break;
    case 0x85:
        remove_delayed(0x4bc419);remove_delayed(0x4a285d);
        if(central_is_ring_owner_side())publish_ring_link_ready();
        else phone_ring_connect_info(0);
        RING_CmdHID(p);break;
    case 0x8a:break; /* acknowledgement log only */
    case 0x8b:RING_CmdBatteryReport(p,n);break;
    case 0x8c:RING_CmdWearStatus(p);break;
    case 0x94:
        if(p[4]==0x20 || p[4]==0x40) {
            remove_delayed(0x4c4fe5);push_delayed(0x4c4fe5,0,100);
            remove_delayed(0x4c4ee5);push_delayed(0x4c4ee5,0,500);
        }
        break;
    case 0x96: {
        uint8_t mac[6]={0};copy_current_ring_mac(mac,0);cleanup_ring_unpair(mac);break;
    }
    default:break;
    }
}

/* 0x004C549C. Stock allocation header: u32 id, u32 length, inline payload.
 * Queue contains a pointer, not the inline bytes. This path OWNS A COPY. */
typedef struct {uint32_t id,length;uint8_t payload[];} RingOwnedMessage;
int ring_task_msg_send(uint32_t id,const void *data,uint16_t length) {
    if((!data && length) || !ring_queue)return -1;
    RingOwnedMessage *m=file_heap_allocate((size_t)length+8);
    if(!m)return -1;
    m->id=id;m->length=length;
    if(length && data)memcpy(m->payload,data,length);
    if(queue_put_pointer(ring_queue,(void *const *)&m,0,0)!=0) {
        file_heap_free(m);return -1;
    }
    set_thread_flags(ring_thread,0x400000);return 0;
}
/* 0x004C548C */
void Thread_SendMsgToRingTaskWithId(const void *p,uint16_t n) {ring_task_msg_send(2,p,n);}
/* 0x00472362; local value is serialized little-endian by target stack store. */
int ring_set_report_interval(uint16_t interval) {return (int8_t)ring_task_msg_send(0x1000,&interval,2);}
/* 0x00472426 */
int ring_set_touch_enabled(uint8_t enable) {return (int8_t)ring_task_msg_send(0x80,&enable,1);}
/* 0x004C4DE8. Exact byte assembly explains public interval endianness. */
void ring_thread_message_handler(void) {
    RingOwnedMessage *m=NULL;
    while(queue_get_pointer(ring_queue,(void **)&m,0,0)==0 && m) {
        switch(m->id) {
        case 2:RING_CmdPackageParse(m->payload,(uint16_t)m->length);break;
        case 0x80:if(m->length)ring_touch_enable_process(m->payload[0]);break;
        case 0x400:if(m->length)ring_glasses_status_process(m->payload[0],m->payload[1]);break;
        case 0x1000:
            if(m->length>1)RING_TouchAlgoReportTimeProcess((uint16_t)((m->payload[0]<<8)|m->payload[1]));
            break;
        default:break;
        }
        file_heap_free(m);m=NULL;
    }
}
/* 0x004D0B36: original return has a Boolean in r0; other return-register
 * guesses in Ghidra are not part of the recovered API. */
bool threadBleWsfTakeTxReady(uint16_t timeout_ticks) {
    return tx_ready_sem && sem_acquire(tx_ready_sem,timeout_ticks)==0;
}
/* 0x004D0B64: wait-before-send, NOT wait-until-this-payload-consumed.
 * Finite best-effort wait; it returns even after all attempts fail. */
void thread_ble_wsf_wait_tx_ready(void) {
    (void)osKernelGetTickCount(); /* instrumentation start */
    if(!threadBleWsfTakeTxReady(0)) {
        bool acquired=false;
        for(unsigned i=0;i<20;++i) {
            if(acquired)break;
            acquired=threadBleWsfTakeTxReady(10);
            if(!acquired)osDelay(10);
        }
    }
    (void)osKernelGetTickCount(); /* instrumentation end; no error returned */
}
/* 0x004D0C36: release at most one token if a semaphore exists and is empty. */
void thread_ble_wsf_tx_complete_notify(void) {
    if(tx_ready_sem && sem_count(tx_ready_sem)==0)(void)sem_release(tx_ready_sem);
}
/* Focused supporting observations, not complete source recovery:
 * 0x004BF9BA WsfMsgSend: q=WsfTaskMsgQueue(id); WsfMsgEnq(q,id,msg);
 *                       WsfTaskSetReady(id,1); no payload copy or wait here.
 * 0x0047697E delayed push: deadline=(osKernelGetTickCount()-epoch_base)+delay;
 *                          delay is kernel ticks, not intrinsically milliseconds.
 * 0x004C507E event bit 4: remove/requeue callbacks 0x4C5033 at +200,
 *                        0x4C4EE5 at +500, 0x4A285D at +3000 ticks.
 * The prior batch's APP_BleRingSendDataMsg uses BORROWED stack data from all
 * five process helpers above. See validation.json's delayed-consumer test.
 */
