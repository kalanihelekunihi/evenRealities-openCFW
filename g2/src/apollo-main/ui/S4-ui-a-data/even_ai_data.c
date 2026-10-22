/* Even AI UI storage (S4-ui-a storage-definition pass, G2 2.2.6.10).
 *
 * Stock owner app\gui\even_ai (dialog list, stream state, layout cache).
 * .data values come from the decoded scatter init streams (records 0x75d3f4
 * for 0x20000000.. and 0x75d404 for 0x20080000..); every other RAM cell is
 * zero-initialised (.bss 0x20004558.. / 0x2013be70..). ROM bytes are copied
 * from ota_s200_firmware_ota.bin (VA = file offset + 0x437fe0). Absolute
 * placement is a linker obligation; compiling this file does not establish
 * byte identity. */
#include <stdint.h>

__attribute__((aligned(4))) uint8_t g2_even_ai_dialogs[0x20]; /* RAM 0x200739fc; extern view: g2_even_ai_dialogs_t g2_even_ai_dialogs; */

__attribute__((aligned(4))) uint8_t g2_even_ai_layout_cache[0x10]; /* RAM 0x20073f04; extern view: g2_even_ai_layout_cache_t g2_even_ai_layout_cache; */

void *g2_even_ai_current_streaming_node; /* RAM 0x20074c08 */

uint8_t g2_even_ai_stream_flag; /* RAM 0x2007503b */

__attribute__((aligned(4))) uint8_t g2_even_ai_dialog_pool[0xb4]; /* RAM 0x20120254; extern view: g2_even_ai_dialog_node_t g2_even_ai_dialog_pool[EVEN_AI_POOL_SIZE]; */
