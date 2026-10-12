/* Native logger-setting BLE cancellation 0x458e48, flag/setter
 * 0x458e32/0x458df0, and descriptor setter 0x448cb8. */
#include <stdint.h>
extern volatile uint8_t audio_uart_logger_ble_enabled; /* RAM0x20074fe2 */
extern volatile uint32_t audio_uart_logger_ble_timeout; /* RAM0x200746b0 */
extern uint8_t audio_uart_ble_logger_descriptor[]; /* RAM0x20073b90, >=16 bytes */
extern void audio_uart_logger_ble_handler_5bf972(void); /* ROM Thumb0x5bf973 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="logger.setting";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\logger\\logger_setting.c";
static const char function[]="loggerSetting_cancel_ble_transmit";
static const char message[]="loggerSetting cancel ble transmit: app startup, cancel ble log transmit";
static const char short_message[]="[logger.setting]loggerSetting cancel ble transmit: app startup, cancel ble log transmit";

uint32_t audio_uart_logger_ble_transmit_enabled_458e32(void)
{
    return audio_uart_logger_ble_enabled==1u;
}

uint32_t audio_uart_logger_descriptor_set_448cb8(uint32_t enabled,void *callback)
{
    uint8_t *descriptor=audio_uart_ble_logger_descriptor;
    descriptor[8u]=(uint8_t)enabled;
    *(void **)(void *)(descriptor+12u)=callback;
    return 0u;
}

void audio_uart_logger_ble_transmit_set_458df0(uint32_t enabled)
{
    if ((uint8_t)enabled!=0u) {
        audio_uart_logger_ble_enabled=1u;
        audio_uart_logger_ble_timeout=1000u;
        (void)audio_uart_logger_descriptor_set_448cb8(1u,(void *)audio_uart_logger_ble_handler_5bf972);
    } else {
        (void)audio_uart_logger_descriptor_set_448cb8(0u,(void *)audio_uart_logger_ble_handler_5bf972);
        audio_uart_logger_ble_enabled=0u;
        audio_uart_logger_ble_timeout=0u;
    }
}

void audio_uart_logger_cancel_ble_transmit_458e48(void)
{
    if (audio_uart_logger_ble_transmit_enabled_458e32()==0u) return;
    if ((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,source,function,0x53u,message);
    if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c000000u,short_message,short_message);
    audio_uart_logger_ble_transmit_set_458df0(0u);
}
