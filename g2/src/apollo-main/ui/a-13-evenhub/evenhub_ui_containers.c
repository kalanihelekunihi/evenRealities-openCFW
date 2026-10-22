/* EvenHub page container list, stock D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenHub\evenhub_ui.c
 * (log tag "evenhub.ui"). Native 0x4935cc..0x4945df (literal pools 0x494028..0x4940e7,
 * 0x494280..0x4942a3, 0x494450..0x494483, 0x4945e0..0x49460f, 0x494828..0x494833,
 * 0x4949b0..0x4949bf, 0x494a74, 0x494b3c..0x494ba3).
 * The page half of the same stock file (0x494610..0x49718c) is ui/a-14-evenhub-ui; the names
 * and record layouts here match its evenhub_ui_private.h declarations.
 *
 * The page keeps a doubly linked list of containers built from the decoded EvenHub protobuf
 * message: up to 4 list, 8 text and 4 image containers (16 in total). When every container
 * carries a z-order index the list is ordered by it (stable insertion sort), otherwise the
 * legacy list/text/image order is kept. Each node owns a heap copy of its protobuf record. */
#include <stdint.h>
#include <stddef.h>

#define EVENHUB_CONTAINER_LIST 0u
#define EVENHUB_CONTAINER_TEXT 1u
#define EVENHUB_CONTAINER_IMAGE 2u
#define EVENHUB_MAX_CONTAINERS 16u

/* Decoded EvenHub message (0x3758 bytes): container arrays used by the list builder. */
#define EVENHUB_PB_LIST_COUNT 0x0004u  /* uint16_t */
#define EVENHUB_PB_LISTS 0x0008u       /* 4 x 0x554 */
#define EVENHUB_PB_TEXT_COUNT 0x1558u  /* uint16_t */
#define EVENHUB_PB_TEXTS 0x155cu       /* 8 x 0x428 */
#define EVENHUB_PB_IMAGE_COUNT 0x369cu /* uint16_t */
#define EVENHUB_PB_IMAGES 0x36a0u      /* 4 x 0x2c */

/* Container protobuf records: size, has-z-order flag and z-order index offsets. */
#define EVENHUB_PB_LIST_SIZE 0x554u
#define EVENHUB_PB_LIST_HAS_Z 0x54cu
#define EVENHUB_PB_LIST_Z 0x550u
#define EVENHUB_PB_TEXT_SIZE 0x428u
#define EVENHUB_PB_TEXT_HAS_Z 0x420u
#define EVENHUB_PB_TEXT_Z 0x424u
#define EVENHUB_PB_IMAGE_SIZE 0x2cu
#define EVENHUB_PB_IMAGE_HAS_Z 0x24u
#define EVENHUB_PB_IMAGE_Z 0x28u

/* Common geometry head of the list/text records ({x, y, width, height}, ..., id at +0x20,
 * name at +0x24); image records keep id at +0x10 and name at +0x14. */
typedef struct {
    uint32_t x, y, width, height; /* +0x00 */
    uint32_t border[4];           /* +0x10 */
    uint32_t id;                  /* +0x20 */
    char name[16];                /* +0x24 */
} evenhub_pb_box_t;

typedef struct {
    uint32_t x, y, width, height; /* +0x00 */
    uint32_t id;                  /* +0x10 */
    char name[16];                /* +0x14 */
} evenhub_pb_image_head_t;

typedef struct evenhub_container_node {
    struct evenhub_container_node *prev; /* +0x00 */
    struct evenhub_container_node *next; /* +0x04 */
    uint8_t type;                        /* +0x08 EVENHUB_CONTAINER_* */
    uint8_t reserved[3];
    void *pb;                            /* +0x0c heap copy of the protobuf record */
    void *ui;                            /* +0x10 common list/text/image container handle */
} evenhub_container_node_t;
_Static_assert(sizeof(evenhub_container_node_t) == 0x14u, "container node");

typedef int32_t (*evenhub_inject_cb_t)(void *handle, int32_t event_code, void *data, void *user);

typedef struct {
    void *parent;                   /* +0x00 lv_obj_t * page root */
    evenhub_container_node_t *head; /* +0x04 */
    evenhub_container_node_t *tail; /* +0x08 */
    uint32_t count;                 /* +0x0c */
    void *bound_handle;             /* +0x10 event-capturing container */
    evenhub_inject_cb_t bound_cb;   /* +0x14 */
    void *bound_user;               /* +0x18 */
    uint32_t bound_id;              /* +0x1c */
    char bound_name[16];            /* +0x20 */
    uint8_t bound_type;             /* +0x30 */
    uint8_t reserved_31[3];
    uint8_t bound;                  /* +0x34 */
    uint8_t timeout_page;           /* +0x35 */
} evenhub_manager_t;
_Static_assert(offsetof(evenhub_manager_t, bound_handle) == 0x10u, "evenhub manager");
_Static_assert(offsetof(evenhub_manager_t, bound) == 0x34u, "evenhub manager");

