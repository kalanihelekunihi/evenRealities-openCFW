/* Private declarations for the EvenHub page (stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenHub\evenhub_ui.c, log tag "evenhub.ui"),
 * native 0x494610..0x49718c. Shared by evenhub_ui_events.c and evenhub_ui_page.c in this
 * directory only. The container-list half of the same stock file (0x4935cc..0x4945e0) is
 * reconstructed separately; its functions are referenced here by stock name + address. */
#ifndef G2_EVENHUB_UI_PRIVATE_H
#define G2_EVENHUB_UI_PRIVATE_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* Container kinds carried in the EvenHub protobuf (node.type). */
#define EVENHUB_CONTAINER_LIST 0u
#define EVENHUB_CONTAINER_TEXT 1u
#define EVENHUB_CONTAINER_IMAGE 2u

/* One node of the page's container list (built by evenhub_container_list_create_from_pb). */
typedef struct evenhub_container_node {
    struct evenhub_container_node *prev; /* +0x00 */
    struct evenhub_container_node *next; /* +0x04 */
    uint8_t type;                        /* +0x08 EVENHUB_CONTAINER_* */
    uint8_t reserved[3];
    void *pb;                            /* +0x0c decoded protobuf container record */
    void *ui;                            /* +0x10 common list/text/image container handle */
} evenhub_container_node_t;

/* Injection callback bound to the event-capturing container.
 * data is the LVGL event: +0x10 points at two words {lo, hi} of the event payload. */
typedef int32_t (*evenhub_inject_cb_t)(void *handle, int32_t event_code, void *data, void *user);

/* Page manager context. */
typedef struct {
    void *parent;                        /* +0x00 lv_obj_t * page root */
    evenhub_container_node_t *head;      /* +0x04 */
    evenhub_container_node_t *tail;      /* +0x08 */
    uint32_t count;                      /* +0x0c */
    void *bound_handle;                  /* +0x10 event-capturing container */
    evenhub_inject_cb_t bound_cb;        /* +0x14 */
    void *bound_user;                    /* +0x18 */
    uint32_t bound_id;                   /* +0x1c */
    char bound_name[16];                 /* +0x20 */
    uint8_t bound_type;                  /* +0x30 */
    uint8_t reserved_31[3];
    uint8_t bound;                       /* +0x34 */
    uint8_t timeout_page;                /* +0x35 set while the timeout exit page is shown */
} evenhub_manager_t;
_Static_assert(offsetof(evenhub_manager_t, bound_type) == 0x30, "evenhub manager");
_Static_assert(offsetof(evenhub_manager_t, timeout_page) == 0x35, "evenhub manager");

/* Decoded protobuf records (only the fields this file reads). */
typedef struct {
    uint32_t x, y, width, height;        /* +0x00 */
    uint32_t border_width;               /* +0x10 */
    uint32_t border_color;               /* +0x14 */
    uint32_t border_radius;              /* +0x18 */
    uint32_t padding;                    /* +0x1c */
    uint32_t id;                         /* +0x20 */
    char name[16];                       /* +0x24 */
    uint8_t has_items;                   /* +0x34 */
    uint8_t reserved_35[3];
    uint32_t item_count;                 /* +0x38 */
    uint32_t item_width;                 /* +0x3c */
    uint32_t select_border;              /* +0x40 */
    uint16_t item_name_count;            /* +0x44 */
    char item_name[20][64];              /* +0x46 */
    uint8_t reserved_546[2];
    uint32_t is_event_capture;           /* +0x548 */
} evenhub_pb_list_t;
_Static_assert(offsetof(evenhub_pb_list_t, is_event_capture) == 0x548, "pb list");

typedef struct {
    uint32_t x, y, width, height;        /* +0x00 */
    uint32_t border_width;               /* +0x10 */
    uint32_t border_color;               /* +0x14 */
    uint32_t border_radius;              /* +0x18 */
    uint32_t padding;                    /* +0x1c */
    uint32_t id;                         /* +0x20 */
    char name[16];                       /* +0x24 */
    uint32_t is_event_capture;           /* +0x34 */
    char content[0x800];                 /* +0x38 */
} evenhub_pb_text_t;

typedef struct {
    uint32_t x, y, width, height;        /* +0x00 */
    uint32_t id;                         /* +0x10 */
    char name[16];                       /* +0x14 */
} evenhub_pb_image_t;

