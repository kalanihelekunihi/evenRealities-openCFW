#include <stdint.h>
struct audio_uart_nema_error_row { uint32_t code; const char *text; };
/* Native4b0560..4b05a4; source-owned error labels from authenticated tables. */
const char *audio_uart_nema_error_lookup_4b0560(const struct audio_uart_nema_error_row *rows,uint32_t count,uint32_t error) {
    for(uint32_t i=0;i<count;++i) if(rows[i].code==error) return rows[i].text;
    return "UNKNOWN";
}
static const struct audio_uart_nema_error_row vg_rows[] = {
    { 0u, "NO_ERROR" },
    { 1u, "BAD_HANDLE" },
    { 2u, "BAD_BUFFER" },
    { 4u, "INVALID_FILL_RULE" },
    { 8u, "INVALID_PAINT_TYPE" },
    { 16u, "INVALID_VERTEX_DATA" },
    { 32u, "NO_RADIAL_ENABLED" },
    { 64u, "NO_BOUND_CL" },
    { 128u, "INVALID_ARGUMENTS" },
    { 256u, "INVALID_ARC_DATA" },
    { 512u, "CL_FULL" },
    { 1024u, "DRAW_OUT_OF_BOUNDS" },
    { 2048u, "INVALID_MASKING_OBJ" },
    { 4096u, "INVALID_MASKING_FORMAT" },
    { 8192u, "INVALID_LUT_IDX_FORMAT" },
    { 16384u, "COORDS_OUT_OF_RANGE" },
    { 32768u, "EMPTY_TSVG" },
    { 65536u, "NO_BOUND_FONT" },
    { 131072u, "UNSUPPORTED_FONT" },
    { 262144u, "NON_INVERTIBLE_MATRIX" },
    { 524288u, "INVALID_GRAD_STOPS" },
    { 1048576u, "NO_INIT" },
    { 2097152u, "INVALID_STROKE_WIDTH" },
    { 4194304u, "INVALID_OPACITY" },
    { 8388608u, "INVALID_CAP_STYLE" },
    { 16777216u, "INVALID_JOIN_STYLE" },
    { 33554432u, "INVALID_STENCIL_SIZE" },
    { 67108864u, "DEPRECATED_FONT" },
};
const char *audio_uart_nema_vg_error_interpret_4b0584(uint32_t error) { return audio_uart_nema_error_lookup_4b0560(vg_rows,28u,error); }
static const struct audio_uart_nema_error_row gfx_rows[] = {
    { 0u, "NO_ERROR" },
    { 1u, "SYS_INIT_FAILURE" },
    { 2u, "GPU_ABSENT" },
    { 4u, "RB_INIT_FAILURE" },
    { 8u, "NON_EXPANDABLE_CL_FULL" },
    { 16u, "CL_EXPANSION" },
    { 32u, "OUT_OF_GFX_MEMORY" },
    { 64u, "OUT_OF_HOST_MEMORY" },
    { 128u, "NO_BOUND_CL" },
    { 256u, "NO_BOUND_FONT" },
    { 512u, "GFX_MEMORY_INIT" },
    { 1024u, "DRIVER_FAILURE" },
    { 2048u, "MUTEX_INIT" },
    { 4096u, "INVALID_BO" },
    { 8192u, "INVALID_CL" },
    { 16384u, "INVALID_CL_ALIGMENT" },
    { 32768u, "NO_INIT" },
    { 65536u, "INVALID_SECTORED_CL_SIZE" },
};
const char *audio_uart_nema_error_interpret_4b0594(uint32_t error) { return audio_uart_nema_error_lookup_4b0560(gfx_rows,18u,error); }
