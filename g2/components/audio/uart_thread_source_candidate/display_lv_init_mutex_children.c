/* Native LV startup mutex/timer children 0x4d465c/0x4d46de/0x4645d8.
 * The first reuses selected exact 0x4d47cc recursive-mutex ensure. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[]; /* RAM0x2006f548 */
extern void audio_uart_lv_mutex_ensure(uint32_t *); /* selected 0x4d47cc */
extern void audio_uart_lv_anim_mutex_ensure_4d47fa(uint32_t *);
extern void audio_uart_lv_timer_update_464696(void); /* selected */
extern void stock_enter_critical(void); /* selected native0x4420d0 */
extern void stock_exit_critical(void); /* selected native0x4420e8 */

void audio_uart_lv_anim_mutex_ensure_4d47fa(uint32_t *cell)
{
    if (cell[0]==0u) {
        stock_enter_critical();
        if (cell[0]==0u) {
            cell[0]=1u;
            cell[1]=0u;
            cell[2]=0u;
        }
        stock_exit_critical();
    }
}

uint32_t audio_uart_lv_async_init_4d465c(void *cell)
{
    audio_uart_lv_mutex_ensure(cell);
    return 1u;
}

uint32_t audio_uart_lv_anim_init_4d46de(void *cell)
{
    audio_uart_lv_anim_mutex_ensure_4d47fa(cell);
    return 1u;
}

void audio_uart_lv_display_init_4645d8(uint32_t enabled)
{
    audio_uart_display_lv_root[0x80u]=(uint8_t)enabled;
    if ((uint8_t)enabled!=0u) audio_uart_lv_timer_update_464696();
}
