/* EvenHub page input path, stock D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenHub\evenhub_ui.c.
 * Native 0x494610..0x494b38 (evenhub_inject_event_to_container, common_list_event_callback,
 * common_text_event_callback) and 0x495f9a..0x496430 (evenhub_list/text_event_inject_adapter);
 * literal pools 0x494b38..0x494bec, 0x4954c4..0x4954ec and 0x4964cc..0x49652c.
 *
 * Input from the touch bar reaches the one container bound with Is_event_capture=1 through
 * evenhub_inject_event_to_container -> adapter; the adapters forward the raw event to the phone
 * app (only on the master side). The common containers report selections back through
 * common_list/text_event_callback. */
#include "evenhub_ui_private.h"

#define EVENHUB_ROLE_SLAVE 2u
#define EVENHUB_EVENT_CLICK 10      /* list only */
#define EVENHUB_EVENT_SCROLL_UP 0x44
#define EVENHUB_EVENT_SCROLL_DOWN 0x45

static const char evenhub_ui_tag[] = "evenhub.ui"; /* ROM 0x78aa24 */
static const char evenhub_ui_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenHub\\evenhub_ui.c"; /* ROM 0x702a54 */

static const char inject_fn[] = "evenhub_inject_event_to_container"; /* ROM 0x754674 */
static const char inject_null[] = "evenhub_inject_event_to_container: manager_ctx is NULL"; /* ROM 0x71ef40 */
static const char inject_null_s[] =
    "[evenhub.ui]evenhub_inject_event_to_container: manager_ctx is NULL"; /* ROM 0x702bec */
static const char inject_unbound[] =
    "evenhub_inject_event_to_container: no event binding, event_code=%d"; /* ROM 0x702c30 */
static const char inject_unbound_s[] =
    "[evenhub.ui]evenhub_inject_event_to_container: no event binding, event_code=%d"; /* ROM 0x6ed3d8 */
static const char inject_no_cb[] = "evenhub_inject_event_to_container: callback is NULL"; /* ROM 0x7298cc */
static const char inject_no_cb_s[] =
    "[evenhub.ui]evenhub_inject_event_to_container: callback is NULL"; /* ROM 0x70b9a4 */
static const char inject_no_handle[] =
    "evenhub_inject_event_to_container: container_handle is NULL"; /* ROM 0x7152c8 */
static const char inject_no_handle_s[] =
    "[evenhub.ui]evenhub_inject_event_to_container: container_handle is NULL"; /* ROM 0x6fa88c */
static const char inject_msg[] =
    "evenhub_inject_event_to_container: injecting event_code=%d to container (id=%u, name=%s, type=%d)"; /* ROM 0x6da868 */
static const char inject_msg_s[] =
    "[evenhub.ui]evenhub_inject_event_to_container: injecting event_code=%d to container (id=%u, name=%s, type=%d)"; /* ROM 0x6d7040 */
static const char inject_ret[] = "evenhub_inject_event_to_container: callback returned %d"; /* ROM 0x71ef78 */
static const char inject_ret_s[] =
    "[evenhub.ui]evenhub_inject_event_to_container: callback returned %d"; /* ROM 0x702c74 */

static const char list_cb_fn[] = "common_list_event_callback"; /* ROM 0x76b880 */
static const char list_cb_msg[] = "common_list_event_callback: selected_index=%d, item_name=%s"; /* ROM 0x715340 */
static const char list_cb_msg_s[] =
    "[evenhub.ui]common_list_event_callback: selected_index=%d, item_name=%s"; /* ROM 0x6fa91c */
static const char list_cb_null[] = "common_list_event_callback: manager_ctx is NULL"; /* ROM 0x734124 */
static const char list_cb_null_s[] = "[evenhub.ui]common_list_event_callback: manager_ctx is NULL"; /* ROM 0x71537c */

static const char text_cb_fn[] = "common_text_event_callback"; /* ROM 0x76b89c */
static const char text_cb_msg[] = "common_text_event_callback: is_top=%d"; /* ROM 0x74a0dc */
static const char text_cb_msg_s[] = "[evenhub.ui]common_text_event_callback: is_top=%d"; /* ROM 0x729900 */
static const char text_cb_null[] = "common_text_event_callback: manager_ctx is NULL"; /* ROM 0x734154 */
static const char text_cb_null_s[] = "[evenhub.ui]common_text_event_callback: manager_ctx is NULL"; /* ROM 0x7153b8 */

