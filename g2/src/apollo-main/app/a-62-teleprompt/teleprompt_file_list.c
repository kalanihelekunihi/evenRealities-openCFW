/* Teleprompt file list cache, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\teleprompt\teleprompt_file_list.c.
 * Native 0x58bce0..0x58bd86; literal pool 0x58bd88..0x58bda7.
 *
 * Holds the last FileList message from the phone: u16 file_count followed
 * by 0xc4-byte items (u16 name_len, name[0x42], title[0x80]); 0xf52 bytes
 * is room for 20 items. */
#include <stddef.h>
#include <stdint.h>
#include "g2_teleprompt_page_data.h"

static uint8_t g2_teleprompt_file_list[G2_TELEPROMPT_FILE_LIST_SIZE] __attribute__((aligned(4))); /* RAM 0x201093d4 */

extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* 0x439be4 memcpy */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "teleprompt.file"; /* ROM 0x789720 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\teleprompt\\teleprompt_file_list.c"; /* ROM 0x6f0088 */
static const char fn_update[] = "teleprompt_file_list_update"; /* ROM 0x772a40 */
static const char list_null[] = "file_list is NULL"; /* ROM 0x783dfc */
static const char list_null_c[] = "[teleprompt.file]file_list is NULL"; /* ROM 0x75abb4 */
static const char list_updated[] = "file_list updated: file_count=%d"; /* ROM 0x75abd8 */
static const char list_updated_c[] = "[teleprompt.file]file_list updated: file_count=%d"; /* ROM 0x72e560 */

void teleprompt_file_list_update(const void *file_list)
{
    if (file_list == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, fn_update, 0x0eu, list_null);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, list_null_c, list_null_c);
        return;
    }
    (void)audio_queue_copy_bytes(g2_teleprompt_file_list, file_list, G2_TELEPROMPT_FILE_LIST_SIZE);
    uint32_t count = *(const uint16_t *)file_list;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, fn_update, 0x13u, list_updated, count);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10400000u, list_updated_c, list_updated_c, count);
}

const void *teleprompt_file_list_get(void)
{
    return g2_teleprompt_file_list;
}

void teleprompt_file_list_reset(void)
{
    (void)aeabi_memset_43c0e4(g2_teleprompt_file_list, G2_TELEPROMPT_FILE_LIST_SIZE, 0);
}
