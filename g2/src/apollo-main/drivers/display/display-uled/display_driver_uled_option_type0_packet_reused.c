/* Apollo S200 type-0 packet submit wrapper at 0x59cc40. */
#include <stdint.h>

extern void audio_uart_lv_memzero_48949c(void *,uint32_t);
extern uint32_t display_driver_uled_packet_validate_59cb42(void *,const char *);
extern void display_driver_uled_packet_begin_59c980(uint32_t,uint32_t);
extern void display_driver_uled_packet_encode_59cafc(void *,void *,uint32_t);
extern uint32_t g2_norflash_transfer_4c2098(uint32_t,void *,uint32_t);
extern void display_driver_uled_packet_end_59ca2c(uint32_t,uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

uint32_t display_driver_uled_type0_packet_59cc40(void *packet) {
    uint8_t scratch[24];
    audio_uart_lv_memzero_48949c(scratch,24u);
    uint32_t result=display_driver_uled_packet_validate_59cb42(
        packet,(const char *)(uintptr_t)0x776e44u);
    if (result != 0u) return result;
    uint32_t device=((const uint32_t *)packet)[6];
    display_driver_uled_packet_begin_59c980(
        *(volatile const uint32_t *)(uintptr_t)0x20074538u,device);
    display_driver_uled_packet_encode_59cafc(packet,scratch,0u);
    result=g2_norflash_transfer_4c2098(
        device,scratch,0xf4240u);
    if (result != 0u) {
        if (g2_flashdb_candidate_flags() & 2u)
            g2_flashdb_candidate_log(1u,(const char *)(uintptr_t)0x77f0a4u,
                (const char *)(uintptr_t)0x6f9fd4u,
                (const char *)(uintptr_t)0x776e44u,0xc0u,
                (const char *)(uintptr_t)0x73e68cu,result);
        if ((g2_flashdb_candidate_flags() & 1u) ||
            (g2_flashdb_candidate_flags() & 4u))
            (void)audio_log_simple(0x04400000u,
                (const char *)(uintptr_t)0x70b0e4u,
                (const char *)(uintptr_t)0x70b0e4u,result);
    }
    display_driver_uled_packet_end_59ca2c(
        *(volatile const uint32_t *)(uintptr_t)0x2007453cu,device);
    return result;
}
