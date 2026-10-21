/* Apollo S200 Hongshi configure sequence at 0x5bbff2. */
#include <stdint.h>

extern uint32_t display_driver_uled_type0_context_46bfe8(void);
extern void display_driver_uled_type0_context_snapshot_46c410(
    uint32_t, uint32_t *, uint32_t *);
extern uint32_t display_driver_uled_type1_write_register_5bbdf0(
    uint32_t, uint32_t, uint32_t);
extern uint32_t display_driver_uled_type1_read_bank_5bbe80(
    uint32_t, uint32_t);
extern void audio_ble_hci_boot_delay_491102(uint32_t);
extern void display_driver_uled_delay_449376(uint32_t);
extern void audio_ble_hci_radio_reset_4910f4(uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint32_t, const char *, const char *,
                                      const char *, uint32_t, const char *, ...);
extern uint32_t audio_log_simple(uint32_t, const char *, const char *, ...);
extern uint32_t display_driver_uled_type1_frame_start_5bcb28(void);
extern uint32_t display_driver_uled_type1_set_brightness_5bc6ae(
    uint32_t, uint32_t, uint32_t);
extern uint32_t display_driver_uled_type1_set_offset_5bc4c0(uint32_t,
                                                                uint32_t);

static const uint8_t hongshi_register_sequence[51] = {
    0x00,0xbe,0x84,0xff,0x06, 0x01,0x7e,0x02,0xff,0x06,
    0x01,0xa5,0x40,0xff,0x06, 0x00,0xf1,0x3f,0xff,0x64,
    0x00,0xe2,0xff,0xff,0x64, 0x00,0xf7,0xfc,0xff,0x64,
    0x00,0x78,0x0a,0xff,0x64, 0x00,0x7c,0x12,0xff,0x64,
    0x00,0xb7,0x80,0xff,0x64, 0x00,0xb0,0x80,0xff,0x64,
    0x63 /* source byte immediately after the native 50-byte table */
};

static void log_bank(uint32_t value, uint32_t line, uint32_t detail,
                     uint32_t short_detail, uint32_t level,
                     uint32_t compact_level) {
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(level,
            (const char *)(uintptr_t)0x785c80u,
            (const char *)(uintptr_t)0x6ecca8u,
            (const char *)(uintptr_t)0x753b58u,line,
            (const char *)(uintptr_t)detail,value);
    if ((g2_flashdb_candidate_flags() & 1u) ||
        (g2_flashdb_candidate_flags() & 4u))
        (void)audio_log_simple(compact_level,
            (const char *)(uintptr_t)short_detail,
            (const char *)(uintptr_t)short_detail,value);
}

static void read_and_log(uint32_t address, uint32_t mode, uint32_t line,
                         uint32_t detail, uint32_t short_detail,
                         uint32_t mismatch_line,
                         uint32_t mismatch_detail,
                         uint32_t mismatch_short_detail,
                         uint32_t expected) {
    const uint32_t value = display_driver_uled_type1_read_bank_5bbe80(
        address,mode) & 0xffu;
    log_bank(value,line,detail,short_detail,
             address == 0xf0u ? 3u : 4u,
             address == 0xf0u ? 0x0c400000u : 0x10400000u);
    if (mismatch_line != 0u && value != expected)
        log_bank(value,mismatch_line,mismatch_detail,mismatch_short_detail,
                 1u,0x04400000u);
}

uint32_t display_driver_uled_type1_step_5bbff2(void) {
    uint32_t luminance = 0, current = 0;
    display_driver_uled_type0_context_snapshot_46c410(
        display_driver_uled_type0_context_46bfe8(),
        &luminance,&current);
    (void)display_driver_uled_type1_write_register_5bbdf0(0x55u,0u,1u);
    uint32_t offset = 0;
    while (offset < 50u) {
        const uint8_t *const p = hongshi_register_sequence + offset;
        (void)display_driver_uled_type1_write_register_5bbdf0(
            p[1],p[2],p[0] != 0u);
        offset += 3u;
        if (hongshi_register_sequence[offset] == 0xffu) {
            audio_ble_hci_boot_delay_491102(hongshi_register_sequence[offset+1]);
            offset += 2u;
        }
        if (hongshi_register_sequence[offset] == 0xeeu) {
            display_driver_uled_delay_449376(hongshi_register_sequence[offset+1]);
            offset += 2u;
        }
    }
    audio_ble_hci_boot_delay_491102(100u);
    (void)display_driver_uled_type1_write_register_5bbdf0(0xf0u,0x28u,0u);
    audio_ble_hci_boot_delay_491102(100u);
    read_and_log(0xf0u,0u,0x1aau,0x776c4cu,0x753b7cu,0u,0u,0u,0u);
    audio_ble_hci_boot_delay_491102(100u);
    read_and_log(0xbeu,0u,0x1afu,0x776c64u,0x753ba0u,0u,0u,0u,0u);
    audio_ble_hci_boot_delay_491102(100u);
    read_and_log(0u,0u,0x1b3u,0x776c7cu,0x749614u,
                 0x1b6u,0x714698u,0x6f9e24u,0x36u);
    audio_ble_hci_boot_delay_491102(100u);
    read_and_log(0xf1u,0u,0x1bbu,0x776c94u,0x74963cu,
                 0x1beu,0x7146d4u,0x6f9e6cu,0x3fu);
    audio_ble_hci_boot_delay_491102(100u);
    read_and_log(0x7eu,1u,0x1c3u,0x776cacu,0x749664u,
                 0x1c6u,0x714710u,0x6f9eb4u,2u);
    audio_ble_hci_boot_delay_491102(100u);
    read_and_log(0xa5u,1u,0x1ccu,0x776cc4u,0x74968cu,0u,0u,0u,0u);
    audio_ble_hci_boot_delay_491102(100u);
    read_and_log(0xe2u,0u,0x1d1u,0x7496b4u,0x728da0u,0u,0u,0u,0u);
    audio_ble_hci_radio_reset_4910f4(1u);
    (void)display_driver_uled_type1_frame_start_5bcb28();
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(3u,
            (const char *)(uintptr_t)0x785c80u,
            (const char *)(uintptr_t)0x6ecca8u,
            (const char *)(uintptr_t)0x753b58u,0x1e6u,
            (const char *)(uintptr_t)0x75f750u,8u,8u);
    if ((g2_flashdb_candidate_flags() & 1u) ||
        (g2_flashdb_candidate_flags() & 4u))
        (void)audio_log_simple(0x0c800000u,
            (const char *)(uintptr_t)0x73e374u,
            (const char *)(uintptr_t)0x73e374u,8u,8u);
    const uint32_t brightness = display_driver_uled_type0_context_46bfe8();
    *(volatile uint32_t *)(uintptr_t)0x20074520u = brightness;
    (void)display_driver_uled_type1_set_brightness_5bc6ae(
        brightness,0u,0u);
    audio_ble_hci_radio_reset_4910f4(2u);
    const volatile uint8_t *const offsets =
        (const volatile uint8_t *)(uintptr_t)0x20003994u;
    (void)display_driver_uled_type1_set_offset_5bc4c0(
        offsets[0x2c],offsets[0x2d]);
    return 0u;
}
