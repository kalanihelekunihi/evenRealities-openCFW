/* Stock 0x4f524: display the YHM charger register block. */
#include <stdint.h>

extern uint32_t r1_native_charger_register_block_read(uint8_t *output);
extern void r1_eat_respond_format(const char *format, ...);

void r1_eat_callback_0004f524(char *argument)
{
    (void)argument;
    uint8_t registers[12] = {0};
    (void)r1_native_charger_register_block_read(registers);
    r1_eat_respond_format("pmic_register_read:\r\n");
    r1_eat_respond_format(
        "0x%02X 0x%02X 0x%02X 0x%02X 0x%02X 0x%02X 0x%02X 0x%02X 0x%02X 0x%02X\r\n",
        registers[0], registers[1], registers[2], registers[3],
        registers[4], registers[5], registers[6], registers[7],
        registers[8], registers[9]);
}
