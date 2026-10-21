/* Apollo uLED recovery guard 0x4ca5be..0x4ca60d. Candidate. */
#include <stdint.h>
void * volatile display_driver_uled_instance; /* source-owned BSS cell, SRAM 0x20074530 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="driver.uled";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\drv_mspi_uled.c";
static const char function[]="uled_status_check_and_recovery";
static const char text[]="Error - Failed to find uled driver.\r\n";
static const char compact[]="[driver.uled]Error - Failed to find uled driver.\r\n";
uint32_t display_driver_case6_guard(uint32_t requested) {
    (void)requested;
    uint8_t *driver=(uint8_t *)display_driver_uled_instance;
    if(driver!=0) {
        uint32_t (*status_check)(void)=*(uint32_t (**)(void))(void *)(driver+0x30u);
        return status_check();
    }
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(1u,module,path,function,0x162u,text);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x04000000u,compact,compact);
    return 0u;
}

static const char set_mode_function[]="uled_set_mode";
uint32_t display_driver_case8(uint32_t mode) {
    uint8_t *driver=(uint8_t *)display_driver_uled_instance;
    if(driver!=0) {
        uint32_t (*set_mode)(uint8_t)=*(uint32_t (**)(uint8_t))(void *)(driver+0x34u);
        return set_mode((uint8_t)mode);
    }
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(1u,module,path,set_mode_function,0x16bu,text);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x04000000u,compact,compact);
    return UINT32_MAX;
}
static void missing_driver(const char *caller,uint32_t line) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(1u,module,path,caller,line,text);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x04000000u,compact,compact);
}
uint32_t display_driver_case1_a(void) { /* native 0x4ca010 uled_driver_init */
    uint8_t *driver=(uint8_t *)display_driver_uled_instance;
    if(driver==0) {
        missing_driver("uled_driver_init",0xa4u);
        return UINT32_MAX;
    }
    void (*initialize)(uint32_t)=*(void (**)(uint32_t))(void *)(driver+0x0cu);
    initialize(0u);
    return 0u;
}
uint32_t display_driver_case2(void) { /* native 0x4c9fb4 uled_clearScreen */
    uint8_t *driver=(uint8_t *)display_driver_uled_instance;
    if(driver==0) {
        missing_driver("uled_clearScreen",0x9au);
        return UINT32_MAX;
    }
    uint32_t (*clear)(void)=*(uint32_t (**)(void))(void *)(driver+0x1cu);
    return clear();
}
uint32_t display_driver_case0(void) { /* native 0x4ca18a uled_driver_power_up */
    uint8_t *driver=(uint8_t *)display_driver_uled_instance;
    if(driver!=0) {
        uint32_t (*power_up)(void)=*(uint32_t (**)(void))(void *)(driver+0x10u);
        if(power_up!=0) return power_up();
    }
    static const char caller[]="uled_driver_power_up";
    static const char power_text[]="Error -no uled device or power_up function, failed.\r\n";
    static const char power_compact[]="[driver.uled]Error -no uled device or power_up function, failed.\r\n";
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(1u,module,path,caller,0xc8u,power_text);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x04000000u,power_compact,power_compact);
    return UINT32_MAX;
}
uint32_t display_driver_case5_b(void) { /* native 0x4ca126 uled_driver_power_down */
    uint8_t *driver=(uint8_t *)display_driver_uled_instance;
    if(driver!=0) {
        uint32_t (*power_down)(void)=*(uint32_t (**)(void))(void *)(driver+0x14u);
        if(power_down!=0) return power_down();
    }
    missing_driver("uled_driver_power_down",0xbfu);
    return UINT32_MAX;
}
uint32_t display_driver_case4_apply(uint32_t brightness,uint32_t upper,uint32_t lower) {
    /* Native 0x4ca1ee uled_mspi_setBrightness. The driver controls the mapping. */
    uint8_t *driver=(uint8_t *)display_driver_uled_instance;
    if(driver==0) {
        missing_driver("uled_mspi_setBrightness",0xd1u);
        return UINT32_MAX;
    }
    uint32_t (*apply)(uint32_t,uint32_t,uint32_t)=
        *(uint32_t (**)(uint32_t,uint32_t,uint32_t))(void *)(driver+0x18u);
    return apply(brightness,upper,lower);
}
uint32_t display_driver_case3(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f) {
    /* Native 0x4ca564 uled_QSPI_PartialReflash_async, six-word ABI. */
    uint8_t *driver=(uint8_t *)display_driver_uled_instance;
    if(driver==0) {
        missing_driver("uled_QSPI_PartialReflash_async",0x157u);
        return UINT32_MAX;
    }
    uint32_t (*reflash)(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t)=
        *(uint32_t (**)(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t))(void *)(driver+0x28u);
    return reflash(a,b,c,d,e,f);
}
