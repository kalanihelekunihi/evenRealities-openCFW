#!/usr/bin/env python3
"""Trial-link eight source-owned option callbacks into Apollo-main display C."""
import hashlib,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[4]
base=root/'build/c-firmware/root-main-round604'
display=root/'build/c-firmware/root-main-display-driver-relocated-fifteen-round711'
option=root/'build/c-firmware/root-main-uled-option-service-round681'
out=root/'build/c-firmware/root-main-uled-option-fifteen-label-vector-draw-integration-round807'
out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
selected_receipt=json.loads((base/'receipt.json').read_text())
selected_link=selected_receipt['images']['apollo_main']['relocatable_link']
display_audit=json.loads((display/'link-audit.json').read_text())
option_audit=json.loads((option/'link-audit.json').read_text())
selected=base/'apollo_main/candidate.o'
display_object=display/'display-driver-combined.o'
option_object=option/'uled-option-service-candidate.o'
leaf_object=out/'display_driver_uled_option_leaf_pair.o'
leaf_source=Path(__file__).resolve().parent/'display_driver_uled_option_leaf_pair.c'
setup_source=Path(__file__).resolve().parent/'display_driver_uled_option_setup_pair.c'
enable_source=Path(__file__).resolve().parent/'display_driver_uled_option_enable_pair_bothfinishbound.c'
setup_object=out/'display_driver_uled_option_setup_pair.o'
enable_object=out/'display_driver_uled_option_enable_pair.o'
pin_source=Path(__file__).resolve().parent/'display_driver_uled_option_pin_prepare_pair.c'
pin_object=out/'display_driver_uled_option_pin_prepare_pair.o'
pre_source=Path(__file__).resolve().parent/'display_driver_uled_option_type1_pre.c'
pre_object=out/'display_driver_uled_option_type1_pre.o'
power_source=Path(__file__).resolve().parent/'display_driver_uled_option_type1_power_pmicbound.c'
power_object=out/'display_driver_uled_option_type1_power_pmicbound.o'
pmic_source=Path(__file__).resolve().parent/'display_driver_uled_option_pmic_helpers.c'
pmic_object=out/'display_driver_uled_option_pmic_helpers.o'
transport_source=Path(__file__).resolve().parent/'display_driver_uled_option_pmic_transport.c'
transport_object=out/'display_driver_uled_option_pmic_transport.o'
type0_pre_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_pre.c'
type0_pre_object=out/'display_driver_uled_option_type0_pre.o'
mode4_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_mode4.c'
mode4_object=out/'display_driver_uled_option_type0_mode4.o'
ldo_find_source=Path(__file__).resolve().parent/'display_driver_uled_option_ldo_find.c'
ldo_find_object=out/'display_driver_uled_option_ldo_find.o'
ldo_helpers_source=Path(__file__).resolve().parent/'display_driver_uled_option_ldo_helpers.c'
ldo_helpers_object=out/'display_driver_uled_option_ldo_helpers.o'
frame_source=Path(__file__).resolve().parent/'display_driver_uled_option_frame_start_pair.c'
frame_object=out/'display_driver_uled_option_frame_start_pair.o'
finish_source=Path(__file__).resolve().parent/'display_driver_uled_option_type1_finish.c'
finish_object=out/'display_driver_uled_option_type1_finish.o'
buck_source=Path(__file__).resolve().parent/'display_driver_uled_option_buck0_enable.c'
buck_object=out/'display_driver_uled_option_buck0_enable.o'
bus_source=Path(__file__).resolve().parent/'display_driver_uled_flash_bus_prepare.c'
bus_object=out/'display_driver_uled_flash_bus_prepare.o'
type0_finish_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_finish.c'
type0_finish_object=out/'display_driver_uled_option_type0_finish.o'
mode4_finish_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_mode4_finish.c'
mode4_finish_object=out/'display_driver_uled_option_type0_mode4_finish.o'
get_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_get.c'
get_object=out/'display_driver_uled_option_type0_get.o'
read_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_read.c'
read_object=out/'display_driver_uled_option_type0_read.o'
packet_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_packet_reused.c'
packet_object=out/'display_driver_uled_option_type0_packet.o'
encode_source=Path(__file__).resolve().parent/'display_driver_uled_option_packet_encode.c'
encode_object=out/'display_driver_uled_option_packet_encode.o'
validate_source=Path(__file__).resolve().parent/'display_driver_uled_option_packet_validate.c'
validate_object=out/'display_driver_uled_option_packet_validate.o'
begin_source=Path(__file__).resolve().parent/'display_driver_uled_option_packet_begin_reused.c'
begin_object=out/'display_driver_uled_option_packet_begin.o'
check_source=Path(__file__).resolve().parent/'display_driver_uled_option_device_check_fully_reused.c'
check_object=out/'display_driver_uled_option_device_check.o'
end_source=Path(__file__).resolve().parent/'display_driver_uled_option_packet_end.c'
end_object=out/'display_driver_uled_option_packet_end.o'
aux_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_aux_finish.c'
aux_object=out/'display_driver_uled_option_type0_aux_finish.o'
complete_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_aux_complete.c'
complete_object=out/'display_driver_uled_option_type0_aux_complete.o'
status_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_aux_status.c'
status_object=out/'display_driver_uled_option_type0_aux_status.o'
regwrite_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_aux_reg_write.c'
regwrite_object=out/'display_driver_uled_option_type0_aux_reg_write.o'
packetwrite_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_packet_write.c'
packetwrite_object=out/'display_driver_uled_option_type0_packet_write.o'
recover_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_aux_recover.c'
recover_object=out/'display_driver_uled_option_type0_aux_recover.o'
context_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_context.c'
context_object=out/'display_driver_uled_option_type0_context.o'
snapshot_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_context_snapshot.c'
snapshot_object=out/'display_driver_uled_option_type0_context_snapshot.o'
aux_config_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_aux_config.c'
aux_config_object=out/'display_driver_uled_option_type0_aux_config.o'
command_lower_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_command_lower.c'
command_lower_object=out/'display_driver_uled_option_type0_command_lower.o'
frame_lower_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_frame_lower.c'
frame_lower_object=out/'display_driver_uled_option_type0_frame_lower.o'
delay_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_delay.c'
delay_object=out/'display_driver_uled_option_type0_delay.o'
qspi_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_qspi_write.c'
qspi_object=out/'display_driver_uled_option_type0_qspi_write.o'
modes_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_mspi_modes.c'
modes_object=out/'display_driver_uled_option_type0_mspi_modes.o'
reconfigure_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_device_reconfigure.c'
reconfigure_object=out/'display_driver_uled_option_type0_device_reconfigure.o'
mspi_power_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_mspi_power.c'
mspi_power_object=out/'display_driver_uled_option_type0_mspi_power.o'
lifecycle_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_mspi_lifecycle.c'
lifecycle_object=out/'display_driver_uled_option_type0_mspi_lifecycle.o'
stop_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_transfer_stop.c'
stop_object=out/'display_driver_uled_option_type0_transfer_stop.o'
prepare_stop_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_transfer_prepare_stop.c'
prepare_stop_object=out/'display_driver_uled_option_type0_transfer_prepare_stop.o'
pin_mode_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_mspi_pin_mode.c'
pin_mode_object=out/'display_driver_uled_option_type0_mspi_pin_mode.o'
pin_apply_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_pin_apply.c'
pin_apply_object=out/'display_driver_uled_option_type0_pin_apply.o'
transfer_setup_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_transfer_setup.c'
transfer_setup_object=out/'display_driver_uled_option_type0_transfer_setup.o'
interrupt_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_mspi_interrupt.c'
interrupt_object=out/'display_driver_uled_option_type0_mspi_interrupt.o'
cache_source=Path(__file__).resolve().parent/'display_driver_uled_option_type0_cache_prepare.c'
cache_object=out/'display_driver_uled_option_type0_cache_prepare.o'
irq_context_source=Path(__file__).resolve().parent/'display_driver_uled_irq_context.c'
irq_context_object=out/'display_driver_uled_irq_context.o'
scheduler_source=Path(__file__).resolve().parent/'display_driver_uled_scheduler_state.c'
scheduler_object=out/'display_driver_uled_scheduler_state.o'
type1_frame_lower_source=Path(__file__).resolve().parent/'display_driver_uled_type1_frame_lower.c'
type1_frame_lower_object=out/'display_driver_uled_type1_frame_lower.o'
type1_chip_id_source=Path(__file__).resolve().parent/'display_driver_uled_type1_chip_id.c'
type1_chip_id_object=out/'display_driver_uled_type1_chip_id.o'
type1_bank_source=Path(__file__).resolve().parent/'display_driver_uled_type1_read_bank.c'
type1_bank_object=out/'display_driver_uled_type1_read_bank.o'
type1_register_source=Path(__file__).resolve().parent/'display_driver_uled_type1_read_register.c'
type1_register_object=out/'display_driver_uled_type1_read_register.o'
type1_sn_source=Path(__file__).resolve().parent/'display_driver_uled_type1_read_sn.c'
type1_sn_object=out/'display_driver_uled_type1_read_sn.o'
type1_write_source=Path(__file__).resolve().parent/'display_driver_uled_type1_write_register.c'
type1_write_object=out/'display_driver_uled_type1_write_register.o'
type0_configure_source=Path(__file__).resolve().parent/'display_driver_uled_type0_configure.c'
type0_configure_object=out/'display_driver_uled_type0_configure.o'
type0_offset_source=Path(__file__).resolve().parent/'display_driver_uled_type0_set_offset.c'
type0_offset_object=out/'display_driver_uled_type0_set_offset.o'
label_vector_draw_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/label_vector_draw.c'
label_vector_draw_object=out/'audio_uart_ambiq_label_vector_draw.o'
label_outline_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/label_outline_available.c'
label_outline_object=out/'audio_uart_ambiq_outline_available.o'
label_fill_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/label_fill_rectangle.c'
label_fill_object=out/'audio_uart_ambiq_label_fill_rectangle.o'
label_vector_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/label_vector_dispatch.c'
label_vector_object=out/'audio_uart_ambiq_label_vector_dispatch.o'
label_glyph_blit_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/label_glyph_blit.c'
label_glyph_blit_object=out/'audio_uart_ambiq_label_glyph_blit.o'
label_rect_copy_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/label_rect_copy.c'
label_rect_copy_object=out/'audio_uart_ambiq_label_rect_copy.o'
label_width_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/label_width_aligned.c'
label_width_object=out/'audio_uart_ambiq_label_width_aligned.o'
draw_label_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/draw_label.c'
draw_label_object=out/'audio_uart_ambiq_draw_label.o'
transform_point_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/transform_point.c'
transform_point_object=out/'audio_uart_lv_transform_point.o'
transform_area_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/transform_area.c'
transform_area_object=out/'audio_uart_ambiq_transform_area.o'
ambiq_state_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/ambiq_state.c'
ambiq_state_object=out/'audio_uart_ambiq_state.o'
draw_quad_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/nema_draw_quad.c'
draw_quad_object=out/'audio_uart_nema_draw_quad.o'
float_fixed_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/nema_float_fixed.c'
float_fixed_object=out/'audio_uart_nema_float_fixed.o'
image_alpha_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/image_alpha.c'
image_alpha_object=out/'audio_uart_ambiq_image_alpha.o'
alpha_command_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/nema_alpha_command.c'
alpha_command_object=out/'audio_uart_nema_alpha_command.o'
texture_color_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/texture_color.c'
texture_color_object=out/'audio_uart_ambiq_texture_color.o'
image_options_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/image_options.c'
image_options_object=out/'audio_uart_ambiq_image_options.o'
mask_rectangle_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/nema_mask_rectangle.c'
mask_rectangle_object=out/'audio_uart_nema_mask_rectangle.o'
float_position_alias_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/nema_float_position_alias.c'
float_position_alias_object=out/'audio_uart_nema_float_position_alias.o'
texture_bind_alias_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/texture_bind_alias.c'
texture_bind_alias_object=out/'audio_uart_ambiq_texture_bind_alias.o'
texture_setup_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/texture_setup.c'
texture_setup_object=out/'audio_uart_ambiq_texture_setup.o'
trigonometry_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/nema_trigonometry.c'
trigonometry_object=out/'audio_uart_nema_trigonometry.o'
matrix_upload_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/matrix_upload.c'
matrix_upload_object=out/'audio_uart_nema_matrix_upload.o'
matrix_finalize_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/matrix_finalize.c'
matrix_finalize_object=out/'audio_uart_nema_matrix_finalize.o'
matrix_rotate_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/matrix_rotate.c'
matrix_rotate_object=out/'audio_uart_nema_matrix_rotate.o'
matrix_scale_shear_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/matrix_scale_shear.c'
matrix_scale_shear_object=out/'audio_uart_nema_matrix_scale_shear.o'
matrix_translate_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/matrix_translate.c'
matrix_translate_object=out/'audio_uart_nema_matrix_translate.o'
matrix_point_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/matrix_point.c'
matrix_point_object=out/'audio_uart_nema_matrix_point.o'
matrix_copy_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/matrix_copy.c'
matrix_copy_object=out/'audio_uart_nema_matrix_copy.o'
color_resolve_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/color_resolve.c'
color_resolve_object=out/'audio_uart_ambiq_color_resolve.o'
mask_position_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/mask_position.c'
mask_position_object=out/'audio_uart_ambiq_mask_position.o'
color_register_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/color_register.c'
color_register_object=out/'audio_uart_ambiq_color_register.o'
premultiply_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/color_premultiply.c'
premultiply_object=out/'audio_uart_ambiq_color_premultiply.o'
image_color_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/image_color.c'
image_color_object=out/'audio_uart_ambiq_image_color.o'
nema_cf_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/nema_cf.c'
nema_cf_object=out/'audio_uart_ambiq_nema_cf.o'
mask_options_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/mask_options.c'
mask_options_object=out/'audio_uart_ambiq_mask_options.o'
stencil_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/stencil.c'
stencil_object=out/'audio_uart_nema_stencil.o'
image_core_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/image_core.c'
image_core_object=out/'audio_uart_ambiq_image_core.o'
decoder_find_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/decoder_find.c'
decoder_find_object=out/'audio_uart_lv_decoder_find.o'
cache_release_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/cache_release.c'
cache_release_object=out/'audio_uart_lv_cache_release.o'
cache_lookup_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/cache_lookup.c'
cache_lookup_object=out/'audio_uart_lv_cache_lookup.o'
cache_entry_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/cache_entry.c'
cache_entry_object=out/'audio_uart_lv_cache_entry.o'
decoder_options_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/decoder_options.c'
decoder_options_object=out/'audio_uart_lv_decoder_options.o'
decoder_cache_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/decoder_cache.c'
decoder_cache_object=out/'audio_uart_lv_decoder_cache.o'
decoder_open_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/decoder_open.c'
decoder_open_object=out/'audio_uart_lv_decoder_open.o'
decoder_close_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/decoder_close.c'
decoder_close_object=out/'audio_uart_lv_decoder_close.o'
ambiq_decode_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/decode.c'
ambiq_decode_object=out/'audio_uart_ambiq_decode_image.o'
image_entry_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/image.c'
image_entry_object=out/'audio_uart_ambiq_draw_image_entry.o'
buffer_layer_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/layer.c'
buffer_layer_object=out/'audio_uart_ambiq_draw_layer.o'
buffer_render_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/render.c'
buffer_render_object=out/'audio_uart_ambiq_buffer_render.o'
buffer_draw_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/draw.c'
buffer_draw_object=out/'audio_uart_ambiq_buffer_draw.o'
buffer_blend_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/blend.c'
buffer_blend_object=out/'audio_uart_ambiq_buffer_blend.o'
buffer_coherency_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/coherency.c'
buffer_coherency_object=out/'audio_uart_ambiq_buffer_coherency.o'
buffer_base_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/base.c'
buffer_base_object=out/'audio_uart_ambiq_buffer_base.o'
buffer_sizes_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/size.c'
buffer_sizes_object=out/'audio_uart_ambiq_buffer_sizes.o'
buffer_handlers_source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/handlers.c'
buffer_handlers_object=out/'audio_uart_ambiq_buffer_handlers.o'
style_removed_source=root/'components/main/lv_style_removed_candidate_20261014/style_removed.c'
style_removed_object=out/'audio_uart_lv_style_removed.o'
npmx_source=root/'components/main/npmx_watchdog_candidate_20261014/kick.c'
npmx_object=out/'audio_ble_npmx_watchdog_kick.o'
type1_brightness_source=Path(__file__).resolve().parent/'display_driver_uled_type1_set_brightness.c'
type1_brightness_object=out/'display_driver_uled_type1_set_brightness.o'
type1_offset_source=Path(__file__).resolve().parent/'display_driver_uled_type1_set_offset.c'
type1_offset_object=out/'display_driver_uled_type1_set_offset.o'
type1_step_source=Path(__file__).resolve().parent/'display_driver_uled_type1_step.c'
type1_step_object=out/'display_driver_uled_type1_step.o'
clip_source=root/'components/main/ambiq_clip_change_candidate_20261014/clip.c'
clip_object=out/'audio_uart_ambiq_clip_change.o'
descriptor_source=Path(__file__).resolve().parent/'display_driver_uled_mspi_descriptor.c'
descriptor_object=out/'display_driver_uled_mspi_descriptor.o'
queue_prepare_source=Path(__file__).resolve().parent/'display_driver_uled_mspi_queue_prepare.c'
queue_prepare_object=out/'display_driver_uled_mspi_queue_prepare.o'
transfer_async_source=Path(__file__).resolve().parent/'display_driver_uled_transfer_async.c'
transfer_async_object=out/'display_driver_uled_transfer_async.o'
mspi_init_source=Path(__file__).resolve().parent/'display_driver_uled_option_config.c'
mspi_init_object=out/'display_driver_uled_option_config.o'
for source,obj in ((label_vector_draw_source,label_vector_draw_object),(label_outline_source,label_outline_object),(label_fill_source,label_fill_object),(label_vector_source,label_vector_object),(label_glyph_blit_source,label_glyph_blit_object),(label_rect_copy_source,label_rect_copy_object),(label_width_source,label_width_object),(draw_label_source,draw_label_object),(transform_point_source,transform_point_object),(transform_area_source,transform_area_object),(ambiq_state_source,ambiq_state_object),(draw_quad_source,draw_quad_object),(float_fixed_source,float_fixed_object),(image_alpha_source,image_alpha_object),(alpha_command_source,alpha_command_object),(texture_color_source,texture_color_object),(image_options_source,image_options_object),(mask_rectangle_source,mask_rectangle_object),(float_position_alias_source,float_position_alias_object),(texture_bind_alias_source,texture_bind_alias_object),(texture_setup_source,texture_setup_object),(trigonometry_source,trigonometry_object),(matrix_upload_source,matrix_upload_object),(matrix_finalize_source,matrix_finalize_object),(matrix_rotate_source,matrix_rotate_object),(matrix_scale_shear_source,matrix_scale_shear_object),(matrix_translate_source,matrix_translate_object),(matrix_point_source,matrix_point_object),(matrix_copy_source,matrix_copy_object),(color_resolve_source,color_resolve_object),(mask_position_source,mask_position_object),(color_register_source,color_register_object),(premultiply_source,premultiply_object),(image_color_source,image_color_object),(nema_cf_source,nema_cf_object),(mask_options_source,mask_options_object),(stencil_source,stencil_object),(image_core_source,image_core_object),(decoder_find_source,decoder_find_object),(cache_release_source,cache_release_object),(cache_lookup_source,cache_lookup_object),(cache_entry_source,cache_entry_object),(decoder_options_source,decoder_options_object),(decoder_cache_source,decoder_cache_object),(decoder_open_source,decoder_open_object),(decoder_close_source,decoder_close_object),(ambiq_decode_source,ambiq_decode_object),(image_entry_source,image_entry_object),(buffer_layer_source,buffer_layer_object),(buffer_render_source,buffer_render_object),(buffer_draw_source,buffer_draw_object),(buffer_blend_source,buffer_blend_object),(buffer_coherency_source,buffer_coherency_object),(buffer_base_source,buffer_base_object),(buffer_sizes_source,buffer_sizes_object),(buffer_handlers_source,buffer_handlers_object),(style_removed_source,style_removed_object),(npmx_source,npmx_object),(type1_brightness_source,type1_brightness_object),(type1_offset_source,type1_offset_object),(type1_step_source,type1_step_object),(clip_source,clip_object),(descriptor_source,descriptor_object),(queue_prepare_source,queue_prepare_object),(transfer_async_source,transfer_async_object),(mspi_init_source,mspi_init_object),(type0_offset_source,type0_offset_object),(type0_configure_source,type0_configure_object),(type1_sn_source,type1_sn_object),(type1_write_source,type1_write_object),(type1_bank_source,type1_bank_object),(type1_register_source,type1_register_object),(type1_chip_id_source,type1_chip_id_object),(type1_frame_lower_source,type1_frame_lower_object),(irq_context_source,irq_context_object),(scheduler_source,scheduler_object),(setup_source,setup_object),(enable_source,enable_object),(pin_source,pin_object),(pre_source,pre_object),(power_source,power_object),(pmic_source,pmic_object),(transport_source,transport_object),(type0_pre_source,type0_pre_object),(mode4_source,mode4_object),(ldo_find_source,ldo_find_object),(ldo_helpers_source,ldo_helpers_object),(frame_source,frame_object),(finish_source,finish_object),(buck_source,buck_object),(bus_source,bus_object),(type0_finish_source,type0_finish_object),(mode4_finish_source,mode4_finish_object),(get_source,get_object),(read_source,read_object),(packet_source,packet_object),(encode_source,encode_object),(validate_source,validate_object),(begin_source,begin_object),(check_source,check_object),(end_source,end_object),(aux_source,aux_object),(complete_source,complete_object),(status_source,status_object),(regwrite_source,regwrite_object),(packetwrite_source,packetwrite_object),(recover_source,recover_object),(context_source,context_object),(snapshot_source,snapshot_object),(aux_config_source,aux_config_object),(command_lower_source,command_lower_object),(frame_lower_source,frame_lower_object),(delay_source,delay_object),(qspi_source,qspi_object),(modes_source,modes_object),(reconfigure_source,reconfigure_object),(mspi_power_source,mspi_power_object),(lifecycle_source,lifecycle_object),(stop_source,stop_object),(prepare_stop_source,prepare_stop_object),(pin_mode_source,pin_mode_object),(pin_apply_source,pin_apply_object),(transfer_setup_source,transfer_setup_object),(interrupt_source,interrupt_object),(cache_source,cache_object)):
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-c',str(source),'-o',str(obj)],check=True)
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-c',str(leaf_source),'-o',str(leaf_object)],check=True)
assert sha(selected)==selected_link['output_sha256']
assert sha(display_object)==display_audit['combined_sha256']
assert sha(option_object)==option_audit['combined_sha256']
groups={'label_vector_draw':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(label_vector_draw_object)],text=True).splitlines()},'label_outline':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(label_outline_object)],text=True).splitlines()},'label_fill':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(label_fill_object)],text=True).splitlines()},'label_vector':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(label_vector_object)],text=True).splitlines()},'label_glyph_blit':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(label_glyph_blit_object)],text=True).splitlines()},'label_rect_copy':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(label_rect_copy_object)],text=True).splitlines()},'label_width':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(label_width_object)],text=True).splitlines()},'draw_label':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(draw_label_object)],text=True).splitlines()},'transform_point':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(transform_point_object)],text=True).splitlines()},'transform_area':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(transform_area_object)],text=True).splitlines()},'ambiq_state':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(ambiq_state_object)],text=True).splitlines()},'draw_quad':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(draw_quad_object)],text=True).splitlines()},'float_fixed':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(float_fixed_object)],text=True).splitlines()},'image_alpha':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(image_alpha_object)],text=True).splitlines()},'alpha_command':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(alpha_command_object)],text=True).splitlines()},'texture_color':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(texture_color_object)],text=True).splitlines()},'image_options':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(image_options_object)],text=True).splitlines()},'mask_rectangle':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(mask_rectangle_object)],text=True).splitlines()},'float_position_alias':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(float_position_alias_object)],text=True).splitlines()},'texture_bind_alias':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(texture_bind_alias_object)],text=True).splitlines()},'texture_setup':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(texture_setup_object)],text=True).splitlines()},'trigonometry':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(trigonometry_object)],text=True).splitlines()},'matrix_upload':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(matrix_upload_object)],text=True).splitlines()},'matrix_finalize':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(matrix_finalize_object)],text=True).splitlines()},'matrix_rotate':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(matrix_rotate_object)],text=True).splitlines()},'matrix_scale_shear':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(matrix_scale_shear_object)],text=True).splitlines()},'matrix_translate':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(matrix_translate_object)],text=True).splitlines()},'matrix_point':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(matrix_point_object)],text=True).splitlines()},'matrix_copy':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(matrix_copy_object)],text=True).splitlines()},'color_resolve':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(color_resolve_object)],text=True).splitlines()},'mask_position':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(mask_position_object)],text=True).splitlines()},'color_register':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(color_register_object)],text=True).splitlines()},'premultiply':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(premultiply_object)],text=True).splitlines()},'image_color':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(image_color_object)],text=True).splitlines()},'nema_cf':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(nema_cf_object)],text=True).splitlines()},'mask_options':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(mask_options_object)],text=True).splitlines()},'stencil':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(stencil_object)],text=True).splitlines()},'image_core':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(image_core_object)],text=True).splitlines()},'selected':set(selected_link['defined_symbols']),
        'display':set(display_audit['defined']),
        'option_service':set(option_audit['defined']),
        'leaf':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(leaf_object)],text=True).splitlines()},
        'setup':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(setup_object)],text=True).splitlines()},
        'enable':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(enable_object)],text=True).splitlines()},
        'pin_prepare':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(pin_object)],text=True).splitlines()},
        'type1_pre':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(pre_object)],text=True).splitlines()},
        'type1_power':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(power_object)],text=True).splitlines()},
        'pmic_helpers':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(pmic_object)],text=True).splitlines()},
        'pmic_transport':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(transport_object)],text=True).splitlines()},
        'type0_pre':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type0_pre_object)],text=True).splitlines()},
        'mode4':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(mode4_object)],text=True).splitlines()},
        'ldo_find':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(ldo_find_object)],text=True).splitlines()},
        'ldo_helpers':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(ldo_helpers_object)],text=True).splitlines()},
        'frame_start':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(frame_object)],text=True).splitlines()},
        'type1_finish':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(finish_object)],text=True).splitlines()},
        'buck0_enable':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(buck_object)],text=True).splitlines()},
        'flash_bus':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(bus_object)],text=True).splitlines()},
        'type0_finish':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type0_finish_object)],text=True).splitlines()},
        'mode4_finish':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(mode4_finish_object)],text=True).splitlines()},
        'type0_get':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(get_object)],text=True).splitlines()},
        'type0_read':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(read_object)],text=True).splitlines()},
        'type0_packet':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(packet_object)],text=True).splitlines()},
        'packet_encode':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(encode_object)],text=True).splitlines()},
        'packet_validate':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(validate_object)],text=True).splitlines()},
        'packet_begin':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(begin_object)],text=True).splitlines()},
        'device_check':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(check_object)],text=True).splitlines()},
        'packet_end':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(end_object)],text=True).splitlines()},
        'type0_aux_finish':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(aux_object)],text=True).splitlines()},
        'type0_aux_complete':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(complete_object)],text=True).splitlines()},
        'type0_aux_status':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(status_object)],text=True).splitlines()},
        'type0_aux_reg_write':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(regwrite_object)],text=True).splitlines()},
        'type0_packet_write':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(packetwrite_object)],text=True).splitlines()},
        'type0_aux_recover':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(recover_object)],text=True).splitlines()},
        'type0_context':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(context_object)],text=True).splitlines()},
        'type0_snapshot':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(snapshot_object)],text=True).splitlines()},
        'type0_aux_config':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(aux_config_object)],text=True).splitlines()},
        'type0_command_lower':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(command_lower_object)],text=True).splitlines()},
        'type0_frame_lower':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(frame_lower_object)],text=True).splitlines()},
        'type0_delay':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(delay_object)],text=True).splitlines()},
        'type0_qspi_write':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(qspi_object)],text=True).splitlines()},
        'type0_mspi_modes':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(modes_object)],text=True).splitlines()},
        'type0_device_reconfigure':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(reconfigure_object)],text=True).splitlines()},
        'type0_mspi_power':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(mspi_power_object)],text=True).splitlines()},
        'type0_mspi_lifecycle':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(lifecycle_object)],text=True).splitlines()},
        'type0_transfer_stop':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(stop_object)],text=True).splitlines()},
        'type0_prepare_stop':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(prepare_stop_object)],text=True).splitlines()},
        'type0_pin_mode':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(pin_mode_object)],text=True).splitlines()},
        'type0_pin_apply':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(pin_apply_object)],text=True).splitlines()},
        'type0_transfer_setup':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(transfer_setup_object)],text=True).splitlines()},
        'type0_mspi_interrupt':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(interrupt_object)],text=True).splitlines()},
        'irq_context':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(irq_context_object)],text=True).splitlines()},
        'scheduler_state':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(scheduler_object)],text=True).splitlines()},
        'type1_frame_lower':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type1_frame_lower_object)],text=True).splitlines()},
        'type1_chip_id':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type1_chip_id_object)],text=True).splitlines()},
        'type1_bank':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type1_bank_object)],text=True).splitlines()},
        'type1_register':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type1_register_object)],text=True).splitlines()},
        'type1_sn':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type1_sn_object)],text=True).splitlines()},
        'type1_write':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type1_write_object)],text=True).splitlines()},
        'type0_configure':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type0_configure_object)],text=True).splitlines()},
        'type0_offset':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type0_offset_object)],text=True).splitlines()},
        'decoder_find':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(decoder_find_object)],text=True).splitlines()},
        'cache_release':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(cache_release_object)],text=True).splitlines()},
        'cache_lookup':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(cache_lookup_object)],text=True).splitlines()},
        'cache_entry':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(cache_entry_object)],text=True).splitlines()},
        'decoder_options':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(decoder_options_object)],text=True).splitlines()},
        'decoder_cache':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(decoder_cache_object)],text=True).splitlines()},
        'decoder_open':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(decoder_open_object)],text=True).splitlines()},
        'decoder_close':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(decoder_close_object)],text=True).splitlines()},
        'ambiq_decode':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(ambiq_decode_object)],text=True).splitlines()},
        'image_entry':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(image_entry_object)],text=True).splitlines()},
        'buffer_layer':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(buffer_layer_object)],text=True).splitlines()},
        'buffer_render':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(buffer_render_object)],text=True).splitlines()},
        'buffer_draw':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(buffer_draw_object)],text=True).splitlines()},
        'buffer_blend':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(buffer_blend_object)],text=True).splitlines()},
        'buffer_coherency':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(buffer_coherency_object)],text=True).splitlines()},
        'buffer_base':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(buffer_base_object)],text=True).splitlines()},
        'buffer_sizes':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(buffer_sizes_object)],text=True).splitlines()},
        'buffer_handlers':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(buffer_handlers_object)],text=True).splitlines()},
        'style_removed':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(style_removed_object)],text=True).splitlines()},
        'npmx':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(npmx_object)],text=True).splitlines()},
        'type1_brightness':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type1_brightness_object)],text=True).splitlines()},
        'type1_offset':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type1_offset_object)],text=True).splitlines()},
        'type1_step':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(type1_step_object)],text=True).splitlines()},
        'clip':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(clip_object)],text=True).splitlines()},
        'descriptor':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(descriptor_object)],text=True).splitlines()},
        'queue_prepare':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(queue_prepare_object)],text=True).splitlines()},
        'transfer_async':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(transfer_async_object)],text=True).splitlines()},
        'mspi_init':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(mspi_init_object)],text=True).splitlines()},
        'type0_cache_prepare':{line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(cache_object)],text=True).splitlines()}}
