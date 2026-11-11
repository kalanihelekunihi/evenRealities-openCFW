/* Stock 0x4f10c: factory device identity report. */
#include <stdint.h>

extern uint32_t r1_motion_refresh_selection(void);
extern uint8_t r1_goodix_identity_probe(void);
extern uint32_t r1_touch_chip_id_probe(void);
extern uint32_t r1_nfc_chip_id_probe(void);
extern uint32_t r1_yhm_chip_id_native(void);
extern void r1_gxt310_id_pair_read(volatile uint8_t *buffer);
extern void r1_eat_respond_format(const char *format, ...);

void r1_eat_callback_0004f10c(char *argument)
{
    (void)argument;
    const uint32_t imu = r1_motion_refresh_selection();
    const uint32_t ppg = r1_goodix_identity_probe();
    const uint32_t touch = r1_touch_chip_id_probe();
    const uint32_t nfc = r1_nfc_chip_id_probe();
    const uint32_t pmic = r1_yhm_chip_id_native();
    uint8_t temperatures[3];
    r1_gxt310_id_pair_read(temperatures);
    r1_eat_respond_format(
        "IMU ID = 0x%x(0x90)\r\n"
        "PPG ID = 0x%X(0xA5)\r\n"
        "TOUCH ID = 0x%X(0x58)\r\n"
        "NFC ID = 0x%x(0x50)\r\n"
        "PMIC ID = 0x%X(0xA0)\r\n"
        "TEMP1 ID = 0x%x(0x50)\r\n"
        "TEMP2 ID = 0x%x(0x50)\r\n",
        imu, ppg, touch, nfc, pmic, (uint32_t)temperatures[1],
        (uint32_t)temperatures[2]);
}