/* One pending container while the list is assembled (16 bytes, copied with memcpy4). */
typedef struct {
    uint8_t type;        /* +0x0 */
    uint8_t reserved[3];
    const uint8_t *src;  /* +0x4 */
    uint32_t size;       /* +0x8 */
    uint32_t z_order;    /* +0xc */
} evenhub_build_entry_t;
_Static_assert(sizeof(evenhub_build_entry_t) == 16u, "build entry");

extern uint32_t g2_evenhub_startup_widget_id; /* RAM 0x200745cc */

extern void audio_uart_page_44120e(void *obj, int32_t value, uint32_t selector); /* style pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t value, uint32_t selector); /* style pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t value, uint32_t selector); /* style pad_left */
extern void audio_uart_page_441238(void *obj, int32_t value, uint32_t selector); /* style pad_right */
extern void *file_heap_allocate(uint32_t size);                                   /* 0x474cd2 */
extern void file_heap_free(void *buffer);                                         /* 0x474d16 */
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);              /* memcpy 0x439be4 */
extern void *aeabi_memcpy4_439c04(void *dst, const void *src, uint32_t len);
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* strncpy 0x44b5a0 */
extern void common_list_destroy_4de17c(void *handle);
extern void common_text_destroy_4df6ee(void *handle);
extern void common_image_destroy_4dca3c(void *handle);
extern uint32_t audio_log_flags(void);                                                /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);       /* 0x43ce9e */

void evenhub_obj_set_style_pad_all_4935cc(void *obj, int32_t value, uint32_t selector);
uint32_t evenhub_main_widget_id_4935fe(void);
evenhub_container_node_t *evenhub_create_container_node_493606(uint8_t type, const void *src, uint32_t size);
int32_t evenhub_build_container_list_493722(evenhub_manager_t *mgr, const uint8_t *lists, uint32_t list_count,
                                            const uint8_t *texts, uint32_t text_count,
                                            const uint8_t *images, uint32_t image_count);
int32_t evenhub_container_list_rebuild_from_pb_493ab6(evenhub_manager_t *mgr, const void *pb);
int32_t evenhub_container_list_create_from_pb_493bdc(evenhub_manager_t *mgr, const void *pb);
void evenhub_container_list_destroy_493d02(evenhub_manager_t *mgr);
int32_t evenhub_container_list_traverse_493ee6(evenhub_manager_t *mgr,
                                               int32_t (*cb)(evenhub_container_node_t *, void *), void *arg);
evenhub_container_node_t *evenhub_container_list_find_by_id_493fa8(evenhub_manager_t *mgr, uint32_t id);
int32_t evenhub_container_list_append_494030(evenhub_manager_t *mgr, evenhub_container_node_t *node);
int32_t evenhub_print_container_info_callback_4940e8(evenhub_container_node_t *node, void *arg);
int32_t evenhub_bind_event_container_4942a4(evenhub_manager_t *mgr, void *handle, evenhub_inject_cb_t cb,
                                            uint32_t id, const char *name, uint8_t type, void *user);
void evenhub_unbind_event_container_494484(evenhub_manager_t *mgr);

static const char evenhub_ui_tag[] = "evenhub.ui"; /* ROM 0x78aa24 */
static const char evenhub_ui_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenHub\\evenhub_ui.c"; /* ROM 0x702a54 */

static const char create_fn[] = "evenhub_create_container_node"; /* ROM 0x75ff90 */
static const char create_invalid[] = "evenhub_create_container_node: invalid parameters"; /* ROM 0x729794 */
static const char create_invalid_s[] =
    "[evenhub.ui]evenhub_create_container_node: invalid parameters"; /* ROM 0x70b764 */
static const char create_nodata[] = "evenhub_create_container_node: malloc private_data failed"; /* ROM 0x715124 */
static const char create_nodata_s[] =
    "[evenhub.ui]evenhub_create_container_node: malloc private_data failed"; /* ROM 0x6fa52c */
