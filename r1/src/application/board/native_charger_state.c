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
