/* SPDX-License-Identifier: MIT */
/* Lvp buffer accessors, reconstructed against pinned SDK field definitions. */
#include <lvp_context.h>
#define HEADER ((volatile LVP_CONTEXT_HEADER *)0x20027b60)
_Static_assert(sizeof(LVP_CONTEXT_HEADER) == 120, "Context header ABI");
void *open_cfw_gx8002_mic_buffer_addr(void) { return HEADER->mic_buffer; }
int open_cfw_gx8002_mic_buffer_size(void) { return HEADER->mic_buffer_size; }
void *open_cfw_gx8002_logfbank_buffer_addr(void) { return HEADER->logfbank_buffer; }
int open_cfw_gx8002_logfbank_buffer_size(void) { return HEADER->logfbank_buffer_size; }
void *open_cfw_gx8002_context_header(void) { return (void *)HEADER; }
void *open_cfw_gx8002_feats_buffer(void) { return (void *)0x20030000; }
