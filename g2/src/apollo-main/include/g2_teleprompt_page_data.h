/* Teleprompt page cache and file list, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\teleprompt\teleprompt_page_data.c
 * (native 0x58a8e0..0x58bc06) and teleprompt_file_list.c (0x58bce0..0x58bd86).
 * Implemented in app/a-62-teleprompt; called by the teleprompt FSM
 * (teleprompt_fsm.c), controller and UI (ui/a-53, ui/a-54). */
#ifndef G2_TELEPROMPT_PAGE_DATA_H
#define G2_TELEPROMPT_PAGE_DATA_H

#include <stddef.h>
#include <stdint.h>

#define G2_TELEPROMPT_PAGE_SLOTS 20u      /* page cache ring, slot = page % 20 */
#define G2_TELEPROMPT_PAGE_SIZE 0x40cu    /* decoded PageData message */
#define G2_TELEPROMPT_FILE_LIST_SIZE 0xf52u

/* Decoded PageData payload as stored in a cache slot. */
typedef struct {
    uint32_t page_id;          /* +0x000 */
    uint32_t field_04;         /* +0x004 */
    uint16_t text_size;        /* +0x008 */
    char text[0x402];          /* +0x00a */
} g2_teleprompt_page_t;
_Static_assert(sizeof(g2_teleprompt_page_t) == G2_TELEPROMPT_PAGE_SIZE, "stock page copy is 0x40c bytes");

/* Page cache (teleprompt_page_data.c). */
int32_t teleprompt_request_page_data(uint32_t page, uint8_t start_timer);
void teleprompt_page_data_init(uint32_t start_page, uint32_t total_pages);
void teleprompt_page_data_deinit(void);
uint8_t teleprompt_page_data_update(const g2_teleprompt_page_t *page);
const g2_teleprompt_page_t *teleprompt_page_data_get(uint32_t page);
uint8_t semantic_page_in_ensure_window(uint32_t page);
void teleprompt_page_data_set_window(uint32_t window_start);

/* File list (teleprompt_file_list.c): u16 count + 0xc4-byte items. */
void teleprompt_file_list_update(const void *file_list);
const void *teleprompt_file_list_get(void);
void teleprompt_file_list_reset(void);

#endif
