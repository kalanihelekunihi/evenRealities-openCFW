/* Apollo S200 type-0 packet-write submit wrapper at 0x59ccdc. */
#include <stdint.h>

extern void audio_uart_lv_memzero_48949c(void *,uint32_t);
extern uint32_t display_driver_uled_packet_validate_59cb42(void *,const char *);
extern void display_driver_uled_packet_begin_59c980(uint32_t,uint32_t);
extern uint32_t audio_uart_cache_clean_range_47510e(const uint32_t *);
extern void display_driver_uled_packet_encode_59cafc(void *,void *,uint32_t);
extern uint32_t g2_norflash_transfer_4c2098(uint32_t,const void *,uint32_t);
extern void display_driver_uled_packet_end_59ca2c(uint32_t,uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

uint32_t display_driver_uled_type0_packet_write_59ccdc(void *packet) {
    uint8_t scratch[24];
    audio_uart_lv_memzero_48949c(scratch,24u);
    uint32_t result=display_driver_uled_packet_validate_59cb42(
        packet,(const char *)(uintptr_t)0x776e5cu);
    if (result != 0u) return result;
    uint32_t device=((const uint32_t *)packet)[6];
    display_driver_uled_packet_begin_59c980(
        *(volatile const uint32_t *)(uintptr_t)0x20074538u,device);
    uint32_t range[2]={((const uint32_t *)packet)[5],
                       ((const uint32_t *)packet)[3]};
    (void)audio_uart_cache_clean_range_47510e(range);
    display_driver_uled_packet_encode_59cafc(packet,scratch,1u);
    result=g2_norflash_transfer_4c2098(device,scratch,0xf4240u);
    if (result != 0u) {
        if (g2_flashdb_candidate_flags() & 2u)
            g2_flashdb_candidate_log(1u,(const char *)(uintptr_t)0x77f0a4u,
                (const char *)(uintptr_t)0x6f9fd4u,
                (const char *)(uintptr_t)0x776e5cu,0xe3u,
                (const char *)(uintptr_t)0x7337f4u,result);
        if ((g2_flashdb_candidate_flags() & 1u) ||
            (g2_flashdb_candidate_flags() & 4u))
            (void)audio_log_simple(0x04400000u,
                (const char *)(uintptr_t)0x702504u,
                (const char *)(uintptr_t)0x702504u,result);
    }
    display_driver_uled_packet_end_59ca2c(
        *(volatile const uint32_t *)(uintptr_t)0x2007453cu,device);
    return result;
}
