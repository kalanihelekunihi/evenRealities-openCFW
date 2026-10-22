/* Stock source: D:\01_workspace\s200_ap510b_iar_git\app\gui\AgingTest\aging_test.c
 * Native range 0x43c450..0x43c758 (literal pool 0x43c758..0x43c7cc), firmware 2.2.6.10.
 *
 * Aging (burn-in) test page: a full-screen black 576x288 LVGL page with one white
 * 576x48 bar. Each UI_EVENT 3 moves the bar down one 48-pixel row, wrapping after
 * six rows. AgingTest_common_data_handler (0x43c400) is in
 * system/registry-callback/registry_callback_43c400.c, which also owns the shared
 * module and path strings used here.
 *
 * Callees keep the audio_uart_page_<addr> names already used across g2/src. Their
 * LVGL meanings are inferred from the arguments: 0x43de82 obj_create(parent),
 * 0x43dfa4 obj flag op (flag 0x10), 0x43f506/0x43f568 set width/height,
 * 0x43f4c0 set_size, 0x43f09a set_pos, 0x44104c color_hex, 0x441068 color_make,
 * 0x44127e/0x44129e style bg_color/bg_opa, 0x4412ec/0x44131c other style setters. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);                                    /* 0x43d0ce */
extern void audio_log_extended(uint8_t level, const char *module, const char *file,
                               const char *function, uint32_t line, const char *format,
                               ...);                                      /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t header, const char *format,
                                    const char *tag, ...);                /* 0x43ce9e */

extern uint32_t audio_uart_page_43de82(uint32_t parent);
extern void audio_uart_page_43dfa4(uint32_t object, uint32_t flag);
extern void audio_uart_page_43f506(uint32_t object, uint32_t width);
extern void audio_uart_page_43f568(uint32_t object, uint32_t height);
extern void audio_uart_page_43f4c0(uint32_t object, uint32_t width, uint32_t height);
extern void audio_uart_page_43f09a(uint32_t object, uint32_t x, uint32_t y);
extern uint32_t audio_uart_page_44104c(uint32_t hex);
extern uint32_t audio_uart_page_441068(uint32_t red, uint32_t green, uint32_t blue);
extern void audio_uart_page_44127e(uint32_t object, uint32_t color, uint32_t selector);
extern void audio_uart_page_44129e(uint32_t object, uint32_t opa, uint32_t selector);
extern void audio_uart_page_4412ec(uint32_t object, uint32_t color, uint32_t selector);
extern void audio_uart_page_44131c(uint32_t object, uint32_t value, uint32_t selector);

/* Shared aging_test.c strings, defined in registry_callback_43c400.c. */
extern const char audio_uart_registry_aging_module[]; /* ROM 0x789f80 "aging_test" */
extern const char audio_uart_registry_aging_source[]; /* ROM 0x6ff794 */

/* Page registry context (registry row native 0x6a44b0); +4 holds the page root. */
extern uint8_t audio_uart_registry_context_20000044;

extern uint8_t g2_aging_test_event_count;    /* RAM 0x20074f4c, 0..5 */
extern uint8_t g2_aging_test_rect_ready;     /* RAM 0x20074f4d */
extern uint32_t g2_aging_test_page_root;     /* RAM 0x200741bc, lv_obj_t * */
extern uint32_t g2_aging_test_rect;          /* RAM 0x2007411c, lv_obj_t * */
extern int32_t g2_aging_test_rect_position;  /* RAM 0x200741b8, row 0..5 */

static const char page_event_function[] = "aging_test_page_event_handler"; /* ROM 0x75d450 */
static const char page_event_format[] = "received event: %d";              /* ROM 0x77d894 */
static const char page_event_compact[] = "[aging_test]received event: %d"; /* ROM 0x75d470 */

static const char ui_event_function[] = "AgingTest_ui_event_handler";      /* ROM 0x768390 */
static const char ui_init_format[] =
    "AgingTest_ui_event_handler UI_EVENT_TYPE_INIT";                       /* ROM 0x730d64 */
static const char ui_init_compact[] =
    "[aging_test]AgingTest_ui_event_handler UI_EVENT_TYPE_INIT";           /* ROM 0x711ca4 */