static const char create_nonode[] = "evenhub_create_container_node: malloc node failed"; /* ROM 0x7297c8 */
static const char create_nonode_s[] =
    "[evenhub.ui]evenhub_create_container_node: malloc node failed"; /* ROM 0x70b7a4 */

static const char build_fn[] = "evenhub_build_container_list"; /* ROM 0x75ffb0 */
static const char build_sorted[] =
    "evenhub: z-order enabled, sort %u containers ascending by z_order_index"; /* ROM 0x6fa574 */
static const char build_sorted_s[] =
    "[evenhub.ui]evenhub: z-order enabled, sort %u containers ascending by z_order_index"; /* ROM 0x6e7d14 */
static const char build_legacy[] =
    "evenhub: z-order disabled (all_have_z=%d, total=%u), use legacy order"; /* ROM 0x6fa5bc */
static const char build_legacy_s[] =
    "[evenhub.ui]evenhub: z-order disabled (all_have_z=%d, total=%u), use legacy order"; /* ROM 0x6e7d68 */
static const char build_created[] =
    "evenhub_build_container_list: node[%u] type=%d z_order=%u created"; /* ROM 0x702b20 */
static const char build_created_s[] =
    "[evenhub.ui]evenhub_build_container_list: node[%u] type=%d z_order=%u created"; /* ROM 0x6ed248 */
static const char build_create_failed[] = "evenhub_build_container_list: create node[%u] failed"; /* ROM 0x71ee98 */
static const char build_create_failed_s[] =
    "[evenhub.ui]evenhub_build_container_list: create node[%u] failed"; /* ROM 0x702a98 */
static const char build_append_failed[] = "evenhub_build_container_list: append node[%u] failed"; /* ROM 0x71eed0 */
static const char build_append_failed_s[] =
    "[evenhub.ui]evenhub_build_container_list: append node[%u] failed"; /* ROM 0x702adc */

static const char rebuild_fn[] = "evenhub_container_list_rebuild_from_pb"; /* ROM 0x74a064 */
static const char rebuild_invalid[] = "evenhub_container_list_rebuild_from_pb: invalid parameters"; /* ROM 0x715160 */
static const char rebuild_invalid_s[] =
    "[evenhub.ui]evenhub_container_list_rebuild_from_pb: invalid parameters"; /* ROM 0x6fa604 */
static const char rebuild_failed[] =
    "evenhub_container_list_rebuild_from_pb: build failed, cleanup all created nodes"; /* ROM 0x6ed298 */
static const char rebuild_failed_s[] =
    "[evenhub.ui]evenhub_container_list_rebuild_from_pb: build failed, cleanup all created nodes"; /* ROM 0x6e0404 */
static const char rebuild_ok[] = "evenhub_container_list_rebuild_from_pb: success, total %d containers"; /* ROM 0x6fa64c */
static const char rebuild_ok_s[] =
    "[evenhub.ui]evenhub_container_list_rebuild_from_pb: success, total %d containers"; /* ROM 0x6e7dbc */

static const char cfp_fn[] = "evenhub_container_list_create_from_pb"; /* ROM 0x74a08c */
static const char cfp_invalid[] = "evenhub_container_list_create_from_pb: invalid parameters"; /* ROM 0x71519c */
static const char cfp_invalid_s[] =
    "[evenhub.ui]evenhub_container_list_create_from_pb: invalid parameters"; /* ROM 0x6fa694 */
static const char cfp_failed[] =
    "evenhub_container_list_create_from_pb: build failed, cleanup all created nodes"; /* ROM 0x6ed2e8 */
static const char cfp_failed_s[] =
    "[evenhub.ui]evenhub_container_list_create_from_pb: build failed, cleanup all created nodes"; /* ROM 0x6e0460 */
static const char cfp_ok[] = "evenhub_container_list_create_from_pb: success, total %d containers"; /* ROM 0x702b64 */
static const char cfp_ok_s[] =
    "[evenhub.ui]evenhub_container_list_create_from_pb: success, total %d containers"; /* ROM 0x6ed338 */

static const char destroy_fn[] = "evenhub_container_list_destroy"; /* ROM 0x75ffd0 */
static const char destroy_list[] = "evenhub_container_list_destroy: destroying List UI handle=%p"; /* ROM 0x70b7e4 */
static const char destroy_list_s[] =
    "[evenhub.ui]evenhub_container_list_destroy: destroying List UI handle=%p"; /* ROM 0x6f3648 */
