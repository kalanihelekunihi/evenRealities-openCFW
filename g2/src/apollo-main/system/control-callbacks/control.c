/* Authenticated type0/type1 callback reconstruction, logger-disabled contract. */
#include <stdint.h>
typedef struct {uint32_t type,mode,value;} audio_control_message;
extern uint32_t audio_role(void);
extern void audio_dsp_enable(void),audio_dsp_disable(void),audio_dsp_gate(uint32_t);
extern void audio_watchdog_stop(void),audio_watchdog_start(void),audio_delay(uint32_t);
extern void audio_i2s_enable(void),audio_special_control(uint32_t);
extern void audio_pdm_enable_primary(void),audio_pdm_enable_alternate(void);
extern void audio_irq_disable(int32_t),audio_clock_stop(uint32_t,uint32_t);
extern void audio_i2s_power(void*,uint32_t,uint32_t),audio_i2s_dma_stop(void*),audio_i2s_uninit(void*);
extern void audio_pdm_interrupt_clear(void*,uint32_t);
void audio_i2s_stop_selected(void){
 if(!*(uint8_t*)0x20074fb7u)return;
 *(uint8_t*)0x20074fb7u=0;
 audio_irq_disable(*(const int16_t*)0x78f558u);audio_clock_stop(0,0);
 void *handle=*(void**)0x2007450cu;audio_i2s_power(handle,1,0);audio_i2s_dma_stop(handle);audio_i2s_uninit(handle);
}
void audio_pdm_stop_prefix(uint32_t primary){
 uint8_t *active=(uint8_t*)(primary?0x20074fbbu:0x20074fbau);
 if(!*active)return;*active=0;
 audio_pdm_interrupt_clear(*(void**)(primary?0x20074550u:0x2007454cu),0x18);
 /* Contract ends before interrupt-clear entry for active channels; no continuation claim. */
}
void audio_type0_selected(const audio_control_message *m){
 uint8_t v=(uint8_t)m->value;
 if(audio_role()==1){if(v){audio_dsp_enable();audio_dsp_gate(1);audio_i2s_enable();}else{audio_dsp_disable();audio_dsp_gate(0);audio_i2s_stop_selected();}return;}
 if(v==2)audio_special_control(0);
 *(uint8_t*)0x2007502eu=!!v;*(uint32_t*)0x20074a9cu=0;
 if(v){audio_dsp_enable();audio_delay(50);audio_dsp_gate(1);audio_delay(50);audio_i2s_enable();audio_watchdog_start();}
 else{audio_watchdog_stop();audio_i2s_stop_selected();audio_delay(50);audio_dsp_gate(0);}
}
void audio_type1_selected(const audio_control_message *m){
 uint8_t v=(uint8_t)m->value;uint32_t primary=audio_role()==1&&!*(uint8_t*)0x20075019u;
 if(v){if(primary)audio_pdm_enable_primary();else audio_pdm_enable_alternate();}
 else audio_pdm_stop_prefix(primary);
}
void audio_control_dispatch_selected(const audio_control_message *m){
 if((uint16_t)m->type==0)audio_type0_selected(m);else if((uint16_t)m->type==1)audio_type1_selected(m);
}
