/* Translate display-text getters, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\translate\translate.c.
 * Stock ranges 0x59ea10..0x59ea13 and 0x59ea14..0x59ea17 (literal pool entries
 * 0x59ea54, 0x59ea5c). Sibling functions of this TU are in
 * app/p-14-translate/translate.c. */
#include <stdint.h>

extern char g2_translate_src_display[0x1008]; /* RAM 0x2011bf14 */
extern char g2_translate_dst_display[0x1008]; /* RAM 0x2011cf1c */

/* Stock 0x0059EA10 (translate_data_get_src_text_59ea10) */
const char *translate_data_get_src_text_59ea10(void)
{
    return g2_translate_src_display;
}

/* Stock 0x0059EA14 (translate_data_get_dst_text_59ea14) */
const char *translate_data_get_dst_text_59ea14(void)
{
    return g2_translate_dst_display;
}
