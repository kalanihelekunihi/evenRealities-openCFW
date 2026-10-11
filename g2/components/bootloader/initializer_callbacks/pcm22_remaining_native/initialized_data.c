extern unsigned opencfw_spot_pcm22_transition19(unsigned,unsigned,unsigned,unsigned);
extern unsigned opencfw_spot_pcm22_transition7(unsigned,unsigned,unsigned,unsigned);
extern unsigned opencfw_spot_pcm22_transition4(unsigned,unsigned,unsigned,unsigned);
extern unsigned opencfw_spot_pcm22_transition13(unsigned,unsigned,unsigned,unsigned);
extern unsigned opencfw_spot_pcm22_transition9(unsigned,unsigned,unsigned,unsigned);
extern unsigned opencfw_spot_pcm22_transition10(unsigned,unsigned,unsigned,unsigned);
extern unsigned opencfw_spot_pcm22_transition23(unsigned,unsigned,unsigned,unsigned);
/* SPDX-License-Identifier: MIT
 * Recovered initialized DATA, not opcodes. Locked-f89a4c46 scatter output:
 * 1371 bytes, SHA e3bea7ccd46bc324829152b5b5a9069aecce5db243876273084d29bd7d47b843.
 * Unknown data fields retain address-based names. Unsupported callback entries
 * are explicit original-address contracts, never source-completeness evidence.
 */
