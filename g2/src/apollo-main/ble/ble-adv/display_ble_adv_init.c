/* Product _bleAdvInit 0x46db04, authenticated Main pseudocode/literals.
 * The advertising config/name RAM and context pointer remain live contracts. */
#include <stdint.h>
extern uint8_t audio_ble_slave_registration_table[]; /* native RAM 0x200003e0 */
extern uint8_t audio_ble_adv_name_buffer[]; /* native RAM 0x200003ec */
extern uint8_t *audio_ble_slave_mode_context; /* native pointer cell 0x20074330 */
extern uint32_t audio_uart_command_pending(void); /* productModeGet 0x4abe60 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern uint32_t g2_log_module_length(const char *); /* selected 0x44a43c */
extern void AppAdvSetData(uint8_t location,uint8_t length,const uint8_t *data);
extern void DmDevSetRandAddr(const uint8_t *address);
extern void DmAdvSetAddrType(uint8_t type);
extern void AppAdvStart(uint8_t mode);
extern void AppSetBondable(uint8_t bondable);
static void set16(uint8_t *p,uint16_t v) { p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8u); }

/* Stock 0x46DB04 (_bleAdvInit) */
void audio_ble_adv_init(void *event)
{
    (void)event;
    static const char module[]="ble.Slave";
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_peripheral.c";
    static const char function[]="_bleAdvInit";
    static const char test_message[]="Product test mode: Keep fast advertising without timeout";
    static const char test_compact[]="[ble.Slave]Product test mode: Keep fast advertising without timeout";
    static const char normal_message[]="Normal mode: Fast advertising for 30s, then slow advertising";
    static const char normal_compact[]="[ble.Slave]Normal mode: Fast advertising for 30s, then slow advertising";
    uint8_t *const config=audio_ble_slave_registration_table;
    if (audio_uart_command_pending()==1u) {
        set16(config,0u);
        set16(config+6u,0xa0u);
        if (audio_log_flags()&2u)
            audio_log_extended(3u,module,source,function,0xc1u,test_message);
        if ((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x0c000000u,test_compact,test_compact);
    } else {
        set16(config,30000u);
        set16(config+6u,0xa0u);
        set16(config+8u,0x640u);
        if (audio_log_flags()&2u)
            audio_log_extended(3u,module,source,function,199u,normal_message);
        if ((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x0c000000u,normal_compact,normal_compact);
    }
    uint8_t *const primary=audio_ble_adv_name_buffer+0x1cu;
    uint8_t *const scan=audio_ble_adv_name_buffer+0x38u;
    AppAdvSetData(2u,0x1cu,primary);
    AppAdvSetData(3u,(uint8_t)g2_log_module_length((const char *)scan),scan);
    AppAdvSetData(0u,0x1cu,primary);
    AppAdvSetData(1u,(uint8_t)g2_log_module_length((const char *)scan),scan);
    DmDevSetRandAddr(audio_ble_slave_mode_context+0x0fu);
    DmAdvSetAddrType(1u);
    AppAdvStart(1u);
    AppSetBondable(1u);
}