/* Creation configs handed to the common list/text/image containers. */
typedef struct {
    uint32_t x, y, width, height;        /* +0x00 */
    uint32_t border_width;               /* +0x10 */
    uint32_t border_color;               /* +0x14 */
    uint32_t border_radius;              /* +0x18 */
    uint32_t padding;                    /* +0x1c */
    uint32_t item_count;                 /* +0x20 */
    uint32_t item_width;                 /* +0x24 */
    uint8_t select_border;               /* +0x28 */
    char item_name[20][64];              /* +0x29 */
    uint8_t reserved[3];
} evenhub_list_config_t;
_Static_assert(sizeof(evenhub_list_config_t) == 0x52c, "list config");

typedef struct {
    int16_t x, y, width, height;         /* +0x00 */
    uint8_t border_width;                /* +0x08 */
    uint8_t border_color;                /* +0x09 */
    uint8_t border_radius;               /* +0x0a */
    uint8_t padding;                     /* +0x0b */
    uint32_t text_color;                 /* +0x0c */
    uint8_t flag_10;                     /* +0x10 always 1 from EvenHub */
    char content[0x800];                 /* +0x11 */
    uint8_t reserved[3];
} evenhub_text_config_t;
_Static_assert(sizeof(evenhub_text_config_t) == 0x814, "text config");

typedef struct {
    int16_t x, y, width, height;         /* +0x00 */
    uint8_t flag_08;                     /* +0x08 */
    uint8_t reserved_09[3];
    uint32_t format;                     /* +0x0c */
    uint8_t flag_10;                     /* +0x10 */
    uint8_t reserved_11[3];
    uint32_t value_14;                   /* +0x14 */
    uint8_t flag_18;                     /* +0x18 */
    uint8_t reserved_19[3];
} evenhub_image_config_t;
_Static_assert(sizeof(evenhub_image_config_t) == 0x1c, "image config");

/* Decoded EvenHub message (0x3758 bytes, RAM 0x203442a0). */
#define EVENHUB_MSG_SIZE 0x3758u
typedef struct {
    uint8_t cmd;                         /* +0x00 */
    uint8_t seq;                         /* +0x01 echoed in every reply */
    uint16_t which;                      /* +0x02 which_Msg_Ctx */
    uint32_t value;                      /* +0x04 container id / flag / value */
    uint8_t body[EVENHUB_MSG_SIZE - 8];  /* +0x08 */
} evenhub_msg_t;
#define EVENHUB_MSG_EVENT_CODE(m) (*(const int32_t *)((const uint8_t *)(m) + 0x18))
#define EVENHUB_MSG_EVENT_DATA(m) (*(const uint32_t *)((const uint8_t *)(m) + 0x1c))
#define EVENHUB_MSG_TEXT(m) ((const char *)(m) + 0x20)
#define EVENHUB_MSG_STARTUP_WIDGET(m) (*(const uint32_t *)((const uint8_t *)(m) + 0x3754))

extern evenhub_msg_t g2_evenhub_rx_msg;                 /* RAM 0x203442a0 */
extern uint32_t g2_evenhub_startup_widget_id;           /* RAM 0x200745cc */
extern const uint8_t g2_evenhub_pb_msg_fields_77754c[]; /* ROM 0x77754c nanopb descriptor */

/* nanopb (by-value stream, IAR copies the temporary with 0x439c04). */
typedef struct {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *errmsg;                  /* +0x0c */
} evenhub_pb_istream_t;
extern evenhub_pb_istream_t audio_uart_pb_stream_init(const void *buf, uint32_t len); /* 0x48f49c */
extern uint32_t audio_uart_pb_decode(evenhub_pb_istream_t *, const void *, void *);   /* 0x490120 */

