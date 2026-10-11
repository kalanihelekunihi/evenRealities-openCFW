/* Native pin mux dispatchers 0x4c44bc/0x4c4530. Each case retains
 * its distinct lower (0x4c3bfc..0x4c43ec); invalid input returns 6. */
#include <stdint.h>

extern uint32_t audio_uart_mux_on0(uint32_t); /* 0x4c3bfc */
extern uint32_t audio_uart_mux_on1(uint32_t); /* 0x4c3c60 */
extern uint32_t audio_uart_mux_on2(uint32_t); /* 0x4c3d9e */
extern uint32_t audio_uart_mux_on3(uint32_t); /* 0x4c3cd4 */
extern uint32_t audio_uart_mux_on4(uint32_t); /* 0x4c3f2a */
extern uint32_t audio_uart_mux_on5(uint32_t); /* 0x4c4086 */
extern uint32_t audio_uart_mux_on6(uint32_t); /* 0x4c427e */
extern uint32_t audio_uart_mux_off0(uint32_t); /* 0x4c3c2e */
extern uint32_t audio_uart_mux_off1(uint32_t); /* 0x4c3ca2 */
extern uint32_t audio_uart_mux_off2(uint32_t); /* 0x4c3e9a */
extern uint32_t audio_uart_mux_off3(uint32_t); /* 0x4c3d28 */
extern uint32_t audio_uart_mux_off4(uint32_t); /* 0x4c4016 */
extern uint32_t audio_uart_mux_off5(uint32_t); /* 0x4c420c */
extern uint32_t audio_uart_mux_off6(uint32_t); /* 0x4c43ec */

uint32_t audio_uart_pin_mux_enable(uint32_t group,uint32_t pin) {
    if((uint8_t)pin>=0x39u) return 6u;
    switch((uint8_t)group) {
    case 0u:return audio_uart_mux_on0((uint8_t)pin);
    case 1u:return audio_uart_mux_on1((uint8_t)pin);
    case 2u:return audio_uart_mux_on2((uint8_t)pin);
    case 3u:return audio_uart_mux_on3((uint8_t)pin);
    case 4u:return audio_uart_mux_on4((uint8_t)pin);
    case 5u:return audio_uart_mux_on5((uint8_t)pin);
    case 6u:return audio_uart_mux_on6((uint8_t)pin);
    default:return 6u;
    }
}
uint32_t audio_uart_pin_mux_disable(uint32_t group,uint32_t pin) {
    if((uint8_t)pin>=0x39u) return 6u;
    switch((uint8_t)group) {
    case 0u:return audio_uart_mux_off0((uint8_t)pin);
    case 1u:return audio_uart_mux_off1((uint8_t)pin);
    case 2u:return audio_uart_mux_off2((uint8_t)pin);
    case 3u:return audio_uart_mux_off3((uint8_t)pin);
    case 4u:return audio_uart_mux_off4((uint8_t)pin);
    case 5u:return audio_uart_mux_off5((uint8_t)pin);
    case 6u:return audio_uart_mux_off6((uint8_t)pin);
    default:return 6u;
    }
}
