/* Timer handles and 44-byte CMSIS control blocks used by selected initializers. */
#include <stdint.h>

void *audio_box_detect_timer __attribute__((section(".g2_ram_20074920")));
uint8_t audio_box_detect_timer_control_block[44u]
    __attribute__((section(".g2_ram_2007367c")));
void *audio_box_reconnect_timer __attribute__((section(".g2_ram_20074924")));
uint8_t audio_box_reconnect_timer_control_block[44u]
    __attribute__((section(".g2_ram_200736a8")));
void *audio_device_manager_timer __attribute__((section(".g2_ram_200744c0")));
uint8_t audio_device_manager_timer_control_block[44u]
    __attribute__((section(".g2_ram_200735a0")));
