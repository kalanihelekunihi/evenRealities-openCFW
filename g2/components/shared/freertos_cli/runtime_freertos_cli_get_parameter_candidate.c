/*
 * FreeRTOS+CLI V1.0.4
 * Copyright (C) 2017 Amazon.com, Inc. or its affiliates.  All Rights Reserved.
 *
 * SPDX-License-Identifier: MIT
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to
 * deal in the Software without restriction, including without limitation the
 * rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 * Production-excluded isolated source candidate for the official
 * FreeRTOS+CLI V1.0.4-compatible FreeRTOS_CLIGetParameter() leaf.
 *
 * The selected source oracle is the authenticated upstream file at commit
 * 43defa566cc440251dbd6b48d1fcca27f88cfcdd.  The G2 stock body occupies
 * [0x005848FC, 0x00584960).  This file is deliberately not registered with a
 * production overlay, manifest, or Makefile recipe.
 */

#include "runtime_freertos_cli_get_parameter_candidate.h"

const char *open_cfw_freertos_cli_get_parameter_candidate(
    const char *pc_command,
    open_cfw_freertos_cli_ubase_type wanted_parameter,
    open_cfw_freertos_cli_base_type *parameter_length
)
{
    open_cfw_freertos_cli_ubase_type parameters_found = 0U;
    const char *result = (const char *)0;

    *parameter_length = 0;

    while (parameters_found < wanted_parameter) {
        while (*pc_command != '\0' && *pc_command != ' ') {
            pc_command++;
        }

        while (*pc_command != '\0' && *pc_command == ' ') {
            pc_command++;
        }

        if (*pc_command != '\0') {
            parameters_found++;

            if (parameters_found == wanted_parameter) {
                result = pc_command;
                while (*pc_command != '\0' && *pc_command != ' ') {
                    (*parameter_length)++;
                    pc_command++;
                }

                if (*parameter_length == 0) {
                    result = (const char *)0;
                }
                break;
            }
        } else {
            break;
        }
    }

    return result;
}
