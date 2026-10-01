/* Manual behavioral reconstruction, not original source or a firmware patch.
 * Geometry and packet assembly execute stock code in verify.py; DSP and LC3
 * bitstream generation are explicit external providers. Logging omitted.
 * Native pointers/structs are conceptual, not the stock 32-bit ABI.
 */
#include <stdint.h>
#include <stddef.h>
#include <string.h>
typedef void (*PcmCallback)(uint8_t,const void *,unsigned);
typedef struct {uint32_t app_id;uint8_t source,pad[3];PcmCallback callback;} Slot;
static Slot slots[2]; /* stock 12-byte slots at 0x20073C20 */
typedef struct {
 uint8_t format,pad[3];uint32_t duration_us,rate_hz,channels,channel,bitrate;
 void *encoder; /* stock +24; encoder workspace follows at +28 */
} Config;
extern Config config; /* initialized 0x20108948: 0,10000,16000,1,0,32000,0 */
extern int lc3_frame_samples(unsigned,unsigned),lc3_frame_bytes(unsigned,unsigned);
extern void *lc3_setup(unsigned,unsigned,unsigned,void *);
extern int lc3_encode(void *,unsigned,const void *,unsigned,unsigned,void *);
extern void *encoder_workspace(Config *);
/* 0x0057A900 */
unsigned sample_bytes(uint8_t format) {
 switch(format){case 0:return 2;case 1:return 4;case 2:return 3;case 3:return 4;default:return 0;}
}
/* 0x0057A940. Assumes a nonzero valid channel count and sufficient output
 * capacity: stock API has no output-capacity argument. */
int encode_pcm(const uint8_t *pcm,unsigned bytes,uint8_t *output,int *written,Config *c) {
 if(!pcm || !output || !written || !c)return -1;
 int samples=lc3_frame_samples(c->duration_us,c->rate_hz);
 int encoded=lc3_frame_bytes(c->duration_us,c->bitrate);
 if(samples<1 || encoded<20)return -1;
 unsigned width=sample_bytes(c->format);if(!width)return -1;
 if(!c->encoder)c->encoder=lc3_setup(c->duration_us,c->rate_hz,0,encoder_workspace(c));
 unsigned input_frame=width*c->channels*(unsigned)samples;
 if(bytes%input_frame)return -1; /* output length untouched on this error */
 *written=0;
 for(unsigned i=0;i<bytes/input_frame;i++) {
  const uint8_t *selected=pcm+(c->channels==1?0:width*c->channel);
  if(lc3_encode(c->encoder,c->format,selected,c->channels,(unsigned)encoded,output))return -1;
  pcm+=input_frame;output+=encoded;*written+=encoded;
 }
 return 0;
}
/* 0x0057AB78: replacement is allowed, not exclusive registration failure. */
int pcm_register(uint32_t app,uint8_t source,PcmCallback callback) {
 if(source>=2 || !callback)return -1;
 if(slots[source].callback)memset(&slots[source],0,sizeof(Slot));
 slots[source].app_id=app;slots[source].source=source;slots[source].callback=callback;return 0;
}
/* 0x0057ACD0: stock lacks the registration function's source<2 guard.
 * Caller must supply a valid source; do not expose this as a safe public API. */
int pcm_unregister(uint32_t app,uint8_t source) {
 if(!slots[source].callback)return 0;
 if(slots[source].app_id!=app)return -1;
 memset(&slots[source],0,sizeof(Slot));return 0;
}
extern void algorithm_process(const void *,unsigned,uint16_t *,int16_t *);
extern void front_buffer_get(const uint8_t **,unsigned *); /* 0x005915DC: 1600 bytes */
extern void streaming_notify(const void *,unsigned);
static uint8_t sequence; /* stock 0x2007500E */
/* 0x0057ADF8. A registered callback replaces the default processing path. */
void process_pcm(uint8_t source,const void *pcm,unsigned bytes) {
 if(source>=2 || !pcm || !bytes)return;
 if(slots[source].callback && slots[source].source==source) {
  slots[source].callback(source,pcm,bytes);return;
 }
 if(source!=0)return;
 uint8_t body[205]={0};uint16_t meta0=0;int16_t meta1=0;int written=0;
 const uint8_t *front=NULL;unsigned front_bytes=0;
 algorithm_process(pcm,bytes,&meta0,&meta1);front_buffer_get(&front,&front_bytes);
 (void)encode_pcm(front,front_bytes,body,&written,&config); /* result ignored */
 memcpy(body+written,&meta0,2);memcpy(body+written+2,&meta1,2); /* stock little endian */
 body[204]=sequence++;streaming_notify(body,205);
}
/* 0x00475D78: actual transport framing is beyond this boundary. */
extern int ota_transfer_active(void);
extern void transport_enqueue(unsigned,unsigned,unsigned,unsigned,const void *,uint16_t);
void streaming_notify(const void *body,unsigned bytes) {
 if(!ota_transfer_active())transport_enqueue(1,1,0,0,body,(uint16_t)bytes);
}
/* 0x0053C6F2: only source-0 DMA dispatch excerpt. Tick units are not renamed ms. */
extern uint32_t kernel_ticks(void);
extern void i2s_buffer_get(const void **,unsigned *);
void codec_dma_message(uint32_t queued_tick) {
 if((uint32_t)(kernel_ticks()-queued_tick)<41) {
  const void *pcm=NULL;unsigned bytes=0;i2s_buffer_get(&pcm,&bytes);process_pcm(0,pcm,bytes);
 }
}
