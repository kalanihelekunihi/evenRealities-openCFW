/* Native image-B sample LVP_APP event callback 0x1000c1c8..0x1000c1f3.
 * This exact C-SKY instruction-shaped source preserves the native stack
 * lifetime: frame_slot writes SP+0/+4, then audio_push receives SP+8.
 * SP+8/+12 are genuinely ambient and are not assigned invented values.
 * A pure C local with an initializer would silently change this contract.
 * Full downstream callback/hardware effects are not qualified here. */
#include <stdint.h>

extern uint32_t gx8002_image_b_audio_frame_slot_10009e8c(
    uint32_t, uint32_t *, uint32_t *);
extern uint32_t gx8002_image_b_audio_out_push_frame_10006b60(
    uint32_t, uint32_t);

__attribute__((naked, used))
int gx8002_image_b_sample_app_event_1000c1c8(void *event)
{
    (void)event;
    __asm__ volatile (
        "push r15\n"
        "subi r14, r14, 16\n"
        "ld.w r3, (r0, 0)\n"
        "cmpnei r3, 91\n"
        "bf 1f\n"
        "movi r0, 0\n"
        "br 2f\n"
        "1:\n"
        "addi r2, r14, 4\n"
        "mov r1, r14\n"
        "ld.w r0, (r0, 4)\n"
        "bsr gx8002_image_b_audio_frame_slot_10009e8c\n"
        "lrw r3, 0x2002d798\n"
        "addi r1, r14, 8\n"
        "ld.w r0, (r3, 0)\n"
        "bsr gx8002_image_b_audio_out_push_frame_10006b60\n"
        "movi r0, 0\n"
        "2:\n"
        "addi r14, r14, 16\n"
        "pop r15\n"
    );
}
