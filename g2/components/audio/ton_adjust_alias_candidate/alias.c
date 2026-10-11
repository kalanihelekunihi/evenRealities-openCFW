#include <stdint.h>

/* Historical transition caller name for native 0x5a423c. The selected
 * callback_voltage source already implements the complete shared body. */
extern void callback_voltage(uint32_t source, uint32_t selection);

void stock_ton_adjust(uint32_t source, uint32_t selection) {
    callback_voltage(source, selection);
}
