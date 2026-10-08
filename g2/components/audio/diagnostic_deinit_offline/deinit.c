/* Logger-disabled codec/PDM diagnostic deinit. Queue control is asynchronous. */
#include <stdint.h>
extern void audio_codec_control(uint32_t),audio_pdm_control(uint32_t);
extern int32_t audio_unregister(uint32_t,uint32_t);
extern int32_t audio_file_close(void*);
extern void audio_encoder_setup(void*);
void audio_recording_stop_selected(uint32_t mode){
 mode=(uint8_t)mode;if(mode>=2)return;
 uint8_t *row=(uint8_t*)(0x20073c08u+12*mode);void *file=*(void**)row;
 if(file){audio_file_close(file);*(void**)row=0;}
 row[10]=0;
}
int32_t audio_diagnostic_deinit_selected(uint32_t mode){
 /* Contract mode0/1. Native mode argument is helper interface; originals are separate entries. */
 if(mode==0)audio_codec_control(0);else audio_pdm_control(0);
 int32_t status=audio_unregister(0x10b,mode);
 if(!status){audio_recording_stop_selected(mode);
  if(mode==0){audio_encoder_setup((void*)0x20106a7cu);audio_encoder_setup((void*)0x201074c0u);}
  else audio_encoder_setup((void*)0x20107f04u);
 }
 return status;
}
