/* Native 0x5588ac points at this 128-byte default layout (0x6d52d8).
 * The first 15 semantic fields are initialized; the remaining bytes are zero.
 * The live 0x200e7934 layout remains an externally placed RAM contract. */
#include <stdint.h>
const uint8_t audio_dashboard_layout_default[128]={0,5,0,1,2,4,3,0,1,0,0,0,0,1,4};
const char audio_dashboard_layout_module[]="dashboard.layout";
const char audio_dashboard_layout_source[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\dashboard_layout.c";
const char audio_dashboard_layout_set_function[]="dashboard_layout_set";
const char audio_dashboard_layout_reset_function[]="dashboard_layout_reset_default";
const char audio_dashboard_layout_e_reset[]="dashboard layout reset to default";
const char audio_dashboard_layout_c_reset[]="[dashboard.layout]dashboard layout reset to default";
const char audio_dashboard_layout_e_count[]="widget_count %u exceeds max %u, clamped";
const char audio_dashboard_layout_c_count[]="[dashboard.layout]widget_count %u exceeds max %u, clamped";
const char audio_dashboard_layout_e_center[]="invalid layout: CENTER not allowed when widget_count>0, fallback to default";
const char audio_dashboard_layout_c_center[]="[dashboard.layout]invalid layout: CENTER not allowed when widget_count>0, fallback to default";
const char audio_dashboard_layout_e_base[]="invalid base_pos %d, fallback to default";
const char audio_dashboard_layout_c_base[]="[dashboard.layout]invalid base_pos %d, fallback to default";
const char audio_dashboard_layout_e_widget[]="invalid widget_order[%u]=%d, fallback to default";
const char audio_dashboard_layout_c_widget[]="[dashboard.layout]invalid widget_order[%u]=%d, fallback to default";
const char audio_dashboard_layout_e_face[]="invalid watchface cfg (kind=%d), fallback to default";
const char audio_dashboard_layout_c_face[]="[dashboard.layout]invalid watchface cfg (kind=%d), fallback to default";
const char audio_dashboard_layout_e_success[]="dashboard layout set: base_pos=%d widget_count=%u watchface_kind=%d";
const char audio_dashboard_layout_c_success[]="[dashboard.layout]dashboard layout set: base_pos=%d widget_count=%u watchface_kind=%d";
