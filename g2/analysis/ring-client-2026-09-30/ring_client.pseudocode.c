/* Manually recovered behavioral pseudocode, NOT original source, NOT a
 * byte-matched firmware implementation. Seven original function bodies were
 * decoded and exercised by verify.py. Logging is omitted; external functions
 * below are abstract dependencies, not implementations.
 *
 * Stock layout (32-bit pointers): RingState at 0x20074074:
 * +0 conn u8, +1 WSF handler u8, +2..3 unassigned, +4 handles pointer,
 * +8 epoch u16. Handles: +0 write value, +2 notify value, +4 CCC descriptor.
 * Stock message: +0 param u16, +2 event u8, +3 status u8, +4 data pointer,
 * +8 length u16, +10 ATT handle u16 (receive) or unspecified (queued TX).
 * Native host pointer widths make these C structs conceptual, NOT wire ABI.
 */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "ring_client.h"
typedef struct { uint16_t write, notify, cccd; } RingHandles;
typedef struct {
    uint8_t conn, handler;
    uint16_t unassigned;
    RingHandles *handles;
    uint16_t epoch;
} RingState;
typedef struct {
    uint16_t param;
    uint8_t event, status;
    const uint8_t *data;
    uint16_t length, att_handle;
} RingMessage;
extern RingState ring; /* represents stock address 0x20074074 */
extern bool DmConnInUse(uint8_t);
extern unsigned DmConnRole(uint8_t); /* observed central=0 */
extern void AttcWriteReq(uint8_t,uint16_t,uint16_t,const void *);
extern void AttcWriteCmd(uint8_t,uint16_t,uint16_t,const void *);
extern void Thread_SendEvtToRingTask(unsigned);
extern void Thread_SendMsgToRingTaskWithId(const void *,uint16_t);
extern void fw_event_loop_remove_delayed(void (*)(uint32_t));
extern void fw_event_loop_push_delayed(void (*)(uint32_t),uint32_t,unsigned);
extern void thread_ble_wsf_tx_complete_notify(void);
extern void thread_ble_wsf_wait_tx_ready(void);
extern RingMessage *WsfMsgAlloc(unsigned stock_byte_count);
extern void WsfMsgSend(uint8_t,RingMessage *);
/* Semantic name for unknown-symbol helper 0x005332B4. Called with six args.
 * Its entire implementation is not reconstructed in this batch. */
extern void app_discover_service(uint8_t,unsigned,const uint8_t *,unsigned,
                                 const void *,RingHandles *);
extern const uint8_t ring_service_uuid_le[16]; /* stock 0x007880B0 */
extern const void *ring_discovery_items[3];    /* stock SRAM 0x200030D8 */

/* 0x004C46C0..0x004C46D0; callers: _ringEnableCccd scheduling in ProcMsg. */
uint32_t ringPackCccdEpochValue(uint8_t conn,uint8_t final_attempt,uint16_t epoch) {
    return g2_ring_cccd_token(conn,final_attempt,epoch);
}

/* 0x004C46D0..0x004C4810; invoked indirectly by delayed event loop.
 * Stock assumes ring.handles is non-null after initialization. */
void _ringEnableCccd(uint32_t token) {
    uint8_t conn=(uint8_t)token, final_attempt=(uint8_t)(token>>8);
    uint16_t epoch=(uint16_t)(token>>16);
    if (!conn || conn!=ring.conn || epoch!=ring.epoch || !DmConnInUse(conn)
        || !ring.handles->cccd) return;
    uint16_t enable_notification=1; /* little-endian bytes 01 00 */
    AttcWriteReq(conn,ring.handles->cccd,2,&enable_notification);
    /* Event is posted after issuing the write. No ATT response is checked here. */
    if (final_attempt==1) Thread_SendEvtToRingTask(4);
}

/* 0x004C4810..0x004C487C; called by APP_MasterHanderInit, 0x004A19F4.
 * Return registers in raw Ghidra output are incidental; callers use side effects. */
