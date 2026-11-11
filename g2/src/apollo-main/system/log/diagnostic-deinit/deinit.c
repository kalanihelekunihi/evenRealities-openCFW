/* Logger-disabled codec/PDM diagnostic deinit. Queue control is asynchronous. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_lc3_encoder_codec_left[] __asm__("g2_lc3_encoder_codec_left");
extern unsigned char g2ref_g2_lc3_encoder_codec_right[] __asm__("g2_lc3_encoder_codec_right");
extern unsigned char g2ref_g2_lc3_encoder_pdm[] __asm__("g2_lc3_encoder_pdm");
extern void audio_codec_control(uint32_t),audio_pdm_control(uint32_t);
extern int32_t audio_unregister(uint32_t,uint32_t);
extern int32_t audio_file_close(void*);
extern void audio_encoder_setup(void*);
extern uint8_t g2_audio_recording_rows_20073c08[]; /* stock 0x20073c08 (pool 0x57b40c), audio_data.c */
/* Stock 0x0057B312 (service_audio_recording_stop) */
void audio_recording_stop_selected(uint32_t mode){
 mode=(uint8_t)mode;if(mode>=2)return;
 uint8_t *row=(g2_audio_recording_rows_20073c08+12*mode);void *file=*(void**)row;
 if(file){audio_file_close(file);*(void**)row=0;}
 row[10]=0;
}
int32_t audio_diagnostic_deinit_selected(uint32_t mode){
 /* Contract mode0/1. Native mode argument is helper interface; originals are separate entries. */
 if(mode==0)audio_codec_control(0);else audio_pdm_control(0);
 int32_t status=audio_unregister(0x10b,mode);
 if(!status){audio_recording_stop_selected(mode);
  if(mode==0){audio_encoder_setup((void*)((uint32_t)(uintptr_t)g2ref_g2_lc3_encoder_codec_left));audio_encoder_setup((void*)((uint32_t)(uintptr_t)g2ref_g2_lc3_encoder_codec_right));}
  else audio_encoder_setup((void*)((uint32_t)(uintptr_t)g2ref_g2_lc3_encoder_pdm));
 }
 return status;
}
