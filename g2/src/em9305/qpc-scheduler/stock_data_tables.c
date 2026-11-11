#include <stdint.h>

/* Rodata tables that were referenced by raw stock address (wave 26 absolute-address fix,
 * g2/docs/em9305-abs-address-audit.md). Contents are the bytes of the stock record
 * firmware_ble_em9305.bin (g2-2.2.6.10; file offset = address - 0x302400 + 1060). Callers
 * now use these symbols so the image layout may shift. Pointer entries are symbolic. */

/* 0x33446c, 0x334470: 4-byte stream-header templates copied by memcpy(...,4) in
 * init_native_child_32874c / _3287b8 (stock bytes 03 00 00 08 / 03 00 00 04). */
const uint8_t opencfw_em9305_stream_header_33446c[4]={0x03u,0x00u,0x00u,0x08u};
const uint8_t opencfw_em9305_stream_header_334470[4]={0x03u,0x00u,0x00u,0x04u};

/* 0x3344b0: 7-byte lookup table indexed by ldb [idx+0x3344b0] in
 * init_native_associated_callback_329888 (stock bytes 02 01 03 01 01 01 04; the next stock
 * table, 0x3344b7, is opencfw_em9305_enc_switch_3344b7). Extent is inferred from that
 * neighbour: guess, indices seen in the callers are < 7. */
const uint8_t opencfw_em9305_event_map_3344b0[7]={0x02u,0x01u,0x03u,0x01u,0x01u,0x01u,0x04u};

/* 0x334b98: two subrate action function pointers selected by ld.as [0x334b98+idx*4] in
 * init_native_child_317f2c; 0x334ba0: byte table indexed by the same idx (stock bytes
 * 00 00 ff ff; the mode-callback table begins at 0x334ba4). Extent of the byte table: 4. */
extern uint32_t opencfw_em9305_subrate_action_315aec(uintptr_t);
extern uint32_t opencfw_em9305_subrate_action_3160d4(uintptr_t);
uint32_t (*const opencfw_em9305_subrate_actions_334b98[2])(uintptr_t)={
    opencfw_em9305_subrate_action_315aec,opencfw_em9305_subrate_action_3160d4};
const uint8_t opencfw_em9305_subrate_flags_334ba0[4]={0x00u,0x00u,0xffu,0xffu};

/* 0x334ae4: WSF buffer-pool descriptors {u16 length,u8 count,u8 pad} x7 consumed by
 * wsf_os_init(7,desc) (stock bytes 10 00 08 00 | 20 00 0d 00 | 40 00 08 00 | 70 00 04 00 |
 * 0f 01 08 00 | 10 01 03 00 | 20 01 08 00). The 0x334b00 pointer table that follows is
 * opencfw_em9305_associated_channel_actions. */
const uint8_t opencfw_em9305_wsf_pool_descriptors_334ae4[28]={
    0x10u,0x00u,0x08u,0x00u, 0x20u,0x00u,0x0du,0x00u, 0x40u,0x00u,0x08u,0x00u,
    0x70u,0x00u,0x04u,0x00u, 0x0fu,0x01u,0x08u,0x00u, 0x10u,0x01u,0x03u,0x00u,
    0x20u,0x01u,0x08u,0x00u};

/* 0x3357c0: AES-CMAC constant Rb (15 x 0x00, 0x87), reduced into the subkey by
 * radio_block_reduce_3335d8 (stock bytes at 0x3357c0..0x3357cf). */
const uint8_t opencfw_em9305_cmac_rb_3357c0[16]={
    0u,0u,0u,0u,0u,0u,0u,0u,0u,0u,0u,0u,0u,0u,0u,0x87u};

/* Stock 0x00334448: byte list read with ldb.ab by bsp_LinkLayerTimeEventCallback (0x315658), each value
 * passed to the PAL timer-channel enable query; 0xff terminates. Name is a guess from that use. */
const uint8_t opencfw_em9305_timer_channels_334448[4] = { 0x00, 0x01, 0x03, 0xff };