/* "Delete the previous aging test page" */
static const char ui_delete_format[] = "删除之前的老化测试页面";             /* ROM 0x7514f4 */
static const char ui_delete_compact[] = "[aging_test]删除之前的老化测试页面"; /* ROM 0x730d94 */
/* "Create a new aging test page" */
static const char ui_create_format[] = "创建新的老化测试页面";               /* ROM 0x75d490 */
static const char ui_create_compact[] = "[aging_test]创建新的老化测试页面";   /* ROM 0x73b7a0 */

static const char rect_init_function[] = "init_rectangle_system";          /* ROM 0x774abc */
/* "Initialise the rectangle cycle display system" */
static const char rect_init_format[] = "初始化矩形循环显示系统";             /* ROM 0x75153c */
static const char rect_init_compact[] = "[aging_test]初始化矩形循环显示系统"; /* ROM 0x730dc4 */
/* "Rectangle cycle display system initialised" */
static const char rect_done_format[] = "矩形循环显示系统初始化完成";           /* ROM 0x746d4c */
static const char rect_done_compact[] =
    "[aging_test]矩形循环显示系统初始化完成";                                  /* ROM 0x7262f8 */

static const char rect_update_function[] = "update_rectangle_display";     /* ROM 0x7683ac */
/* "Rectangle moved to position %d (y=%d)" */
static const char rect_update_format[] = "矩形移动到位置 %d (y=%d)";          /* ROM 0x75d4b0 */
static const char rect_update_compact[] =
    "[aging_test]矩形移动到位置 %d (y=%d)";                                    /* ROM 0x73b7cc */

#define AGING_SCREEN_WIDTH 576u
#define AGING_SCREEN_HEIGHT 288u
#define AGING_RECT_HEIGHT 48u
#define AGING_RECT_ROWS 6

/* Both logging sinks are gated by audio_log_flags(): bit 1 for the extended
 * logger, bit 0 or bit 2 for the compact logger. */
static int compact_log_enabled(void)
{
    return (audio_log_flags() & 1u) || (audio_log_flags() & 4u);
}

void init_rectangle_system_43c5f6(void);
void update_rectangle_display_43c6ce(void);

/* 0x43c450: logs the event and reports it handled. No stock caller or pointer
 * reference was found. */
uint32_t aging_test_page_event_handler_43c450(uint32_t unused0, uint32_t unused1,
                                              uint32_t event)
{
    (void)unused0;
    (void)unused1;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, audio_uart_registry_aging_module,
                           audio_uart_registry_aging_source, page_event_function, 0x39u,
                           page_event_format, event);
    if (compact_log_enabled())
        (void)compress_log_output(0x10400000u, page_event_compact, page_event_compact,
                                  event);
    return 1u;
}

/* 0x43c496, stock AgingTest_ui_event_handler (registry row native 0x6a44b0, slot 2).
 * The name matches the existing extern in system/ui-registry/ui_registry_table.c.
 * Type 2 (UI_EVENT_TYPE_INIT) builds the page under `parent`. It does not delete an
 * old page; it only forgets the old object pointers. Type 3 steps the bar. */
