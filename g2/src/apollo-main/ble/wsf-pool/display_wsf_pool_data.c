/* Source-owned Cordio pool configuration recovered from startup's compressed
 * SRAM copy: descriptor 0x75d3f4 -> RAM 0x200003b0. The BLE initializer
 * 0x4b7f64 passes this table, arena 0x2004fa98, count 4, size 0x2940 to
 * WsfBufInit. Final placement requires the product linker layout. */
#include <stdint.h>

struct wsf_pool_config_data { uint16_t size; uint8_t count; uint8_t reserved; };
_Static_assert(sizeof(struct wsf_pool_config_data)==4u,"WSF config ABI");

const struct wsf_pool_config_data audio_wsf_product_pool_config[4]={
    {16u,8u,0u}, {32u,4u,0u}, {64u,10u,0u}, {480u,20u,0u}
};
_Alignas(8) uint8_t audio_wsf_product_pool_arena[0x2940u];

/* Native BSS cells written by WsfBufInit and the critical-section provider.
 * No invented startup values: C static storage provides the source's zero
 * initialization before these native-equivalent bodies run. */
struct wsf_pool_desc_data;
struct wsf_pool_desc_data *audio_wsf_pool_list;
volatile uint8_t audio_wsf_pool_count;
volatile uint16_t audio_wsf_pool_used_bytes;
volatile uint8_t audio_wsf_cs_depth;