overlap={f'{a}/{b}':sorted(groups[a]&groups[b]) for i,a in enumerate(groups) for b in list(groups)[i+1:]}
assert all(not x for x in overlap.values()),overlap
candidate=out/'candidate.o'
subprocess.run(['arm-none-eabi-ld','-r',str(selected),str(display_object),
                str(option_object),str(leaf_object),str(setup_object),str(enable_object),str(pin_object),str(pre_object),str(power_object),str(pmic_object),str(transport_object),str(type0_pre_object),str(mode4_object),str(ldo_find_object),str(ldo_helpers_object),str(frame_object),str(finish_object),str(buck_object),str(bus_object),str(type0_finish_object),str(mode4_finish_object),str(get_object),str(read_object),str(packet_object),str(encode_object),str(validate_object),str(begin_object),str(check_object),str(end_object),str(aux_object),str(complete_object),str(status_object),str(regwrite_object),str(packetwrite_object),str(recover_object),str(context_object),str(snapshot_object),str(aux_config_object),str(command_lower_object),str(frame_lower_object),str(delay_object),str(qspi_object),str(modes_object),str(reconfigure_object),str(mspi_power_object),str(lifecycle_object),str(stop_object),str(prepare_stop_object),str(pin_mode_object),str(pin_apply_object),str(transfer_setup_object),str(interrupt_object),str(cache_object),str(irq_context_object),str(scheduler_object),str(type1_frame_lower_object),str(type1_chip_id_object),str(type1_bank_object),str(type1_register_object),str(type1_sn_object),str(type1_write_object),str(type0_configure_object),str(type0_offset_object),str(mspi_init_object),str(transfer_async_object),str(queue_prepare_object),str(descriptor_object),str(clip_object),str(type1_step_object),str(type1_offset_object),str(type1_brightness_object),str(npmx_object),str(style_removed_object),str(buffer_handlers_object),str(buffer_sizes_object),str(buffer_base_object),str(buffer_coherency_object),str(buffer_blend_object),str(buffer_render_object),str(buffer_draw_object),str(buffer_layer_object),str(image_entry_object),str(decoder_options_object),str(decoder_cache_object),str(decoder_open_object),str(decoder_close_object),str(ambiq_decode_object),str(cache_entry_object),str(cache_lookup_object),str(cache_release_object),str(decoder_find_object),str(image_core_object),str(stencil_object),str(mask_options_object),str(nema_cf_object),str(image_color_object),str(premultiply_object),str(color_register_object),str(mask_position_object),str(color_resolve_object),str(matrix_copy_object),str(matrix_point_object),str(matrix_translate_object),str(matrix_scale_shear_object),str(matrix_rotate_object),str(matrix_finalize_object),str(matrix_upload_object),str(trigonometry_object),str(texture_setup_object),str(texture_bind_alias_object),str(float_position_alias_object),str(mask_rectangle_object),str(image_options_object),str(texture_color_object),str(image_alpha_object),str(alpha_command_object),str(draw_quad_object),str(float_fixed_object),str(ambiq_state_object),str(transform_area_object),str(transform_point_object),str(draw_label_object),str(label_rect_copy_object),str(label_width_object),str(label_glyph_blit_object),str(label_fill_object),str(label_vector_object),str(label_outline_object),str(label_vector_draw_object),'-o',str(candidate)],check=True)