uint32_t audio_uart_registry_callback_43c496(uint32_t type, uint32_t unused1,
                                             uint32_t unused2, uint32_t parent)
{
    (void)unused1;
    (void)unused2;
    if (type == 2u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, audio_uart_registry_aging_module,
                               audio_uart_registry_aging_source, ui_event_function, 0x41u,
                               ui_init_format);
        if (compact_log_enabled())
            (void)compress_log_output(0x10000000u, ui_init_compact, ui_init_compact);
        g2_aging_test_event_count = 0u;
        if (g2_aging_test_page_root != 0u) {
            if (audio_log_flags() & 2u)
                audio_log_extended(4u, audio_uart_registry_aging_module,
                                   audio_uart_registry_aging_source, ui_event_function,
                                   0x47u, ui_delete_format);
            if (compact_log_enabled())
                (void)compress_log_output(0x10000000u, ui_delete_compact,
                                          ui_delete_compact);
            g2_aging_test_page_root = 0u;
            g2_aging_test_rect = 0u;
            g2_aging_test_rect_ready = 0u;
        }
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, audio_uart_registry_aging_module,
                               audio_uart_registry_aging_source, ui_event_function, 0x4du,
                               ui_create_format);
        if (compact_log_enabled())
            (void)compress_log_output(0x10000000u, ui_create_compact, ui_create_compact);

        g2_aging_test_page_root = audio_uart_page_43de82(parent);
        audio_uart_page_43dfa4(g2_aging_test_page_root, 0x10u);
        audio_uart_page_43f506(g2_aging_test_page_root, AGING_SCREEN_WIDTH);
        audio_uart_page_43f568(g2_aging_test_page_root, AGING_SCREEN_HEIGHT);
        audio_uart_page_43dfa4(g2_aging_test_page_root, 0x10u);
        audio_uart_page_44127e(g2_aging_test_page_root, audio_uart_page_44104c(0u), 0u);
        audio_uart_page_44129e(g2_aging_test_page_root, 0xffu, 0u);
        /* Stock passes a 3-byte black colour struct {0,0,0} by value. The top byte
         * of r1 is uninitialised stack in stock; it is zero here. */
        audio_uart_page_4412ec(g2_aging_test_page_root, 0u, 0u);
        init_rectangle_system_43c5f6();
        *(uint32_t *)(void *)(&audio_uart_registry_context_20000044 + 4) =
            g2_aging_test_page_root;
    } else if (type == 3u) {
        g2_aging_test_event_count = (uint8_t)(g2_aging_test_event_count + 1u);
        if (g2_aging_test_event_count >= AGING_RECT_ROWS)
            g2_aging_test_event_count = 0u;
        update_rectangle_display_43c6ce();
    }
    return 0u;
}

/* 0x43c5f6: creates the white 576x48 bar at row 0, once per page. */
void init_rectangle_system_43c5f6(void)
{
    if (g2_aging_test_rect_ready != 0u || g2_aging_test_page_root == 0u)
        return;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, audio_uart_registry_aging_module,
                           audio_uart_registry_aging_source, rect_init_function, 0x7au,
                           rect_init_format);
    if (compact_log_enabled())
        (void)compress_log_output(0x0c000000u, rect_init_compact, rect_init_compact);

    g2_aging_test_rect = audio_uart_page_43de82(g2_aging_test_page_root);
    audio_uart_page_43f4c0(g2_aging_test_rect, AGING_SCREEN_WIDTH, AGING_RECT_HEIGHT);
    audio_uart_page_43f09a(g2_aging_test_rect, 0u, 0u);
    audio_uart_page_44127e(g2_aging_test_rect, audio_uart_page_441068(0xffu, 0xffu, 0xffu),
                           0u);
    audio_uart_page_44131c(g2_aging_test_rect, 0u, 0u);
    audio_uart_page_44129e(g2_aging_test_rect, 0xffu, 0u);
    g2_aging_test_rect_position = 0;
    g2_aging_test_rect_ready = 1u;

    if (audio_log_flags() & 2u)
        audio_log_extended(3u, audio_uart_registry_aging_module,
                           audio_uart_registry_aging_source, rect_init_function, 0x88u,
                           rect_done_format);
    if (compact_log_enabled())
        (void)compress_log_output(0x0c000000u, rect_done_compact, rect_done_compact);
}

/* 0x43c6ce: moves the bar to the next row (signed modulo 6, y = row * 48). */
void update_rectangle_display_43c6ce(void)
{
    if (g2_aging_test_rect_ready == 0u) {
        init_rectangle_system_43c5f6();
        return;
    }
    if (g2_aging_test_rect == 0u)
        return;
    g2_aging_test_rect_position = (g2_aging_test_rect_position + 1) % AGING_RECT_ROWS;
    audio_uart_page_43f09a(g2_aging_test_rect, 0u,
                           (uint32_t)g2_aging_test_rect_position * AGING_RECT_HEIGHT);
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, audio_uart_registry_aging_module,
                           audio_uart_registry_aging_source, rect_update_function, 0x9cu,
                           rect_update_format, g2_aging_test_rect_position,
                           g2_aging_test_rect_position * (int32_t)AGING_RECT_HEIGHT);
    if (compact_log_enabled())
        (void)compress_log_output(0x10800000u, rect_update_compact, rect_update_compact,
                                  g2_aging_test_rect_position,
                                  g2_aging_test_rect_position * (int32_t)AGING_RECT_HEIGHT);
}
