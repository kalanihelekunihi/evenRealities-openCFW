/* Pinned spi_master_v3.o local BSS lays out 16-byte context slots, a
 * 36-byte master, then a 44-byte dwspi record. Native probe uses the same
 * +0x10 and +0x34 subrecord starts at 0x20017670. This source allocation
 * retains the conditional CRT BSS behavior; hardware effects are separate. */
#include <stdint.h>

volatile uint32_t gx8002_image_b_spi_device_state_20017670[24]
    __attribute__((section(".bss.image_b_spi_device_state"), used, aligned(4)));