undefined=sorted({line.split()[-1] for line in subprocess.check_output(
    ['arm-none-eabi-nm','-u',str(candidate)],text=True).splitlines()})
assert len(undefined)==615,len(undefined)
assert 'audio_uart_ambiq_outline_available_529ca4' not in undefined
assert 'audio_uart_ambiq_label_fill_rectangle_4b1ab0' not in undefined
assert 'audio_uart_ambiq_label_vector_dispatch_53d6ea' not in undefined
assert 'audio_uart_ambiq_label_vector_draw_53d708' not in undefined
assert 'audio_uart_ambiq_label_glyph_blit_53fb18' not in undefined
assert 'audio_uart_ambiq_label_rect_copy_53fa94' not in undefined
assert 'audio_uart_ambiq_label_width_aligned_53faba' not in undefined
assert 'audio_uart_ambiq_draw_label_53faa6' not in undefined
assert 'audio_uart_lv_draw_label_48a0be' in undefined
assert 'audio_uart_ambiq_label_pixel_53fcc4' in undefined
assert 'audio_uart_lv_transform_point_4513ae' not in undefined
assert 'audio_uart_ambiq_transform_area_488cda' not in undefined
for state_name in ('audio_uart_ambiq_unit_cell','audio_uart_ambiq_vector_current_path_200746c4','audio_uart_ambiq_vector_path_data_20073cd4','audio_uart_ambiq_vector_path_segments_20073cc0'):
 assert state_name not in undefined,state_name
