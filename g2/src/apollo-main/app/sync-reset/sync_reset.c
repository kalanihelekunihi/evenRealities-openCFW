/* Native sync transport setup0x584bc0, callback cell0x584c8c and
 * receiver restart0x584db6. ROM pin configuration words0x78f108/10 are4. */
#include <stdint.h>
#include "sync_uart_config_contract.h"

extern void *g2_uart_sync_driver; /* pointer cell0x20074610 */
extern volatile uint8_t g2_uart_sync_started; /* cell0x20074fc9 */
extern void *g2_uart_sync_semaphore_handle; /* cell0x2007461c */
extern void *g2_uart_sync_mutex; /* cell0x20074620 */
extern void (*g2_uart_sync_callback_cell)(void); /* cell0x20074618 */
extern g2_sync_uart_config_prefix_t g2_uart_sync_buffer; /* observed prefix at 0x20000d9c */
extern void *audio_uart_sync_sem_new(uint32_t,uint32_t,const void *); /* 0x44989a */
extern void *audio_uart_mutex_new(uint32_t); /* selected0x44971c */
extern uint32_t audio_uart_sync_driver_bind(uint32_t,void **); /* 0x58dae4 */
extern uint32_t g2_codec_pin_function(uint32_t,uint32_t); /* selected0x480f0c */
extern uint32_t audio_uart_sync_driver_mode(void *,uint32_t,uint32_t); /* 0x58dbb8 */
extern uint32_t audio_uart_sync_driver_buffer(void *,void *); /* 0x58e09e */
extern uint32_t audio_uart_sync_driver_prepare(void *,uint32_t,uint32_t,uint32_t,uint32_t); /* 0x58ddd6 */
extern void audio_uart_sync_hal0(uint32_t); /* 0x5849f2 */
extern void audio_uart_sync_hal1(uint32_t,uint32_t); /* 0x584a10 */
extern void audio_uart_sync_hal2(uint32_t); /* 0x5849d4 */
extern uint32_t audio_uart_sync_driver_baud(void *,uint32_t); /* 0x58e782 */
extern uint32_t audio_uart_sync_finalize(void); /* 0x584df4 */

/* Stock 0x00584BC0 (sync UART transport setup) */
uint32_t audio_uart_sync_reset0(void) {
    if (g2_uart_sync_semaphore_handle == 0) {
        g2_uart_sync_semaphore_handle=audio_uart_sync_sem_new(1u,0u,0);
        if (g2_uart_sync_semaphore_handle == 0) return 1u;
    }
    if (g2_uart_sync_mutex == 0) {
        g2_uart_sync_mutex=audio_uart_mutex_new(0u);
        if (g2_uart_sync_mutex == 0) return 1u;
    }
    uint32_t bound=audio_uart_sync_driver_bind(0u,&g2_uart_sync_driver);
    if (bound != 0u || g2_uart_sync_driver == 0) return 1u;
    uint32_t pin0=g2_codec_pin_function(0u,4u);
    uint32_t pin2=g2_codec_pin_function(2u,4u);
    uint32_t mode=audio_uart_sync_driver_mode(g2_uart_sync_driver,0u,0u);
    uint32_t buffer=audio_uart_sync_driver_buffer(g2_uart_sync_driver,
                                                   &g2_uart_sync_buffer);
    uint32_t prep=audio_uart_sync_driver_prepare(g2_uart_sync_driver,0u,0u,0u,0u);
    audio_uart_sync_hal0(15u);
    audio_uart_sync_hal1(15u,3u);
    audio_uart_sync_hal2(15u);
    uint32_t baud=audio_uart_sync_driver_baud(g2_uart_sync_driver,0x1fd0u);
    g2_uart_sync_started=1u;
    (void)audio_uart_sync_finalize();
    return (pin0==0u && pin2==0u && mode==0u && buffer==0u &&
            prep==0u && baud==0u) ? 0u : 1u;
}

/* Stock 0x584C8C (sync UART receive-callback setter) */
void audio_uart_sync_reset1(void (*callback)(void)) {
    if (callback != 0) g2_uart_sync_callback_cell=callback;
}

/* Stock 0x584DB6 (sync UART receiver restart) */
uint32_t audio_uart_sync_reset2(void) {
    if (g2_uart_sync_driver == 0) return 1u;
    uint32_t mode=audio_uart_sync_driver_mode(g2_uart_sync_driver,0u,1u);
    uint32_t pin2=g2_codec_pin_function(2u,4u);
    uint32_t pin0=g2_codec_pin_function(0u,4u);
    g2_uart_sync_started=1u;
    return mode|pin2|pin0;
}
