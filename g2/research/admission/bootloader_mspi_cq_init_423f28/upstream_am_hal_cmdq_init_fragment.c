// SPDX-License-Identifier: BSD-3-Clause
// Copyright (c) 2025, Ambiq Micro, Inc.
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
//
// 1. Redistributions of source code must retain the above copyright notice,
// this list of conditions and the following disclaimer.
//
// 2. Redistributions in binary form must reproduce the above copyright
// notice, this list of conditions and the following disclaimer in the
// documentation and/or other materials provided with the distribution.
//
// 3. Neither the name of the copyright holder nor the names of its
// contributors may be used to endorse or promote products derived from this
// software without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
// SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
// CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
// ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
// POSSIBILITY OF SUCH DAMAGE.
//
// Exact evidence fragment from AmbiqSuite SDK 5.1.0 am_hal_cmdq.c at commit
// 5efc0228528a8adce5eae0d226fac85d2551eb3b. This fragment is not compiled.

uint32_t
am_hal_cmdq_init(am_hal_cmdq_if_e hwIf, am_hal_cmdq_cfg_t *pCfg, void **ppHandle)
{
    am_hal_cmdq_t *pCmdQ;
#ifndef AM_HAL_DISABLE_API_VALIDATION
    if (hwIf >= AM_HAL_CMDQ_IF_MAX)
    {
        return AM_HAL_STATUS_OUT_OF_RANGE;
    }
    if (!pCfg || !pCfg->pCmdQBuf || !ppHandle || (pCfg->cmdQSize < 2))
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }
    if (gAmHalCmdq[hwIf].prefix.s.bInit)
    {
        return AM_HAL_STATUS_INVALID_OPERATION;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

#ifdef AM_HAL_CMDQ_RAM_TABLE
    am_hal_cmdq_init_registers();
#endif // AM_HAL_CMDQ_RAM_TABLE

    pCmdQ = &gAmHalCmdq[hwIf];
    pCmdQ->cmdQSize = pCfg->cmdQSize * sizeof(am_hal_cmdq_entry_t);
    pCmdQ->cmdQTail = pCmdQ->cmdQNextTail = pCmdQ->cmdQHead = pCmdQ->cmdQBufStart = (uint32_t)pCfg->pCmdQBuf;
    pCmdQ->cmdQBufEnd = (uint32_t)pCfg->pCmdQBuf + pCfg->cmdQSize * sizeof(am_hal_cmdq_entry_t);
    pCmdQ->prefix.s.bInit = true;
    pCmdQ->prefix.s.bEnable = false;
    pCmdQ->prefix.s.magic = AM_HAL_MAGIC_CMDQ;
    pCmdQ->pReg = &gAmHalCmdQReg[hwIf];
    pCmdQ->curIdx = 0;
    pCmdQ->endIdx = 0;
    AM_REGVAL(pCmdQ->pReg->regCurIdx) = 0;
    AM_REGVAL(pCmdQ->pReg->regEndIdx) = 0;
    AM_REGVAL(pCmdQ->pReg->regCQPause) |= pCmdQ->pReg->bitMaskCQPauseIdx;
    // Initialize the hardware registers
    AM_REGVAL(pCmdQ->pReg->regCQAddr) = (uint32_t)pCfg->pCmdQBuf;
    AM_HAL_CMDQ_INIT_CQCFG(pCmdQ->pReg->regCQCfg, pCfg->priority, false);
    *ppHandle = pCmdQ;
    return AM_HAL_STATUS_SUCCESS;
}
