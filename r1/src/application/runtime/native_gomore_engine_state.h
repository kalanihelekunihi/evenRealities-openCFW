#ifndef R1_NATIVE_GOMORE_ENGINE_STATE_H
#define R1_NATIVE_GOMORE_ENGINE_STATE_H
/* Native71714: initialize a0x1f8-byte header. */
void r1_gomore_native_engine_header_initialize(void *);
/* Native71db6: clear0x3894 bytes,bind previous at0x3890,initialize header. */
void r1_gomore_native_engine_state_initialize(void *,const void *);
#endif
