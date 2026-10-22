/* Stock D:\01_workspace\s200_ap510b_iar_git\platform\service\callback_mgr\callback_manager.c
 * Native CALLBACK_MGR_Deinit 0x5101ae..0x510217 (literal pool entries
 * 0x510550, 0x510554, 0x510570..0x510578).
 *
 * The rest of this source is in system/callback-manager under the audio_*
 * names: CreateNode 0x5100a0 and is_registered 0x510218 (static there),
 * delete_node 0x5100fc, Init 0x510108, Register 0x510240, Unregister 0x5103c4.
 * Stock Deinit returns no value; callers declare it uint32_t and discard it. */
#include <stdint.h>

struct callback_node {
    void *callback;            /* +0x0 */
    struct callback_node *next; /* +0x4 */
};
struct callback_manager {
    struct callback_node *head; /* +0x0 */
    uint8_t count;              /* +0x4 */
    uint8_t pad[3];
    const char *name;           /* +0x8 */
};
_Static_assert(sizeof(struct callback_node) == 8u, "stock callback node is 8 bytes");
_Static_assert(sizeof(struct callback_manager) == 12u, "stock callback manager is 12 bytes");

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t level, const char *module, const char *file, const char *function,
                               uint32_t line, const char *format, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t code, const char *format, const char *text, ...); /* 0x43ce9e */
extern void audio_callback_mgr_delete_node(void *node); /* callback_mgr_delete_node 0x5100fc */

static const char s_module[] = "callback.mgr"; /* ROM 0x7856c0 */
static const char s_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\callback_mgr\\callback_manager.c"; /* ROM 0x6e26f8 */
static const char s_function[] = "CALLBACK_MGR_Deinit"; /* ROM 0x77e80c */
static const char s_deinit[] = "[%s] Callback manager deinitialized"; /* ROM 0x7526ac */
static const char s_deinit_short[] = "[callback.mgr][%s] Callback manager deinitialized"; /* ROM 0x7273a0 */

void CALLBACK_MGR_Deinit(void *manager_storage)
{
    struct callback_manager *manager = (struct callback_manager *)manager_storage;

    if (manager == 0)
        return;

    struct callback_node *node = manager->head;
    while (node != 0) {
        struct callback_node *next = node->next;
        audio_callback_mgr_delete_node(node);
        node = next;
    }
    manager->head = 0;
    manager->count = 0u;

    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, s_module, s_file, s_function, 78u, s_deinit, manager->name);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x10400000u, s_deinit_short, s_deinit_short, manager->name);
}
