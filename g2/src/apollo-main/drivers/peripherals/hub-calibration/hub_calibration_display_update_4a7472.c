/* Native hub_calibration_display_update 0x4a7472..0x4a76e4. */
#include <stdint.h>

extern uint32_t audio_uart_calibration_snapshot_200749a8;
extern uint32_t audio_uart_calibration_success_primary_200749ac;
extern uint32_t audio_uart_calibration_success_secondary_200749b0;
extern uint32_t audio_uart_ring_secondary_head_cell; /* native RAM 0x200746e0 */
extern uint32_t audio_uart_calibration_panel_left_200749b4;
extern uint32_t audio_uart_calibration_panel_right_200749b8;
extern uint32_t audio_uart_calibration_panel_mark_200749bc;

extern uint32_t audio_uart_page_43de82(uint32_t);
extern uint32_t audio_uart_page_499416(uint32_t);
extern void audio_uart_page_43f4c0(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43f09a(uint32_t, int32_t, int32_t);
extern void audio_uart_page_43dfa4(uint32_t, uint32_t);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_44127e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44129e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44131c(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44146a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_hub_calibration_labels_update_4a7440(uint32_t, uint32_t,
                                                               uint32_t);
extern void audio_uart_page_44145a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44140e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44143e(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_uart_page_460084(const char *);
extern uint32_t audio_uart_page_45fffe(const char *, uint32_t);
extern void audio_uart_page_49942e(uint32_t, uint32_t);
extern void audio_uart_page_43f568(uint32_t, uint32_t);
extern void audio_uart_page_43f506(uint32_t, uint32_t);
extern void audio_uart_page_43f66c(uint32_t);
extern uint32_t audio_uart_lv_obj_width_43fd9e(uint32_t);
extern void audio_uart_page_43f0e0(uint32_t, int32_t);
extern void audio_uart_page_43f142(uint32_t, int32_t);

static const char first_id[] = "ID_HEADUP_CALIBRATING_1";
static const char second_id[] = "ID_HEADUP_CALIBRATING_2";

void audio_uart_hub_calibration_display_update_4a7472(uint32_t parent) {
    uint32_t root = audio_uart_page_43de82(parent);
    audio_uart_calibration_snapshot_200749a8 = root;
    audio_uart_page_43f4c0(root, 0x240u, 0x120u);
    audio_uart_page_43f09a(root, 0, 0);
    audio_uart_page_43dfa4(root, 0x10u);
    audio_uart_page_44127e(root, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(root, 0xffu, 0u);
    audio_uart_page_44131c(root, 0u, 0u);
    audio_uart_page_44146a(root, 0u, 0u);
    audio_uart_hub_calibration_labels_update_4a7440(root, 0u, 0u);

    uint32_t first = audio_uart_page_499416(root);
    audio_uart_calibration_success_primary_200749ac = first;
    audio_uart_page_43f4c0(first, 300u, 0x1cu);
    audio_uart_page_43f09a(first, 0x8a, 99);
    audio_uart_page_44145a(first, 2u, 0u);
    audio_uart_page_44140e(first, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44143e(first, audio_uart_ring_secondary_head_cell, 0u);
    audio_uart_page_44129e(first, 0u, 0u);
    audio_uart_page_44131c(first, 0u, 0u);
    audio_uart_page_49942e(first, audio_uart_page_45fffe(
        first_id, audio_uart_page_460084(first_id)));

    uint32_t second = audio_uart_page_499416(root);
    audio_uart_calibration_success_secondary_200749b0 = second;
    audio_uart_page_43f568(second, 0x1cu);
    audio_uart_page_44145a(second, 2u, 0u);
    audio_uart_page_44140e(second, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44143e(second, audio_uart_ring_secondary_head_cell, 0u);
    audio_uart_page_44129e(second, 0u, 0u);
    audio_uart_page_44131c(second, 0u, 0u);
    audio_uart_page_49942e(second, audio_uart_page_45fffe(
        second_id, audio_uart_page_460084(second_id)));
    audio_uart_page_43f506(second, 0x3fffffffu);
    audio_uart_page_43f66c(second);
    const uint32_t width = audio_uart_lv_obj_width_43fd9e(second);
    audio_uart_page_43f09a(second, (int32_t)(0x240u - width) / 2, 0xa1);

    uint32_t left = audio_uart_page_43de82(root);
    audio_uart_calibration_panel_left_200749b4 = left;
    audio_uart_page_43f506(left, 0xf0u);
    audio_uart_page_43f568(left, 2u);
    audio_uart_page_43f0e0(left, 0x27);
    audio_uart_page_43f142(left, 0x8f);
    audio_uart_page_44127e(left, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44129e(left, 0xffu, 0u);
    audio_uart_page_44131c(left, 0u, 0u);
    audio_uart_hub_calibration_labels_update_4a7440(left, 0u, 0u);

    uint32_t right = audio_uart_page_43de82(root);
    audio_uart_calibration_panel_right_200749b8 = right;
    audio_uart_page_43f506(right, 0xf0u);
    audio_uart_page_43f568(right, 2u);
    audio_uart_page_43f0e0(right, 0x129);
    audio_uart_page_43f142(right, 0x8f);
    audio_uart_page_44127e(right, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44129e(right, 0xffu, 0u);
    audio_uart_page_44131c(right, 0u, 0u);
    audio_uart_hub_calibration_labels_update_4a7440(right, 0u, 0u);

    uint32_t mark = audio_uart_page_43de82(root);
    audio_uart_calibration_panel_mark_200749bc = mark;
    audio_uart_page_43f4c0(mark, 2u, 2u);
    audio_uart_page_43f09a(mark, 0x11f, 0x8f);
    audio_uart_page_44146a(mark, 1u, 0u);
    audio_uart_page_44127e(mark, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44129e(mark, 0xffu, 0u);
    audio_uart_page_44131c(mark, 0u, 0u);
    audio_uart_page_43dfa4(mark, 0x12u);
}
