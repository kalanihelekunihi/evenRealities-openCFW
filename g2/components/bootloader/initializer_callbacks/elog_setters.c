/* Reconstructed from locked G2 bootloader f89a4c46...; no upstream source
 * imported. Callback-return behavior intentionally preserves stock invalid
 * writes. These setters are not safe validation APIs for untrusted input. */
#include "elog_setters.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define NI __attribute__((noinline))
extern void opencfw_bl_logger_output(uint32_t level,const char *tag,
 const char *file,const char *function,uint32_t line,const char *format,...);
NI void opencfw_boot_elog_reset_request(void) {
    __asm__ volatile("dsb sy" ::: "memory");
    W(0xe000ed0c)=(W(0xe000ed0c)&0x700)|0x05fa0004;
    __asm__ volatile("dsb sy" ::: "memory");
    for(;;)__asm__ volatile("nop");
}
NI void opencfw_boot_elog_assert(const char *condition,const char *function,uint32_t line) {
    uint32_t callback=W(0x200270e4);
    if(callback) {
        ((void (*)(const char *,const char *,uint32_t))(uintptr_t)callback)(condition,function,line);
        return;
    }
    opencfw_bl_logger_output(0,"elog",
        "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\EasyLogger-master\\easylogger\\src\\elog.c",
        function,line,"(%s) has assert failed at %s:%ld.",condition,function,line);
    opencfw_boot_elog_reset_request();
}
NI void opencfw_bl_service_mode(uint32_t enabled) {
    if((uint8_t)enabled>1)opencfw_boot_elog_assert("(enabled == false) || (enabled == true)","elog_set_output_enabled",278);
    B(0x200267f1)=(uint8_t)enabled;
}
NI void opencfw_bl_service_enable(uint32_t enabled) {
    if((uint8_t)enabled>1)opencfw_boot_elog_assert("(enabled == false) || (enabled == true)","elog_set_text_color_enabled",290);
    B(0x200267f5)=(uint8_t)enabled;
}
NI void opencfw_bl_invalid_pin_configure(uint32_t level,uint32_t format) {
    uint8_t selected=(uint8_t)level;
    if(selected>=6)opencfw_boot_elog_assert("level <= ELOG_LVL_VERBOSE","elog_set_fmt",321);
    W(0x200267d8+4u*selected)=format;
}
NI void opencfw_bl_service_configure(uint32_t level) {
    if((uint8_t)level>=6)opencfw_boot_elog_assert("level <= ELOG_LVL_VERBOSE","elog_set_filter_lvl",347);
    B(0x20026700)=(uint8_t)level;
}
