/*
 * Copyright (c) 2013-2022 Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may
 * not use this file except in compliance with the License. You may obtain
 * a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 *
 * Bounded, freestanding port of osMessageQueueDelete() from CMSIS-FreeRTOS
 * v10.5.1 cmsis_os2.c at commit
 * d213f261b5be6bb29a7cce8b84071706b72f4d53. The exact source blob first
 * appeared at commit 13acfbef7be85119fc6bc56832c455d4547d92c7.
 *
 * The official G2 entry is [0x00449BEC, 0x00449C14). The recovered
 * configQUEUE_REGISTRY_SIZE == 0 removes vQueueUnregisterQueue. Its only
 * dependencies are the already source-owned CMSIS IRQ classifier and
 * FreeRTOS vQueueDelete provider.
 */

typedef __UINT32_TYPE__ open_cfw_cmsis_mq_delete_uint32;
typedef __INT32_TYPE__ open_cfw_cmsis_mq_delete_status;
typedef void *open_cfw_cmsis_mq_delete_id;

enum {
    OPEN_CFW_CMSIS_MQ_DELETE_OK = 0,
    OPEN_CFW_CMSIS_MQ_DELETE_ERROR_PARAMETER = -4,
    OPEN_CFW_CMSIS_MQ_DELETE_ERROR_ISR = -6
};

_Static_assert(sizeof(open_cfw_cmsis_mq_delete_status) == 4U,
    "G2 CMSIS status width changed");

extern open_cfw_cmsis_mq_delete_uint32 open_cfw_cmsis_irq_context(void);
extern void open_cfw_freertos_queue_delete(open_cfw_cmsis_mq_delete_id queue);

__attribute__((used, noinline))
open_cfw_cmsis_mq_delete_status
open_cfw_cmsis_message_queue_delete(open_cfw_cmsis_mq_delete_id mq_id)
{
    open_cfw_cmsis_mq_delete_status status;

    if (open_cfw_cmsis_irq_context() != 0U) {
        status = OPEN_CFW_CMSIS_MQ_DELETE_ERROR_ISR;
    } else if (mq_id == (open_cfw_cmsis_mq_delete_id)0) {
        status = OPEN_CFW_CMSIS_MQ_DELETE_ERROR_PARAMETER;
    } else {
        status = OPEN_CFW_CMSIS_MQ_DELETE_OK;
        open_cfw_freertos_queue_delete(mq_id);
    }

    return status;
}
