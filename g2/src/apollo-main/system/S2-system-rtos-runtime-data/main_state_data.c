/* Apollo main configuration and thread-manager state (a-67-main-config,
 * a-22-thread-manager). Zero-initialised; sizes are the sizeof of the
 * referencing declarations and match the gap to the next stock object. */
#include <stdint.h>

/* RAM 0x20073ea4: am_hal_reset_status_t snapshot (16 B, 2-byte fields). */
uint8_t g2_reset_status[16] __attribute__((aligned(4)));

/* RAM 0x20075030: set once the OTA exit sequence has started. */
volatile uint8_t g2_tm_ota_exit_started;
