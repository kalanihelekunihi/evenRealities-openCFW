/* Native _bleExactleStackInit 0x4b7f64, source-order Cordio startup.
 * Every still-unrecovered vendor child is an explicit function import. */
#include <stdint.h>
struct wsf_pool_config {uint16_t size;uint8_t count;uint8_t reserved;};
extern uint8_t audio_wsf_product_pool_arena[0x2940u];
extern const struct wsf_pool_config audio_wsf_product_pool_config[4];
extern void audio_wsf_os_initialize(void); /* WsfOsInit 0x52b9b2 */
extern void WsfTimerInit(void); /* 0x52a474 */
extern uint16_t audio_wsf_buffer_init(uint16_t,void *,uint8_t,const struct wsf_pool_config *); /* 0x530364 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern void audio_ble_stack_lower_536324(void);
extern void audio_ble_stack_lower_53648e(void);
extern void audio_ble_stack_lower_5366cc(void);
extern void audio_ble_stack_lower_5367ca(void);
extern uint8_t WsfOsSetNextHandler(void (*)(void));
extern void audio_ble_stack_lower_5367f8(uint8_t);
extern void audio_ble_stack_lower_5369ea(void);
extern void audio_ble_stack_lower_4bae6c(uint8_t);
extern void audio_ble_comm_handler_init(uint8_t);
extern void audio_ble_hci_driver_handler_init(uint8_t);
extern void audio_ble_handler_536814(void);
extern void audio_ble_handler_4d2a5c(void);
extern void audio_ble_handler_536fa4(void);
extern void audio_ble_handler_4b5146(void);
extern void audio_ble_smp_handler_537d0c(void); /* native SmpHandler 0x537d0c */
extern void audio_ble_app_handler_4bae84(void); /* native AppHandler 0x4bae84 */
extern void audio_ble_handler_4b7d32(void);
extern void audio_ble_handler_4b4ab2(void);
extern void DmDevVsInit(uint32_t);
extern void DmAdvInit(void);
extern void DmPhyInit(void);
extern void DmConnInit(void);
extern void DmConnMasterInit(void);
extern void DmConnSlaveInit(void);
extern void DmSecInit(void);
extern void DmSecLescInit(void);
extern void DmPrivInit(void);
extern void DmHandlerInit(uint8_t);
extern void L2cSlaveHandlerInit(uint8_t);
extern void L2cInit(void);
extern void L2cSlaveInit(void);
extern void L2cMasterInit(void);
extern void AttHandlerInit(uint8_t);
extern void AttsInit(void);
extern void AttsIndInit(void);
extern void AttcInit(void);
extern void SmpHandlerInit(uint8_t);
extern void SmpiInit(void);
extern void SmpiScInit(void);
extern void SmprInit(void);
extern void SmprScInit(void);
extern void HciSetMaxRxAclLen(uint16_t);
static const char module[]="ble.comm";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble.c";
static const char function[]="_bleExactleStackInit";
static const char error[]="Memory pool is too small by %d\r\n";
static const char compact_error[]="[ble.comm]Memory pool is too small by %d\r\n";

void audio_ble_exactle_stack_initialize(void) {
    audio_wsf_os_initialize();
    WsfTimerInit();
    uint16_t used=audio_wsf_buffer_init(0x2940u,audio_wsf_product_pool_arena,
                                       4u,audio_wsf_product_pool_config);
    if(used>0x2940u) {
        uint32_t excess=(uint32_t)used-0x2940u;
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,781u,error,excess);
        if((audio_log_flags()&5u)!=0u)
            (void)compressed_log_output(0x04400000u,compact_error,compact_error,excess);
    }
    audio_ble_stack_lower_536324();
    audio_ble_stack_lower_53648e();
    audio_ble_stack_lower_5366cc();
    audio_ble_stack_lower_5367ca();
    uint8_t handler=WsfOsSetNextHandler(audio_ble_handler_536814);
    audio_ble_stack_lower_5367f8(handler);
    handler=WsfOsSetNextHandler(audio_ble_handler_4d2a5c);
    DmDevVsInit(0u);DmAdvInit();audio_ble_stack_lower_5369ea();DmPhyInit();
    DmConnInit();DmConnMasterInit();DmConnSlaveInit();DmSecInit();
    DmSecLescInit();DmPrivInit();DmHandlerInit(handler);
    handler=WsfOsSetNextHandler(audio_ble_handler_536fa4);
    L2cSlaveHandlerInit(handler);L2cInit();L2cSlaveInit();L2cMasterInit();
    handler=WsfOsSetNextHandler(audio_ble_handler_4b5146);
    AttHandlerInit(handler);AttsInit();AttsIndInit();AttcInit();
    handler=WsfOsSetNextHandler(audio_ble_smp_handler_537d0c);
    SmpHandlerInit(handler);SmpiInit();SmpiScInit();SmprInit();SmprScInit();
    HciSetMaxRxAclLen(0xfbu);
    handler=WsfOsSetNextHandler(audio_ble_app_handler_4bae84);
    audio_ble_stack_lower_4bae6c(handler);
    handler=WsfOsSetNextHandler(audio_ble_handler_4b7d32);
    audio_ble_comm_handler_init(handler);
    handler=WsfOsSetNextHandler(audio_ble_handler_4b4ab2);
    audio_ble_hci_driver_handler_init(handler);
}
