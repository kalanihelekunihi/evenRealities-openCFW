/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_PCM_REGISTRATION_H
#define OPENCFW_PCM_REGISTRATION_H
#include <stdint.h>
typedef struct {uint32_t provider,stage;int32_t status;} opencfw_pcm_registration_cut_t;
/* provider0 means completed stock-like return;43d574/43ce9e means before
 * unimplemented logger. Stage1 invalid,2 replacement,3 published,4 empty,
 *5 owner mismatch,6 before clear. No lock or PCM ownership is introduced. */
void opencfw_pcm_register_prefix(uint32_t owner,uint32_t mode,uint32_t callback,opencfw_pcm_registration_cut_t *cut);
/* Faithful missing range guard: low-byte mode can address outside two rows.
 * Callers need mapped/aligned storage; this is not a safe public app API. */
void opencfw_pcm_unregister_prefix(uint32_t owner,uint32_t mode,opencfw_pcm_registration_cut_t *cut);
#endif