static const char destroy_text[] = "evenhub_container_list_destroy: destroying Text UI handle=%p"; /* ROM 0x70b824 */
static const char destroy_text_s[] =
    "[evenhub.ui]evenhub_container_list_destroy: destroying Text UI handle=%p"; /* ROM 0x6f3694 */
static const char destroy_image[] = "evenhub_container_list_destroy: destroying Image UI handle=%p"; /* ROM 0x70b864 */
static const char destroy_image_s[] =
    "[evenhub.ui]evenhub_container_list_destroy: destroying Image UI handle=%p"; /* ROM 0x6f36e0 */
static const char destroy_unknown[] = "evenhub_container_list_destroy: unknown container type %d"; /* ROM 0x7151d8 */
static const char destroy_unknown_s[] =
    "[evenhub.ui]evenhub_container_list_destroy: unknown container type %d"; /* ROM 0x6fa6dc */
static const char destroy_done[] =
    "evenhub_container_list_destroy: all nodes destroyed (UI handles: %d)"; /* ROM 0x6fa724 */
static const char destroy_done_s[] =
    "[evenhub.ui]evenhub_container_list_destroy: all nodes destroyed (UI handles: %d)"; /* ROM 0x6e7e10 */

static const char traverse_fn[] = "evenhub_container_list_traverse"; /* ROM 0x75fff0 */
static const char traverse_invalid[] = "evenhub_container_list_traverse: invalid parameters"; /* ROM 0x7297fc */
static const char traverse_invalid_s[] =
    "[evenhub.ui]evenhub_container_list_traverse: invalid parameters"; /* ROM 0x70b8a4 */
static const char traverse_stop[] =
    "evenhub_container_list_traverse: callback returned %d, stop traversing"; /* ROM 0x6fa76c */
static const char traverse_stop_s[] =
    "[evenhub.ui]evenhub_container_list_traverse: callback returned %d, stop traversing"; /* ROM 0x6e7e64 */

static const char find_fn[] = "evenhub_container_list_find_by_id"; /* ROM 0x754650 */
static const char find_invalid[] = "evenhub_container_list_find_by_id: invalid parameters"; /* ROM 0x71ef08 */
static const char find_invalid_s[] =
    "[evenhub.ui]evenhub_container_list_find_by_id: invalid parameters"; /* ROM 0x702ba8 */

static const char append_fn[] = "evenhub_container_list_append"; /* ROM 0x760010 */
static const char append_invalid[] = "evenhub_container_list_append: invalid parameters"; /* ROM 0x729830 */
static const char append_invalid_s[] =
    "[evenhub.ui]evenhub_container_list_append: invalid parameters"; /* ROM 0x70b8e4 */

static const char print_fn[] = "evenhub_print_container_info_callback"; /* ROM 0x74a0b4 */
static const char print_info[] =
    "  - Type: %s, ID: %d, Name: %s, Pos: (%d,%d), Size: (%dx%d)"; /* ROM 0x715214 */
static const char print_info_s[] =
    "[evenhub.ui]  - Type: %s, ID: %d, Name: %s, Pos: (%d,%d), Size: (%dx%d)"; /* ROM 0x6fa7b4 */
static const char type_list[] = "LIST";   /* ROM 0x78d5c4 */
static const char type_text[] = "TEXT";   /* ROM 0x78d5cc */
static const char type_image[] = "IMAGE"; /* ROM 0x78d5d4 */

static const char bind_fn[] = "evenhub_bind_event_container"; /* ROM 0x760030 */
static const char bind_nomgr[] = "evenhub_bind_event_container: manager_ctx is NULL"; /* ROM 0x729864 */
static const char bind_nomgr_s[] = "[evenhub.ui]evenhub_bind_event_container: manager_ctx is NULL"; /* ROM 0x70b924 */
static const char bind_invalid[] =
    "evenhub_bind_event_container: invalid parameters (handle=%p, callback=%p)"; /* ROM 0x6f372c */
static const char bind_invalid_s[] =
    "[evenhub.ui]evenhub_bind_event_container: invalid parameters (handle=%p, callback=%p)"; /* ROM 0x6e3460 */
static const char bind_busy[] =
    "evenhub_bind_event_container: already has event binding (container_id=%u, name=%s)"; /* ROM 0x6e7eb8 */
static const char bind_busy_s[] =
    "[evenhub.ui]evenhub_bind_event_container: already has event binding (container_id=%u, name=%s)"; /* ROM 0x6dd3b4 */
static const char bind_ok[] =
    "evenhub_bind_event_container: bound container (id=%u, name=%s, type=%d)"; /* ROM 0x6fa7fc */
