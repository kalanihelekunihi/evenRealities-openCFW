/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_GX8002_BACKUP_RUNTIME_BOUNDARY_H
#define OPEN_CFW_GX8002_BACKUP_RUNTIME_BOUNDARY_H

#include "runtime_gx8002_kws_model_boundary.h"

#define OPEN_CFW_GX8002_BACKUP_RUNTIME_SIZE ((size_t)79132U)
#define OPEN_CFW_GX8002_BACKUP_RUNTIME_SHA256_HEX \
    "cd2ccdc2bca9decff0cc514d3cca6317c28ebdbe22891660f5d9ba00276ecdb3"

typedef open_cfw_gx8002_segment_provider_fn open_cfw_gx8002_backup_runtime_provider_fn;
typedef open_cfw_gx8002_segment_ports open_cfw_gx8002_backup_runtime_ports;

int32_t open_cfw_gx8002_backup_runtime_load(
    const open_cfw_gx8002_backup_runtime_ports *ports,
    uint8_t *destination,
    size_t capacity);

#endif
