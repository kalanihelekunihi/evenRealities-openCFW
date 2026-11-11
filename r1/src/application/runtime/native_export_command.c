/* Stock 0x4e740: BLE command state machine for the virtual log export. */
#include "native_export_snapshot.h"
#include <stddef.h>
#include <stdint.h>
#include <string.h>

struct r1_export_plan_state {
    uint8_t complete;
    uint8_t reserved[3];
    struct r1_export_file_descriptor *file;
    uint32_t offset;
};
struct r1_export_plan_state r1_export_plan_state={0,{0},&r1_log_export_file,0};
#if UINTPTR_MAX==UINT32_MAX
_Static_assert(sizeof(struct r1_export_plan_state)==12,
               "stock export command state");
#endif

extern uint32_t r1_fragment_message(uint32_t,const void *,uint32_t);
extern uint32_t r1_pb_fragment_message(uint32_t,uint32_t,const void *,uint32_t);
extern void r1_app_ble_set_fast_mode(uint32_t);
extern int32_t osDelay(uint32_t);
extern void *pvPortMalloc(size_t);
extern void vPortFree(void *);
extern void nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);

static void finish(void)
{
    (void)r1_export_plan_state.file->finish();
    r1_export_plan_state.complete=1;
}

static void send_chunk(uint32_t handle,uint32_t length)
{
    if (!length) {finish();return;}
    uint8_t notice=1;
    (void)r1_fragment_message(handle,&notice,1);
    (void)osDelay(50);
    uint8_t *scratch=pvPortMalloc(length);
    if (!scratch) {finish();return;}
    (void)r1_export_plan_state.file->read(r1_export_plan_state.offset,
                                          scratch,length);
    (void)r1_pb_fragment_message(handle,2,scratch,(uint16_t)length);
    vPortFree(scratch);
    r1_export_plan_state.offset+=length;
}

void r1_export_plan_command(uint32_t handle,void *payload,uint32_t length)
{
    const uint8_t *request=payload;
    nrf_log_frontend_std_3(0x001c0003u,
        "app_export cid = %d, data[1]:%d, pack_length = %d",
        request[0],request[1],length);
    if (request[0]==0) {
        uint8_t reply[10]={0};
        if (request[1]==1) {
            uint32_t information[2]={0,0};
            if (r1_export_plan_state.file->prepare(information)) {
                r1_app_ble_set_fast_mode(handle);
                (void)r1_export_plan_state.file->start();
                r1_export_plan_state.complete=0;
                memcpy(reply+2,information,sizeof information);
            } else reply[1]=1;
        } else reply[1]=1;
        r1_export_plan_state.offset=0;
        (void)r1_fragment_message(handle,reply,sizeof reply);
        (void)osDelay(50);
        if (reply[1]) return;
        uint32_t remaining=r1_export_plan_state.file->length-
                           r1_export_plan_state.offset;
        send_chunk(handle,remaining<4096u?remaining:4096u);
        return;
    }
    if (request[0]!=1) return;
    if (request[1]==2) {
        r1_export_plan_state.offset=0;
        finish();return;
    }
    uint32_t remaining=r1_export_plan_state.file->length-
                       r1_export_plan_state.offset;
    if (request[1]==0 &&
        r1_export_plan_state.file->length<=r1_export_plan_state.offset) {
        if (!r1_export_plan_state.complete) {
            uint8_t notice=3;
            (void)r1_fragment_message(handle,&notice,1);
        }
        finish();return;
    }
    uint32_t chunk=remaining<4096u?remaining:4096u;
    nrf_log_frontend_std_3(0x001c0003u,
        "app_export all:%d, offset = %d,len = %d",
        (uint32_t)request[1],r1_export_plan_state.offset,chunk);
    send_chunk(handle,chunk);
}
