/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOTLOADER_CONTROL_REQUEST_HELPERS_H
#define OPENCFW_BOOTLOADER_CONTROL_REQUEST_HELPERS_H

#include <stdint.h>

/* Stock 0x423e14: add the current descriptor-state flags and update mode. */
uint32_t opencfw_bl_control_stage_two_flags(uint32_t handle,
                                             uint32_t flags);

/* Stock 0x427c12: post one four-word command-queue descriptor. */
uint32_t opencfw_provider_427c12(uint32_t queue, uint32_t command_kind);

/* Stock 0x4279be: discard the most recent unpublished queue reservation. */
uint32_t opencfw_provider_4279be(uint32_t queue);

#endif