static const char list_ad_fn[] = "evenhub_list_event_inject_adapter"; /* ROM 0x754704 */
static const char text_ad_fn[] = "evenhub_text_event_inject_adapter"; /* ROM 0x754728 */
/* The text adapter reuses the list adapter's messages except for the two below. */
static const char ad_slave[] = "evenhub_list_event_inject_adapter: slave role, return 0"; /* ROM 0x71f100 */
static const char ad_slave_s[] =
    "[evenhub.ui]evenhub_list_event_inject_adapter: slave role, return 0"; /* ROM 0x702ed8 */
static const char list_ad_no_handle[] = "evenhub_list_event_inject_adapter: NULL handle"; /* ROM 0x7341e4 */
static const char list_ad_no_handle_s[] =
    "[evenhub.ui]evenhub_list_event_inject_adapter: NULL handle"; /* ROM 0x71546c */
static const char ad_busy[] = "evenhub_list_event_inject_adapter: list is animating, return 0"; /* ROM 0x70bb64 */
static const char ad_busy_s[] =
    "[evenhub.ui]evenhub_list_event_inject_adapter: list is animating, return 0"; /* ROM 0x6f38a8 */
static const char ad_null[] = "evenhub_list_event_inject_adapter: manager_ctx is NULL"; /* ROM 0x71f138 */
static const char ad_null_s[] =
    "[evenhub.ui]evenhub_list_event_inject_adapter: manager_ctx is NULL"; /* ROM 0x702f1c */
static const char list_ad_unknown[] = "common_list_inject_event: unknown event type %d"; /* ROM 0x734214 */
static const char list_ad_unknown_s[] = "[evenhub.ui]common_list_inject_event: unknown event type %d"; /* ROM 0x7154a8 */
static const char ad_event[] = "evenhub_list_event_inject_adapter: event_code=%d, data=%d"; /* ROM 0x7154e4 */
static const char ad_event_s[] =
    "[evenhub.ui]evenhub_list_event_inject_adapter: event_code=%d, data=%d"; /* ROM 0x6faa84 */
static const char text_ad_no_handle[] = "evenhub_text_event_inject_adapter: NULL handle"; /* ROM 0x734244 */
static const char text_ad_no_handle_s[] =
    "[evenhub.ui]evenhub_text_event_inject_adapter: NULL handle"; /* ROM 0x715520 */
static const char text_ad_unknown[] = "common_text_inject_event: unknown event type %d"; /* ROM 0x734274 */
static const char text_ad_unknown_s[] = "[evenhub.ui]common_text_inject_event: unknown event type %d"; /* ROM 0x71555c */

/* LVGL event: +0x10 param -> {lo, hi} payload words (lv_event_get_param inlined in stock). */
#define EVENHUB_EVENT_PAYLOAD(e)                                                              \
    ((*(const uint32_t *const *)((const uint8_t *)(e) + 0x10))[0] |                           \
     ((*(const uint32_t *const *)((const uint8_t *)(e) + 0x10))[1] << 16))

int32_t evenhub_inject_event_to_container_494610(evenhub_manager_t *mgr, int32_t event_code,
                                                 void *data)
{
    int32_t ret;

    if (mgr == NULL) {
        EH_LOG(1, inject_fn, 0x2bb, 0x4000000u, inject_null, inject_null_s);
        return -1;
    }
    if (mgr->bound == 0u) {
        EH_LOG(4, inject_fn, 0x2c1, 0x10400000u, inject_unbound, inject_unbound_s, event_code);
        return -1;
    }
    if (mgr->bound_cb == NULL) {
        EH_LOG(1, inject_fn, 0x2c7, 0x4000000u, inject_no_cb, inject_no_cb_s);
        return -1;
    }
    if (mgr->bound_handle == NULL) {
        EH_LOG(1, inject_fn, 0x2cd, 0x4000000u, inject_no_handle, inject_no_handle_s);
        return -1;
    }
    EH_LOG(4, inject_fn, 0x2d5, 0x11000000u, inject_msg, inject_msg_s, event_code, mgr->bound_id,
           mgr->bound_name, mgr->bound_type);
    ret = mgr->bound_cb(mgr->bound_handle, event_code, data, mgr->bound_user);
    if (ret != 0)
        EH_LOG(4, inject_fn, 0x2e0, 0x10400000u, inject_ret, inject_ret_s, ret);
    return ret;
}

/* List selection -> phone app event type 1 (index of the selected item). */
int32_t common_list_event_callback_4949c0(int32_t selected_index, const char *item_name,
                                          evenhub_manager_t *mgr)
{
    EH_LOG(4, list_cb_fn, 0x312, 0x10800000u, list_cb_msg, list_cb_msg_s, selected_index, item_name);
    if (mgr == NULL) {
        EH_LOG(1, list_cb_fn, 0x315, 0x4000000u, list_cb_null, list_cb_null_s);
        return -1;
    }
    (void)evenhub_send_container_event_4da16a(1u, mgr->bound_id, mgr->bound_name, 0u,
                                              selected_index, 0);
    return 0;
}