static const char bind_ok_s[] =
    "[evenhub.ui]evenhub_bind_event_container: bound container (id=%u, name=%s, type=%d)"; /* ROM 0x6e7f0c */

static const char unbind_fn[] = "evenhub_unbind_event_container"; /* ROM 0x760050 */
static const char unbind_nomgr[] = "evenhub_unbind_event_container: manager_ctx is NULL"; /* ROM 0x729898 */
static const char unbind_nomgr_s[] =
    "[evenhub.ui]evenhub_unbind_event_container: manager_ctx is NULL"; /* ROM 0x70b964 */
static const char unbind_none[] = "evenhub_unbind_event_container: no event binding to unbind"; /* ROM 0x715250 */
static const char unbind_none_s[] =
    "[evenhub.ui]evenhub_unbind_event_container: no event binding to unbind"; /* ROM 0x6fa844 */
static const char unbind_start[] =
    "evenhub_unbind_event_container: unbinding container (id=%u, name=%s, type=%d)"; /* ROM 0x6ed388 */
static const char unbind_start_s[] =
    "[evenhub.ui]evenhub_unbind_event_container: unbinding container (id=%u, name=%s, type=%d)"; /* ROM 0x6e04bc */
static const char unbind_done[] = "evenhub_unbind_event_container: unbind complete"; /* ROM 0x7340c4 */
static const char unbind_done_s[] = "[evenhub.ui]evenhub_unbind_event_container: unbind complete"; /* ROM 0x71528c */