#include <stdint.h>
#include <stddef.h>
extern uint32_t opencfw_spot_pcm22_transition22(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_spot_pcm22_transition11(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_spot_pcm22_transition12(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_spot_pcm22_transition21(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_spot_pcm22_transition5(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_spot_pcm22_transition20(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_spot_pcm22_transition6(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint64_t opencfw_spot_pcm22_transition1(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t event_a_pcm22_transition_sequence_0(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t event_a_pcm22_transition_sequence_2(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint64_t opencfw_spot_pcm22_transition3(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t event_a_transition_sequence_8_timer_native(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_spot_pcm22_transition14(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint64_t opencfw_spot_pcm22_transition15(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint64_t opencfw_spot_pcm22_transition16(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint64_t opencfw_spot_pcm22_transition17(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_spot_pcm22_transition18(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t event_a_transition_sequence_24(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t event_a_transition_sequence_25(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t event_a_transition_sequence_26(uint32_t,uint32_t,uint32_t,uint32_t);
struct recovered_data {
 uint32_t words_0000_00a0[41];
 uint32_t vddc_order_00a4[20];
 uint32_t vddf_order_00f4[20];
 uint32_t state_0144,pcm21_power_0148,shared_ton_014c,pcm22_power_0150,last_timer_power_0154;
 uintptr_t sequence_0158[27];
 uint32_t words_01c4_0554[229];
 uint8_t bytes_0558_055a[3];
};
_Static_assert(sizeof(uintptr_t)==4,"locked ARM32 pointer width");
_Static_assert(offsetof(struct recovered_data,vddc_order_00a4)==0xa4,"rank layout");
_Static_assert(offsetof(struct recovered_data,vddf_order_00f4)==0xf4,"rank layout");
_Static_assert(offsetof(struct recovered_data,sequence_0158)==0x158,"callback layout");
_Static_assert(offsetof(struct recovered_data,bytes_0558_055a)==1368,"tail layout");
extern uint32_t opencfw_boot_dfu_thread_deinit_native(void);
extern uint32_t opencfw_boot_manager_thread_deinit(void);
extern const uint32_t opencfw_boot_context_config_records[];
extern const uint32_t opencfw_boot_platform_config_table[];
extern const char opencfw_boot_elog_level_suffixes[6][4];
extern const char opencfw_boot_elog_color_suffixes[6][8];
extern const char opencfw_boot_locale_empty[1];
extern const char opencfw_boot_locale_decimal_point[2];
extern void opencfw_boot_dfu_thread_init(void);
extern void opencfw_boot_main_callback(void);
extern uint32_t opencfw_boot_storage_read(void *,const void *,uint32_t);
extern uint32_t opencfw_boot_storage_program(uint32_t,const void *,uint32_t);
extern uint32_t opencfw_boot_storage_erase_validate(uint32_t);
static const struct recovered_data initialized = {
 .words_0000_00a0={
  0x00000581u,0x00000480u,0x00000480u,0x00000480u,0x00000480u,0x00000480u,
  0x00000480u,0x00000480u,0x00000480u,0x00000880u,0x00000480u,0x00000480u,
  0x00000480u,0x00000480u,0x00000480u,0x00000480u,0x00000480u,0x00000480u,
  0x00000480u,0x00000582u,0x00000480u,0x00000480u,0x00000c00u,0x00000c00u,
  0x00000c00u,0x00000c00u,0x00000c00u,0x00000c00u,0x00000c00u,0x00000c00u,
  0x00040606u,0x00000000u,0x016e3600u,0x00000001u,0x00008000u,0x00000000u,
  0x0000002cu,0x00000004u,0xffffffffu,0x03000700u,0x00000000u,
 },
 .vddc_order_00a4={
  0x00000000u,0x00000000u,0x00000001u,0x00000002u,0x00000001u,0x00000001u,
  0x00000002u,0x00000003u,0x00000006u,0x00000004u,0x00000004u,0x00000004u,
  0x00000008u,0x00000007u,0x00000005u,0x00000005u,0x00000001u,0x00000001u,
  0x00000002u,0x00000003u,
 },
 .vddf_order_00f4={
  0x00000001u,0x00000000u,0x00000000u,0x00000000u,0x00000003u,0x00000002u,
  0x00000002u,0x00000002u,0x00000005u,0x00000004u,0x00000004u,0x00000004u,
  0x00000006u,0x00000004u,0x00000004u,0x00000004u,0x00000006u,0x00000004u,
  0x00000004u,0x00000004u,
 },
 .state_0144=7,.pcm21_power_0148=7,.shared_ton_014c=6,.pcm22_power_0150=7,.last_timer_power_0154=255,
 .sequence_0158={
  (uintptr_t)&event_a_pcm22_transition_sequence_0, /* selector0 */
  (uint32_t)(uintptr_t)&opencfw_spot_pcm22_transition1, /* selector1 */
  (uintptr_t)&event_a_pcm22_transition_sequence_2, /* selector2 */
  (uintptr_t)&opencfw_spot_pcm22_transition3, /* selector3 */
  (uintptr_t)&opencfw_spot_pcm22_transition4, /* selector4 native */
  (uintptr_t)&opencfw_spot_pcm22_transition5, /* selector5 native */
  (uintptr_t)&opencfw_spot_pcm22_transition6, /* selector6 native */
  (uintptr_t)&opencfw_spot_pcm22_transition7, /* selector7 native */
  (uintptr_t)&event_a_transition_sequence_8_timer_native, /* selector8 */
  (uintptr_t)&opencfw_spot_pcm22_transition9, /* selector9 native */
  (uintptr_t)&opencfw_spot_pcm22_transition10, /* selector10 native */
  (uintptr_t)&opencfw_spot_pcm22_transition11, /* selector11 */
  (uintptr_t)&opencfw_spot_pcm22_transition12, /* selector12 */
  (uintptr_t)&opencfw_spot_pcm22_transition13, /* selector13 native */
  (uintptr_t)&opencfw_spot_pcm22_transition14, /* selector14 */
  (uintptr_t)&opencfw_spot_pcm22_transition15, /* selector15 */
  (uintptr_t)&opencfw_spot_pcm22_transition16, /* selector16 */
  (uintptr_t)&opencfw_spot_pcm22_transition17, /* selector17 */
  (uintptr_t)&opencfw_spot_pcm22_transition18, /* selector18 */
  (uintptr_t)&opencfw_spot_pcm22_transition19, /* selector19 native */
  (uintptr_t)&opencfw_spot_pcm22_transition20, /* selector20 native */
  (uintptr_t)&opencfw_spot_pcm22_transition21, /* selector21 */
  (uintptr_t)&opencfw_spot_pcm22_transition22, /* selector22 */
  (uintptr_t)&opencfw_spot_pcm22_transition23, /* selector23 native */
  (uintptr_t)&event_a_transition_sequence_24, /* selector24 */
  (uintptr_t)&event_a_transition_sequence_25, /* selector25 */
  (uintptr_t)&event_a_transition_sequence_26, /* selector26 */
 },
 .words_01c4_0554={
  0x00000006u,0xfffffffeu,0xfffffffeu,0xfffffffeu,0xfffffffeu,0xfffffffeu,
  0xfffffffeu,0xfffffffeu,0xfffffffeu,0x00001000u,0x00001000u,0x00000000u,
  0x00000000u,0x00000000u,0x00000000u,
  (uintptr_t)&opencfw_boot_storage_read,(uintptr_t)&opencfw_boot_storage_program,
  (uintptr_t)&opencfw_boot_storage_erase_validate,
  0x00000308u,0x00020003u,0x14000000u,0x01010100u,0x00000000u,0x00000000u,
  0x00000308u,0x0002006bu,0x14000010u,0x01010100u,0x00000000u,0x00000000u,
  0x06010001u,0x0000080eu,0x01000001u,0x00012001u,0x20010200u,0x03000001u,
  0x00012001u,0x20010400u,0x05000001u,0x00012001u,0x20010600u,0x07000001u,
  0x00012001u,0x20010800u,0x09000001u,0x00012001u,0x20010101u,0x02010001u,
  0x00012001u,0x20010301u,0x04010001u,0x00012001u,0x20010501u,0x06010001u,
  0x00012001u,0x20010701u,0x08010001u,0x00012001u,0x20010901u,0x01000101u,
  0x01012001u,0x20010200u,0x03000101u,0x01012001u,0x20010400u,0x05000101u,
  0x01012001u,0x20010600u,0x07000101u,0x01012001u,0x20010800u,0x09000101u,
  0x01012001u,0x20010101u,0x02010101u,0x01012001u,0x20010301u,0x04010101u,
  0x01012001u,0x20010501u,0x06010101u,0x01012001u,0x20010701u,0x08010101u,
  0x01012001u,0x20010901u,
  (uintptr_t)&opencfw_boot_elog_level_suffixes[0][0],(uintptr_t)&opencfw_boot_elog_level_suffixes[1][0],
  (uintptr_t)&opencfw_boot_elog_level_suffixes[2][0],(uintptr_t)&opencfw_boot_elog_level_suffixes[3][0],
  (uintptr_t)&opencfw_boot_elog_level_suffixes[4][0],(uintptr_t)&opencfw_boot_elog_level_suffixes[5][0],
  (uintptr_t)&opencfw_boot_elog_color_suffixes[0][0],(uintptr_t)&opencfw_boot_elog_color_suffixes[1][0],
  (uintptr_t)&opencfw_boot_elog_color_suffixes[2][0],(uintptr_t)&opencfw_boot_elog_color_suffixes[3][0],
  (uintptr_t)&opencfw_boot_elog_color_suffixes[4][0],(uintptr_t)&opencfw_boot_elog_color_suffixes[5][0],
  0x00000001u,0x00061a80u,0x00000000u,0x00000000u,
  0x00000000u,0x00000001u,0x000f4240u,0x00000000u,0x200f1800u,0x00000800u,
  0x00000000u,0x00000000u,0x00000000u,0x00000000u,0x00000001u,0x00000000u,
  0x00000000u,0x00000000u,0x00000002u,0x00000000u,(uintptr_t)&opencfw_boot_context_config_records[0],0x2000034cu,
  0x00000003u,0x00000000u,0x00000000u,0x00000000u,0x00000004u,0x00000000u,
  (uintptr_t)&opencfw_boot_context_config_records[4],0x20000360u,0x00000005u,0x00000000u,(uintptr_t)&opencfw_boot_context_config_records[8],0x2000034cu,
  0x00000006u,0x00000000u,0x00000000u,0x00000000u,0x00000007u,0x00000000u,
  (uintptr_t)&opencfw_boot_context_config_records[12],0x2000034cu,0x000e1000u,0x00000203u,0x02020000u,0x00000000u,
  0x000f4240u,0x00000203u,0x02020000u,0x00000000u,0x00038400u,0x00000203u,
  0x02020000u,0x00000000u,0x00000000u,0x00000000u,0x00000000u,0x20080000u,
  0x00000000u,0x00000000u,0x00000000u,0x20080400u,0x00000400u,0x20080800u,
  0x00000000u,0x20080c00u,0x00000000u,0x00000000u,0x00000000u,0x00000000u,
  0x00000000u,0x00000000u,0x00000000u,0x00000001u,0x00000000u,(uintptr_t)&opencfw_boot_platform_config_table[0],
  0x200003f4u,0x20000424u,0x00000000u,0x00000000u,0x00000002u,0x00000000u,
  (uintptr_t)&opencfw_boot_platform_config_table[4],0x20000404u,0x20000434u,0x00000000u,0x00000000u,0x00000003u,
  0x00000000u,(uintptr_t)&opencfw_boot_platform_config_table[8],0x20000414u,0x20000444u,0x00000000u,0x00000000u,
  0xaaaaaaaau,0x00000037u,(uintptr_t)&opencfw_boot_dfu_thread_init,(uintptr_t)&opencfw_boot_dfu_thread_deinit_native,0x00000000u,0x00000000u,
  0x00000000u,0x00000000u,0x00000000u,0x00000000u,0x00000000u,0x200001e8u,
  (uintptr_t)&opencfw_boot_main_callback,(uintptr_t)&opencfw_boot_manager_thread_deinit,0x00000000u,0x00000000u,0x00000000u,0x00000000u,
  0x00000000u,0x00000000u,0x00000000u,(uintptr_t)&opencfw_boot_locale_empty[0],(uintptr_t)&opencfw_boot_locale_empty[0],(uintptr_t)&opencfw_boot_locale_empty[0],
  (uintptr_t)&opencfw_boot_locale_empty[0],(uintptr_t)&opencfw_boot_locale_empty[0],(uintptr_t)&opencfw_boot_locale_empty[0],(uintptr_t)&opencfw_boot_locale_empty[0],0xffffffffu,0xffffffffu,
  (uintptr_t)&opencfw_boot_locale_decimal_point[0],(uintptr_t)&opencfw_boot_locale_empty[0],(uintptr_t)&opencfw_boot_locale_empty[0],0xffffffffu,0x0000ffffu,0x01010101u,
  0x0b0b0d0du,
 },
 .bytes_0558_055a={
  0x00000012u,0x00000019u,0x0000001au,
 },
};
/* Source-defined .data install with compiler callback relocations. Firmware
 * compressed-byte reproduction and the other scatter records are separate.
 * The final padding byte remains untouched, exactly like stock decoder. */
void opencfw_boot_install_initialized_data(void) {
 volatile uint8_t *destination=(volatile uint8_t *)(uintptr_t)0x20000000u;
 const uint8_t *source=(const uint8_t *)&initialized;
 for(uint32_t i=0;i<1371;i++)destination[i]=source[i];
}
uint32_t opencfw_boot_selector_source_mask(void) {return 0x7ffffffu;}

/* Preserve the scatter-record ABI. Authenticated output descriptors select
 * source-owned data for all three stock records. Unknown descriptors retain
 * the reconstructed decoder contract. */
extern uint32_t *opencfw_boot_expand_record(uint32_t *,uint32_t);
extern const uint8_t opencfw_boot_itcm_image_start[];
extern const uint8_t opencfw_boot_itcm_image_end[];
uint32_t *opencfw_boot_expand_locked_data_record(uint32_t *record,uint32_t static_base) {
 /* The authenticated 24-byte ITCM helper image is source assembly. Its
  * instructions are position independent and occupy the original 0x40 slot. */
 if(record[1]==44u && record[2]==0x40u) {
  volatile uint8_t *destination=(volatile uint8_t *)(uintptr_t)0x40u;
  const uint8_t *source=opencfw_boot_itcm_image_start;
  for(uint32_t i=0;i<24u;i++)destination[i]=source[i];
  return record+3;
 }
 /* The record's compressed-source offset is irrelevant for the source-owned
  * SRAM block. Its authenticated output descriptor selects this installer. */
 if(record[1]==1250u && record[2]==0x20000000u) {
  opencfw_boot_install_initialized_data();
  return record+3;
 }
 /* The other SRAM stream expands to exactly 4096 zero bytes. This is source
  * initialization of that region, not a copy of its encoded payload. */
 if(record[1]==96u && record[2]==0x20080000u) {
  volatile uint32_t *destination=(volatile uint32_t *)(uintptr_t)0x20080000u;
  for(uint32_t i=0;i<1024u;i++)destination[i]=0u;
  return record+3;
 }
 return opencfw_boot_expand_record(record,static_base);
}
