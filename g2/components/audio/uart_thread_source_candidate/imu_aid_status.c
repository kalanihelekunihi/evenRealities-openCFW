/* Native 0x4a4822: one-byte IMU AID enabled state read. */
#include <stdint.h>
extern volatile uint8_t g2_imu_aid_enabled_cell; /* product RAM 0x20074fd8 */
uint32_t semantic_get_aid_enabled(void) {
    return g2_imu_aid_enabled_cell;
}
