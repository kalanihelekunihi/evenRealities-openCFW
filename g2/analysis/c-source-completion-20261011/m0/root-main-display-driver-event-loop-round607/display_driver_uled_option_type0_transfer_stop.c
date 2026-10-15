/* Apollo S200 transfer stop helpers at 0x538e8c and 0x53909a. */
#include <stdint.h>

extern void display_driver_uled_transfer_prepare_stop_538d18(uint32_t *);

static uint32_t valid(uint32_t *transfer) {
    return transfer!=0 && (transfer[0]&0x01ffffffu)==0x01cdcdcdu;
}
static volatile uint32_t *register_at(uint32_t address) {
    return (volatile uint32_t *)(uintptr_t)address;
}

uint32_t display_driver_uled_wait_lower_538e8c(uint32_t *transfer) {
    if (!valid(transfer)) return 2u;
    if ((transfer[0]&0x02000000u)==0u) return 0u;
    uint32_t table=transfer[9];
    volatile uint32_t *control=register_at(*register_at(table));
    *control&=~1u;
    transfer[0]&=~0x02000000u;
    return 0u;
}

uint32_t display_driver_uled_shutdown_lower_53909a(uint32_t *transfer,
                                                     uint32_t force) {
    if (!valid(transfer)) return 2u;
    display_driver_uled_transfer_prepare_stop_538d18(transfer);
    if (((uint8_t)force)==0u && transfer[7]!=transfer[8]) return 3u;
    transfer[0]&=~0x01000000u;
    uint32_t table=transfer[9];
    volatile uint32_t *control=register_at(*register_at(table));
    *control&=~1u;
    volatile uint32_t *interrupt=register_at(*register_at(table+16u));
    *interrupt&=~*register_at(table+20u);
    return 0u;
}
