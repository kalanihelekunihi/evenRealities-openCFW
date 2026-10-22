/* Stock widget storage (S4-ui-a storage-definition pass, G2 2.2.6.10).
 *
 * Stock owner app\gui\dashboard\widget_stock (tile + expanded page).
 * .data values come from the decoded scatter init streams (records 0x75d3f4
 * for 0x20000000.. and 0x75d404 for 0x20080000..); every other RAM cell is
 * zero-initialised (.bss 0x20004558.. / 0x2013be70..). ROM bytes are copied
 * from ota_s200_firmware_ota.bin (VA = file offset + 0x437fe0). Absolute
 * placement is a linker obligation; compiling this file does not establish
 * byte identity. */
#include <stdint.h>

uint32_t g2_stock_tilelist_index_20004328 = 0xffffffffu; /* RAM 0x20004328 (.data, init record 0x75d3f4) */

void *g2_stock_page_dots_200740e0[3]; /* RAM 0x200740e0 */

uint32_t g2_stock_widget_init_flag_20074e2c; /* RAM 0x20074e2c */

uint32_t g2_stock_ext_active_20074e30; /* RAM 0x20074e30 */

void *g2_stock_ext_fifo_20074e34; /* RAM 0x20074e34 */

int32_t g2_stock_container_index_20074e38; /* RAM 0x20074e38 */

void *g2_stock_container_frame_20074e3c; /* RAM 0x20074e3c */

void *g2_stock_ext_container_frame_20074e40; /* RAM 0x20074e40 */

void *g2_stock_no_data_icon_20074e44; /* RAM 0x20074e44 */

void *g2_stock_no_data_label1_20074e48; /* RAM 0x20074e48 */

void *g2_stock_no_data_label2_20074e4c; /* RAM 0x20074e4c */

void *g2_stock_no_data_icon; /* RAM 0x20074e50 */

void *g2_stock_no_data_title; /* RAM 0x20074e54 */

void *g2_stock_no_data_hint; /* RAM 0x20074e58 */

int32_t g2_stock_page_dots_count_20074e5c; /* RAM 0x20074e5c */

uint8_t g2_stock_page_dots_visible_20075042; /* RAM 0x20075042 */

extern uint8_t g2_stock_bmp_0[]; /* RAM 0x200bac20, app segment */
extern uint8_t g2_stock_bmp_1[]; /* RAM 0x200bcc18, app segment */
extern uint8_t g2_stock_bmp_2[]; /* RAM 0x200bec10, app segment */
extern uint8_t g2_stock_bmp_3[]; /* RAM 0x200c0c08, app segment */
extern uint8_t g2_stock_bmp_4[]; /* RAM 0x200c2c00, app segment */
extern uint8_t g2_stock_bmp_5[]; /* RAM 0x200c4bf8, app segment */
extern uint8_t g2_stock_bmp_6[]; /* RAM 0x200c6bf0, app segment */
extern uint8_t g2_stock_bmp_7[]; /* RAM 0x200c8be8, app segment */
extern uint8_t g2_stock_bmp_8[]; /* RAM 0x200cabe0, app segment */
/* RAM 0x200e7880 (.data 0x20080000 init stream): nine 20-byte L8 132x62 image
 * headers {magic/cf, w|h<<16, stride, data_size, data}; extern view uint8_t[9][0x14]. */
__attribute__((aligned(4))) struct {
    uint32_t header, dimensions, stride, data_size;
    const uint8_t *data;
} g2_stock_chart_images[9] = {
    {0x619u, 0x003e0084u, 0x84u, 0x1ff8u, g2_stock_bmp_0},
    {0x619u, 0x003e0084u, 0x84u, 0x1ff8u, g2_stock_bmp_1},
    {0x619u, 0x003e0084u, 0x84u, 0x1ff8u, g2_stock_bmp_2},
    {0x619u, 0x003e0084u, 0x84u, 0x1ff8u, g2_stock_bmp_3},
    {0x619u, 0x003e0084u, 0x84u, 0x1ff8u, g2_stock_bmp_4},
    {0x619u, 0x003e0084u, 0x84u, 0x1ff8u, g2_stock_bmp_5},
    {0x619u, 0x003e0084u, 0x84u, 0x1ff8u, g2_stock_bmp_6},
    {0x619u, 0x003e0084u, 0x84u, 0x1ff8u, g2_stock_bmp_7},
    {0x619u, 0x003e0084u, 0x84u, 0x1ff8u, g2_stock_bmp_8},
};

/* RAM 0x201308dc: stock page data {g2_stock_record_t records[9] (0x2568 bytes),
 * u16 count at +0x2568}; extern views g2_stock_page_data_t / g2_stock_record_t[9]
 * (g2_stock_data, defsym alias) / uint16_t g2_stock_count (RAM 0x20132e44). */
__attribute__((aligned(4))) uint8_t g2_stock_page_data_201308dc[0x256c];
__asm__(".globl g2_stock_count\n\t.type g2_stock_count, %object\n\t"
        ".set g2_stock_count, g2_stock_page_data_201308dc + 0x2568\n\t.size g2_stock_count, 2");

__attribute__((aligned(4))) uint8_t g2_stock_ext_page_20132e48[0x128]; /* RAM 0x20132e48; extern view: g2_stock_ext_page_t g2_stock_ext_page_20132e48; */
