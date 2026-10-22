/* Native APP_MasterRingMacIsSet 0x4a2fdc. The six-byte product MAC
 * begins at hand context +12; all-FF is the absent sentinel. */
#include <stdint.h>

extern const volatile uint8_t *const audio_uart_hand_context; /* DAT_004667ec */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern const char audio_uart_mac_module[],audio_uart_mac_source[],
                  audio_uart_mac_function[];
extern const char audio_uart_mac_e_hi[],audio_uart_mac_c_hi[];
extern const char audio_uart_mac_e_lo[],audio_uart_mac_c_lo[];
extern const char audio_uart_mac_e_absent[],audio_uart_mac_c_absent[];

static void log3(uint32_t line,const char *extended,const char *short_text,
                 uint32_t a,uint32_t b,uint32_t c) {
    if(audio_log_flags()&2u)
        audio_log_extended(3u,audio_uart_mac_module,audio_uart_mac_source,
                           audio_uart_mac_function,line,extended,a,b,c);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0xcc00000u,short_text,short_text,a,b,c);
}

/* Stock 0x004A2FDC (APP_MasterRingMacIsSet) */
uint32_t audio_uart_ring_mac_ready(void) {
    uint8_t mac[6];
    for(uint32_t i=0;i<6u;i++) mac[i]=audio_uart_hand_context[12u+i];
    log3(0x5fbu,audio_uart_mac_e_hi,audio_uart_mac_c_hi,
         mac[5],mac[4],mac[3]);
    log3(0x5fcu,audio_uart_mac_e_lo,audio_uart_mac_c_lo,
         mac[2],mac[1],mac[0]);
    for(uint32_t i=0;i<6u;i++) if(mac[i]!=0xffu) return 1u;
    if(audio_log_flags()&2u)
        audio_log_extended(2u,audio_uart_mac_module,audio_uart_mac_source,
                           audio_uart_mac_function,0x601u,
                           audio_uart_mac_e_absent);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x8000000u,audio_uart_mac_c_absent,
                                    audio_uart_mac_c_absent);
    return 0u;
}
