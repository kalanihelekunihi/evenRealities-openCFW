/* Stock 0x6210c, 0x72898, 0x93414: touch ATI calibration command and
 * its two small state accessors. */
#include <stdint.h>
#include <stddef.h>
#include "native_iqs_state.h"
#include "native_touch_task_control.h"

extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern uint32_t r1_touch_task_event_post(uint32_t);
extern uint32_t r1_touch_task_message_boundary(const void *);
extern uint32_t r1_service_touch_open(uint32_t),r1_service_touch_close(uint32_t);
extern uint32_t r1_product_sn_letter_decode(void);
extern uint32_t r1_legacy_bounded_reply_send(const void *,uint32_t);
extern void __aeabi_memclr(void *,size_t);

/* Stock 0x72898: the two public ATI bytes come from the existing twelve-byte
 * factory touch record, at offsets three and four. */
uint32_t r1_touch_ati_data_get(uint8_t *first,uint8_t *second)
{
    if (!first || !second) return 0u;
    *first = r1_touch_factory_state.reserved3;
    *second = (uint8_t)r1_touch_factory_state.reserved4;
    return 1u;
}

/* Stock 0x93414: only modes zero through three are stored. */
void r1_touch_ati_mode_set(uint32_t mode)
{
    if (mode <= 3u) r1_iqs_raw_report_selection = (int8_t)mode;
}

static void log_step(const char *ring,const char *sdk)
{
    uint32_t mode = r1_structured_log_mode_get();
    if ((mode & 1u) || (r1_structured_log_mode_get() & 4u))
        (void)r1_structured_log_format(0x0c000000u,ring,ring);
    if (r1_structured_log_mode_get() & 2u)
        nrf_log_frontend_std_0(0x001c0003u,sdk);
}

static void send_task_message(uint32_t type,uint32_t subtype,
                              uint8_t first,uint8_t second)
{
    uint8_t message[44];
    __aeabi_memclr(message,sizeof(message));
    message[4] = (uint8_t)type;
    message[8] = (uint8_t)subtype;
    message[12] = first;
    message[13] = second;
    (void)r1_touch_task_message_boundary(message);
}

uint32_t r1_ati_calibration_command_plan(uint32_t handle,void *packet)
{
    (void)handle;
    uint8_t *bytes=packet;
    switch (bytes[3]) {
    case 0u: {
        uint32_t mode=r1_structured_log_mode_get();
        if ((mode & 1u) || (r1_structured_log_mode_get() & 4u))
            (void)r1_structured_log_format(0x0c400000u,
                "[RING]ATI_calibration: Print Trackpad Reg sel=%d",
                "[RING]ATI_calibration: Print Trackpad Reg sel=%d",bytes[4]);
        if (r1_structured_log_mode_get() & 2u)
            nrf_log_frontend_std_1(0x001c0003u,
                "ATI_calibration: Print Trackpad Reg sel=%d",bytes[4]);
        r1_touch_ati_mode_set(bytes[4]);
        break;
    }
    case 1u:
        log_step("[RING]ATI_calibration step1","ATI_calibration step1");
        (void)r1_touch_task_event_post(0x40u);
        break;
    case 2u:
        log_step("[RING]ATI_calibration step2","ATI_calibration step2");
        (void)r1_touch_task_event_post(0x80u);
        break;
    case 3u:
        send_task_message(1u,1u,bytes[4],0u);
        (void)r1_touch_task_event_post(0x100u);
        break;
    case 4u:
        send_task_message(2u,2u,bytes[4],bytes[5]);
        (void)r1_touch_task_event_post(0x200u);
        break;
    case 5u:
        send_task_message(3u,1u,bytes[4],0u);
        (void)r1_touch_task_event_post(0x400u);
        break;
    case 6u:
        send_task_message(4u,1u,bytes[4] ? 1u : 0u,0u);
        (void)r1_touch_task_event_post(0x800u);
        break;
    case 7u: {
        uint8_t first=0u,second=0u;
        if (r1_touch_ati_data_get(&first,&second)) {
            bytes[4]=first;
            bytes[5]=second;
            return r1_legacy_bounded_reply_send(bytes,6u);
        }
        bytes[4]=0xffu;
        return r1_legacy_bounded_reply_send(bytes,5u);
    }
    case 8u:
        (void)r1_service_touch_open(2u);
        break;
    case 9u:
        (void)r1_service_touch_close(2u);
        break;
    case 10u:
        bytes[4]=(uint8_t)r1_product_sn_letter_decode();
        break;
    default:
        break;
    }
    return r1_legacy_bounded_reply_send(bytes,5u);
}
