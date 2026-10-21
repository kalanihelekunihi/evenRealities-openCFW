/* Three native UI test handlers: 0x5cf2e6, 0x5cf634, 0x5cf7a8. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

const char audio_uart_registry_distortion_extended[]="PdtDistortionTest recv data len = %d";
const char audio_uart_registry_distortion_function[]="PdtDistortionTest_common_data_handler";
const char audio_uart_registry_distortion_source[]=
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\PdtDistortionTest\\pdt_distortion_test.c";
const char audio_uart_registry_distortion_module[]="pdt_distortion_test";
const char audio_uart_registry_distortion_compact[]=
    "[pdt_distortion_test]PdtDistortionTest recv data len = %d";

const char audio_uart_registry_gray_extended[]="PdtGrayScreen recv data len = %d";
const char audio_uart_registry_gray_function[]="PdtGrayScreen_common_data_handler";
const char audio_uart_registry_gray_source[]=
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\PdtGrayScreen\\pdt_gray_screen.c";
const char audio_uart_registry_gray_module[]="pdt_gray_screen";
const char audio_uart_registry_gray_compact[]=
    "[pdt_gray_screen]PdtGrayScreen recv data len = %d";

const char audio_uart_registry_production_extended[]="ProductionTest recv data len = %d";
const char audio_uart_registry_production_function[]="ProductionTest_common_data_handler";
const char audio_uart_registry_production_source[]=
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\ProductionTest\\production_test.c";
const char audio_uart_registry_production_module[]="production_test";
const char audio_uart_registry_production_compact[]=
    "[production_test]ProductionTest recv data len = %d";

static uint32_t report_length(uint32_t line,const char *module,
                              const char *source,const char *function,
                              const char *extended,const char *compact,
                              uint32_t length) {
    if(audio_log_flags()&2u)
        audio_log_extended(3u,module,source,function,line,extended,length);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x0c400000u,compact,compact,length);
    return 0u;
}

uint32_t audio_uart_registry_callback_5cf2e6(uint32_t unused1,
                                               uint32_t unused2,uint32_t length) {
    (void)unused1;(void)unused2;
    return report_length(0x26u,audio_uart_registry_distortion_module,
                         audio_uart_registry_distortion_source,
                         audio_uart_registry_distortion_function,
                         audio_uart_registry_distortion_extended,
                         audio_uart_registry_distortion_compact,length);
}
uint32_t audio_uart_registry_callback_5cf634(uint32_t unused1,
                                               uint32_t unused2,uint32_t length) {
    (void)unused1;(void)unused2;
    return report_length(0x21u,audio_uart_registry_gray_module,
                         audio_uart_registry_gray_source,
                         audio_uart_registry_gray_function,
                         audio_uart_registry_gray_extended,
                         audio_uart_registry_gray_compact,length);
}
uint32_t audio_uart_registry_callback_5cf7a8(uint32_t unused1,
                                               uint32_t unused2,uint32_t length) {
    (void)unused1;(void)unused2;
    return report_length(0x21u,audio_uart_registry_production_module,
                         audio_uart_registry_production_source,
                         audio_uart_registry_production_function,
                         audio_uart_registry_production_extended,
                         audio_uart_registry_production_compact,length);
}