/* Both sinks are tested separately and every argument is evaluated per sink, as in stock. */
#define EH_LOG(level, func, line, cflags, text, short_text, ...)                              \
    do {                                                                                      \
        if ((audio_log_flags() & 2u) != 0u)                                                   \
            audio_log_extended((level), evenhub_ui_tag, evenhub_ui_file, (func), (line),      \
                               (text), ##__VA_ARGS__);                                        \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                 \
            (void)compress_log_output((cflags), (short_text), (short_text), ##__VA_ARGS__);   \
    } while (0)

/* Out-of-line instance of LVGL's static inline lv_obj_set_style_pad_all in this TU. */
void evenhub_obj_set_style_pad_all_4935cc(void *obj, int32_t value, uint32_t selector)
{
    audio_uart_page_44122a(obj, value, selector);
    audio_uart_page_441238(obj, value, selector);
    audio_uart_page_44120e(obj, value, selector);
    audio_uart_page_44121c(obj, value, selector);
}

uint32_t evenhub_main_widget_id_4935fe(void)
{
    return g2_evenhub_startup_widget_id;
}

/* Copy the protobuf record to the heap and wrap it in an unlinked node. */
evenhub_container_node_t *evenhub_create_container_node_493606(uint8_t type, const void *src, uint32_t size)
{
    if (src == NULL || size == 0u) {
        EH_LOG(1u, create_fn, 0x49u, 0x04000000u, create_invalid, create_invalid_s);
        return NULL;
    }
    void *data = file_heap_allocate(size);
    if (data == NULL) {
        EH_LOG(1u, create_fn, 0x50u, 0x04000000u, create_nodata, create_nodata_s);
        return NULL;
    }
    (void)audio_queue_copy_bytes(data, src, size);
    evenhub_container_node_t *node = file_heap_allocate(sizeof(*node));
    if (node == NULL) {
        EH_LOG(1u, create_fn, 0x5au, 0x04000000u, create_nonode, create_nonode_s);
        file_heap_free(data);
        return NULL;
    }
    node->type = type;
    node->pb = data;
    node->prev = NULL;
    node->next = NULL;
    return node;
}

int32_t evenhub_build_container_list_493722(evenhub_manager_t *mgr, const uint8_t *lists, uint32_t list_count,
                                            const uint8_t *texts, uint32_t text_count,
                                            const uint8_t *images, uint32_t image_count)
{
    evenhub_build_entry_t key;
    evenhub_build_entry_t entries[EVENHUB_MAX_CONTAINERS];
    uint32_t total = 0u;
    uint8_t all_have_z = 1u;
    uint32_t i;

    for (i = 0u; i < list_count && total < EVENHUB_MAX_CONTAINERS; i++, total++) {
        const uint8_t *rec = lists + i * EVENHUB_PB_LIST_SIZE;
        entries[total].type = EVENHUB_CONTAINER_LIST;
        entries[total].src = rec;
        entries[total].size = EVENHUB_PB_LIST_SIZE;
        entries[total].z_order = *(const uint32_t *)(const void *)(rec + EVENHUB_PB_LIST_Z);
        if (rec[EVENHUB_PB_LIST_HAS_Z] == 0u)
            all_have_z = 0u;
    }
    for (i = 0u; i < text_count && total < EVENHUB_MAX_CONTAINERS; i++, total++) {
        const uint8_t *rec = texts + i * EVENHUB_PB_TEXT_SIZE;
        entries[total].type = EVENHUB_CONTAINER_TEXT;
        entries[total].src = rec;
        entries[total].size = EVENHUB_PB_TEXT_SIZE;
        entries[total].z_order = *(const uint32_t *)(const void *)(rec + EVENHUB_PB_TEXT_Z);
        if (rec[EVENHUB_PB_TEXT_HAS_Z] == 0u)
            all_have_z = 0u;
    }
    for (i = 0u; i < image_count && total < EVENHUB_MAX_CONTAINERS; i++, total++) {
        const uint8_t *rec = images + i * EVENHUB_PB_IMAGE_SIZE;
        entries[total].type = EVENHUB_CONTAINER_IMAGE;
        entries[total].src = rec;
        entries[total].size = EVENHUB_PB_IMAGE_SIZE;
        entries[total].z_order = *(const uint32_t *)(const void *)(rec + EVENHUB_PB_IMAGE_Z);
        if (rec[EVENHUB_PB_IMAGE_HAS_Z] == 0u)
            all_have_z = 0u;
    }

    if (all_have_z != 0u && total >= 2u) {
        EH_LOG(3u, build_fn, 0xa4u, 0x0c400000u, build_sorted, build_sorted_s, total);
        /* Stable insertion sort, ascending z_order. */
        for (i = 1u; i < total; i++) {
            int32_t j;
            (void)aeabi_memcpy4_439c04(&key, &entries[i], sizeof(key));
            for (j = (int32_t)i - 1; j >= 0 && key.z_order < entries[j].z_order; j--)
                (void)aeabi_memcpy4_439c04(&entries[j + 1], &entries[j], sizeof(key));
            (void)aeabi_memcpy4_439c04(&entries[j + 1], &key, sizeof(key));
        }
    } else {
        EH_LOG(3u, build_fn, 0xb0u, 0x0c800000u, build_legacy, build_legacy_s, all_have_z, total);
    }

    for (i = 0u; i < total; i++) {
        evenhub_container_node_t *node =
            evenhub_create_container_node_493606(entries[i].type, entries[i].src, entries[i].size);
        if (node == NULL) {
            EH_LOG(1u, build_fn, 0xb8u, 0x04400000u, build_create_failed, build_create_failed_s, i);
            return -1;
        }
        if (evenhub_container_list_append_494030(mgr, node) != 0) {
            EH_LOG(1u, build_fn, 0xbcu, 0x04400000u, build_append_failed, build_append_failed_s, i);
            file_heap_free(node->pb);
            file_heap_free(node);
            return -1;
        }
        EH_LOG(4u, build_fn, 0xc2u, 0x10c00000u, build_created, build_created_s, i, entries[i].type,
               entries[i].z_order);
    }
    return 0;
}

static int32_t build_from_pb(evenhub_manager_t *mgr, const uint8_t *pb)
{
    return evenhub_build_container_list_493722(
        mgr, pb + EVENHUB_PB_LISTS, *(const uint16_t *)(const void *)(pb + EVENHUB_PB_LIST_COUNT),
        pb + EVENHUB_PB_TEXTS, *(const uint16_t *)(const void *)(pb + EVENHUB_PB_TEXT_COUNT),
        pb + EVENHUB_PB_IMAGES, *(const uint16_t *)(const void *)(pb + EVENHUB_PB_IMAGE_COUNT));
}

int32_t evenhub_container_list_rebuild_from_pb_493ab6(evenhub_manager_t *mgr, const void *pb)
{
    if (mgr == NULL || pb == NULL) {
        EH_LOG(1u, rebuild_fn, 0xcbu, 0x04000000u, rebuild_invalid, rebuild_invalid_s);
        return -1;
    }
    evenhub_container_list_destroy_493d02(mgr);
    if (build_from_pb(mgr, pb) != 0) {
        EH_LOG(1u, rebuild_fn, 0xd6u, 0x04000000u, rebuild_failed, rebuild_failed_s);
        evenhub_container_list_destroy_493d02(mgr);
        return -1;
    }
    EH_LOG(3u, rebuild_fn, 0xdbu, 0x0c400000u, rebuild_ok, rebuild_ok_s, mgr->count);
    return 0;
}

int32_t evenhub_container_list_create_from_pb_493bdc(evenhub_manager_t *mgr, const void *pb)
{
    if (mgr == NULL || pb == NULL) {
        EH_LOG(1u, cfp_fn, 0xe7u, 0x04000000u, cfp_invalid, cfp_invalid_s);
        return -1;
    }
    evenhub_container_list_destroy_493d02(mgr);
    if (build_from_pb(mgr, pb) != 0) {
        EH_LOG(1u, cfp_fn, 0xf2u, 0x04000000u, cfp_failed, cfp_failed_s);
        evenhub_container_list_destroy_493d02(mgr);
        return -1;
    }
    EH_LOG(3u, cfp_fn, 0xf7u, 0x0c400000u, cfp_ok, cfp_ok_s, mgr->count);
    return 0;
}

/* Destroy each node's UI handle (by container type), its protobuf copy and the node. */
void evenhub_container_list_destroy_493d02(evenhub_manager_t *mgr)
{
    if (mgr == NULL)
        return;
    int32_t destroyed = 0;
    evenhub_container_node_t *node = mgr->head;
    while (node != NULL) {
        evenhub_container_node_t *next = node->next;
        if (node->ui != NULL) {
            switch (node->type) {
            case EVENHUB_CONTAINER_LIST:
                EH_LOG(4u, destroy_fn, 0x10eu, 0x10400000u, destroy_list, destroy_list_s, node->ui);
                common_list_destroy_4de17c(node->ui);
                destroyed++;
                break;
            case EVENHUB_CONTAINER_TEXT:
                EH_LOG(4u, destroy_fn, 0x113u, 0x10400000u, destroy_text, destroy_text_s, node->ui);
                common_text_destroy_4df6ee(node->ui);
                destroyed++;
                break;
            case EVENHUB_CONTAINER_IMAGE:
                EH_LOG(4u, destroy_fn, 0x118u, 0x10400000u, destroy_image, destroy_image_s, node->ui);
                common_image_destroy_4dca3c(node->ui);
                destroyed++;
                break;
            default:
                EH_LOG(2u, destroy_fn, 0x11du, 0x08400000u, destroy_unknown, destroy_unknown_s, node->type);
                break;
            }
            node->ui = NULL;
        }
        if (node->pb != NULL) {
            file_heap_free(node->pb);
            node->pb = NULL;
        }
        file_heap_free(node);
        node = next;
    }
    mgr->head = NULL;
    mgr->tail = NULL;
    mgr->count = 0u;
    EH_LOG(4u, destroy_fn, 0x132u, 0x10400000u, destroy_done, destroy_done_s, destroyed);
}

/* Returns the number of nodes visited before the callback asked to stop (or all), -1 on bad args. */
int32_t evenhub_container_list_traverse_493ee6(evenhub_manager_t *mgr,
                                               int32_t (*cb)(evenhub_container_node_t *, void *), void *arg)
{
    if (mgr == NULL || cb == NULL) {
        EH_LOG(1u, traverse_fn, 0x13cu, 0x04000000u, traverse_invalid, traverse_invalid_s);
        return -1;
    }
    int32_t visited = 0;
    for (evenhub_container_node_t *node = mgr->head; node != NULL; node = node->next) {
        int32_t ret = cb(node, arg);
        if (ret != 0) {
            EH_LOG(4u, traverse_fn, 0x146u, 0x10400000u, traverse_stop, traverse_stop_s, ret);
            return visited;
        }
        visited++;
    }
    return visited;
}

evenhub_container_node_t *evenhub_container_list_find_by_id_493fa8(evenhub_manager_t *mgr, uint32_t id)
{
    if (mgr == NULL) {
        EH_LOG(1u, find_fn, 0x156u, 0x04000000u, find_invalid, find_invalid_s);
        return NULL;
    }
    for (evenhub_container_node_t *node = mgr->head; node != NULL; node = node->next) {
        uint32_t node_id = 0u;
        switch (node->type) {
        case EVENHUB_CONTAINER_LIST:
            node_id = ((const evenhub_pb_box_t *)node->pb)->id;
            break;
        case EVENHUB_CONTAINER_TEXT:
            node_id = ((const evenhub_pb_box_t *)node->pb)->id;
            break;
        case EVENHUB_CONTAINER_IMAGE:
            node_id = ((const evenhub_pb_image_head_t *)node->pb)->id;
            break;
        default:
            break;
        }
        if (node_id == id)
            return node;
    }
    return NULL;
}

int32_t evenhub_container_list_append_494030(evenhub_manager_t *mgr, evenhub_container_node_t *node)
{
    if (mgr == NULL || node == NULL) {
        EH_LOG(1u, append_fn, 0x1a6u, 0x04000000u, append_invalid, append_invalid_s);
        return -1;
    }
    node->prev = NULL;
    node->next = NULL;
    if (mgr->head == NULL) {
        mgr->head = node;
        mgr->tail = node;
    } else {
        node->prev = mgr->tail;
        mgr->tail->next = node;
        mgr->tail = node;
    }
    mgr->count++;
    return 0;
}

/* evenhub_container_list_traverse callback: log one container's geometry. */
int32_t evenhub_print_container_info_callback_4940e8(evenhub_container_node_t *node, void *arg)
{
    (void)arg;
    if (node == NULL)
        return -1;
    switch (node->type) {
    case EVENHUB_CONTAINER_LIST: {
        const evenhub_pb_box_t *pb = node->pb;
        EH_LOG(4u, print_fn, 0x233u, 0x11c00000u, print_info, print_info_s, type_list, pb->id, pb->name, pb->x,
               pb->y, pb->width, pb->height);
        break;
    }
    case EVENHUB_CONTAINER_TEXT: {
        const evenhub_pb_box_t *pb = node->pb;
        EH_LOG(4u, print_fn, 0x23eu, 0x11c00000u, print_info, print_info_s, type_text, pb->id, pb->name, pb->x,
               pb->y, pb->width, pb->height);
        break;
    }
    case EVENHUB_CONTAINER_IMAGE: {
        const evenhub_pb_image_head_t *pb = node->pb;
        EH_LOG(4u, print_fn, 0x249u, 0x11c00000u, print_info, print_info_s, type_image, pb->id, pb->name, pb->x,
               pb->y, pb->width, pb->height);
        break;
    }
    default:
        break;
    }
    return 0;
}

/* Only one container may capture input events at a time. */
int32_t evenhub_bind_event_container_4942a4(evenhub_manager_t *mgr, void *handle, evenhub_inject_cb_t cb,
                                            uint32_t id, const char *name, uint8_t type, void *user)
{
    if (mgr == NULL) {
        EH_LOG(1u, bind_fn, 0x270u, 0x04000000u, bind_nomgr, bind_nomgr_s);
        return -1;
    }
    if (handle == NULL || cb == NULL) {
        EH_LOG(1u, bind_fn, 0x276u, 0x04800000u, bind_invalid, bind_invalid_s, handle, cb);
        return -1;
    }
    if (mgr->bound != 0u) {
        EH_LOG(2u, bind_fn, 0x27eu, 0x08800000u, bind_busy, bind_busy_s, mgr->bound_id, mgr->bound_name);
        return -1;
    }
    mgr->bound_handle = handle;
    mgr->bound_cb = cb;
    mgr->bound_user = user;
    mgr->bound_id = id;
    mgr->bound_type = type;
    if (name != NULL) {
        (void)audio_settings_copy_text(mgr->bound_name, name, sizeof(mgr->bound_name) - 1u);
        mgr->bound_name[sizeof(mgr->bound_name) - 1u] = '\0';
    } else {
        mgr->bound_name[0] = '\0';
    }
    mgr->bound = 1u;
    EH_LOG(3u, bind_fn, 0x295u, 0x0cc00000u, bind_ok, bind_ok_s, id, mgr->bound_name, type);
    return 0;
}

void evenhub_unbind_event_container_494484(evenhub_manager_t *mgr)
{
    if (mgr == NULL) {
        EH_LOG(2u, unbind_fn, 0x29fu, 0x08000000u, unbind_nomgr, unbind_nomgr_s);
        return;
    }
    if (mgr->bound == 0u) {
        EH_LOG(4u, unbind_fn, 0x2a4u, 0x10000000u, unbind_none, unbind_none_s);
        return;
    }
    EH_LOG(3u, unbind_fn, 0x2abu, 0x0cc00000u, unbind_start, unbind_start_s, mgr->bound_id, mgr->bound_name,
           mgr->bound_type);
    /* Clears bound_handle..bound_type (+0x10..+0x33). */
    (void)aeabi_memset_43c0e4(&mgr->bound_handle, 0x24u, 0);
    mgr->bound = 0u;
    EH_LOG(4u, unbind_fn, 0x2b1u, 0x10000000u, unbind_done, unbind_done_s);
}
