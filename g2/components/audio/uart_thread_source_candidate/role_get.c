/* Native role strap sampling 0x45a578, GPIO read 0x480f8a, and
 * millisecond wait 0x4910f4. Five 5-ms samples determine role. */
#include <stdint.h>

extern const uint32_t audio_uart_role_pin_config; /* *DAT_0045ade0 */
extern volatile uint8_t audio_uart_device_role_cell; /* *DAT_0045b0f4 */
extern const volatile uint32_t *const audio_uart_gpio_input_base; /* DAT_0048174c */
extern const volatile uint32_t *const audio_uart_gpio_output_base; /* DAT_00481750 */
extern const volatile uint32_t *const audio_uart_gpio_enable_base; /* DAT_00481754 */
extern uint32_t g2_codec_pin_function(uint32_t,uint32_t); /* selected 0x480f0c */
extern void audio_delay_us_selected(uint32_t); /* selected 0x4807a0 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern const char audio_uart_role_module[],audio_uart_role_source[],
                  audio_uart_role_function[];
extern const char audio_uart_role_e_read[],audio_uart_role_c_read[];
extern const char audio_uart_role_e_unstable[],audio_uart_role_c_unstable[];
extern const char audio_uart_role_e_stable[],audio_uart_role_c_stable[];

uint32_t audio_uart_pin_read(uint32_t pin,uint32_t mode,uint32_t *value) {
    const volatile uint32_t *base;
    if(mode==0u) base=audio_uart_gpio_input_base;
    else if(mode==1u) base=audio_uart_gpio_output_base;
    else if(mode==2u) base=audio_uart_gpio_enable_base;
    else return 6u;
    *value=(base[(pin&255u)>>5]>>(pin&31u))&1u;
    return 0u;
}

void audio_uart_wait_ms(uint32_t milliseconds) {
    audio_delay_us_selected(milliseconds*1000u);
}

uint8_t audio_uart_role_get(void) {
    (void)g2_codec_pin_function(0x9cu,audio_uart_role_pin_config);
    uint32_t samples[5]={0u,0u,0u,0u,0u};
    uint8_t stable=1u;
    for(uint32_t i=0;i<5u;i++) {
        uint32_t value;
        if(audio_uart_pin_read(0x9cu,0u,&value)!=0u) {
            if(audio_log_flags()&2u)
                audio_log_extended(1u,audio_uart_role_module,
                                   audio_uart_role_source,
                                   audio_uart_role_function,0x7fu,
                                   audio_uart_role_e_read,i);
            if((audio_log_flags()&1u)||(audio_log_flags()&4u))
                (void)compressed_log_output(0x4400000u,
                                            audio_uart_role_c_read,
                                            audio_uart_role_c_read,i);
            return 3u;
        }
        samples[i]=value;
        if(i>0u && value!=samples[0]) stable=0u;
        if(i<4u) audio_uart_wait_ms(5u);
    }
    if(stable==0u) {
        if(audio_log_flags()&2u)
            audio_log_extended(2u,audio_uart_role_module,
                               audio_uart_role_source,
                               audio_uart_role_function,0x91u,
                               audio_uart_role_e_unstable);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x8000000u,
                                        audio_uart_role_c_unstable,
                                        audio_uart_role_c_unstable);
        return 3u;
    }
    if(audio_log_flags()&2u)
        audio_log_extended(4u,audio_uart_role_module,
                           audio_uart_role_source,
                           audio_uart_role_function,0x98u,
                           audio_uart_role_e_stable,samples[0]);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x10400000u,
                                    audio_uart_role_c_stable,
                                    audio_uart_role_c_stable,samples[0]);
    audio_uart_device_role_cell=(samples[0]==1u)?2u:1u;
    return audio_uart_device_role_cell;
}