/* Text scrolled to an edge -> phone app event type 2 (1 = top, 2 = bottom). */
int32_t common_text_event_callback_494a78(uint8_t is_top, evenhub_manager_t *mgr)
{
    EH_LOG(4, text_cb_fn, 0x31e, 0x10400000u, text_cb_msg, text_cb_msg_s, is_top);
    if (mgr == NULL) {
        EH_LOG(1, text_cb_fn, 0x321, 0x4000000u, text_cb_null, text_cb_null_s);
        return -1;
    }
    (void)evenhub_send_container_event_4da16a(2u, mgr->bound_id, mgr->bound_name,
                                              (is_top != 0u) ? 1u : 2u, 0, 0);
    return 0;
}

/* Returns 0 when handled or ignored, -1 on bad arguments, 1 for an unknown event. */
int32_t evenhub_list_event_inject_adapter_495f9a(void *handle, int32_t event_code, void *data,
                                                 void *user)
{
    evenhub_manager_t *mgr = (evenhub_manager_t *)user;
    uint32_t payload;

    if (audio_uart_service_mode() == EVENHUB_ROLE_SLAVE) {
        EH_LOG(4, list_ad_fn, 0x527, 0x10000000u, ad_slave, ad_slave_s);
        return 0;
    }
    if (handle == NULL) {
        EH_LOG(1, list_ad_fn, 0x52d, 0x4000000u, list_ad_no_handle, list_ad_no_handle_s);
        return -1;
    }
    if (*((const uint8_t *)handle + 0x57c) == 1u) { /* list scroll animation running */
        EH_LOG(4, list_ad_fn, 0x532, 0x10000000u, ad_busy, ad_busy_s);
        return 0;
    }
    if (mgr == NULL) {
        EH_LOG(1, list_ad_fn, 0x538, 0x4000000u, ad_null, ad_null_s);
        return -1;
    }
    if (event_code != EVENHUB_EVENT_SCROLL_UP && event_code != EVENHUB_EVENT_SCROLL_DOWN &&
        event_code != EVENHUB_EVENT_CLICK) {
        EH_LOG(2, list_ad_fn, 0x53d, 0x8400000u, list_ad_unknown, list_ad_unknown_s, event_code);
        return 1;
    }
    payload = EVENHUB_EVENT_PAYLOAD(data);
    (void)evenhub_send_input_event_4da382(mgr->bound_id, mgr->bound_name, event_code, payload);
    EH_LOG(4, list_ad_fn, 0x547, 0x10800000u, ad_event, ad_event_s, event_code, payload);
    return 0;
}

int32_t evenhub_text_event_inject_adapter_4961e4(void *handle, int32_t event_code, void *data,
                                                 void *user)
{
    evenhub_manager_t *mgr = (evenhub_manager_t *)user;
    uint32_t payload;

    if (audio_uart_service_mode() == EVENHUB_ROLE_SLAVE) {
        EH_LOG(4, text_ad_fn, 0x555, 0x10000000u, ad_slave, ad_slave_s);
        return 0;
    }
    if (handle == NULL) {
        EH_LOG(1, text_ad_fn, 0x55b, 0x4000000u, text_ad_no_handle, text_ad_no_handle_s);
        return -1;
    }
    if (*((const uint8_t *)handle + 0x13) == 1u) { /* text scroll animation running */
        EH_LOG(4, text_ad_fn, 0x560, 0x10000000u, ad_busy, ad_busy_s);
        return 0;
    }
    if (mgr == NULL) {
        EH_LOG(1, text_ad_fn, 0x567, 0x4000000u, ad_null, ad_null_s);
        return -1;
    }
    if (event_code != EVENHUB_EVENT_SCROLL_UP && event_code != EVENHUB_EVENT_SCROLL_DOWN) {
        EH_LOG(4, text_ad_fn, 0x56d, 0x10400000u, text_ad_unknown, text_ad_unknown_s, event_code);
        return 1;
    }
    payload = EVENHUB_EVENT_PAYLOAD(data);
    (void)evenhub_send_input_event_4da382(mgr->bound_id, mgr->bound_name, event_code, payload);
    EH_LOG(4, text_ad_fn, 0x576, 0x10800000u, ad_event, ad_event_s, event_code, payload);
    return 0;
}