void APP_BleRingHandlerInit(uint8_t handler,RingHandles *handles) {
    ring.handler=handler; ring.conn=0; ring.epoch=1; ring.handles=handles;
    handles->write=0x10; handles->notify=0x12; handles->cccd=0x13;
}

/* 0x004C487C..0x004C48AC; caller 0x005355E0, direct BL 0x00535B52.
 * Assembly supplies the fifth and sixth arguments on the stack. Ghidra's
 * original export omits them in its call expression. Diagnostic hex dump omitted. */
void APP_BleRingSvcDiscover(uint8_t conn,RingHandles *result_handles) {
    app_discover_service(conn,16,ring_service_uuid_le,3,
                         ring_discovery_items,result_handles);
}

/* 0x004C48AC..0x004C4910; caller APP_BleRingProcMsg.
 * No connection-id comparison is performed locally; routing may constrain it. */
void _bleRingReceiveData(const RingMessage *msg) {
    if (msg->status==0 && msg->att_handle==ring.handles->notify)
        Thread_SendMsgToRingTaskWithId(msg->data,msg->length);
}

/* 0x004C4910..0x004C4B7E; caller ring_dm_event_dispatch at 0x004A19C0.
 * event_mask argument is unused by this body. */
void APP_BleRingProcMsg(unsigned event_mask,const RingMessage *msg) {
    (void)event_mask;
    if (!msg) return;
    uint8_t conn=(uint8_t)msg->param;
    switch (msg->event) {
    case 0x05: case 0x0d: case 0x0e:
        if (DmConnRole(ring.conn)==0) _bleRingReceiveData(msg);
        break;
    case 0x27: /* connection open */
        if (DmConnRole(conn)!=0) break;
        ring.conn=conn; ring.epoch=(uint16_t)(ring.epoch+1);
        ring.handles->write=0x10; ring.handles->notify=0x12; ring.handles->cccd=0x13;
        if (ring.handles->cccd) {
            fw_event_loop_remove_delayed(_ringEnableCccd);
            fw_event_loop_push_delayed(_ringEnableCccd,ringPackCccdEpochValue(conn,0,ring.epoch),500);
            fw_event_loop_push_delayed(_ringEnableCccd,ringPackCccdEpochValue(conn,0,ring.epoch),700);
            fw_event_loop_push_delayed(_ringEnableCccd,ringPackCccdEpochValue(conn,1,ring.epoch),900);
        }
        break;
    case 0x28: /* connection close; no active-connection equality check here */
        if (DmConnRole(conn)!=0) break;
        ring.conn=0; ring.epoch=(uint16_t)(ring.epoch+1);
        if (ring.handles) ring.handles->write=ring.handles->notify=ring.handles->cccd=0;
        fw_event_loop_remove_delayed(_ringEnableCccd);
        Thread_SendEvtToRingTask(8);
        break;
    case 0xac: { /* queued outbound message */
        uint16_t handle=ring.handles ? ring.handles->write : 0;
        if (!conn || conn!=ring.conn || !handle) thread_ble_wsf_tx_complete_notify();
        else AttcWriteCmd(conn,handle,msg->length,msg->data);
        break;
    }
    default: break;
    }
}

/* 0x004C4B7E..0x004C4C66; multiple ring_service and AT command callers.
 * Always returns zero, including drops and allocation failure. This layer
 * stores a borrowed pointer; it does not copy data into its 12-byte message. */
unsigned APP_BleRingSendDataMsg(const uint8_t *data,uint16_t length) {
    if (ring.conn && ring.handles && ring.handles->write) {
        thread_ble_wsf_wait_tx_ready();
        RingMessage *msg=WsfMsgAlloc(12);
        if (!msg) thread_ble_wsf_tx_complete_notify();
        else {
            msg->event=0xac; msg->param=ring.conn; msg->data=data; msg->length=length;
            /* status and trailing halfword are not set by this function. */
            WsfMsgSend(ring.handler,msg);
        }
    }
    return 0;
}
