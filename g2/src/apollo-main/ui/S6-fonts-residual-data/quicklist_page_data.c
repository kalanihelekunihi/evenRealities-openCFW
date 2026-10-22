/* QuickList page storage (S6-fonts-residual storage-definition pass,
 * G2 2.2.6.10). Stock owner:
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\quicklist\ui_quicklist_page.c.
 *
 * The cell lies in the 0x20080000 .data region (scatter record 0x75d404) but
 * every byte of it decodes to zero, so it is defined zero-initialised like
 * g2_quicklist_ui_data_2012a72c (ui/S4-ui-a-data/quicklist_page_data.c).
 * Absolute placement is a linker obligation; compiling this file does not
 * establish byte identity. */
#include <stdint.h>

/* RAM 0x2012d57c..0x201303cb (0x2e50 = 11856 bytes): second QuickList storage
 * block with the g2_quicklist_storage_t shape (count + 40 x 0x128-byte items
 * + reflash tail), sitting between g2_quicklist_ui_data_2012a72c (which ends
 * exactly at 0x2012d57c) and g2_quicklist_completed_201303cc. Stock code only
 * reaches its item array at +8: literal 0x4f631c (= 0x2012d584) is loaded by
 * handle_add_down 0x4f5966 and handle_add_up 0x4f5b48 / 0x4f5b80 as the
 * scratch buffer for shifting records (app/quicklist-mode/
 * quicklist_mode_two_detail_4f5838.c and quicklist_mode_two_4f5a1c.c, which
 * use the absolute address 0x2012d584). No word in the image addresses
 * 0x2012d57c itself. */
__attribute__((aligned(8))) uint8_t g2_quicklist_shift_scratch_2012d57c[0x2e50];
