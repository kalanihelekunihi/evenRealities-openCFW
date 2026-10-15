/* Native AgingTest_common_data_handler at 0x43c400. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

const char audio_uart_registry_aging_module[]="aging_test";
const char audio_uart_registry_aging_source[]=
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\AgingTest\\aging_test.c";
const char audio_uart_registry_aging_function[]="AgingTest_common_data_handler";
const char audio_uart_registry_aging_extended[]="AgingTest recv data len = %d";
const char audio_uart_registry_aging_compact[]="[aging_test]AgingTest recv data len = %d";

uint32_t audio_uart_registry_callback_43c400(uint32_t unused1,
                                               uint32_t unused2,
                                               uint32_t length) {
    (void)unused1;(void)unused2;
    if(audio_log_flags()&2u)
        audio_log_extended(3u,audio_uart_registry_aging_module,
                           audio_uart_registry_aging_source,
                           audio_uart_registry_aging_function,0x33u,
                           audio_uart_registry_aging_extended,length);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x0c400000u,
                                    audio_uart_registry_aging_compact,
                                    audio_uart_registry_aging_compact,length);
    return 0u;
}
