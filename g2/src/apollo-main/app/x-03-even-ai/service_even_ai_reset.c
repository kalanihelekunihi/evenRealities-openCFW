/* EvenAI service state reset, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\evenAI\service_even_ai.c.
 * Native 0x497db4..0x497dbf (service_even_ai_reset_all), 0x497dc0..0x497ddb
 * (state block clear) and 0x497ddc..0x497de5 (wake debounce clear); literal
 * pool 0x4985a8..0x4985af shared with app/a-15-even-ai-service.
 * service_even_ai_reset_all is called from the EvenAI page events
 * (app/a-28-even-ai-page). */
#include <stdint.h>

#define EVEN_AI_STATE_SIZE 0x218u

extern uint8_t audio_even_ai_service_state_2006ed10[EVEN_AI_STATE_SIZE]; /* RAM 0x2006ed10 */
extern uint32_t g2_even_ai_last_wakeup_tick;                             /* RAM 0x20074978 */

extern void audio_even_ai_state_lock_4e1fa6(void);
extern void audio_even_ai_state_unlock_4e1fbe(void);
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);

void service_even_ai_state_clear_497dc0(void);
void service_even_ai_wakeup_tick_clear_497ddc(void);
void service_even_ai_reset_all_497db4(void);

void service_even_ai_state_clear_497dc0(void)
{
    audio_even_ai_state_lock_4e1fa6();
    (void)aeabi_memset_43c0e4(audio_even_ai_service_state_2006ed10, EVEN_AI_STATE_SIZE, 0);
    audio_even_ai_state_unlock_4e1fbe();
}

void service_even_ai_wakeup_tick_clear_497ddc(void)
{
    g2_even_ai_last_wakeup_tick = 0u;
}

void service_even_ai_reset_all_497db4(void)
{
    service_even_ai_state_clear_497dc0();
    service_even_ai_wakeup_tick_clear_497ddc();
}
