/* Native 0x52fc04 deinitializes EM9305 firmware staging state and releases
 * its live buffer. Product RAM cells are reset by this body, not seeded. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_stock_ram_200731f0[] __asm__("g2_stock_ram_200731f0");
extern unsigned char g2ref_g2_stock_ram_20073488[] __asm__("g2_stock_ram_20073488");
extern unsigned char g2ref_g2_stock_ram_20074948[] __asm__("g2_stock_ram_20074948");
extern unsigned char g2ref_g2_stock_ram_20075010[] __asm__("g2_stock_ram_20075010");
extern void audio_file_heap_free(void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="srv.em9305";
static const char source_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\DFU\\service_em9305_dfu.c";
static const char function[]="SVC_Em9305FwDeinit";
static const char free_message[]="free g_file_buffer success";
static const char free_compact[]="[srv.em9305]free g_file_buffer success";
static const char done_message[]="BLE firmware data deinitialized";
static const char done_compact[]="[srv.em9305]BLE firmware data deinitialized";
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
static void log_event(uint32_t line,const char *message,const char *compact) {
    if(audio_log_flags()&2u)
        audio_log_extended(4u,module,source_path,function,line,message);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x10000000u,compact,compact);
}
void audio_ble_hci_radio_finalize_52fc04(void) {
    if(W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074948+0x4u))!=0u) {
        audio_file_heap_free((void *)(uintptr_t)W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074948+0x4u)));
        log_event(0x162u,free_message,free_compact);
        W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074948+0x4u))=0u;
        W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074948+0x8u))=0u;
    }
    __builtin_memset((void *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200731f0),0,0x40u);
    __builtin_memset((void *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20073488+0x4u),0,0x30u);
    W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074948+0x10u))=0u;
    W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074948+0x14u))=0u;
    W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074948+0x18u))=0u;
    W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074948+0x1cu))=0u;
    B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20075010+0x6u))=0u;
    log_event(0x177u,done_message,done_compact);
}
