/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern void open_cfw_gx8002_aout_play_check_idle(uint32_t, uint32_t);
extern void open_cfw_gx8002_aout_set_r1_frame_over_int_enable(uint32_t, uint32_t);
typedef void (*frame_callback)(uint32_t,uint32_t);
typedef void (*completion_callback)(void);
/* Stock e658: snapshot enabled pending bits once, then service in order.
 * Status acknowledgments are read-and-mask writes, not clear-bit updates. */
int open_cfw_gx8002_aout_handle_isr(int irq, void *handle)
{
    if (irq!=13) return 0;
    volatile uint32_t *hw=(volatile uint32_t *)0xa0b00000u;
    uint32_t status=hw[3];
    uint32_t enabled=hw[2];
    uint32_t pending=status&enabled;
    if (pending&4u) {
        hw[6]=hw[6]&0x7fffffffu;
        hw[3]=hw[3]&4u;
        hw[2]=hw[2]&~4u;
    }
    if (pending&8u) {
        hw[7]=hw[7]&0x7fffffffu;
        hw[3]=hw[3]&8u;
        hw[2]=hw[2]&~8u;
    }
    if (pending&64u) hw[3]=hw[3]&64u;
    uint8_t *state=handle;
    if (pending&1u) {
        hw[3]=hw[3]&1u;
        frame_callback callback=*(frame_callback volatile *)(state+40);
        if (callback) {
            uint32_t end=*(volatile uint32_t *)(state+36);
            uint32_t start=*(volatile uint32_t *)(state+32);
            callback(start,end);
        }
    }
    if (pending&2u) {
        hw[3]=hw[3]&4u;
        hw[3]=hw[3]&8u;
        hw[3]=hw[3]&64u;
        hw[3]=hw[3]&1u;
        open_cfw_gx8002_aout_play_check_idle(0xa0b00000u,0);
        open_cfw_gx8002_aout_set_r1_frame_over_int_enable(0xa0b00000u,0);
        hw[3]=hw[3]&2u;
        *(volatile uint8_t *)(state+28)=1;
        completion_callback callback=*(completion_callback volatile *)(state+44);
        if (callback) callback();
    }
    return 0;
}