assert 'audio_uart_nema_draw_quad_522db4' not in undefined
assert 'audio_uart_nema_float_fixed_5242cc' not in undefined
assert 'audio_uart_ambiq_image_alpha_513e2e' not in undefined
assert 'audio_uart_nema_alpha_command_522960' not in undefined
assert 'audio_uart_ambiq_texture_color_4b146c' not in undefined
assert 'audio_uart_ambiq_image_options_4b0d38' not in undefined
assert 'audio_uart_nema_mask_rectangle_522ae0' not in undefined
assert 'audio_uart_nema_float_position_5228b0' not in undefined
assert 'audio_uart_ambiq_texture_bind_4b1298' not in undefined
relocations=subprocess.check_output(['arm-none-eabi-readelf','-r',
                                     str(display/'display_driver_uled_options_relocated_fifteen.o')],
                                    text=True)
assert 'contains 15 entries' in relocations,relocations
assert relocations.count('R_ARM_ABS32')==15,relocations
audit={'status':'candidate relocatable link with fifteen source-owned uLED option callback entries',
       'selected_round':604,'selected_object_sha256':sha(selected),
       'display_object_sha256':sha(display_object),
       'option_service_object_sha256':sha(option_object),
       'integrated_object_sha256':sha(candidate),
       'acquire_alias':'audio_semaphore_acquire at native 0x44994e',
       'delay_alias':'audio_uart_task_delay at native 0x454b4c',
       'semaphore_alias':'audio_uart_sync_sem_new at native 0x44989a',
       'label_vector_draw_source_sha256':sha(label_vector_draw_source),
       'label_vector_draw_object_sha256':sha(label_vector_draw_object),
       'label_outline_source_sha256':sha(label_outline_source),
       'label_outline_object_sha256':sha(label_outline_object),
       'label_fill_source_sha256':sha(label_fill_source),
       'label_fill_object_sha256':sha(label_fill_object),
       'label_vector_source_sha256':sha(label_vector_source),
       'label_vector_object_sha256':sha(label_vector_object),
       'label_glyph_blit_source_sha256':sha(label_glyph_blit_source),
       'label_glyph_blit_object_sha256':sha(label_glyph_blit_object),
       'label_rect_copy_source_sha256':sha(label_rect_copy_source),
       'label_rect_copy_object_sha256':sha(label_rect_copy_object),
       'label_width_source_sha256':sha(label_width_source),
       'label_width_object_sha256':sha(label_width_object),
       'draw_label_source_sha256':sha(draw_label_source),
       'draw_label_object_sha256':sha(draw_label_object),
       'transform_point_source_sha256':sha(transform_point_source),
       'transform_point_object_sha256':sha(transform_point_object),
       'transform_area_source_sha256':sha(transform_area_source),
       'transform_area_object_sha256':sha(transform_area_object),
       'ambiq_state_source_sha256':sha(ambiq_state_source),
       'ambiq_state_object_sha256':sha(ambiq_state_object),
       'draw_quad_source_sha256':sha(draw_quad_source),
       'draw_quad_object_sha256':sha(draw_quad_object),
       'float_fixed_source_sha256':sha(float_fixed_source),
       'float_fixed_object_sha256':sha(float_fixed_object),
       'image_alpha_source_sha256':sha(image_alpha_source),
       'image_alpha_object_sha256':sha(image_alpha_object),
       'alpha_command_source_sha256':sha(alpha_command_source),
       'alpha_command_object_sha256':sha(alpha_command_object),
       'texture_color_source_sha256':sha(texture_color_source),
       'texture_color_object_sha256':sha(texture_color_object),
       'image_options_source_sha256':sha(image_options_source),
       'image_options_object_sha256':sha(image_options_object),
       'mask_rectangle_source_sha256':sha(mask_rectangle_source),
       'mask_rectangle_object_sha256':sha(mask_rectangle_object),
       'float_position_alias_source_sha256':sha(float_position_alias_source),
       'float_position_alias_object_sha256':sha(float_position_alias_object),
       'texture_bind_alias_source_sha256':sha(texture_bind_alias_source),
       'texture_bind_alias_object_sha256':sha(texture_bind_alias_object),
       'texture_setup_source_sha256':sha(texture_setup_source),
       'texture_setup_object_sha256':sha(texture_setup_object),
       'trigonometry_source_sha256':sha(trigonometry_source),
       'trigonometry_object_sha256':sha(trigonometry_object),
       'matrix_upload_source_sha256':sha(matrix_upload_source),
       'matrix_upload_object_sha256':sha(matrix_upload_object),
       'matrix_finalize_source_sha256':sha(matrix_finalize_source),
       'matrix_finalize_object_sha256':sha(matrix_finalize_object),
       'matrix_rotate_source_sha256':sha(matrix_rotate_source),
       'matrix_rotate_object_sha256':sha(matrix_rotate_object),
       'matrix_scale_shear_source_sha256':sha(matrix_scale_shear_source),
       'matrix_scale_shear_object_sha256':sha(matrix_scale_shear_object),
       'matrix_translate_source_sha256':sha(matrix_translate_source),
       'matrix_translate_object_sha256':sha(matrix_translate_object),
       'matrix_point_source_sha256':sha(matrix_point_source),
       'matrix_point_object_sha256':sha(matrix_point_object),
       'matrix_copy_source_sha256':sha(matrix_copy_source),
       'matrix_copy_object_sha256':sha(matrix_copy_object),
       'color_resolve_source_sha256':sha(color_resolve_source),
       'color_resolve_object_sha256':sha(color_resolve_object),
       'mask_position_source_sha256':sha(mask_position_source),
       'mask_position_object_sha256':sha(mask_position_object),
       'color_register_source_sha256':sha(color_register_source),
       'color_register_object_sha256':sha(color_register_object),
       'premultiply_source_sha256':sha(premultiply_source),
       'premultiply_object_sha256':sha(premultiply_object),
       'image_color_source_sha256':sha(image_color_source),
       'image_color_object_sha256':sha(image_color_object),
       'nema_cf_source_sha256':sha(nema_cf_source),
       'nema_cf_object_sha256':sha(nema_cf_object),
       'mask_options_source_sha256':sha(mask_options_source),
       'mask_options_object_sha256':sha(mask_options_object),
       'stencil_source_sha256':sha(stencil_source),
       'stencil_object_sha256':sha(stencil_object),
       'image_core_source_sha256':sha(image_core_source),
       'image_core_object_sha256':sha(image_core_object),
       'decoder_find_source_sha256':sha(decoder_find_source),
       'decoder_find_object_sha256':sha(decoder_find_object),
       'cache_release_source_sha256':sha(cache_release_source),
       'cache_release_object_sha256':sha(cache_release_object),
       'cache_lookup_source_sha256':sha(cache_lookup_source),
       'cache_lookup_object_sha256':sha(cache_lookup_object),
       'cache_entry_source_sha256':sha(cache_entry_source),
       'cache_entry_object_sha256':sha(cache_entry_object),
       'decoder_options_source_sha256':sha(decoder_options_source),
       'decoder_options_object_sha256':sha(decoder_options_object),
       'decoder_cache_source_sha256':sha(decoder_cache_source),
       'decoder_cache_object_sha256':sha(decoder_cache_object),
       'decoder_open_source_sha256':sha(decoder_open_source),
       'decoder_open_object_sha256':sha(decoder_open_object),
       'decoder_close_source_sha256':sha(decoder_close_source),
       'decoder_close_object_sha256':sha(decoder_close_object),
       'ambiq_decode_source_sha256':sha(ambiq_decode_source),
       'ambiq_decode_object_sha256':sha(ambiq_decode_object),
       'image_entry_source_sha256':sha(image_entry_source),
       'image_entry_object_sha256':sha(image_entry_object),
       'buffer_layer_source_sha256':sha(buffer_layer_source),
       'buffer_layer_object_sha256':sha(buffer_layer_object),
       'buffer_render_source_sha256':sha(buffer_render_source),
       'buffer_render_object_sha256':sha(buffer_render_object),
       'buffer_draw_source_sha256':sha(buffer_draw_source),
       'buffer_draw_object_sha256':sha(buffer_draw_object),
       'buffer_blend_source_sha256':sha(buffer_blend_source),
       'buffer_blend_object_sha256':sha(buffer_blend_object),
       'buffer_coherency_source_sha256':sha(buffer_coherency_source),
       'buffer_coherency_object_sha256':sha(buffer_coherency_object),
       'buffer_base_source_sha256':sha(buffer_base_source),
       'buffer_base_object_sha256':sha(buffer_base_object),
       'buffer_sizes_source_sha256':sha(buffer_sizes_source),
       'buffer_sizes_object_sha256':sha(buffer_sizes_object),
       'buffer_handlers_source_sha256':sha(buffer_handlers_source),
       'buffer_handlers_object_sha256':sha(buffer_handlers_object),
       'style_removed_source_sha256':sha(style_removed_source),
       'style_removed_object_sha256':sha(style_removed_object),
       'npmx_source_sha256':sha(npmx_source),
       'npmx_object_sha256':sha(npmx_object),
       'type1_brightness_source_sha256':sha(type1_brightness_source),
       'type1_brightness_object_sha256':sha(type1_brightness_object),
       'type1_offset_source_sha256':sha(type1_offset_source),
       'type1_offset_object_sha256':sha(type1_offset_object),
       'type1_step_source_sha256':sha(type1_step_source),
       'type1_step_object_sha256':sha(type1_step_object),
       'clip_source_sha256':sha(clip_source),
       'clip_object_sha256':sha(clip_object),
       'descriptor_source_sha256':sha(descriptor_source),
       'descriptor_object_sha256':sha(descriptor_object),
       'queue_prepare_source_sha256':sha(queue_prepare_source),
       'queue_prepare_object_sha256':sha(queue_prepare_object),
       'transfer_async_source_sha256':sha(transfer_async_source),
       'transfer_async_object_sha256':sha(transfer_async_object),
       'mspi_init_source_sha256':sha(mspi_init_source),
       'mspi_init_object_sha256':sha(mspi_init_object),
       'type0_offset_source_sha256':sha(type0_offset_source),
       'type0_offset_object_sha256':sha(type0_offset_object),
       'type0_configure_source_sha256':sha(type0_configure_source),
       'type0_configure_object_sha256':sha(type0_configure_object),
       'type1_sn_source_sha256':sha(type1_sn_source),
       'type1_write_source_sha256':sha(type1_write_source),
       'type1_sn_object_sha256':sha(type1_sn_object),
       'type1_write_object_sha256':sha(type1_write_object),
       'type1_bank_source_sha256':sha(type1_bank_source),
       'type1_register_source_sha256':sha(type1_register_source),
       'type1_bank_object_sha256':sha(type1_bank_object),
       'type1_register_object_sha256':sha(type1_register_object),
       'type1_chip_id_source_sha256':sha(type1_chip_id_source),
       'type1_chip_id_object_sha256':sha(type1_chip_id_object),
       'type1_frame_lower_source_sha256':sha(type1_frame_lower_source),
       'type1_frame_lower_object_sha256':sha(type1_frame_lower_object),
       'irq_context_source_sha256':sha(irq_context_source),
       'scheduler_source_sha256':sha(scheduler_source),
       'irq_context_object_sha256':sha(irq_context_object),
       'scheduler_object_sha256':sha(scheduler_object),
       'command_lower_source_sha256':sha(command_lower_source),
       'writer_alias':'display_driver_uled_type0_packet_write_59ccdc',
       'validator_alias':'display_driver_uled_packet_validate_59cb42',
       'qspi_source_sha256':sha(qspi_source),
       'provider_alias_source_sha256':{p.name:sha(p) for p in (enable_source,reconfigure_source,mspi_power_source,modes_source)},
       'duplicate_definitions':overlap,
       'unresolved_symbols':undefined,'integrated_unresolved_after':len(undefined),
       'option_callback_unique_total':29,
       'option_callback_C_bodies':15,
       'option_callback_relocation_entries':15,
       'option_callback_native_addresses_remaining':14,
       'leaf_object_sha256':sha(leaf_object),
       'setup_object_sha256':sha(setup_object),
       'enable_object_sha256':sha(enable_object),
       'pin_prepare_object_sha256':sha(pin_object),
       'type1_pre_object_sha256':sha(pre_object),
       'type1_power_object_sha256':sha(power_object),
       'pmic_helpers_object_sha256':sha(pmic_object),
       'pmic_transport_object_sha256':sha(transport_object),
       'type0_pre_object_sha256':sha(type0_pre_object),
       'mode4_object_sha256':sha(mode4_object),
       'ldo_find_object_sha256':sha(ldo_find_object),
       'ldo_helpers_object_sha256':sha(ldo_helpers_object),
       'frame_start_object_sha256':sha(frame_object),
       'type1_finish_object_sha256':sha(finish_object),
       'buck0_enable_object_sha256':sha(buck_object),
       'flash_bus_object_sha256':sha(bus_object),
       'type0_finish_object_sha256':sha(type0_finish_object),
       'mode4_finish_object_sha256':sha(mode4_finish_object),
       'type0_get_object_sha256':sha(get_object),
       'type0_read_object_sha256':sha(read_object),
       'type0_packet_object_sha256':sha(packet_object),
       'packet_encode_object_sha256':sha(encode_object),
       'packet_validate_object_sha256':sha(validate_object),
       'packet_begin_object_sha256':sha(begin_object),
       'device_check_object_sha256':sha(check_object),
       'packet_end_object_sha256':sha(end_object),
       'type0_aux_finish_object_sha256':sha(aux_object),
       'type0_aux_complete_object_sha256':sha(complete_object),
       'type0_aux_status_object_sha256':sha(status_object),
       'type0_aux_reg_write_object_sha256':sha(regwrite_object),
       'type0_packet_write_object_sha256':sha(packetwrite_object),
       'type0_aux_recover_object_sha256':sha(recover_object),
       'type0_context_object_sha256':sha(context_object),
       'type0_snapshot_object_sha256':sha(snapshot_object),
       'type0_aux_config_object_sha256':sha(aux_config_object),
       'type0_command_lower_object_sha256':sha(command_lower_object),
       'type0_frame_lower_object_sha256':sha(frame_lower_object),
       'type0_delay_object_sha256':sha(delay_object),
       'type0_qspi_write_object_sha256':sha(qspi_object),
       'type0_mspi_modes_object_sha256':sha(modes_object),
       'type0_device_reconfigure_object_sha256':sha(reconfigure_object),
       'type0_mspi_power_object_sha256':sha(mspi_power_object),
       'type0_mspi_lifecycle_object_sha256':sha(lifecycle_object),
       'type0_transfer_stop_object_sha256':sha(stop_object),
       'type0_prepare_stop_object_sha256':sha(prepare_stop_object),
       'type0_pin_mode_object_sha256':sha(pin_mode_object),
       'type0_pin_apply_object_sha256':sha(pin_apply_object),
       'type0_transfer_setup_object_sha256':sha(transfer_setup_object),
       'type0_mspi_interrupt_object_sha256':sha(interrupt_object),
       'type0_cache_prepare_object_sha256':sha(cache_object),
       'source_complete':False,'whole_image_linked':False}
(out/'link-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print('PASS_ULED_OPTION_FIFTEEN_LABEL_VECTOR_DRAW_APOLLO_INTEGRATION',len(undefined),15,15)
