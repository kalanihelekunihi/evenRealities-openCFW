/* Apollo S200 MSPI pin group selection at 0x4c32b4. */
#include <stdint.h>

extern void display_driver_uled_pin_apply_480f0c(uint32_t,uint32_t);

static void pin(uint32_t number,uint32_t address) {
    display_driver_uled_pin_apply_480f0c(number,
        *(volatile const uint32_t *)(uintptr_t)address);
}
static void group0_common(void) {
    pin(199u,0x20000138u);pin(0x40u,0x2000013cu);
    pin(0x41u,0x20000140u);pin(0x48u,0x2000015cu);
}
static void group1_common(void) {
    pin(0x31u,0x20000184u);pin(0x5fu,0x20000188u);
    pin(0x60u,0x2000018cu);pin(0x67u,0x200001a8u);
    pin(0x68u,0x200001acu);
}

void display_driver_uled_mspi_pin_mode_4c32b4(uint32_t group,uint32_t mode_value) {
    uint32_t mode=mode_value&255u;
    if (group==0u) {
        if (mode==0u) {group0_common();return;}
        if (mode==1u || mode==5u || mode==7u || mode==9u ||
            mode==11u || mode==17u) return;
        if (mode==10u) {
            for (uint32_t i=0;i<9u;i++)
                pin(0x25u+i,0x20000160u+4u*i);
        }
        if (mode==6u || mode==8u || mode==10u) {
            for (uint32_t i=0;i<4u;i++)
                pin(0x44u+i,0x2000014cu+4u*i);
        } else if (mode!=4u && mode!=16u && mode!=18u) return;
        pin(0x42u,0x20000144u);pin(0x43u,0x20000148u);
        group0_common();return;
    }
    if (group!=1u) return;
    if (mode==0u) {group1_common();return;}
    if (mode==1u || mode==5u || mode==7u || mode==9u ||
        mode==17u || mode==19u || mode==23u) return;
    if (mode==6u || mode==8u || mode==22u || mode==24u) {
        for (uint32_t i=0;i<4u;i++)
            pin(0x63u+i,0x20000198u+4u*i);
    } else if (mode!=4u && mode!=16u && mode!=18u) return;
    pin(0x61u,0x20000190u);pin(0x62u,0x20000194u);
    group1_common();
}
