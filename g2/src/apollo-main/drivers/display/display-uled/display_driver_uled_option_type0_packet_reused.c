/* Apollo S200 type-0 packet submit wrapper at 0x59cc40. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_uled_mspi_quad_config[] __asm__("g2_uled_mspi_quad_config");
extern unsigned char g2ref_g2_uled_mspi_serial_config[] __asm__("g2_uled_mspi_serial_config");

extern void audio_uart_lv_memzero_48949c(void *,uint32_t);
extern uint32_t display_driver_uled_packet_validate_59cb42(void *,const char *);
extern void display_driver_uled_serial_mode_59c980(const void *,uint32_t);
extern void display_driver_uled_packet_encode_59cafc(void *,void *,uint32_t);
extern uint32_t g2_norflash_transfer_4c2098(uint32_t,void *,uint32_t);
extern void display_driver_uled_quad_mode_59ca2c(const void *,uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

uint32_t display_driver_uled_type0_packet_59cc40(void *packet) {
    uint8_t scratch[24];
    audio_uart_lv_memzero_48949c(scratch,24u);
    uint32_t result=display_driver_uled_packet_validate_59cb42(
        packet,"am_devices_mspi_read" /* stock 0x776e44 */);
    if (result != 0u) return result;
    uint32_t device=((const uint32_t *)packet)[6];
    display_driver_uled_serial_mode_59c980(
        (const void *)(uintptr_t)(*(volatile const uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_uled_mspi_serial_config)),device);
    display_driver_uled_packet_encode_59cafc(packet,scratch,0u);
    result=g2_norflash_transfer_4c2098(
        device,scratch,0xf4240u);
    if (result != 0u) {
        if (g2_flashdb_candidate_flags() & 2u)
            g2_flashdb_candidate_log(1u,"driver.uled_common" /* stock 0x77f0a4 */,
                "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\drv_mspi_uled_common.c" /* stock 0x6f9fd4 */,
                "am_devices_mspi_read" /* stock 0x776e44 */,0xc0u,
                "MSPI read transfer failed, status: 0x%08X\r\n" /* stock 0x73e68c */,result);
        if ((g2_flashdb_candidate_flags() & 1u) ||
            (g2_flashdb_candidate_flags() & 4u))
            (void)audio_log_simple(0x04400000u,
                "[driver.uled_common]MSPI read transfer failed, status: 0x%08X\r\n" /* stock 0x70b0e4 */,
                "[driver.uled_common]MSPI read transfer failed, status: 0x%08X\r\n" /* stock 0x70b0e4 */,result);
    }
    display_driver_uled_quad_mode_59ca2c(
        (const void *)(uintptr_t)(*(volatile const uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_uled_mspi_quad_config)),device);
    return result;
}
