/* Apollo Main product RAM cells observed through native byte getters
 * 0x4a7832 and 0x4a4822. Startup values remain a linker/startup contract. */
#include <stdint.h>

volatile uint8_t g2_onboarding_flag
    __attribute__((section(".g2_ram_20000040")));
volatile uint8_t g2_imu_aid_enabled_cell
    __attribute__((section(".g2_ram_20074fd8")));
