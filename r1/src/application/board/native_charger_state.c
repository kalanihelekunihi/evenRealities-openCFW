#include <stdint.h>
/* Raw status and transport behavior remain a separate native ABI boundary. */
extern uint32_t r1_yhm_status_native(void);
uint32_t r1_yhm_charge_state_native(void)
{
    uint32_t status=r1_yhm_status_native();
    if (status>=10 && status<=12) return 1;
    return status==13 ? 2 : 0;
}
uint32_t r1_native_charger_state_get(void)
{
    return r1_yhm_charge_state_native();
}

extern uint32_t r1_yhm_chip_id_native(void);
/* Historical stock name at 0x50690: store the chip-ID check's low byte,
 * then report one independently of that result. */
__attribute__((noinline)) uint32_t r1_yhm_status_byte_get(volatile uint8_t *out)
{
    *out = (uint8_t)r1_yhm_chip_id_native();
    return 1;
}
extern uint32_t r1_charge_state_byte_get(void);
uint32_t r1_charge_state_byte_thunk(void)
{
    return r1_charge_state_byte_get();
}