/* Logging (stock helpers). */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* Each including file defines static evenhub_ui_tag / evenhub_ui_file strings. */
/* Both sinks are tested separately and every argument is evaluated per sink, as in stock. */
#define EH_LOG(level, func, line, cflags, text, short_text, ...)                              \
    do {                                                                                      \
        if ((audio_log_flags() & 2u) != 0u)                                                   \
            audio_log_extended((level), evenhub_ui_tag, evenhub_ui_file, (func), (line),      \
                               (text), ##__VA_ARGS__);                                        \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                 \
            (void)compress_log_output((cflags), (short_text), (short_text), ##__VA_ARGS__);   \
    } while (0)

/* libc-like helpers. */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);                  /* memset(p, n, c) 0x43c0e4 */
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* strncpy 0x44b5a0 */

/* Device role byte (1 = master/right, 2 = slave/left). */
extern uint8_t audio_uart_device_role_get(void); /* 0x45a568 */
extern uint32_t audio_uart_service_mode(void);   /* 0x45a570, same byte */

/* Container list half of evenhub_ui.c (0x4935cc..0x4945e0). */
extern int32_t evenhub_container_list_rebuild_from_pb_493ab6(evenhub_manager_t *, const void *pb);
extern int32_t evenhub_container_list_create_from_pb_493bdc(evenhub_manager_t *, const void *pb);
extern void evenhub_container_list_destroy_493d02(evenhub_manager_t *);
extern int32_t evenhub_container_list_traverse_493ee6(evenhub_manager_t *,
                                                      int32_t (*cb)(evenhub_container_node_t *, void *),
                                                      void *arg);
extern evenhub_container_node_t *evenhub_container_list_find_by_id_493fa8(evenhub_manager_t *,
                                                                          uint32_t id);
extern int32_t evenhub_print_container_info_callback_4940e8(evenhub_container_node_t *, void *);
extern int32_t evenhub_bind_event_container_4942a4(evenhub_manager_t *, void *handle,
                                                   evenhub_inject_cb_t cb, uint32_t id,
                                                   const char *name, uint8_t type, void *user);
extern void evenhub_unbind_event_container_494484(evenhub_manager_t *);
extern uint32_t evenhub_main_widget_id_4935fe(void); /* returns g2_evenhub_startup_widget_id */

/* EvenHub protobuf replies / app events (g2-evenhub-data-parser). */
extern int32_t evenhub_send_reply_4d9c86(uint8_t cmd, uint8_t seq, uint16_t which, uint32_t value);
extern int32_t evenhub_send_container_event_4da16a(uint8_t type, uint32_t id, const char *name,
                                                   uint8_t sub, int32_t index, int16_t extra);
extern int32_t evenhub_send_input_event_4da382(uint32_t id, const char *name, int32_t event_code,
                                               uint32_t data);

/* Common containers. */
extern void *common_image_container_create_4dbede(void *parent, const evenhub_image_config_t *);
extern void *common_list_container_create_4dd510(void *parent, const evenhub_list_config_t *,
                                                 void *event_cb, void *user);
extern void *common_text_container_create_4dee96(void *parent, const evenhub_text_config_t *,
                                                 void *event_cb, void *user);

/* Functions in this directory. */
int32_t evenhub_inject_event_to_container_494610(evenhub_manager_t *mgr, int32_t event_code,
                                                 void *data);
void *evenhub_ui_create_root_container_494834(void *parent);
int32_t common_list_event_callback_4949c0(int32_t selected_index, const char *item_name,
                                          evenhub_manager_t *mgr);
int32_t common_text_event_callback_494a78(uint8_t is_top, evenhub_manager_t *mgr);
int32_t evenhub_ui_page_create_494bec(const void *data, int16_t len, evenhub_manager_t *mgr);
int32_t evenhub_ui_page_rebuild_4955b4(const void *data, int16_t len, evenhub_manager_t *mgr);
void evenhub_list_config_from_pb_495e84(const evenhub_pb_list_t *pb, evenhub_list_config_t *cfg);
void evenhub_text_config_from_pb_495f1a(const evenhub_pb_text_t *pb, evenhub_text_config_t *cfg);
void evenhub_image_config_from_pb_495f6a(const evenhub_pb_image_t *pb, evenhub_image_config_t *cfg);
int32_t evenhub_list_event_inject_adapter_495f9a(void *handle, int32_t event_code, void *data,
                                                 void *user);
int32_t evenhub_text_event_inject_adapter_4961e4(void *handle, int32_t event_code, void *data,
                                                 void *user);
void evenhub_ui_create_timeout_exit_page_496430(void *parent);
int32_t evenhub_ui_reflash_event_handler_496544(evenhub_manager_t *mgr, const void *data,
                                                int16_t len);

#endif
