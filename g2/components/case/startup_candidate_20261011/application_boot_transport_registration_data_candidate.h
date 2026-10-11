/* SPDX-License-Identifier: MIT */
#ifndef CASE_BOOT_TRANSPORT_REGISTRATION_DATA_CANDIDATE_H
#define CASE_BOOT_TRANSPORT_REGISTRATION_DATA_CANDIDATE_H
#include <stdint.h>
typedef struct {const char *name;uint32_t field1,field2,field3;} TimerSpec;
typedef struct {const char *name;uint32_t field1,field2,field3,field4,stack_bytes,
                priority,field7,field8;} WorkerSpec;
typedef struct {const char *name;uint32_t field1,field2,field3,field4,field5,
                field6,field7,field8;} EventSpec;
typedef struct {TimerSpec timers[6];WorkerSpec workers[4];EventSpec event;} Registry;
extern const Registry case_boot_transport_registration_storage;
#endif
