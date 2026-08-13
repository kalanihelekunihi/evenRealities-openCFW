/*
 * Mechanical Ghidra 12.1.2 decompilation of the live R1 bootloader.
 * Base: 0x000f8000; logical bytes: 0x5f64; dump bytes: 0x6000.
 * This is analysis pseudocode, not a claim of source-level identity.
 */

#include <stdbool.h>
#include <stdint.h>

typedef uint8_t undefined1;
typedef uint16_t undefined2;
typedef uint32_t undefined4;
typedef uint64_t undefined8;
typedef uint8_t undefined;
typedef uint8_t byte;
typedef unsigned int uint;
typedef unsigned short ushort;
typedef unsigned long ulong;


/* ============================================================
 * entry: 000f8208
 * name: armcc_runtime_entry_veneer
 * body: 000f8208-000f820b
 * ============================================================ */

void armcc_runtime_entry_veneer(void)

{
  (*DAT_000f820c)();
  return;
}



/* ============================================================
 * entry: 000f8218
 * name: nrf_atfifo_wspace_req
 * body: 000f8218-000f824f
 * ============================================================ */

undefined4 nrf_atfifo_wspace_req(int param_1,uint *param_2)

{
  bool bVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;

  while( true ) {
    ExclusiveAccess((uint *)(param_1 + 4));
    uVar3 = *(uint *)(param_1 + 4);
    uVar4 = (uVar3 & 0xffff) + (uint)*(ushort *)(param_1 + 0xe);
    if (*(ushort *)(param_1 + 0xc) <= uVar4) {
      uVar4 = uVar4 - *(ushort *)(param_1 + 0xc);
    }
    if (uVar4 == *(ushort *)(param_1 + 8)) break;
    bVar1 = (bool)hasExclusiveAccess((uint *)(param_1 + 4));
    if (bVar1) {
      *(uint *)(param_1 + 4) = uVar4 & 0xffff | uVar3 & 0xffff0000;
      uVar2 = 1;
LAB_000f824a:
      *param_2 = uVar3;
      return uVar2;
    }
  }
  ClearExclusiveLocal();
  uVar2 = 0;
  goto LAB_000f824a;
}



/* ============================================================
 * entry: 000f8250
 * name: nrf_atfifo_wspace_close
 * body: 000f8250-000f8261
 * ============================================================ */

void nrf_atfifo_wspace_close(int param_1)

{
  bool bVar1;
  uint uVar2;

  do {
    ExclusiveAccess((uint *)(param_1 + 4));
    uVar2 = *(uint *)(param_1 + 4);
    bVar1 = (bool)hasExclusiveAccess((uint *)(param_1 + 4));
  } while (!bVar1);
  *(uint *)(param_1 + 4) = uVar2 & 0xffff | uVar2 << 0x10;
  return;
}



/* ============================================================
 * entry: 000f8262
 * name: nrf_atfifo_rspace_req
 * body: 000f8262-000f829b
 * ============================================================ */

undefined4 nrf_atfifo_rspace_req(int param_1,uint *param_2)

{
  bool bVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;

  do {
    ExclusiveAccess((uint *)(param_1 + 8));
    uVar3 = *(uint *)(param_1 + 8);
    if (uVar3 >> 0x10 == (uint)*(ushort *)(param_1 + 6)) {
      ClearExclusiveLocal();
      uVar2 = 0;
      goto LAB_000f8296;
    }
    uVar4 = (uVar3 >> 0x10) + (uint)*(ushort *)(param_1 + 0xe);
    if (*(ushort *)(param_1 + 0xc) <= uVar4) {
      uVar4 = uVar4 - *(ushort *)(param_1 + 0xc);
    }
    bVar1 = (bool)hasExclusiveAccess((uint *)(param_1 + 8));
  } while (!bVar1);
  *(uint *)(param_1 + 8) = uVar3 & 0xffff | uVar4 << 0x10;
  uVar2 = 1;
LAB_000f8296:
  *param_2 = uVar3;
  return uVar2;
}



/* ============================================================
 * entry: 000f829c
 * name: nrf_atfifo_rspace_close
 * body: 000f829c-000f82ad
 * ============================================================ */

void nrf_atfifo_rspace_close(int param_1)

{
  bool bVar1;
  uint uVar2;

  do {
    ExclusiveAccess((uint *)(param_1 + 8));
    uVar2 = *(uint *)(param_1 + 8);
    bVar1 = (bool)hasExclusiveAccess((uint *)(param_1 + 8));
  } while (!bVar1);
  *(uint *)(param_1 + 8) = uVar2 & 0xffff0000 | (int)uVar2 >> 0x10 & 0xffffU;
  return;
}



/* ============================================================
 * entry: 000f82ae
 * name: nrf_atfifo_space_clear
 * body: 000f82ae-000f82df
 * ============================================================ */

undefined4 nrf_atfifo_space_clear(int param_1)

{
  ushort uVar1;
  bool bVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uVar5;

  do {
    ExclusiveAccess((uint *)(param_1 + 8));
    uVar4 = *(uint *)(param_1 + 8);
    uVar1 = *(ushort *)(param_1 + 6);
    uVar3 = 0;
    if (uVar4 == (uVar4 >> 0x10 | uVar4 << 0x10)) {
      uVar4 = CONCAT22(uVar1,uVar1);
      uVar5 = *(uint *)(param_1 + 4);
      if (uVar5 == (uVar5 >> 0x10 | uVar5 << 0x10)) {
        uVar3 = 1;
      }
    }
    else {
      uVar4 = uVar4 & 0xffff | (uint)uVar1 << 0x10;
    }
    bVar2 = (bool)hasExclusiveAccess((uint *)(param_1 + 8));
  } while (!bVar2);
  *(uint *)(param_1 + 8) = uVar4;
  return uVar3;
}



/* ============================================================
 * entry: 000f82e0
 * name: nrf_atomic_internal_mov
 * body: 000f82e0-000f82f7
 * ============================================================ */

undefined4 nrf_atomic_internal_mov(undefined4 *param_1,undefined4 param_2,undefined4 *param_3)

{
  bool bVar1;
  undefined4 uVar2;

  do {
    ExclusiveAccess(param_1);
    uVar2 = *param_1;
    bVar1 = (bool)hasExclusiveAccess(param_1);
  } while (!bVar1);
  *param_1 = param_2;
  *param_3 = param_2;
  return uVar2;
}



/* ============================================================
 * entry: 000f82f8
 * name: nrf_atomic_internal_orr
 * body: 000f82f8-000f8311
 * ============================================================ */

void nrf_atomic_internal_orr(uint *param_1,uint param_2,uint *param_3)

{
  bool bVar1;
  uint uVar2;

  do {
    ExclusiveAccess(param_1);
    uVar2 = *param_1;
    bVar1 = (bool)hasExclusiveAccess(param_1);
  } while (!bVar1);
  *param_1 = uVar2 | param_2;
  *param_3 = uVar2 | param_2;
  return;
}



/* ============================================================
 * entry: 000f8312
 * name: nrf_atomic_internal_and
 * body: 000f8312-000f832b
 * ============================================================ */

void nrf_atomic_internal_and(uint *param_1,uint param_2,uint *param_3)

{
  bool bVar1;
  uint uVar2;

  do {
    ExclusiveAccess(param_1);
    uVar2 = *param_1;
    bVar1 = (bool)hasExclusiveAccess(param_1);
  } while (!bVar1);
  *param_1 = uVar2 & param_2;
  *param_3 = uVar2 & param_2;
  return;
}



/* ============================================================
 * entry: 000f832c
 * name: nrf_atomic_internal_eor
 * body: 000f832c-000f8345
 * ============================================================ */

void nrf_atomic_internal_eor(uint *param_1,uint param_2,uint *param_3)

{
  bool bVar1;
  uint uVar2;

  do {
    ExclusiveAccess(param_1);
    uVar2 = *param_1;
    bVar1 = (bool)hasExclusiveAccess(param_1);
  } while (!bVar1);
  *param_1 = uVar2 ^ param_2;
  *param_3 = uVar2 ^ param_2;
  return;
}



/* ============================================================
 * entry: 000f8346
 * name: nrf_atomic_internal_add
 * body: 000f8346-000f835f
 * ============================================================ */

void nrf_atomic_internal_add(int *param_1,int param_2,int *param_3)

{
  bool bVar1;
  int iVar2;

  do {
    ExclusiveAccess(param_1);
    iVar2 = *param_1;
    bVar1 = (bool)hasExclusiveAccess(param_1);
  } while (!bVar1);
  *param_1 = iVar2 + param_2;
  *param_3 = iVar2 + param_2;
  return;
}



/* ============================================================
 * entry: 000f8360
 * name: nrf_atomic_internal_sub
 * body: 000f8360-000f8379
 * ============================================================ */

void nrf_atomic_internal_sub(int *param_1,int param_2,int *param_3)

{
  bool bVar1;
  int iVar2;

  do {
    ExclusiveAccess(param_1);
    iVar2 = *param_1;
    bVar1 = (bool)hasExclusiveAccess(param_1);
  } while (!bVar1);
  *param_1 = iVar2 - param_2;
  *param_3 = iVar2 - param_2;
  return;
}



/* ============================================================
 * entry: 000f837a
 * name: nrf_atomic_internal_cmp_exch
 * body: 000f837a-000f83a3
 * ============================================================ */

undefined4 nrf_atomic_internal_cmp_exch(int *param_1,int *param_2,int param_3,int param_4)

{
  bool bVar1;
  undefined4 uVar2;
  int iVar3;
  bool bVar4;

  do {
    uVar2 = 0;
    ExclusiveAccess(param_1);
    iVar3 = *param_1;
    bVar4 = iVar3 == *param_2;
    if (bVar4) {
      bVar1 = (bool)hasExclusiveAccess(param_1);
      param_4 = 1;
      if (bVar1) {
        param_4 = 0;
        *param_1 = param_3;
      }
    }
    if (bVar4) {
      uVar2 = 1;
    }
    else {
      bVar1 = (bool)hasExclusiveAccess(param_1);
      param_4 = 1;
      if (bVar1) {
        param_4 = 0;
        *param_1 = iVar3;
      }
    }
    if (!bVar4) {
      *param_2 = iVar3;
    }
  } while (param_4 != 0);
  return uVar2;
}



/* ============================================================
 * entry: 000f83a4
 * name: nrf_atomic_internal_sub_hs
 * body: 000f83a4-000f83c1
 * ============================================================ */

void nrf_atomic_internal_sub_hs(uint *param_1,uint param_2,uint *param_3)

{
  bool bVar1;
  uint uVar2;

  do {
    ExclusiveAccess(param_1);
    uVar2 = *param_1;
    if (param_2 <= uVar2) {
      uVar2 = uVar2 - param_2;
    }
    bVar1 = (bool)hasExclusiveAccess(param_1);
  } while (!bVar1);
  *param_1 = uVar2;
  *param_3 = uVar2;
  return;
}



/* ============================================================
 * entry: 000f83c4
 * name: SVC_Handler
 * body: 000f83c4-000f83d5
 * ============================================================ */

void SVC_Handler(void)

{
  undefined4 uVar1;
  uint unaff_lr;

  if ((unaff_lr & 4) == 0) {
    uVar1 = getMainStackPointer();
  }
  else {
    uVar1 = getProcessStackPointer();
  }
  nrf_svc_handler_c(uVar1);
  return;
}



/* ============================================================
 * entry: 000f83d8
 * name: Reset_Handler
 * body: 000f83d8-000f83df
 * ============================================================ */

void Reset_Handler(void)

{
  (*DAT_000f83f4)();
                    /* WARNING: Could not recover jumptable at 0x000f83de. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*DAT_000f83f8)();
  return;
}



/* ============================================================
 * entry: 000f83e0
 * name: NMI_Handler
 * body: 000f83e0-000f83e1
 * ============================================================ */

void NMI_Handler(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* ============================================================
 * entry: 000f83e2
 * name: HardFault_Handler
 * body: 000f83e2-000f83e3
 * ============================================================ */

void HardFault_Handler(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* ============================================================
 * entry: 000f83e4
 * name: MemoryManagement_Handler
 * body: 000f83e4-000f83e5
 * ============================================================ */

void MemoryManagement_Handler(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* ============================================================
 * entry: 000f83e6
 * name: BusFault_Handler
 * body: 000f83e6-000f83e7
 * ============================================================ */

void BusFault_Handler(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* ============================================================
 * entry: 000f83e8
 * name: UsageFault_Handler
 * body: 000f83e8-000f83e9
 * ============================================================ */

void UsageFault_Handler(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* ============================================================
 * entry: 000f83ec
 * name: DebugMon_Handler
 * body: 000f83ec-000f83ed
 * ============================================================ */

void DebugMon_Handler(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* ============================================================
 * entry: 000f83ee
 * name: PendSV_Handler
 * body: 000f83ee-000f83ef
 * ============================================================ */

void PendSV_Handler(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* ============================================================
 * entry: 000f83f0
 * name: SysTick_Handler
 * body: 000f83f0-000f83f1
 * ============================================================ */

void SysTick_Handler(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* ============================================================
 * entry: 000f83f2
 * name: Default_Handler
 * body: 000f83f2-000f83f3
 * ============================================================ */

void Default_Handler(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* ============================================================
 * entry: 000f83fc
 * name: armcc_runtime_lsl64
 * body: 000f83fc-000f8419
 * ============================================================ */

longlong armcc_runtime_lsl64(uint param_1,int param_2,uint param_3)

{
  if (0x1f < (int)param_3) {
    return (ulonglong)(param_1 << (param_3 - 0x20 & 0xff)) << 0x20;
  }
  return CONCAT44(param_2 << (param_3 & 0xff) | param_1 >> (0x20 - param_3 & 0xff),
                  param_1 << (param_3 & 0xff));
}



/* ============================================================
 * entry: 000f841a
 * name: memmove
 * body: 000f841a-000f845b
 * ============================================================ */

void memmove(undefined4 *param_1,undefined4 *param_2,uint param_3)

{
  undefined1 *puVar1;
  undefined1 *puVar2;
  undefined4 uVar3;
  bool bVar4;

  if (param_3 <= (uint)((int)param_1 - (int)param_2)) {
    if ((((uint)param_1 | (uint)param_2) & 3) == 0) {
      for (; 3 < param_3; param_3 = param_3 - 4) {
        uVar3 = *param_2;
        param_2 = param_2 + 1;
        *param_1 = uVar3;
        param_1 = param_1 + 1;
      }
    }
    while (bVar4 = param_3 != 0, param_3 = param_3 - 1, bVar4) {
      *(undefined1 *)param_1 = *(undefined1 *)param_2;
      param_2 = (undefined4 *)((int)param_2 + 1);
      param_1 = (undefined4 *)((int)param_1 + 1);
    }
    return;
  }
  puVar2 = (undefined1 *)((int)param_1 + param_3);
  puVar1 = (undefined1 *)((int)param_2 + param_3);
  while (bVar4 = param_3 != 0, param_3 = param_3 - 1, bVar4) {
    puVar1 = puVar1 + -1;
    puVar2 = puVar2 + -1;
    *puVar2 = *puVar1;
  }
  return;
}



/* ============================================================
 * entry: 000f845c
 * name: armcc_memset_core
 * body: 000f845c-000f8469
 * ============================================================ */

void armcc_memset_core(undefined1 *param_1,int param_2,undefined1 param_3)

{
  bool bVar1;

  while (bVar1 = param_2 != 0, param_2 = param_2 + -1, bVar1) {
    *param_1 = param_3;
    param_1 = param_1 + 1;
  }
  return;
}



/* ============================================================
 * entry: 000f846a
 * name: armcc_memclr
 * body: 000f846a-000f846d
 * ============================================================ */

void armcc_memclr(undefined4 param_1,undefined4 param_2)

{
  armcc_memset_core(param_1,param_2,0);
  return;
}



/* ============================================================
 * entry: 000f846e
 * name: memset
 * body: 000f846e-000f847f
 * ============================================================ */

undefined4 memset(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  armcc_memset_core(param_1,param_3,param_2);
  return param_1;
}



/* ============================================================
 * entry: 000f8480
 * name: strlen
 * body: 000f8480-000f848d
 * ============================================================ */

int strlen(char *param_1)

{
  char cVar1;
  char *pcVar2;
  char *pcVar3;

  pcVar3 = param_1;
  do {
    pcVar2 = pcVar3 + 1;
    cVar1 = *pcVar3;
    pcVar3 = pcVar2;
  } while (cVar1 != '\0');
  return (int)pcVar2 - (int)(param_1 + 1);
}



/* ============================================================
 * entry: 000f848e
 * name: memcmp
 * body: 000f848e-000f84a7
 * ============================================================ */

void memcmp(int param_1,int param_2,uint param_3)

{
  uint uVar1;

  for (uVar1 = 0; (uVar1 < param_3 && (*(char *)(param_1 + uVar1) == *(char *)(param_2 + uVar1)));
      uVar1 = uVar1 + 1) {
  }
  return;
}



/* ============================================================
 * entry: 000f84a8
 * name: strncmp
 * body: 000f84a8-000f84c5
 * ============================================================ */

void strncmp(int param_1,int param_2,uint param_3)

{
  uint uVar1;

  for (uVar1 = 0;
      ((uVar1 < param_3 && (*(char *)(param_1 + uVar1) == *(char *)(param_2 + uVar1))) &&
      (*(char *)(param_1 + uVar1) != '\0')); uVar1 = uVar1 + 1) {
  }
  return;
}



/* ============================================================
 * entry: 000f84c8
 * name: armcc_scatterload
 * body: 000f84c8-000f84e5
 * ============================================================ */

void armcc_scatterload(void)

{
  code *pcVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;

  puVar2 = DAT_000f84e8;
  for (puVar3 = puRam000f84e4; puVar3 < puVar2; puVar3 = puVar3 + 4) {
    (*(code *)puVar3[3])(*puVar3,puVar3[1],puVar3[2]);
  }
  armcc_runtime_entry_veneer();
                    /* WARNING: Does not return */
  pcVar1 = (code *)software_udf(0x1c,0xf84e4);
  (*pcVar1)();
}



/* ============================================================
 * entry: 000f84ec
 * name: CRYPTOCELL_IRQHandler
 * body: 000f84ec-000f8503
 * ============================================================ */

void CRYPTOCELL_IRQHandler(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;

  puVar1 = DAT_000f8504;
  *DAT_000f8504 = 0xffffffff;
  puVar2 = DAT_000f8508;
  *DAT_000f8508 = puVar1[-1];
  *DAT_000f850c = *puVar2;
  return;
}



/* ============================================================
 * entry: 000f8510
 * name: CRYS_COMMON_ReverseMemcpy32
 * body: 000f8510-000f8529
 * ============================================================ */

undefined4 CRYS_COMMON_ReverseMemcpy32(int param_1,uint *param_2,int param_3)

{
  uint *puVar1;
  uint *puVar2;
  uint uVar3;

  puVar2 = param_2 + param_3;
  puVar1 = (uint *)(param_1 + -4);
  while (puVar2 != param_2) {
    puVar2 = puVar2 + -1;
    uVar3 = *puVar2;
    puVar1 = puVar1 + 1;
    *puVar1 = uVar3 << 0x18 | (uVar3 >> 8 & 0xff) << 0x10 | (uVar3 >> 0x10 & 0xff) << 8 |
              uVar3 >> 0x18;
  }
  return 0;
}



/* ============================================================
 * entry: 000f852c
 * name: PkaAddAff
 * body: 000f852c-000f8603
 * ============================================================ */

void PkaAddAff(void)

{
  int *piVar1;
  undefined4 *puVar2;
  undefined4 uVar3;

  puVar2 = DAT_000f8608;
  piVar1 = DAT_000f8604;
  do {
  } while (-1 < *DAT_000f8604 << 0x1f);
  *DAT_000f8608 = DAT_000f860c;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8610;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8614;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8618;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f861c;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8620;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8624;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8628;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f862c;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8630;
  uVar3 = DAT_000f8634;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8634;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = uVar3;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8638;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f863c;
  PkaJcb2Afn(0,0xe,0xf,0xd);
  return;
}



/* ============================================================
 * entry: 000f8640
 * name: PkaAddJcbAfn2Mdf
 * body: 000f8640-000f8781
 * ============================================================ */

void PkaAddJcbAfn2Mdf(int param_1,int param_2)

{
  int *piVar1;
  uint *puVar2;
  uint uVar3;

  puVar2 = DAT_000f8788;
  piVar1 = DAT_000f8784;
  do {
  } while (-1 < *DAT_000f8784 << 0x1f);
  *DAT_000f8788 = DAT_000f878c;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8790;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8794 | param_1 << 0x12;
  uVar3 = DAT_000f8798;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8798;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = uVar3 - 0x400000 | param_2 << 0x12;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f879c;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f87a0;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f87a4;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f87a8;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f87ac;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f87b0;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f87b4;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f87b8;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f87bc;
  uVar3 = DAT_000f87c0;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f87c0;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = uVar3;
  puVar2 = DAT_000f8788;
  piVar1 = DAT_000f8784;
  do {
  } while (-1 < *DAT_000f8784 << 0x1f);
  *DAT_000f8788 = DAT_000f87c4;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f87c8;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f878c;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f87cc;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f87d0;
  return;
}



/* ============================================================
 * entry: 000f87d4
 * name: PkaClearBlockOfRegs
 * body: 000f87d4-000f88fb
 * ============================================================ */

void PkaClearBlockOfRegs(int param_1,uint param_2,int param_3)

{
  uint *puVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;

  puVar4 = DAT_000f890c;
  puVar2 = DAT_000f8904;
  puVar1 = DAT_000f88fc;
  do {
  } while (-1 < (int)(*DAT_000f88fc << 0x1f));
  if (0x1e < param_2 + param_1) {
    param_2 = 0x1e - param_1;
  }
  uVar9 = *(int *)((DAT_000f8900 + param_3) * 4) + 0x1fU >> 5;
  uVar6 = uVar9 * (param_2 + param_1);
  if (0x400 < uVar6) {
    param_2 = 0x400;
  }
  iVar7 = 0;
  if (0x400 < uVar6) {
    param_2 = param_2 / uVar9 - param_1;
  }
  param_1 = param_1 << 2;
  for (; puVar5 = DAT_000f890c, puVar3 = DAT_000f8904, iVar7 < (int)param_2; iVar7 = iVar7 + 1) {
    do {
    } while (-1 < (int)(*puVar1 << 0x1f));
    do {
    } while ((*puVar1 & 1) == 0);
    *puVar4 = *(undefined4 *)(param_1 + 0x5002b000);
    for (uVar6 = 0; uVar8 = uVar9, uVar6 != uVar9; uVar6 = uVar6 + 1) {
      *puVar2 = 0;
    }
    for (; uVar8 < (uVar9 + 1 & 0xfffffffe); uVar8 = uVar8 + 1) {
      *puVar2 = 0;
    }
    param_1 = param_1 + 4;
  }
  do {
  } while (-1 < (int)(*puVar1 << 0x1f));
  do {
  } while (-1 < (int)(*puVar1 << 0x1f));
  *DAT_000f890c = *DAT_000f8908;
  for (uVar6 = 0; puVar2 = DAT_000f8904, uVar6 != uVar9; uVar6 = uVar6 + 1) {
    *puVar3 = 0;
  }
  uVar8 = uVar9 + 1 & 0xfffffffe;
  for (uVar6 = uVar9; uVar6 < uVar8; uVar6 = uVar6 + 1) {
    *puVar2 = 0;
  }
  do {
  } while (-1 < (int)(*puVar1 << 0x1f));
  do {
  } while (-1 < (int)(*puVar1 << 0x1f));
  *puVar5 = *DAT_000f8910;
  puVar2 = DAT_000f8904;
  for (uVar6 = 0; puVar4 = DAT_000f8904, uVar6 != uVar9; uVar6 = uVar6 + 1) {
    *puVar2 = 0;
  }
  for (; uVar9 < uVar8; uVar9 = uVar9 + 1) {
    *puVar4 = 0;
  }
  return;
}



/* ============================================================
 * entry: 000f8914
 * name: PkaCopyDataIntoPkaReg
 * body: 000f8914-000f89bd
 * ============================================================ */

void PkaCopyDataIntoPkaReg(int param_1,int param_2,undefined4 *param_3,uint param_4)

{
  int *piVar1;
  int *piVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  undefined4 *puVar8;

  puVar3 = DAT_000f89c8;
  piVar2 = DAT_000f89c4;
  piVar1 = DAT_000f89c0;
  do {
  } while (-1 < *DAT_000f89c0 << 0x1f);
  iVar7 = *(int *)((param_1 + 0x1400ac00) * 4);
  do {
  } while (-1 < *DAT_000f89c0 << 0x1f);
  *DAT_000f89c4 = iVar7;
  puVar8 = param_3 + param_4;
  for (; puVar4 = DAT_000f89c8, param_3 != puVar8; param_3 = param_3 + 1) {
    *puVar3 = *param_3;
  }
  uVar6 = param_4 + 1 & 0xfffffffe;
  for (; puVar3 = DAT_000f89c8, param_4 < uVar6; param_4 = param_4 + 1) {
    *puVar4 = 0;
  }
  do {
  } while (-1 < *piVar1 << 0x1f);
  uVar5 = *(int *)((DAT_000f89cc + param_2) * 4) + 0x1f;
  if (uVar6 < uVar5 >> 5) {
    do {
    } while (-1 < *piVar1 << 0x1f);
    uVar5 = (uVar5 >> 5) - uVar6;
    *piVar2 = iVar7 + uVar6;
    for (uVar6 = 0; puVar8 = DAT_000f89c8, uVar6 < uVar5; uVar6 = uVar6 + 1) {
      *puVar3 = 0;
    }
    uVar6 = uVar5 + 1;
    for (; uVar5 < (uVar6 & 0xfffffffe); uVar5 = uVar5 + 1) {
      *puVar8 = 0;
    }
  }
  return;
}



/* ============================================================
 * entry: 000f89d0
 * name: PkaDoubleMdf2Jcb
 * body: 000f89d0-000f8af7
 * ============================================================ */

void PkaDoubleMdf2Jcb(void)

{
  int *piVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  undefined4 uVar4;

  puVar2 = DAT_000f8afc;
  piVar1 = DAT_000f8af8;
  do {
  } while (-1 < *DAT_000f8af8 << 0x1f);
  *DAT_000f8afc = DAT_000f8b00;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8b04;
  uVar3 = DAT_000f8b08;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8b08;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8b0c;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8b10;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8b14;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8b18;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8b1c;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8b20;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8b24;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8b28;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8b2c;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8b30;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8b34;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8b38;
  uVar4 = DAT_000f8b3c;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8b3c;
  puVar2 = DAT_000f8afc;
  piVar1 = DAT_000f8af8;
  do {
  } while (-1 < *DAT_000f8af8 << 0x1f);
  *DAT_000f8afc = uVar3;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = uVar4;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8b40;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8b44;
  return;
}



/* ============================================================
 * entry: 000f8b48
 * name: PkaDoubleMdf2Mdf
 * body: 000f8b48-000f8c99
 * ============================================================ */

void PkaDoubleMdf2Mdf(void)

{
  int *piVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  undefined4 uVar4;

  puVar2 = DAT_000f8ca0;
  piVar1 = DAT_000f8c9c;
  do {
  } while (-1 < *DAT_000f8c9c << 0x1f);
  *DAT_000f8ca0 = DAT_000f8ca4;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8ca8;
  uVar3 = DAT_000f8cac;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8cac;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8cb0;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8cb4;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8cb8;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8cbc;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8cc0;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8cc4;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8cc8;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8ccc;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8cd0;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8cd4;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8cd8;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8cdc;
  uVar4 = DAT_000f8ce0;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8ce0;
  puVar2 = DAT_000f8ca0;
  piVar1 = DAT_000f8c9c;
  do {
  } while (-1 < *DAT_000f8c9c << 0x1f);
  *DAT_000f8ca0 = uVar3;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = uVar4;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8ca4;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8ce4;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8ce8;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8cec;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f8cf0;
  return;
}



/* ============================================================
 * entry: 000f8cf4
 * name: PkaEcdsaVerify
 * body: 000f8cf4-000f8f05
 * ============================================================ */

int PkaEcdsaVerify(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  int *piVar3;
  uint *puVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  int iVar7;
  uint uVar8;
  int *piVar9;
  undefined4 uVar10;

  puVar2 = DAT_000f8f0c;
  uVar10 = *DAT_000f8f08;
  uVar6 = DAT_000f8f08[2];
  piVar9 = DAT_000f8f08 + 8;
  do {
  } while (-1 < *piVar9 << 0x1f);
  *DAT_000f8f0c = DAT_000f8f10;
  do {
  } while (-1 < *piVar9 << 0x1f);
  *puVar2 = DAT_000f8f14;
  puVar4 = DAT_000f8f1c;
  piVar3 = DAT_000f8f18;
  do {
  } while (-1 < *DAT_000f8f18 << 0x1f);
  uVar8 = *DAT_000f8f1c;
  do {
  } while (-1 < *piVar9 << 0x1f);
  *puVar2 = DAT_000f8f20;
  do {
  } while (-1 < *piVar3 << 0x1f);
  iVar7 = DAT_000f8f78;
  if (((int)(uVar8 << 0x16) < 0) && ((int)(*puVar4 << 0x16) < 0)) {
    do {
    } while (-1 < *piVar9 << 0x1f);
    *puVar2 = DAT_000f8f24;
    do {
    } while (-1 < *piVar3 << 0x1f);
    uVar8 = *puVar4;
    do {
    } while (-1 < *piVar9 << 0x1f);
    *puVar2 = DAT_000f8f28;
    do {
    } while (-1 < *piVar3 << 0x1f);
    iVar7 = DAT_000f8f7c;
    if (((int)(uVar8 << 0x16) < 0) && ((int)(*puVar4 << 0x16) < 0)) {
      do {
      } while (-1 < *piVar9 << 0x1f);
      *puVar2 = DAT_000f8f10;
      uVar5 = DAT_000f8f2c;
      do {
      } while (-1 < *piVar9 << 0x1f);
      *puVar2 = DAT_000f8f2c;
      do {
      } while (-1 < *piVar9 << 0x1f);
      *puVar2 = DAT_000f8f30;
      do {
      } while (-1 < *piVar9 << 0x1f);
      *puVar2 = DAT_000f8f34;
      do {
      } while (-1 < *piVar9 << 0x1f);
      *puVar2 = DAT_000f8f38;
      do {
      } while (-1 < *piVar9 << 0x1f);
      *puVar2 = DAT_000f8f3c;
      piVar9 = DAT_000f8f40;
      puVar2 = DAT_000f8f0c;
      do {
      } while (-1 < *DAT_000f8f40 << 0x1f);
      *DAT_000f8f0c = DAT_000f8f44;
      do {
      } while (-1 < *piVar9 << 0x1f);
      *puVar2 = DAT_000f8f48;
      do {
      } while (-1 < *piVar9 << 0x1f);
      *puVar2 = DAT_000f8f4c;
      piVar3 = DAT_000f8f18;
      puVar1 = DAT_000f8f08;
      do {
      } while (-1 < *DAT_000f8f18 << 0x1f);
      *DAT_000f8f08 = uVar6;
      do {
      } while (-1 < *piVar9 << 0x1f);
      *puVar2 = uVar5;
      do {
      } while (-1 < *piVar9 << 0x1f);
      *puVar2 = DAT_000f8f50;
      do {
      } while (-1 < *piVar9 << 0x1f);
      *puVar2 = DAT_000f8f54;
      do {
      } while (-1 < *piVar9 << 0x1f);
      *puVar2 = DAT_000f8f58;
      do {
      } while (-1 < *piVar9 << 0x1f);
      *puVar2 = DAT_000f8f5c;
      do {
      } while (-1 < *piVar9 << 0x1f);
      *puVar2 = DAT_000f8f60;
      do {
      } while (-1 < *piVar9 << 0x1f);
      *puVar2 = DAT_000f8f64;
      do {
      } while (-1 < *piVar9 << 0x1f);
      *puVar2 = DAT_000f8f68;
      iVar7 = PkaSum2ScalarMullt();
      if (iVar7 == 0) {
        do {
        } while (-1 < *piVar3 << 0x1f);
        *puVar1 = uVar10;
        do {
        } while (-1 < *piVar9 << 0x1f);
        *puVar2 = DAT_000f8f6c;
        do {
        } while (-1 < *piVar9 << 0x1f);
        *puVar2 = DAT_000f8f70;
        do {
        } while (-1 < *piVar3 << 0x1f);
        if ((*DAT_000f8f1c & 0x1000) == 0) {
          iVar7 = DAT_000f8f74;
        }
      }
    }
  }
  return iVar7;
}



/* ============================================================
 * entry: 000f8f80
 * name: PkaFinishAndMutexUnlock
 * body: 000f8f80-000f8f9d
 * ============================================================ */

void PkaFinishAndMutexUnlock(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  if (param_1 != 0) {
    if (0x1f < param_1) {
      param_1 = 0x20;
    }
    PkaClearBlockOfRegs(0,param_1,7,param_4,param_4);
  }
  *DAT_000f8fa0 = 0;
  return;
}



/* ============================================================
 * entry: 000f8fa4
 * name: PkaGetNextMsBit
 * body: 000f8fa4-000f900b
 * ============================================================ */

uint PkaGetNextMsBit(int param_1,uint param_2,uint *param_3,int *param_4)

{
  uint uVar1;

  if ((*param_4 != 0) || ((param_2 & 0x1f) == 0x1f)) {
    do {
    } while (-1 < *DAT_000f900c << 0x1f);
    do {
    } while (-1 < *DAT_000f900c << 0x1f);
    *DAT_000f9010 = *(int *)((param_1 + 0x1400ac00) * 4) + ((int)param_2 >> 5);
    if ((param_2 & 0x1f) == 0x1f) {
      *param_3 = *DAT_000f9014;
    }
    else {
      *param_3 = *DAT_000f9014 << (~param_2 & 0x1f);
    }
    *param_4 = 0;
  }
  uVar1 = *param_3;
  *param_3 = uVar1 << 1;
  return uVar1 >> 0x1f;
}



/* ============================================================
 * entry: 000f9018
 * name: PkaGetRegEffectiveSizeInBits
 * body: 000f9018-000f9097
 * ============================================================ */

void PkaGetRegEffectiveSizeInBits(int param_1)

{
  int *piVar1;
  int *piVar2;
  uint *puVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;

  puVar3 = DAT_000f90a4;
  piVar2 = DAT_000f90a0;
  piVar1 = DAT_000f9098;
  do {
  } while (-1 < *DAT_000f9098 << 0x1f);
  iVar6 = *(int *)((param_1 + 0x1400ac00) * 4);
  do {
  } while (-1 < *DAT_000f9098 << 0x1f);
  iVar4 = *DAT_000f909c + 0x1f;
  if (iVar4 < 0) {
    iVar4 = *DAT_000f909c + 0x3e;
  }
  iVar4 = iVar4 >> 5;
  do {
    iVar5 = iVar4;
    iVar4 = iVar5 + -1;
    if (iVar4 < 0) {
      uVar8 = 0;
      break;
    }
    do {
    } while (-1 < *piVar1 << 0x1f);
    *piVar2 = iVar4 + iVar6;
    uVar8 = *puVar3;
  } while (uVar8 == 0);
  iVar5 = iVar5 * 0x20;
  if (uVar8 != 0) {
    iVar6 = iVar5 + -0x20;
    uVar7 = 0x80000000;
    do {
      if ((uVar8 & uVar7) != 0) {
        return;
      }
      iVar5 = iVar5 + -1;
      uVar7 = uVar7 >> 1;
    } while (iVar5 != iVar6);
  }
  return;
}



/* ============================================================
 * entry: 000f90a8
 * name: PkaInitPka
 * body: 000f90a8-000f911b
 * ============================================================ */

/* WARNING: Removing unreachable block (ram,0x000f90de) */
/* WARNING: Removing unreachable block (ram,0x000f90e2) */

undefined4 PkaInitPka(uint param_1,uint *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  uint uVar3;
  int iVar4;

  uVar2 = DAT_000f9120;
  if (param_1 - 0x20 < 0xc21) {
    if (param_1 < 0x90) {
      uVar3 = param_1 + 0x66 >> 5;
      if ((param_1 + 0x47 & 0x1f) != 0) {
        uVar3 = uVar3 + 1;
      }
    }
    else {
      uVar3 = param_1 + 0x1f >> 5;
    }
    iVar4 = (uVar3 * 0x20 + 0x3f >> 6) + 1;
    uVar3 = 0x1000 / (uint)(iVar4 * 8);
    if (0x1f < uVar3) {
      uVar3 = 0x20;
    }
    if (param_2 != (uint *)0x0) {
      *param_2 = uVar3;
    }
    puVar1 = DAT_000f911c;
    *DAT_000f911c = 1;
    PkaSetRegsMapTab(uVar3,iVar4,1,puVar1,param_4);
    PkaSetRegsSizesTab(param_1,iVar4);
    uVar2 = 0;
  }
  return uVar2;
}



/* ============================================================
 * entry: 000f9124
 * name: PkaJcb2Afn
 * body: 000f9124-000f91bf
 * ============================================================ */

void PkaJcb2Afn(undefined4 param_1,int param_2,int param_3,int param_4)

{
  int *piVar1;
  uint *puVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;

  puVar2 = DAT_000f91c4;
  piVar1 = DAT_000f91c0;
  do {
  } while (-1 < *DAT_000f91c0 << 0x1f);
  *DAT_000f91c4 = DAT_000f91c8;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f91cc | param_4 << 0x12;
  uVar4 = param_3 << 6 | param_3 << 0x12;
  uVar5 = uVar4 | 0x90006000;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = uVar5;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = DAT_000f91d0;
  uVar3 = param_2 << 6 | param_2 << 0x12;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = uVar3 | 0x90006000;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = uVar5;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = uVar3 | 0xd8000000;
  do {
  } while (-1 < *piVar1 << 0x1f);
  *puVar2 = uVar4 | 0xd8000000;
  return;
}



/* ============================================================
 * entry: 000f91d4
 * name: PkaSetRegsMapTab
 * body: 000f91d4-000f920d
 * ============================================================ */

void PkaSetRegsMapTab(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int *piVar4;

  iVar3 = 0;
  iVar1 = 0;
  do {
    piVar4 = (int *)(iVar1 * 4 + 0x5002b000);
    iVar2 = iVar1 + 1;
    if (iVar1 < param_1 + -2) {
      *piVar4 = iVar3;
      iVar3 = iVar3 + param_2 * 2;
    }
    else {
      *piVar4 = 0xffc;
    }
    piVar4 = DAT_000f9210;
    iVar1 = iVar2;
  } while (iVar2 != 0x1e);
  *DAT_000f9210 = iVar3;
  piVar4[1] = iVar3 + param_2 * 2;
  *DAT_000f9214 = DAT_000f9218;
  return;
}



/* ============================================================
 * entry: 000f921c
 * name: PkaSetRegsSizesTab
 * body: 000f921c-000f924d
 * ============================================================ */

void PkaSetRegsSizesTab(int param_1,int param_2)

{
  int *piVar1;
  int *piVar2;

  piVar1 = DAT_000f9250;
  *DAT_000f9250 = param_1;
  param_2 = param_2 << 6;
  piVar1[1] = (param_1 + 0x3fU & 0xffffffc0) + 0x40;
  piVar1[2] = param_2;
  piVar1[3] = param_2;
  piVar1[4] = param_2;
  piVar1[5] = param_2;
  piVar1[6] = param_2;
  piVar2 = DAT_000f9254;
  piVar1[7] = param_2;
  do {
  } while (-1 < *piVar2 << 0x1f);
  piVar1[7] = param_2;
  return;
}



/* ============================================================
 * entry: 000f9258
 * name: PkaSum2ScalarMullt
 * body: 000f9258-000f93ef
 * ============================================================ */

uint PkaSum2ScalarMullt(void)

{
  int *piVar1;
  undefined4 *puVar2;
  int *piVar3;
  uint *puVar4;
  uint uVar5;
  uint uVar6;
  undefined4 uVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  undefined4 uVar11;
  uint uVar12;
  undefined1 auStack_5c [4];
  undefined1 auStack_58 [4];
  undefined4 local_54;
  undefined4 uStack_50;
  int local_4c;
  int local_48;
  int local_44;
  int local_40;
  int local_3c;
  int local_38;
  int local_34;
  int local_30;
  int local_2c;
  int local_28;
  int local_24;
  int local_20;
  int local_1c;

  puVar2 = DAT_000f93f4;
  piVar1 = DAT_000f93f0;
  local_54 = 1;
  uStack_50 = 1;
  do {
    local_4c = *DAT_000f93f0;
  } while (-1 < local_4c << 0x1f);
  *DAT_000f93f4 = DAT_000f93f8;
  puVar4 = DAT_000f9400;
  piVar3 = DAT_000f93fc;
  do {
    local_48 = *DAT_000f93fc;
  } while (-1 < local_48 << 0x1f);
  uVar5 = DAT_000f942c;
  if (-1 < (int)(*DAT_000f9400 << 0x13)) {
    do {
      local_44 = *piVar1;
    } while (-1 < local_44 << 0x1f);
    *puVar2 = DAT_000f9404;
    do {
      local_40 = *piVar3;
    } while (-1 < local_40 << 0x1f);
    uVar12 = *puVar4;
    uVar5 = DAT_000f9430;
    if (-1 < (int)(uVar12 << 0x13)) {
      uVar5 = PkaGetRegEffectiveSizeInBits(0x12);
      uVar6 = PkaGetRegEffectiveSizeInBits(0x13);
      if (uVar6 < uVar5) {
        uVar7 = 0x12;
      }
      else {
        uVar7 = 0x13;
      }
      iVar8 = PkaGetRegEffectiveSizeInBits(uVar7);
      iVar8 = iVar8 + -1;
      PkaAddAff();
      iVar9 = PkaGetNextMsBit(0x12,iVar8,auStack_5c,&local_54);
      iVar10 = PkaGetNextMsBit(0x13,iVar8,auStack_58,&uStack_50);
      iVar10 = iVar10 + iVar9 * 2;
      if (iVar10 == 2) {
        do {
          local_34 = *piVar1;
        } while (-1 < local_34 << 0x1f);
        *puVar2 = DAT_000f941c;
        do {
          local_30 = *piVar1;
          uVar7 = DAT_000f9420;
        } while (-1 < local_30 << 0x1f);
      }
      else if (iVar10 == 3) {
        do {
          local_2c = *piVar1;
        } while (-1 < local_2c << 0x1f);
        *puVar2 = DAT_000f9424;
        do {
          local_28 = *piVar1;
          uVar7 = DAT_000f9428;
        } while (-1 < local_28 << 0x1f);
      }
      else {
        if (iVar10 != 1) {
          return DAT_000f9434;
        }
        do {
          local_3c = *piVar1;
        } while (-1 < local_3c << 0x1f);
        *puVar2 = DAT_000f9408;
        do {
          local_38 = *piVar1;
          uVar7 = DAT_000f940c;
        } while (-1 < local_38 << 0x1f);
      }
      *puVar2 = uVar7;
      do {
        local_24 = *piVar1;
      } while (-1 < local_24 << 0x1f);
      *puVar2 = DAT_000f9410;
      do {
        local_20 = *piVar1;
      } while (-1 < local_20 << 0x1f);
      *puVar2 = DAT_000f9414;
      do {
        local_1c = *piVar1;
      } while (-1 < local_1c << 0x1f);
      *puVar2 = DAT_000f9418;
      while (iVar8 = iVar8 + -1, -1 < iVar8) {
        iVar9 = PkaGetNextMsBit(0x12,iVar8,auStack_5c,&local_54);
        iVar10 = PkaGetNextMsBit(0x13,iVar8,auStack_58,&uStack_50);
        iVar10 = iVar10 + iVar9 * 2;
        if (iVar10 == 0) {
          PkaDoubleMdf2Mdf();
        }
        else {
          PkaDoubleMdf2Jcb();
          if (iVar10 == 2) {
            uVar11 = 0x15;
            uVar7 = 0x14;
          }
          else if (iVar10 == 3) {
            uVar11 = 0xf;
            uVar7 = 0xe;
          }
          else {
            if (iVar10 != 1) {
              return DAT_000f9438;
            }
            uVar11 = 0x17;
            uVar7 = 0x16;
          }
          PkaAddJcbAfn2Mdf(uVar7,uVar11);
        }
      }
      PkaJcb2Afn(0,0x18,0x19,0x10);
      uVar5 = (uVar12 & 0x1fff) >> 0xc;
    }
  }
  return uVar5;
}



/* ============================================================
 * entry: 000f943c
 * name: SaSi_HalClearInterruptBit
 * body: 000f943c-000f9441
 * ============================================================ */

void SaSi_HalClearInterruptBit(undefined4 param_1)

{
  *DAT_000f9444 = param_1;
  return;
}



/* ============================================================
 * entry: 000f9448
 * name: SaSi_HalMaskInterrupt
 * body: 000f9448-000f944d
 * ============================================================ */

void SaSi_HalMaskInterrupt(undefined4 param_1)

{
  *DAT_000f9450 = param_1;
  return;
}



/* ============================================================
 * entry: 000f9454
 * name: SaSi_HalWaitInterrupt
 * body: 000f9454-000f947b
 * ============================================================ */

uint SaSi_HalWaitInterrupt(uint param_1)

{
  uint *puVar1;
  uint *puVar2;
  uint local_4;

  puVar1 = DAT_000f947c;
  *DAT_000f947c = ~param_1;
  puVar2 = DAT_000f9480;
  local_4 = puVar1[-1];
  while ((local_4 & param_1) == 0) {
    WaitForEvent();
    local_4 = *DAT_000f9480;
  }
  *DAT_000f9484 = param_1;
  return *puVar2;
}



/* ============================================================
 * entry: 000f9488
 * name: SaSi_PalMemCopy
 * body: 000f9488-000f948b
 * ============================================================ */

void SaSi_PalMemCopy(undefined4 *param_1,undefined4 *param_2,uint param_3)

{
  undefined1 *puVar1;
  undefined1 *puVar2;
  undefined4 uVar3;
  bool bVar4;

  if (param_3 <= (uint)((int)param_1 - (int)param_2)) {
    if ((((uint)param_1 | (uint)param_2) & 3) == 0) {
      for (; 3 < param_3; param_3 = param_3 - 4) {
        uVar3 = *param_2;
        param_2 = param_2 + 1;
        *param_1 = uVar3;
        param_1 = param_1 + 1;
      }
    }
    while (bVar4 = param_3 != 0, param_3 = param_3 - 1, bVar4) {
      *(undefined1 *)param_1 = *(undefined1 *)param_2;
      param_2 = (undefined4 *)((int)param_2 + 1);
      param_1 = (undefined4 *)((int)param_1 + 1);
    }
    return;
  }
  puVar2 = (undefined1 *)((int)param_1 + param_3);
  puVar1 = (undefined1 *)((int)param_2 + param_3);
  while (bVar4 = param_3 != 0, param_3 = param_3 - 1, bVar4) {
    puVar1 = puVar1 + -1;
    puVar2 = puVar2 + -1;
    *puVar2 = *puVar1;
  }
  return;
}



/* ============================================================
 * entry: 000f948c
 * name: SaSi_PalMemSet
 * body: 000f948c-000f948f
 * ============================================================ */

undefined4 SaSi_PalMemSet(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  armcc_memset_core(param_1,param_3,param_2);
  return param_1;
}



/* ============================================================
 * entry: 000f9490
 * name: PkaInitAndMutexLock
 * body: 000f9490-000f9497
 * ============================================================ */

void PkaInitAndMutexLock(undefined4 param_1,undefined4 param_2)

{
  memset(param_1,0,param_2);
  return;
}



/* ============================================================
 * entry: 000f95fc
 * name: nrf_cc310_bl_ecdsa_verify_init_secp256r1
 * body: 000f95fc-000f9639
 * ============================================================ */

undefined4
nrf_cc310_bl_ecdsa_verify_init_secp256r1
          (undefined4 *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;

  uVar1 = DAT_000f9640;
  if ((param_1 != (undefined4 *)0x0) &&
     (SaSi_PalMemSet(param_1 + 1,0,0xa0,param_4,param_4), uVar1 = DAT_000f9644, param_2 != 0)) {
    CRYS_COMMON_ReverseMemcpy32(param_1 + 0x19,param_2,8);
    CRYS_COMMON_ReverseMemcpy32(param_1 + 0x21,param_2 + 0x20,8);
    *param_1 = DAT_000f963c;
    uVar1 = 0;
  }
  return uVar1;
}



/* ============================================================
 * entry: 000f9648
 * name: nrf_cc310_bl_ecdsa_verify_hash_secp256r1
 * body: 000f9498-000f95cb;000f9648-000f966f
 * ============================================================ */

int nrf_cc310_bl_ecdsa_verify_hash_secp256r1
              (int param_1,undefined4 param_2,int param_3,undefined4 param_4,int param_5)

{
  undefined4 *puVar1;
  int iVar2;
  int iVar3;
  undefined8 uVar4;
  int local_24;
  undefined4 uStack_20;
  int local_18;

  local_18 = param_5;
  iVar3 = nrf_cc310_bl_ecdsa_verify_init_secp256r1();
  if (iVar3 != 0) {
    return iVar3;
  }
  local_24 = param_3;
  uStack_20 = param_4;
  uVar4 = verify_context_ecdsa_verify_secp256r1(param_1,param_4,param_4,local_18,param_1);
  iVar2 = (int)((ulonglong)uVar4 >> 0x20);
  iVar3 = (int)uVar4;
  if (((((int)uVar4 == 0) && (iVar3 = DAT_000f95f0, param_3 != 0)) &&
      (iVar3 = DAT_000f95f4, iVar2 != 0)) && (iVar3 = DAT_000f95f8, local_18 == 0x20)) {
    CRYS_COMMON_ReverseMemcpy32(param_1 + 0x44,iVar2,8);
    CRYS_COMMON_ReverseMemcpy32(param_1 + 4,param_3,8);
    CRYS_COMMON_ReverseMemcpy32(param_1 + 0x24,param_3 + 0x20,8);
    local_24 = local_18;
    iVar2 = PkaInitPka(0x100,&local_24);
    puVar1 = DAT_000f95cc;
    iVar3 = DAT_000f95ec;
    if (iVar2 == 0) {
      *DAT_000f95cc = 0x100;
      puVar1[2] = 0x100;
      PkaCopyDataIntoPkaReg(0,1,DAT_000f95d0,8);
      PkaCopyDataIntoPkaReg(1,1,DAT_000f95d4,5);
      PkaCopyDataIntoPkaReg(0x1c,1,param_1 + 4,8);
      PkaCopyDataIntoPkaReg(3,1,param_1 + 0x24,8);
      PkaCopyDataIntoPkaReg(2,1,param_1 + 0x44,8);
      PkaCopyDataIntoPkaReg(0x1a,1,DAT_000f95d8,8);
      PkaCopyDataIntoPkaReg(0x1b,1,DAT_000f95dc,5);
      PkaCopyDataIntoPkaReg(0x14,1,DAT_000f95e0,8);
      PkaCopyDataIntoPkaReg(0x15,1,DAT_000f95e4,8);
      PkaCopyDataIntoPkaReg(0x16,1,param_1 + 100,8);
      PkaCopyDataIntoPkaReg(0x17,1,param_1 + 0x84,8);
      PkaCopyDataIntoPkaReg(0xb,1,DAT_000f95e8,8);
      iVar2 = PkaEcdsaVerify();
      PkaFinishAndMutexUnlock(local_24);
      iVar3 = 0;
      if (iVar2 != 0) {
        iVar3 = DAT_000f95ec;
      }
    }
    PkaInitAndMutexLock(param_1,0xa4);
  }
  return iVar3;
}



/* ============================================================
 * entry: 000f9670
 * name: nrf_cc310_bl_hash_sha256_finalize
 * body: 000f9670-000f96c5
 * ============================================================ */

int nrf_cc310_bl_hash_sha256_finalize(int param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  uint *puVar3;
  uint *puVar5;
  int iVar6;
  undefined4 local_28;
  uint *local_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  uint *puVar4;

  local_28 = *DAT_000f96c8;
  local_24 = (uint *)DAT_000f96c8[1];
  uStack_20 = DAT_000f96c8[2];
  uStack_1c = DAT_000f96c8[3];
  iVar1 = verify_context_hash_sha256(param_1);
  iVar6 = iVar1;
  if ((iVar1 == 0) && (iVar6 = DAT_000f96cc, param_2 != 0)) {
    if (*(int *)(param_1 + 0x24) == 0) {
      *(undefined4 *)(param_1 + 0x24) = 1;
      local_24 = (uint *)(param_1 + 4);
      nrf_cc310_bl_hash_update_internal(&local_28,param_1 + 0x30,*(undefined4 *)(param_1 + 0x70));
    }
    puVar5 = (uint *)(param_2 + -4);
    puVar3 = (uint *)(param_1 + 4);
    do {
      puVar4 = puVar3 + 1;
      uVar2 = *puVar3;
      puVar5 = puVar5 + 1;
      *puVar5 = uVar2 << 0x18 | (uVar2 >> 8 & 0xff) << 0x10 | (uVar2 >> 0x10 & 0xff) << 8 |
                uVar2 >> 0x18;
      puVar3 = puVar4;
      iVar6 = iVar1;
    } while (puVar4 != (uint *)(param_1 + 0x24));
  }
  return iVar6;
}



/* ============================================================
 * entry: 000f96d0
 * name: nrf_cc310_bl_hash_sha256_init
 * body: 000f96d0-000f96f7
 * ============================================================ */

undefined4
nrf_cc310_bl_hash_sha256_init
          (undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;

  uVar1 = DAT_000f9700;
  if (param_1 != (undefined4 *)0x0) {
    PkaInitAndMutexLock(param_1 + 1,0x70,param_3,param_4,param_1);
    SaSi_PalMemCopy(param_1 + 1,DAT_000f96f8,0x20);
    *param_1 = DAT_000f96fc;
    uVar1 = 0;
  }
  return uVar1;
}



/* ============================================================
 * entry: 000f9704
 * name: nrf_cc310_bl_hash_sha256_update
 * body: 000f9704-000f979f
 * ============================================================ */

int nrf_cc310_bl_hash_sha256_update(int param_1,int param_2,uint param_3)

{
  int iVar1;
  uint uVar2;
  undefined4 local_30;
  int local_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;

  local_30 = *DAT_000f97a0;
  local_2c = DAT_000f97a0[1];
  uStack_28 = DAT_000f97a0[2];
  uStack_24 = DAT_000f97a0[3];
  if (param_3 != 0) {
    iVar1 = verify_context_hash_sha256(param_1);
    if (iVar1 != 0) {
      return iVar1;
    }
    local_2c = param_1 + 4;
    if (*(int *)(param_1 + 0x24) != 0) {
      return DAT_000f97a4;
    }
    iVar1 = *(int *)(param_1 + 0x70);
    if (iVar1 != 0) {
      uVar2 = 0x40U - iVar1;
      if (param_3 <= 0x40U - iVar1) {
        uVar2 = param_3;
      }
      SaSi_PalMemCopy(iVar1 + param_1 + 0x30,param_2,uVar2);
      iVar1 = *(int *)(param_1 + 0x70) + uVar2;
      param_2 = param_2 + uVar2;
      *(int *)(param_1 + 0x70) = iVar1;
      param_3 = param_3 - uVar2;
      if (iVar1 == 0x40) {
        nrf_cc310_bl_hash_update_internal(&local_30,param_1 + 0x30);
        *(undefined4 *)(param_1 + 0x70) = 0;
      }
    }
    uVar2 = param_3 & 0x3f;
    param_3 = param_3 & 0xffffffc0;
    if (param_3 != 0) {
      nrf_cc310_bl_hash_update_internal(&local_30,param_2,param_3);
      param_2 = param_2 + param_3;
    }
    if (uVar2 != 0) {
      SaSi_PalMemCopy(param_1 + 0x30,param_2,uVar2);
      *(uint *)(param_1 + 0x70) = uVar2;
      return 0;
    }
  }
  return 0;
}



/* ============================================================
 * entry: 000f97a8
 * name: nrf_cc310_bl_hash_update_internal
 * body: 000f97a8-000f9871
 * ============================================================ */

void nrf_cc310_bl_hash_update_internal(undefined4 *param_1,undefined4 param_2,int param_3)

{
  int *piVar1;
  int *piVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  undefined4 *puVar6;
  int iVar7;

  piVar2 = DAT_000f9878;
  piVar1 = DAT_000f9874;
  iVar7 = param_1[1];
  do {
  } while (*DAT_000f9874 != 0);
  do {
  } while (*DAT_000f9878 != 0);
  SaSi_HalClearInterruptBit(0xffffffff);
  SaSi_HalMaskInterrupt(0x80);
  puVar6 = DAT_000f9894;
  puVar5 = DAT_000f9884;
  puVar4 = DAT_000f9880;
  puVar3 = DAT_000f987c;
  *DAT_000f987c = 1;
  *puVar4 = 7;
  puVar4[-0x4f] = 1;
  *puVar6 = *(undefined4 *)(iVar7 + 0x24);
  *puVar5 = *(undefined4 *)(iVar7 + 0x28);
  puVar4[-0x50] = *param_1;
  (*(code *)param_1[2])(iVar7);
  do {
  } while (*piVar1 != 0);
  if (param_3 == 0) {
    *DAT_000f9888 = 4;
  }
  else {
    if (*(int *)(iVar7 + 0x20) == 1) {
      *DAT_000f988c = 1;
    }
    puVar4 = DAT_000f9890;
    *DAT_000f9890 = param_2;
    puVar4[1] = param_3;
    SaSi_HalWaitInterrupt(0x40);
  }
  do {
  } while (*piVar1 != 0);
  do {
  } while (*piVar2 != 0);
  (*(code *)param_1[3])(iVar7);
  *(undefined4 *)(iVar7 + 0x24) = *puVar6;
  *(undefined4 *)(iVar7 + 0x28) = *puVar5;
  puVar4 = DAT_000f988c;
  *DAT_000f988c = 0;
  puVar4[0x51] = 0;
  do {
  } while (*piVar1 != 0);
  *puVar3 = 0;
  return;
}



/* ============================================================
 * entry: 000f9898
 * name: nrf_cc310_bl_init
 * body: 000f9898-000f98bb
 * ============================================================ */

undefined4 nrf_cc310_bl_init(void)

{
  if (*DAT_000f98bc >> 0x18 != 0xf0) {
    return 5;
  }
  if (*DAT_000f98c0 == DAT_000f98c4) {
    *DAT_000f98c8 = 0;
    return 0;
  }
  return 6;
}



/* ============================================================
 * entry: 000f9958
 * name: verify_context_ecdsa_verify_secp256r1
 * body: 000f9958-000f996b
 * ============================================================ */

undefined4 verify_context_ecdsa_verify_secp256r1(int *param_1)

{
  undefined4 uVar1;

  if (param_1 != (int *)0x0) {
    uVar1 = DAT_000f9970;
    if (*param_1 == DAT_000f996c) {
      uVar1 = 0;
    }
    return uVar1;
  }
  return DAT_000f9974;
}



/* ============================================================
 * entry: 000f9978
 * name: verify_context_hash_sha256
 * body: 000f9978-000f998b
 * ============================================================ */

undefined4 verify_context_hash_sha256(int *param_1)

{
  undefined4 uVar1;

  if (param_1 != (int *)0x0) {
    uVar1 = DAT_000f9990;
    if (*param_1 == DAT_000f998c) {
      uVar1 = 0;
    }
    return uVar1;
  }
  return DAT_000f9994;
}



/* ============================================================
 * entry: 000f9998
 * name: RTC2_IRQHandler
 * body: 000f9998-000f9a01
 * ============================================================ */

void RTC2_IRQHandler(void)

{
  ushort uVar1;
  int iVar2;
  undefined4 *puVar3;
  uint uVar4;

  iVar2 = DAT_000f9a04;
  if (*(int *)(DAT_000f9a04 + 0x104) != 0) {
    *(int *)(DAT_000f9a08 + 0xc) = *(int *)(DAT_000f9a08 + 0xc) + 1;
    nrf_rtc_event_clear(iVar2,0x104);
  }
  uVar4 = 0;
  do {
    uVar1 = (short)(uVar4 << 2) + 0x140;
    if (*(int *)(iVar2 + (uint)uVar1) != 0) {
      nrf_rtc_event_clear(iVar2,uVar1);
      puVar3 = (undefined4 *)(DAT_000f9a08 + 0x10 + uVar4 * 0x10);
      timer_stop(puVar3);
      if (puVar3[1] == 0) {
        if (puVar3[2] != 0) {
          timer_activate(puVar3);
        }
        if ((code *)*puVar3 != (code *)0x0) {
          (*(code *)*puVar3)();
        }
      }
      else {
        timer_activate(puVar3);
      }
    }
    uVar4 = uVar4 + 1;
  } while (uVar4 < 2);
  return;
}



/* ============================================================
 * entry: 000f9a0c
 * name: SWI2_EGU2_IRQHandler_vector
 * body: 000f9a0c-000f9a0f
 * ============================================================ */

void SWI2_EGU2_IRQHandler_vector
               (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 *param_4)

{
  undefined4 uStack_10;
  undefined4 uStack_c;
  undefined4 *puStack_8;

  uStack_10 = param_2;
  uStack_c = param_3;
  puStack_8 = param_4;
  nrf_section_iter_init(&uStack_10,DAT_000fc32c);
  while (puStack_8 != (undefined4 *)0x0) {
    (*(code *)*puStack_8)(puStack_8[1]);
    nrf_section_iter_next(&uStack_10);
  }
  return;
}



/* ============================================================
 * entry: 000f9a10
 * name: SystemInit
 * body: 000f9a10-000f9bef
 * ============================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void SystemInit(void)

{
  undefined4 *puVar1;
  uint uVar2;
  undefined4 *puVar3;
  int *extraout_r2;
  int *extraout_r2_00;
  int *extraout_r2_01;
  undefined4 extraout_r3;
  undefined4 extraout_r3_00;

  uVar2 = _DAT_10000134;
  puVar3 = _DAT_10000130;
  if (_DAT_10000130 == (undefined4 *)&NMI) {
    uRam4000010c = 0;
    uRam40000110 = 0;
    *DAT_000f9bf0 = 0;
    puVar1 = DAT_000f9bf8;
    *DAT_000f9bf8 = *DAT_000f9bf4;
    puVar1[1] = DAT_000f9bf4[1];
    puVar1[2] = DAT_000f9bf4[2];
    puVar1[3] = DAT_000f9bf4[3];
    puVar1[4] = DAT_000f9bf4[4];
    puVar1[5] = DAT_000f9bf4[5];
    puVar1 = DAT_000f9bf8;
    DAT_000f9bf8[8] = DAT_000f9bf4[6];
    puVar1[9] = DAT_000f9bf4[7];
    puVar1[10] = DAT_000f9bf4[8];
    puVar1[0xb] = DAT_000f9bf4[9];
    puVar1[0xc] = DAT_000f9bf4[10];
    puVar1[0xd] = DAT_000f9bf4[0xb];
    puVar1 = DAT_000f9bf8;
    DAT_000f9bf8[0x10] = DAT_000f9bf4[0xc];
    puVar1[0x11] = DAT_000f9bf4[0xd];
    puVar1[0x12] = DAT_000f9bf4[0xe];
    puVar1[0x13] = DAT_000f9bf4[0xf];
    puVar1[0x14] = DAT_000f9bf4[0x10];
    if (uVar2 == 0) {
      *DAT_000f9c00 = DAT_000f9bfc;
    }
  }
  if ((puVar3 == (undefined4 *)&NMI) && (uVar2 == 0)) {
    *DAT_000f9c04 = 0xfb;
  }
  if ((puVar3 == (undefined4 *)&NMI) && (uVar2 == 0)) {
    *DAT_000f9c08 = *DAT_000f9c08 & 0xfffffff0 | DAT_10000258 & 0xf;
  }
  if ((puVar3 == (undefined4 *)&NMI) && (uVar2 == 0)) {
    *DAT_000f9c0c = 0x200;
  }
  if ((puVar3 == (undefined4 *)&NMI) && ((*DAT_000f9c10 & 1) != 0)) {
    *DAT_000f9c10 = 0xfffffffe;
  }
  *DAT_000f9c14 = *DAT_000f9c14 | 0xf00000;
  DataSynchronizationBarrier(0xf);
  InstructionSynchronizationBarrier(0xf);
  puVar3 = _DAT_10000130;
  if ((_DAT_10000130 == (undefined4 *)&NMI) && (4 < _DAT_10000134)) {
    puVar3 = DAT_000f9bf0 + 8;
    *puVar3 = _DAT_10001208;
  }
  nvmc_wait(0,puVar3,0x10000000,1);
  do {
  } while (*DAT_000f9c18 == 0);
  if ((_DAT_10001200 < 0) && (_DAT_10001204 < 0)) {
    *DAT_000f9c2c = DAT_000f9c28;
    return;
  }
  nvmc_wait(2);
  do {
  } while (*extraout_r2 == 0);
  *DAT_000f9c1c = extraout_r3;
  do {
  } while (*extraout_r2 == 0);
  nvmc_wait(0);
  do {
  } while (*extraout_r2_00 == 0);
  DAT_000f9c1c[-4] = extraout_r3_00;
  do {
  } while (*extraout_r2_00 == 0);
  _DAT_10001200 = DAT_000f9c20;
  do {
  } while (*extraout_r2_00 == 0);
  _DAT_10001204 = DAT_000f9c20;
  do {
  } while (*extraout_r2_00 == 0);
  nvmc_wait(0);
  do {
  } while (*extraout_r2_01 == 0);
  DataSynchronizationBarrier(0xf);
  DAT_000f9c14[-0x1f] = DAT_000f9c14[-0x1f] & 0x700 | DAT_000f9c24;
  DataSynchronizationBarrier(0xf);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* ============================================================
 * entry: 000f9c30
 * name: SWI0_EGU0_IRQHandler
 * body: 000f9c30-000f9c3d
 * ============================================================ */

void SWI0_EGU0_IRQHandler(void)

{
  *DAT_000f9c40 = 0;
  return;
}



/* ============================================================
 * entry: 000f9c44
 * name: armcc_scatterload_copy
 * body: 000f9c44-000f9c45
 * ============================================================ */

void armcc_scatterload_copy(undefined4 *param_1,undefined4 *param_2,int param_3)

{
  undefined4 uVar1;

  for (; param_3 != 0; param_3 = param_3 + -4) {
    uVar1 = *param_1;
    param_1 = param_1 + 1;
    *param_2 = uVar1;
    param_2 = param_2 + 1;
  }
  return;
}



/* ============================================================
 * entry: 000f9c4c
 * name: armcc_scatterload_copy_loop
 * body: 000f9c46-000f9c51
 * ============================================================ */

void armcc_scatterload_copy_loop(undefined4 *param_1,undefined4 *param_2,int param_3)

{
  undefined4 uVar1;

  for (; param_3 != 0; param_3 = param_3 + -4) {
    uVar1 = *param_1;
    param_1 = param_1 + 1;
    *param_2 = uVar1;
    param_2 = param_2 + 1;
  }
  return;
}



/* ============================================================
 * entry: 000f9c64
 * name: __sd_nvic_app_accessible_irq
 * body: 000f9c64-000f9c83
 * ============================================================ */

undefined4 __sd_nvic_app_accessible_irq(uint param_1)

{
  uint uVar1;

  if ((int)param_1 < 0x20) {
    uVar1 = 1 << (param_1 & 0xff) & DAT_000f9c84;
  }
  else {
    if (0x3f < (int)param_1) {
      return 1;
    }
    uVar1 = 1 << (param_1 - 0x20 & 0xff);
  }
  if (uVar1 != 0) {
    return 1;
  }
  return 0;
}



/* ============================================================
 * entry: 000f9c88
 * name: addr_is_aligned32
 * body: 000f9c88-000f9c93
 * ============================================================ */

undefined4 addr_is_aligned32(uint param_1)

{
  if ((param_1 & 3) != 0) {
    return 0;
  }
  return 1;
}



/* ============================================================
 * entry: 000f9c94
 * name: addr_is_within_bounds
 * body: 000f9c94-000f9cab
 * ============================================================ */

undefined4 addr_is_within_bounds(int param_1,uint param_2,int param_3)

{
  if ((*(uint *)(param_1 + 0xc) <= param_2) &&
     ((param_2 + param_3) - 1 <= *(uint *)(param_1 + 0x10))) {
    return 1;
  }
  return 0;
}



/* ============================================================
 * entry: 000f9cac
 * name: dfu_advertising_name_get
 * body: 000f9cac-000f9d37
 * ============================================================ */

undefined8 dfu_advertising_name_get(undefined1 param_1)

{
  undefined1 *puVar1;
  undefined1 *puVar2;
  undefined2 *puVar3;
  undefined2 local_30 [2];
  undefined4 local_2b;
  undefined2 local_27;
  undefined1 local_24 [20];

  puVar3 = local_30;
  local_30[0] = 0x16;
  software_interrupt(0x6d);
  if (&stack0x00000000 != &SVCall) {
    app_error_handler_bare();
  }
  puVar1 = DAT_000f9d3c;
  *DAT_000f9d3c = 2;
  puVar1[1] = 1;
  puVar1[2] = param_1;
  puVar1[3] = 3;
  puVar1[4] = 2;
  puVar1[5] = 0x59;
  puVar1[6] = 0xfe;
  software_interrupt(0x7d);
  puVar2 = puVar1 + 9;
  if (puVar1 + 9 == (undefined1 *)0x0) {
    puVar1[7] = (char)local_30[0] + '\x01';
    puVar1[8] = 9;
    puVar1[0x1f] = 9;
    puVar1[0x20] = 0xff;
    puVar1[0x21] = 0x45;
    puVar1[0x22] = 0x52;
    *(undefined4 *)(puVar1 + 0x23) = local_2b;
    *(undefined2 *)(puVar1 + 0x27) = local_27;
    puVar3 = (undefined2 *)local_24;
    software_interrupt(0x72);
    puVar2 = DAT_000f9d40;
  }
  return CONCAT44(puVar3,puVar2);
}



/* ============================================================
 * entry: 000f9d44
 * name: advertising_start
 * body: 000f9d44-000f9d6f
 * ============================================================ */

uint advertising_start(void)

{
  uint uVar1;
  undefined1 auStack_20 [24];

  memmove(auStack_20,DAT_000f9d70,0x18);
  uVar1 = dfu_advertising_name_get(6,auStack_20);
  if (uVar1 == 0) {
    software_interrupt(0x74);
    uVar1 = (uint)*DAT_000f9d74;
    software_interrupt(0x73);
  }
  return uVar1;
}



/* ============================================================
 * entry: 000f9d78
 * name: nrf_bootloader_app_activate
 * body: 000f9d78-000f9db9
 * ============================================================ */

int nrf_bootloader_app_activate(void)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;

  iVar1 = DAT_000f9dbc;
  iVar7 = *(int *)(DAT_000f9dbc + 0x48);
  iVar6 = *(int *)(DAT_000f9dbc + 0x24);
  iVar2 = nrf_dfu_bank0_start_addr();
  iVar4 = *(int *)(iVar1 + 0x30);
  iVar5 = iVar6 - iVar4;
  iVar7 = iVar4 + iVar7;
  if (iVar7 == iVar2 + iVar4) {
    iVar5 = 0;
  }
  iVar2 = image_copy(iVar2 + iVar4,iVar7,iVar5,8);
  if (iVar2 == 0) {
    uVar3 = nrf_dfu_bank0_start_addr();
    iVar4 = crc32_compute(uVar3,iVar6,0);
    if (*(int *)(iVar1 + 0x28) == iVar4) {
      *(int *)(iVar1 + 0x18) = iVar6;
      *(int *)(iVar1 + 0x1c) = iVar4;
      *(undefined4 *)(iVar1 + 0x20) = 1;
    }
  }
  return iVar2;
}



/* ============================================================
 * entry: 000f9dc4
 * name: app_error_handler_bare
 * body: 000f9dc4-000f9dc7
 * ============================================================ */

undefined4 app_error_handler_bare(void)

{
  char *pcVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  undefined4 extraout_r2;
  uint extraout_r3;
  uint uVar6;
  undefined8 uVar7;
  uint uStack_28;

  uVar7 = app_error_fault_handler();
  pcVar1 = DAT_000f9e64;
  uVar5 = (uint)((ulonglong)uVar7 >> 0x20);
  if (*(ushort *)(DAT_000f9e64 + 2) < uVar5) {
    uVar4 = 9;
  }
  else {
    uStack_28 = extraout_r3 & 0xffffff00;
    app_util_critical_region_enter(&uStack_28);
    if ((ushort)(byte)pcVar1[1] < *(ushort *)(pcVar1 + 4)) {
      cVar2 = pcVar1[1] + 1;
    }
    else {
      cVar2 = '\0';
    }
    if (cVar2 == *pcVar1) {
      app_util_critical_region_exit(uStack_28 & 0xff);
    }
    else {
      uVar6 = (uint)(byte)pcVar1[1];
      if ((ushort)(byte)pcVar1[1] < *(ushort *)(pcVar1 + 4)) {
        cVar2 = pcVar1[1] + 1;
      }
      else {
        cVar2 = '\0';
      }
      pcVar1[1] = cVar2;
      app_util_critical_region_exit(uStack_28 & 0xff);
      if (uVar6 != 0xffff) {
        iVar3 = *(int *)(pcVar1 + 8);
        *(undefined4 *)(iVar3 + uVar6 * 8) = extraout_r2;
        if (((int)uVar7 == 0) || (uVar5 == 0)) {
          *(undefined2 *)(iVar3 + uVar6 * 8 + 4) = 0;
        }
        else {
          memmove(uVar6 * *(ushort *)(pcVar1 + 2) + *(int *)(pcVar1 + 0xc),(int)uVar7,uVar5);
          *(short *)(*(int *)(pcVar1 + 8) + uVar6 * 8 + 4) = (short)((ulonglong)uVar7 >> 0x20);
        }
        return 0;
      }
    }
    uVar4 = 4;
  }
  return uVar4;
}



/* ============================================================
 * entry: 000f9dc8
 * name: app_sched_event_put
 * body: 000f9dc8-000f9e61
 * ============================================================ */

undefined4 app_sched_event_put(int param_1,uint param_2,undefined4 param_3,uint param_4)

{
  char *pcVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint local_28;

  pcVar1 = DAT_000f9e64;
  if (*(ushort *)(DAT_000f9e64 + 2) < param_2) {
    uVar4 = 9;
  }
  else {
    local_28 = param_4 & 0xffffff00;
    app_util_critical_region_enter(&local_28);
    if ((ushort)(byte)pcVar1[1] < *(ushort *)(pcVar1 + 4)) {
      cVar2 = pcVar1[1] + 1;
    }
    else {
      cVar2 = '\0';
    }
    if (cVar2 == *pcVar1) {
      app_util_critical_region_exit(local_28 & 0xff);
    }
    else {
      uVar5 = (uint)(byte)pcVar1[1];
      if ((ushort)(byte)pcVar1[1] < *(ushort *)(pcVar1 + 4)) {
        cVar2 = pcVar1[1] + 1;
      }
      else {
        cVar2 = '\0';
      }
      pcVar1[1] = cVar2;
      app_util_critical_region_exit(local_28 & 0xff);
      if (uVar5 != 0xffff) {
        iVar3 = *(int *)(pcVar1 + 8);
        *(undefined4 *)(iVar3 + uVar5 * 8) = param_3;
        if ((param_1 == 0) || (param_2 == 0)) {
          *(undefined2 *)(iVar3 + uVar5 * 8 + 4) = 0;
        }
        else {
          memmove(uVar5 * *(ushort *)(pcVar1 + 2) + *(int *)(pcVar1 + 0xc),param_1,param_2);
          *(short *)(*(int *)(pcVar1 + 8) + uVar5 * 8 + 4) = (short)param_2;
        }
        return 0;
      }
    }
    uVar4 = 4;
  }
  return uVar4;
}



/* ============================================================
 * entry: 000f9e68
 * name: app_sched_execute
 * body: 000f9e68-000f9ea1
 * ============================================================ */

void app_sched_execute(void)

{
  byte *pbVar1;
  byte bVar2;
  uint uVar3;

  pbVar1 = DAT_000f9ea4;
  while (pbVar1[1] != *pbVar1) {
    uVar3 = (uint)*pbVar1;
    (**(code **)(*(int *)(pbVar1 + 8) + uVar3 * 8))
              (uVar3 * *(ushort *)(pbVar1 + 2) + *(int *)(pbVar1 + 0xc),
               *(undefined2 *)(*(int *)(pbVar1 + 8) + uVar3 * 8 + 4));
    if ((ushort)*pbVar1 < *(ushort *)(pbVar1 + 4)) {
      bVar2 = *pbVar1 + 1;
    }
    else {
      bVar2 = 0;
    }
    *pbVar1 = bVar2;
  }
  return;
}



/* ============================================================
 * entry: 000f9ea8
 * name: app_sched_init
 * body: 000f9ea8-000f9ecf
 * ============================================================ */

undefined4 app_sched_init(undefined2 param_1,short param_2,uint param_3)

{
  undefined1 *puVar1;

  puVar1 = DAT_000f9ed0;
  if ((param_3 & 3) != 0) {
    return 7;
  }
  *(uint *)(DAT_000f9ed0 + 8) = param_3;
  *(uint *)(puVar1 + 0xc) = param_3 + (ushort)(param_2 * 8 + 8);
  puVar1[1] = 0;
  *puVar1 = 0;
  *(undefined2 *)(puVar1 + 2) = param_1;
  *(short *)(puVar1 + 4) = param_2;
  return 0;
}



/* ============================================================
 * entry: 000f9ed4
 * name: app_util_critical_region_enter
 * body: 000f9ed4-000f9f13
 * ============================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void app_util_critical_region_enter(undefined1 *param_1)

{
  bool bVar1;
  uint *puVar2;
  uint uVar3;
  int iVar4;

  puVar2 = DAT_000f9f14;
  iVar4 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    iVar4 = isIRQinterruptsEnabled();
  }
  disableIRQinterrupts();
  if (DAT_000f9f14[2] == 0) {
    DAT_000f9f14[2] = 1;
    uVar3 = DAT_000f9f18;
    *puVar2 = _DAT_e000e180 & DAT_000f9f18;
    _DAT_e000e180 = uVar3;
    puVar2[1] = _DAT_e000e184;
    _DAT_e000e184 = 0xffffffff;
    *param_1 = 0;
  }
  else {
    *param_1 = 1;
  }
  if (iVar4 == 0) {
    enableIRQinterrupts();
  }
  return;
}



/* ============================================================
 * entry: 000f9f1c
 * name: app_util_critical_region_exit
 * body: 000f9f1c-000f9f49
 * ============================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void app_util_critical_region_exit(int param_1)

{
  bool bVar1;
  int iVar2;

  if ((DAT_000f9f4c[2] != 0) && (param_1 == 0)) {
    iVar2 = 0;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      iVar2 = isIRQinterruptsEnabled();
    }
    disableIRQinterrupts();
    _DAT_e000e100 = *DAT_000f9f4c;
    _DAT_e000e104 = DAT_000f9f4c[1];
    DAT_000f9f4c[2] = 0;
    if (iVar2 == 0) {
      enableIRQinterrupts();
    }
  }
  return;
}



/* ============================================================
 * entry: 000f9f50
 * name: nrf_bootloader_bl_activate
 * body: 000f9f50-000f9f91
 * ============================================================ */

void nrf_bootloader_bl_activate(void)

{
  int iVar1;
  int iVar2;
  int iVar3;

  iVar3 = *(int *)(DAT_000f9f94 + 0x24);
  iVar2 = *(int *)(DAT_000f9f94 + 0x48);
  if (*(int *)(DAT_000f9f94 + 0x2c) == 0xac) {
    iVar2 = iVar2 + *(int *)(DAT_000f9f94 + 0x34);
    iVar3 = iVar3 - *(int *)(DAT_000f9f94 + 0x34);
  }
  else if (iVar2 == 0) {
    iVar2 = nrf_dfu_bank1_start_addr();
  }
  iVar1 = memcmp(DAT_000f9f98,iVar2,iVar3);
  if (iVar1 == 0) {
    return;
  }
  nrf_bootloader_wdt_feed();
  nrf_dfu_mbr_copy_bl(iVar2,iVar3);
  return;
}



/* ============================================================
 * entry: 000f9f9c
 * name: ble_dfu_init
 * body: 000f9f9c-000fa051
 * ============================================================ */

/* WARNING: Removing unreachable block (ram,0x000f9fc4) */
/* WARNING: Removing unreachable block (ram,0x000f9fd6) */
/* WARNING: Removing unreachable block (ram,0x000fa014) */

undefined8 ble_dfu_init(void)

{
  undefined1 local_50 [68];

  *(undefined2 *)(DAT_000fa054 + 2) = 0xffff;
  software_interrupt(0xa8);
  return CONCAT44(local_50,1);
}



/* ============================================================
 * entry: 000fa060
 * name: ble_dfu_req_handler_callback
 * body: 000fa060-000fa0c7;000fa0d2-000fa113
 * ============================================================ */

void ble_dfu_req_handler_callback(char *param_1)

{
  short sVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  short sVar5;
  uint uVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  undefined1 local_28;
  char local_27;
  char local_26;
  undefined1 local_25 [17];

  armcc_memclr(&local_28,0x14);
  iVar2 = DAT_000fa114;
  if (*param_1 == '\b') {
    sVar5 = *(short *)(DAT_000fa114 + 6) + -1;
    *(short *)(DAT_000fa114 + 6) = sVar5;
    sVar1 = *(short *)(iVar2 + 4);
    if (sVar1 == 0) {
      return;
    }
    if (sVar5 != 0) {
      return;
    }
    *(short *)(iVar2 + 6) = sVar1;
    *param_1 = '\x03';
  }
  local_27 = *param_1;
  local_26 = param_1[1];
  local_28 = 0x60;
  uVar6 = 3;
  if (param_1[1] == '\x01') {
    switch(*param_1) {
    default:
      goto switchD_000fa0c4_caseD_0;
    case '\x03':
    case '\b':
      iVar4 = response_crc_add(&local_28,*(undefined4 *)(param_1 + 4),*(undefined4 *)(param_1 + 8));
      break;
    case '\x06':
      uVar8 = *(undefined4 *)(param_1 + 8);
      uVar7 = *(undefined4 *)(param_1 + 4);
      iVar2 = uint32_encode(*(undefined4 *)(param_1 + 0xc),local_25);
      iVar3 = uint32_encode(uVar7,local_25 + iVar2);
      iVar4 = uint32_encode(uVar8,local_25 + iVar2 + iVar3);
      iVar4 = iVar4 + iVar2 + iVar3;
    }
    uVar6 = iVar4 + 3U & 0xff;
  }
  else if (param_1[1] == '\v') {
    local_25[0] = ext_error_get(0xb,3);
    ext_error_set(0);
    uVar6 = 4;
  }
switchD_000fa0c4_caseD_0:
  response_send(&local_28,uVar6);
  return;
}



/* ============================================================
 * entry: 000fa118
 * name: ble_dfu_transport_close
 * body: 000fa118-000fa169
 * ============================================================ */

uint ble_dfu_transport_close(int param_1)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  int iVar4;
  undefined8 uVar5;

  if (((*(uint *)(DAT_000fa16c + 8) & 1) != 0) && (param_1 != DAT_000fa170)) {
    uVar2 = (uint)*(ushort *)(DAT_000fa16c + 2);
    if (uVar2 == 0xffff) {
      uVar2 = (uint)*DAT_000fa16c;
      software_interrupt(0x74);
    }
    else {
      *(uint *)(DAT_000fa16c + 8) = *(uint *)(DAT_000fa16c + 8) | 4;
      iVar1 = DAT_000fa174;
      uVar3 = 0x13;
      software_interrupt(0x76);
      if (uVar2 != 0) {
        return uVar2;
      }
      iVar4 = 200;
      do {
        uVar5 = (*(code *)(iVar1 + 1))(64000,uVar3);
        uVar3 = (undefined4)((ulonglong)uVar5 >> 0x20);
        uVar2 = (uint)uVar5;
        iVar4 = iVar4 + -1;
      } while (iVar4 != 0);
    }
    uVar2 = nrf_sdh_disable_request(uVar2);
    return uVar2;
  }
  return 0;
}



/* ============================================================
 * entry: 000fa178
 * name: ble_dfu_transport_init
 * body: 000fa178-000fa1fd
 * ============================================================ */

int ble_dfu_transport_init
              (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 local_10;

  iVar1 = DAT_000fa200;
  if ((*(byte *)(DAT_000fa200 + 8) & 1) == 0) {
    *(undefined4 *)(DAT_000fa200 + 0xc) = param_1;
    local_10 = param_4;
    nrf_balloc_init(DAT_000fa204);
    local_10 = 0;
    iVar2 = nrf_dfu_mbr_init_sd();
    if (iVar2 == 0) {
      software_interrupt(0x13);
      iVar2 = DAT_000fa208;
      if ((((DAT_000fa208 == 0) && (iVar2 = nrf_sdh_enable_request(), iVar2 == 0)) &&
          (iVar2 = nrf_sdh_ble_app_ram_start_get(&local_10), iVar2 == 0)) &&
         (iVar2 = nrf_sdh_ble_default_cfg_set(1,&local_10), iVar2 == 0)) {
        iVar2 = nrf_sdh_ble_enable(&local_10);
      }
    }
    if (iVar2 == 0) {
      iVar2 = bootloader_adv_name_record_valid();
      if (iVar2 != 0) {
        nrf_dfu_settings_adv_name_copy(DAT_000fa20c);
        *(uint *)(iVar1 + 8) = *(uint *)(iVar1 + 8) | 2;
      }
      iVar2 = gap_params_init();
      if (((iVar2 == 0) && (iVar2 = ble_dfu_init(DAT_000fa20c + 0x1c), iVar2 == 0)) &&
         (iVar2 = advertising_start(), iVar2 == 0)) {
        *(uint *)(iVar1 + 8) = *(uint *)(iVar1 + 8) | 1;
        return 0;
      }
    }
  }
  else {
    iVar2 = 0;
  }
  return iVar2;
}



/* ============================================================
 * entry: 000fa210
 * name: ble_evt_handler
 * body: 000fa210-000fa3d7
 * ============================================================ */

uint ble_evt_handler(ushort *param_1,undefined4 param_2,undefined4 param_3,ushort *param_4)

{
  ushort uVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  ushort *puVar5;
  undefined4 *puVar6;
  ushort *puVar7;
  undefined4 local_28;
  undefined1 *local_24;
  undefined1 auStack_20 [8];
  int local_18;
  ushort local_14;

  iVar3 = DAT_000fa3dc;
  iVar4 = DAT_000fa3d8;
  puVar5 = param_1 + 2;
  uVar2 = (uint)*param_1;
  puVar7 = (ushort *)0x0;
  puVar6 = &local_28;
  if (uVar2 == 0x21) {
    local_28 = 0;
    uVar1 = *puVar5;
    software_interrupt(0x8f);
LAB_000fa384:
    if (uVar1 == 0) {
      uVar2 = 0;
    }
    else {
      uVar2 = app_error_handler_bare(uVar1,puVar6,0);
    }
  }
  else {
    if (uVar2 < 0x22) {
      if (uVar2 == 0x13) {
        local_28 = *(undefined4 *)(DAT_000fa3e4 + -0x68);
        local_24 = auStack_20;
        software_interrupt(0xad);
        if (*(short *)(DAT_000fa3d8 + 2) != 0) {
          app_error_handler_bare(*(short *)(DAT_000fa3d8 + 2),0x2a05,&local_28);
        }
        uVar1 = *(ushort *)(iVar4 + 2);
        software_interrupt(0x7f);
        puVar6 = (undefined4 *)(undefined1 *)0x85;
        goto LAB_000fa384;
      }
      if (uVar2 < 0x14) {
        if (uVar2 != 1) {
          if (uVar2 == 0x10) {
            *(ushort *)(DAT_000fa3d8 + 2) = *puVar5;
            if (*(code **)(iVar4 + 0xc) != (code *)0x0) {
              (**(code **)(iVar4 + 0xc))(1);
            }
            software_interrupt(0x75);
            return (uint)*(ushort *)(iVar4 + 2);
          }
          if (uVar2 != 0x11) {
            return uVar2;
          }
          *(undefined2 *)(DAT_000fa3d8 + 2) = 0xffff;
          uVar2 = (uint)*(byte *)(iVar4 + 8) << 0x1d;
          if (-1 < (int)uVar2) {
            iVar3 = advertising_start();
            uVar2 = 0;
            if (iVar3 != 0) {
              uVar2 = app_error_handler_bare();
            }
          }
          if (*(code **)(iVar4 + 0xc) == (code *)0x0) {
            return uVar2;
          }
                    /* WARNING: Could not recover jumptable at 0x000fa25a. Too many branches */
                    /* WARNING: Treating indirect jump as call */
          uVar2 = (**(code **)(iVar4 + 0xc))(2);
          return uVar2;
        }
        param_1 = (ushort *)0x0;
        uVar1 = *(ushort *)(DAT_000fa3d8 + 2);
        software_interrupt(0x66);
      }
      else if (uVar2 == 0x14) {
        param_4 = (ushort *)0x0;
        uVar1 = *puVar5;
        puVar7 = (ushort *)0x0;
        param_1 = (ushort *)0x0;
        software_interrupt(0x86);
      }
      else {
        if (uVar2 == 0x1a) goto LAB_000fa3cc;
        if (uVar2 != 0x1f) {
          return uVar2;
        }
        uVar1 = *(ushort *)(DAT_000fa3d8 + 2);
        param_1 = param_1 + 4;
        software_interrupt(0x75);
      }
    }
    else {
      if (uVar2 == 0x51) {
        if ((char)param_1[3] == '\0') {
          return 0;
        }
        iVar4 = on_rw_authorize_req(DAT_000fa3dc,param_1);
        if (iVar4 == 0) {
          return 0;
        }
        uVar2 = on_ctrl_pt_write(DAT_000fa3dc,param_1 + 4);
        return uVar2;
      }
      if (uVar2 < 0x52) {
        if (uVar2 == 0x22) {
          return 0x22;
        }
        if (uVar2 != 0x23) {
          if (uVar2 == 0x24) {
            return 0x24;
          }
          if (uVar2 != 0x50) {
            return uVar2;
          }
          if ((uint)param_1[3] != (uint)*(ushort *)(DAT_000fa3dc + 4)) {
            return (uint)param_1[3];
          }
          iVar4 = nrf_balloc_alloc(DAT_000fa3e0);
          if (iVar4 == 0) {
            return 0;
          }
          memmove(iVar4,param_1 + 9,param_1[8]);
          memmove(&local_28,DAT_000fa3e4,0x18);
          local_24 = (undefined1 *)iVar3;
          local_14 = param_1[8];
          local_18 = iVar4;
          iVar3 = nrf_dfu_req_handler_on_req(&local_28);
          if (iVar3 == 0) {
            return 0;
          }
          uVar2 = nrf_balloc_free(DAT_000fa3e0,iVar4);
          return uVar2;
        }
        local_28 = 0;
        local_24 = (undefined1 *)0x0;
        uVar1 = param_1[2];
        software_interrupt(0x90);
        puVar6 = &local_28;
        goto LAB_000fa384;
      }
      if (uVar2 == 0x52) {
LAB_000fa3cc:
        param_1 = (ushort *)0x0;
        uVar1 = *puVar5;
        software_interrupt(0xb1);
        puVar7 = param_1;
        param_4 = param_1;
      }
      else if (uVar2 == 0x55) {
        param_1 = (ushort *)(uint)param_1[3];
        if (param_1 < (ushort *)0xf7) {
          if (((uint)param_1 & 3) != 3) {
            uVar2 = (int)param_1 - 7U & 0xffff;
            iVar4 = uVar2 - 1;
            puVar7 = (ushort *)((iVar4 / 4) * 4);
            param_1 = (ushort *)((uVar2 - iVar4 % 4) + 6 & 0xffff);
          }
        }
        else {
          param_1 = (ushort *)0xf7;
        }
        uVar1 = *(ushort *)(DAT_000fa3d8 + 2);
        software_interrupt(0xb5);
      }
      else {
        if (uVar2 != 0x56) {
          return uVar2;
        }
        if ((byte)param_1[3] != 0) {
          return (uint)(byte)param_1[3];
        }
        param_1 = (ushort *)0x13;
        uVar1 = *(ushort *)(DAT_000fa3d8 + 2);
        software_interrupt(0x76);
      }
    }
    uVar2 = 0;
    if (uVar1 != 0) {
      uVar2 = app_error_handler_bare(uVar1,param_1,puVar7,param_4);
      return uVar2;
    }
  }
  return uVar2;
}



/* ============================================================
 * entry: 000fa3e8
 * name: ble_srv_is_notification_enabled
 * body: 000fa3e8-000fa3ef
 * ============================================================ */

byte ble_srv_is_notification_enabled(byte *param_1)

{
  return *param_1 & 1;
}



/* ============================================================
 * entry: 000fa3f0
 * name: boot_validate
 * body: 000fa3f0-000fa3ff
 * ============================================================ */

undefined4 boot_validate(char *param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  undefined4 uVar1;

  if ((param_4 == 0) && (*param_1 == '\x01')) {
    return 1;
  }
  uVar1 = nrf_dfu_validation_boot_validate();
  return uVar1;
}



/* ============================================================
 * entry: 000fa400
 * name: boot_validation_crc
 * body: 000fa400-000fa40b
 * ============================================================ */

void boot_validation_crc(int param_1)

{
  crc32_compute(param_1 + 0x260,0xc3,0);
  return;
}



/* ============================================================
 * entry: 000fa40c
 * name: boot_validation_extract
 * body: 000fa40c-000fa49d
 * ============================================================ */

undefined4
boot_validation_extract
          (undefined1 *param_1,int param_2,uint param_3,undefined4 param_4,undefined4 param_5,
          uint param_6)

{
  undefined4 uVar1;
  int iVar2;
  undefined1 auStack_a0 [124];
  undefined4 local_24 [2];

  local_24[0] = 0x20;
  armcc_memclr(auStack_a0,0x7c);
  armcc_memclr(param_1,0x41);
  iVar2 = param_2 + param_3 * 0x44;
  if (param_3 < *(ushort *)(param_2 + 0x94)) {
    param_6 = (uint)*(byte *)(iVar2 + 0x96);
  }
  *param_1 = (char)param_6;
  if (param_6 != 0) {
    if (param_6 == 1) {
      uVar1 = crc32_compute(param_4,param_5,0);
      *(undefined4 *)(param_1 + 1) = uVar1;
    }
    else if (param_6 == 2) {
      iVar2 = nrf_crypto_hash_finalize(auStack_a0,DAT_000fa4a0,param_4,param_5,param_1 + 1,local_24)
      ;
      if (iVar2 != 0) {
        return 0;
      }
    }
    else {
      if (param_6 != 3) {
        return 0;
      }
      memmove(param_1 + 1,iVar2 + 0x9a,*(undefined2 *)(iVar2 + 0x98));
    }
  }
  uVar1 = nrf_dfu_validation_boot_validate(param_1,param_4,param_5);
  return uVar1;
}



/* ============================================================
 * entry: 000fa4a4
 * name: bootloader_reset
 * body: 000fa4a4-000fa4e3
 * ============================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void bootloader_reset(int param_1)

{
  undefined1 *puVar1;
  int extraout_r2;
  int iVar2;
  undefined1 *puVar3;
  undefined1 *puVar4;
  bool bVar5;

  if (param_1 != 0) {
    *puRam000fa4c0 = 0;
    nrf_dfu_settings_backup(uRam000fa4c4);
    return;
  }
  __NVIC_SystemReset();
  iVar2 = extraout_r2;
  do {
    do {
      puVar4 = _Reset + iVar2;
      puVar1 = &stack0x000001dc;
      puVar3 = _Reset;
      _Reset = puVar4;
    } while (&stack0x000001dc == (undefined1 *)0x0);
    while (bVar5 = iVar2 != 0, iVar2 = iVar2 + -1, bVar5) {
      *puVar1 = *puVar3;
      puVar1 = puVar1 + 1;
      puVar3 = puVar3 + 1;
    }
  } while( true );
}



/* ============================================================
 * entry: 000fa4e4
 * name: cc310_backend_mutex_trylock
 * body: 000fa4e4-000fa4fb
 * ============================================================ */

undefined4 cc310_backend_mutex_trylock(void)

{
  int iVar1;

  iVar1 = nrf_atomic_u32_fetch_store(DAT_000fa4fc,1);
  DataMemoryBarrier(0x1f);
  if (iVar1 != 0) {
    return 0;
  }
  return 1;
}



/* ============================================================
 * entry: 000fa500
 * name: cc310_backend_mutex_unlock
 * body: 000fa500-000fa50b
 * ============================================================ */

void cc310_backend_mutex_unlock(void)

{
  DataMemoryBarrier(0x1f);
  *DAT_000fa50c = 0;
  return;
}



/* ============================================================
 * entry: 000fa510
 * name: cc310_bl_backend_disable
 * body: 000fa510-000fa529
 * ============================================================ */

void cc310_bl_backend_disable(void)

{
  *DAT_000fa52c = 0;
  *(undefined4 *)(DAT_000fa530 + 0x180) = 0x400;
  DataSynchronizationBarrier(0xf);
  InstructionSynchronizationBarrier(0xf);
  return;
}



/* ============================================================
 * entry: 000fa534
 * name: cc310_bl_backend_enable
 * body: 000fa534-000fa543
 * ============================================================ */

void cc310_bl_backend_enable(void)

{
  *DAT_000fa544 = 1;
  *(undefined4 *)(DAT_000fa548 + 0x100) = 0x400;
  return;
}



/* ============================================================
 * entry: 000fa54c
 * name: cc310_bl_backend_hash_sha256_finalize
 * body: 000fa54c-000fa593
 * ============================================================ */

int cc310_bl_backend_hash_sha256_finalize(int param_1,undefined4 param_2,uint *param_3)

{
  int iVar1;
  undefined4 uVar2;

  if (*param_3 < 0x20) {
    iVar1 = 0x8514;
  }
  else {
    iVar1 = cc310_backend_mutex_trylock();
    if (iVar1 == 0) {
      return 0x8504;
    }
    cc310_bl_backend_enable();
    uVar2 = nrf_cc310_bl_hash_sha256_finalize(param_1 + 8,param_2);
    cc310_bl_backend_disable();
    cc310_backend_mutex_unlock();
    iVar1 = hash_result_get(uVar2);
    if (iVar1 == 0) {
      *param_3 = 0x20;
      return 0;
    }
  }
  return iVar1;
}



/* ============================================================
 * entry: 000fa594
 * name: cc310_bl_backend_hash_sha256_init
 * body: 000fa594-000fa5a3
 * ============================================================ */

void cc310_bl_backend_hash_sha256_init(int param_1)

{
  nrf_cc310_bl_hash_sha256_init(param_1 + 8);
  hash_result_get();
  return;
}



/* ============================================================
 * entry: 000fa5a4
 * name: cc310_bl_backend_hash_sha256_update
 * body: 000fa5a4-000fa603
 * ============================================================ */

undefined4 cc310_bl_backend_hash_sha256_update(int param_1,int param_2,uint param_3)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;

  iVar1 = cc310_backend_mutex_trylock();
  if (iVar1 != 0) {
    cc310_bl_backend_enable();
    do {
      uVar3 = 0x1000;
      if (param_3 < 0x1001) {
        uVar3 = param_3;
      }
      memmove(DAT_000fa604,param_2,uVar3);
      iVar1 = nrf_cc310_bl_hash_sha256_update(param_1 + 8,DAT_000fa604,uVar3);
      param_3 = param_3 - uVar3;
      param_2 = param_2 + uVar3;
    } while ((iVar1 == 0) && (param_3 != 0));
    cc310_bl_backend_disable();
    cc310_backend_mutex_unlock();
    uVar2 = hash_result_get(iVar1);
    return uVar2;
  }
  return 0x8504;
}



/* ============================================================
 * entry: 000fa608
 * name: cc310_bl_backend_init
 * body: 000fa608-000fa635
 * ============================================================ */

undefined4 cc310_bl_backend_init(void)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;

  *DAT_000fa638 = 0;
  puVar1 = DAT_000fa63c;
  DataMemoryBarrier(0x1f);
  *DAT_000fa63c = 1;
  iVar2 = nrf_cc310_bl_init();
  *puVar1 = 0;
  uVar3 = 3;
  if (iVar2 != 0) {
    if (iVar2 == 5) {
      uVar3 = 0x8503;
    }
    return uVar3;
  }
  return 0;
}



/* ============================================================
 * entry: 000fa640
 * name: cc310_bl_backend_uninit
 * body: 000fa640-000fa647
 * ============================================================ */

void cc310_bl_backend_uninit(void)

{
  *DAT_000fa648 = 0;
  return;
}



/* ============================================================
 * entry: 000fa64c
 * name: cmd_response_offset_and_crc_set
 * body: 000fa64c-000fa657
 * ============================================================ */

void cmd_response_offset_and_crc_set(int param_1)

{
  int iVar1;

  iVar1 = DAT_000fa658;
  *(undefined4 *)(param_1 + 4) = *(undefined4 *)(DAT_000fa658 + 0x3c);
  *(undefined4 *)(param_1 + 8) = *(undefined4 *)(iVar1 + 0x40);
  return;
}



/* ============================================================
 * entry: 000fa65c
 * name: crc32_compute
 * body: 000fa65c-000fa691
 * ============================================================ */

uint crc32_compute(int param_1,uint param_2,uint *param_3)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;

  uVar3 = 0xffffffff;
  if (param_3 != (uint *)0x0) {
    uVar3 = ~*param_3;
  }
  for (uVar1 = 0; uVar1 < param_2; uVar1 = uVar1 + 1) {
    uVar3 = uVar3 ^ *(byte *)(param_1 + uVar1);
    iVar2 = 8;
    do {
      uVar4 = 0;
      if ((uVar3 & 1) != 0) {
        uVar4 = 0xffffffff;
      }
      uVar3 = uVar4 & DAT_000fa694 ^ uVar3 >> 1;
      iVar2 = iVar2 + -1;
    } while (iVar2 != 0);
  }
  return ~uVar3;
}



/* ============================================================
 * entry: 000fa698
 * name: crc_ok
 * body: 000fa698-000fa6b5
 * ============================================================ */

undefined4 crc_ok(int *param_1)

{
  int iVar1;

  if ((*param_1 != -1) && (iVar1 = settings_crc_get(param_1), *param_1 == iVar1)) {
    return 1;
  }
  return 0;
}



/* ============================================================
 * entry: 000fa6b8
 * name: crypto_init
 * body: 000fa6b8-000fa6e5
 * ============================================================ */

void crypto_init(void)

{
  int iVar1;
  undefined1 auStack_48 [64];

  iVar1 = DAT_000fa6e8;
  if (*(char *)(DAT_000fa6e8 + 1) == '\0') {
    nrf_crypto_init();
    nrf_crypto_internal_double_swap_endian(auStack_48,DAT_000fa6ec,0x20);
    nrf_crypto_ecc_public_key_from_raw(DAT_000fa6f4,DAT_000fa6f0,auStack_48,0x40);
    *(undefined1 *)(iVar1 + 1) = 1;
  }
  return;
}



/* ============================================================
 * entry: 000fa776
 * name: nanopb_decode_field
 * body: 000fa6f8-000fa86b
 * ============================================================ */

undefined4 nanopb_decode_field(int param_1,int param_2,int param_3)

{
  byte bVar1;
  ushort uVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  undefined2 *puVar6;
  uint uVar7;
  int *piVar8;
  code *UNRECOVERED_JUMPTABLE;
  ushort *puVar9;
  undefined4 local_48;
  undefined4 local_44;
  int local_40;
  undefined4 uStack_3c;
  int iStack_38;
  undefined4 local_34;
  int iStack_30;
  undefined4 uStack_2c;
  int iStack_28;
  int local_24;
  int local_20;
  uint uStack_1c;

  bVar1 = *(byte *)(*(int *)(param_3 + 4) + 2);
  uStack_1c = bVar1 & 0xc0;
  if ((bVar1 & 0xc0) != 0) {
    if (uStack_1c != 0x40) {
      return 0;
    }
    piVar8 = *(int **)(param_3 + 0x10);
    if (*piVar8 == 0) {
      uVar4 = pb_skip_field(param_1);
      return uVar4;
    }
    if (param_2 == 2) {
      iVar3 = pb_make_string_substream(param_1,&local_48);
      uVar4 = 0;
      if (iVar3 != 0) {
        do {
          iVar3 = (*(code *)*piVar8)(&local_48,*(undefined4 *)(param_3 + 4),piVar8 + 1);
          if (iVar3 == 0) {
            return 0;
          }
        } while (local_40 != 0);
        *(undefined4 *)(param_1 + 4) = local_44;
        uVar4 = 1;
      }
    }
    else {
      local_48 = 10;
      iVar3 = read_raw_value(param_1,param_2,&local_24,&local_48);
      uVar4 = 0;
      if (iVar3 != 0) {
        pb_istream_from_buffer(&local_44,&local_24,local_48);
        local_34 = local_44;
        iStack_30 = local_40;
        uStack_2c = uStack_3c;
        iStack_28 = iStack_38;
        uVar4 = (*(code *)*piVar8)(&local_34,*(undefined4 *)(param_3 + 4),piVar8 + 1);
      }
    }
    return uVar4;
  }
  puVar6 = *(undefined2 **)(param_3 + 4);
  bVar1 = *(byte *)(puVar6 + 1);
  uVar7 = bVar1 & 0xf;
  uVar5 = bVar1 & 0x30;
  UNRECOVERED_JUMPTABLE = *(code **)(DAT_000fa86c + uVar7 * 4);
  iStack_28 = param_1;
  local_24 = param_2;
  local_20 = param_3;
  if ((bVar1 & 0x30) == 0) {
    iVar3 = *(int *)(param_3 + 0x10);
  }
  else {
    if (uVar5 == 0x10) {
      **(undefined1 **)(param_3 + 0x14) = 1;
    }
    else {
      if (uVar5 == 0x20) {
        if ((param_2 == 2) && (uVar7 < 5)) {
          uVar4 = 1;
          puVar9 = *(ushort **)(param_3 + 0x14);
          iVar3 = pb_make_string_substream(param_1,&iStack_28);
          if (iVar3 == 0) {
            return 0;
          }
          while (local_20 != 0) {
            iVar3 = *(int *)(param_3 + 4);
            if ((uint)*(ushort *)(iVar3 + 10) <= (uint)*puVar9) break;
            iVar3 = (*UNRECOVERED_JUMPTABLE)
                              (&iStack_28,iVar3,
                               (uint)*(ushort *)(iVar3 + 8) * (uint)*puVar9 +
                               *(int *)(param_3 + 0x10));
            if (iVar3 == 0) {
              uVar4 = 0;
              break;
            }
            *puVar9 = *puVar9 + 1;
          }
          *(int *)(param_1 + 4) = local_24;
          if (local_20 == 0) {
            return uVar4;
          }
        }
        else {
          uVar2 = **(ushort **)(param_3 + 0x14);
          iVar3 = (uint)(ushort)puVar6[4] * (uint)uVar2 + *(int *)(param_3 + 0x10);
          if ((uint)uVar2 < (uint)(ushort)puVar6[5]) {
            **(ushort **)(param_3 + 0x14) = uVar2 + 1;
            puVar6 = *(undefined2 **)(param_3 + 4);
            goto LAB_000fa85c;
          }
        }
        return 0;
      }
      if (uVar5 != 0x30) {
        return 0;
      }
      **(undefined2 **)(param_3 + 0x14) = *puVar6;
      if (uVar7 == 7) {
        armcc_memclr(*(undefined4 *)(param_3 + 0x10),*(undefined2 *)(*(int *)(param_3 + 4) + 8));
        pb_message_set_to_defaults
                  (*(undefined4 *)(*(int *)(param_3 + 4) + 0xc),*(undefined4 *)(param_3 + 0x10));
      }
    }
    iVar3 = *(int *)(param_3 + 0x10);
    puVar6 = *(undefined2 **)(param_3 + 4);
  }
LAB_000fa85c:
                    /* WARNING: Could not recover jumptable at 0x000fa866. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  uVar4 = (*UNRECOVERED_JUMPTABLE)(param_1,puVar6,iVar3);
  return uVar4;
}



/* ============================================================
 * entry: 000fa870
 * name: nrf_bootloader_app_is_valid
 * body: 000fa870-000fa8e3
 * ============================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 nrf_bootloader_app_is_valid(void)

{
  uint *puVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;

  uVar6 = 1;
  if ((int)(*DAT_000fa8e4 << 0xf) < 0) {
    uVar5 = (int)DAT_000fa8e4 >> 0xe;
    puVar1 = DAT_000fa8e4;
  }
  else {
    if ((*DAT_000fa8e8 & 0xf9) != 0xa9) goto LAB_000fa896;
    uVar5 = *DAT_000fa8e8 & 0x56;
    puVar1 = DAT_000fa8e8;
  }
  *puVar1 = uVar5;
  uVar6 = 0;
LAB_000fa896:
  iVar4 = DAT_000fa8ec;
  if (*(int *)(DAT_000fa8ec + 0x20) == 1) {
    if ((_DAT_00003004 != DAT_000fa8f0) ||
       (iVar2 = boot_validate(DAT_000fa8ec + 0x260,0x1000,*(undefined4 *)(DAT_000fa8ec + 0x34),uVar6
                             ), iVar2 != 0)) {
      uVar3 = nrf_dfu_bank0_start_addr();
      iVar4 = boot_validate(DAT_000fa8f4,uVar3,*(undefined4 *)(iVar4 + 0x18),uVar6);
      if ((iVar4 != 0) && ((DAT_000fa8e8[-1] & 0xf9) != 0xb1)) {
        return 0;
      }
    }
  }
  return 1;
}



/* ============================================================
 * entry: 000fa908
 * name: nrf_bootloader_dfu_observer
 * body: 000fa908-000fa915;000fa91c-000fa945
 * ============================================================ */

void nrf_bootloader_dfu_observer(undefined4 param_1)

{
  switch(param_1) {
  case 2:
    nrf_dfu_settings_reinit();
    break;
  case 3:
  case 4:
    nrf_bootloader_dfu_inactivity_timer_restart(0x3c0000,DAT_000fa948);
    break;
  case 6:
  case 7:
    bootloader_reset(1);
  }
  if (*(code **)(DAT_000fa94c + 4) != (code *)0x0) {
                    /* WARNING: Could not recover jumptable at 0x000fa942. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (**(code **)(DAT_000fa94c + 4))(param_1);
    return;
  }
  return;
}



/* ============================================================
 * entry: 000fa950
 * name: nrf_dfu_observer
 * body: 000fa950-000fa973
 * ============================================================ */

void nrf_dfu_observer(int param_1)

{
  if ((param_1 == 6) || (param_1 == 7)) {
    nrf_dfu_transports_close(0);
  }
  if ((code *)*DAT_000fa974 != (code *)0x0) {
                    /* WARNING: Could not recover jumptable at 0x000fa970. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*(code *)*DAT_000fa974)(param_1);
    return;
  }
  return;
}



/* ============================================================
 * entry: 000fa978
 * name: __NVIC_SystemReset
 * body: 000fa978-000fa991
 * ============================================================ */

void __NVIC_SystemReset(void)

{
  DataSynchronizationBarrier(0xf);
  *DAT_000fa994 = *DAT_000fa994 & 0x700 | DAT_000fa998;
  DataSynchronizationBarrier(0xf);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* ============================================================
 * entry: 000fa99c
 * name: nrf_fstorage_nvmc_erase
 * body: 000fa99c-000fa9df
 * ============================================================ */

undefined4 nrf_fstorage_nvmc_erase(undefined4 param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;

  iVar3 = 0;
  iVar1 = nrf_atomic_u32_fetch_or(DAT_000fa9e0);
  if (iVar1 == 0) {
    for (; iVar3 != param_3; iVar3 = iVar3 + 1) {
      nrf_nvmc_page_erase(param_2 + iVar3 * 0x1000);
    }
    nrf_atomic_flag_clear(DAT_000fa9e0);
    nrf_fstorage_nvmc_event_send(param_1,2,0,param_2,param_3,param_4);
    uVar2 = 0;
  }
  else {
    uVar2 = 0x11;
  }
  return uVar2;
}



/* ============================================================
 * entry: 000fa9e4
 * name: nrf_fstorage_sd_erase
 * body: 000fa9e4-000faa2b
 * ============================================================ */

undefined4
nrf_fstorage_sd_erase(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  undefined4 uStack_20;

  puVar1 = DAT_000faa2c;
  uStack_20 = param_4;
  puVar2 = (undefined4 *)nrf_atfifo_item_alloc(*DAT_000faa2c,&uStack_20);
  if (puVar2 == (undefined4 *)0x0) {
    uVar3 = 4;
  }
  else {
    armcc_memclr(puVar2,0x1c);
    *(undefined1 *)(puVar2 + 1) = 1;
    puVar2[5] = param_3;
    *puVar2 = param_1;
    puVar2[2] = param_4;
    puVar2[3] = param_2 >> 0xc;
    nrf_atfifo_item_put(*puVar1,&uStack_20);
    queue_start();
    uVar3 = 0;
  }
  return uVar3;
}



/* ============================================================
 * entry: 000faa30
 * name: nrf_fstorage_nvmc_event_send
 * body: 000faa30-000faa65
 * ============================================================ */

void nrf_fstorage_nvmc_event_send
               (int param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4,
               undefined4 param_5,undefined4 param_6)

{
  undefined1 local_38 [8];
  undefined4 local_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;

  if (*(int *)(param_1 + 8) != 0) {
    armcc_memclr(local_38,0x18);
    uStack_28 = param_5;
    uStack_24 = param_6;
    local_38[0] = param_2;
    local_30 = param_4;
    uStack_2c = param_3;
    (**(code **)(param_1 + 8))(local_38);
  }
  return;
}



/* ============================================================
 * entry: 000faa66
 * name: event_send
 * body: 000faa66-000faab9
 * ============================================================ */

void event_send(int *param_1,undefined4 param_2)

{
  undefined1 local_28 [4];
  undefined4 local_24;
  int local_20;
  int local_1c;
  int local_18;
  int local_14;

  if (*(int *)(*param_1 + 8) == 0) {
    return;
  }
  armcc_memclr(local_28,0x18);
  local_14 = param_1[2];
  if ((char)param_1[1] == '\0') {
    local_28[0] = 1;
    local_20 = param_1[4];
    local_1c = param_1[3];
  }
  else {
    if ((char)param_1[1] != '\x01') goto LAB_000faaae;
    local_28[0] = 2;
    local_20 = param_1[3] << 0xc;
  }
  local_18 = param_1[5];
LAB_000faaae:
  local_24 = param_2;
  (**(code **)(*param_1 + 8))(local_28);
  return;
}



/* ============================================================
 * entry: 000faaba
 * name: ext_err_code_handle
 * body: 000faaba-000faac7
 * ============================================================ */

void ext_err_code_handle(uint param_1)

{
  if (10 < param_1) {
    ext_error_set(param_1 - 0xb & 0xff);
    return;
  }
  return;
}



/* ============================================================
 * entry: 000faac8
 * name: ext_error_get
 * body: 000faac8-000faad1
 * ============================================================ */

undefined1 ext_error_get(void)

{
  undefined1 uVar1;

  uVar1 = *DAT_000faad4;
  *DAT_000faad4 = 0;
  return uVar1;
}



/* ============================================================
 * entry: 000faad8
 * name: ext_error_set
 * body: 000faad8-000faadf
 * ============================================================ */

undefined4 ext_error_set(undefined1 param_1)

{
  *DAT_000faae0 = param_1;
  return 0xb;
}



/* ============================================================
 * entry: 000faafc
 * name: fw_hash_ok
 * body: 000faafc-000fab03
 * ============================================================ */

undefined4 fw_hash_ok(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_b8 [124];
  undefined1 auStack_3c [32];
  undefined4 uStack_1c;

  uStack_1c = 0x20;
  uVar2 = 1;
  armcc_memclr(auStack_b8,0x7c);
  crypto_init();
  nrf_crypto_internal_swap_endian(auStack_3c,param_1 + 0x72,0x20);
  iVar1 = nrf_crypto_hash_finalize(auStack_b8,DAT_000fbc24,param_2,param_3,DAT_000fbc20,&uStack_1c);
  if ((iVar1 != 0) || (iVar1 = memcmp(DAT_000fbc20,auStack_3c,0x20), iVar1 != 0)) {
    uVar2 = 0;
  }
  return uVar2;
}



/* ============================================================
 * entry: 000fab04
 * name: gap_params_init
 * body: 000fab04-000fabd9
 * ============================================================ */

undefined8
gap_params_init(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 *puVar5;
  int iVar6;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined1 local_20;
  undefined3 uStack_1f;

  iVar4 = DAT_000fabdc;
  puVar5 = &uStack_28;
  iVar6 = DAT_000fabdc + 4;
  _local_20 = CONCAT31((int3)((uint)param_4 >> 8),0x11);
  software_interrupt(0x6d);
  uStack_28 = param_2;
  if (puVar5 == (undefined4 *)0x0) {
    uStack_28._1_1_ = (char)((uint)param_2 >> 8);
    uStack_28._1_1_ = uStack_28._1_1_ + '\x01';
    uStack_28._2_2_ = (undefined2)((uint)param_2 >> 0x10);
    uStack_28._0_1_ = (undefined1)param_2;
    software_interrupt(0x6c);
    if (-1 < (int)((uint)*(byte *)(DAT_000fabe0 + 8) << 0x1e)) {
      software_interrupt(0x6d);
      uStack_24 = param_3;
      if (DAT_000fabe0 != -0x10) {
        app_error_handler_bare();
      }
      armcc_memclr(iVar6,0x14);
      iVar2 = strlen(s_B210_DFU_000fabe4);
      memmove(iVar4 + 4,s_B210_DFU_000fabe4,iVar2);
      iVar3 = strncmp(iVar4 + 4,s_B210_DFU_000fabe4,8);
      iVar6 = DAT_000fabe0;
      if (iVar3 == 0) {
        iVar4 = iVar4 + iVar2;
        *(undefined1 *)(iVar4 + 4) = 0x5f;
        iVar2 = DAT_000fabf0;
        bVar1 = *(byte *)(iVar6 + 0x13);
        *(undefined1 *)(iVar4 + 5) = *(undefined1 *)(DAT_000fabf0 + (uint)(bVar1 >> 4));
        *(undefined1 *)(iVar4 + 6) = *(undefined1 *)(iVar2 + (bVar1 & 0xf));
        bVar1 = *(byte *)(iVar6 + 0x12);
        *(undefined1 *)(iVar4 + 7) = *(undefined1 *)(iVar2 + (uint)(bVar1 >> 4));
        *(undefined1 *)(iVar4 + 8) = *(undefined1 *)(iVar2 + (bVar1 & 0xf));
        bVar1 = *(byte *)(iVar6 + 0x11);
        *(undefined1 *)(iVar4 + 9) = *(undefined1 *)(iVar2 + (uint)(bVar1 >> 4));
        *(undefined1 *)(iVar4 + 10) = *(undefined1 *)(iVar2 + (bVar1 & 0xf));
        *(undefined1 *)(iVar4 + 0xb) = 0;
      }
    }
    puVar5 = (undefined4 *)&local_20;
    software_interrupt(0x7c);
    if (puVar5 == (undefined4 *)0x0) {
      puVar5 = (undefined4 *)(DAT_000fabf0 + -0x92);
      software_interrupt(0x7a);
    }
  }
  return CONCAT44(uStack_28,puVar5);
}



/* ============================================================
 * entry: 000fabf4
 * name: hash_result_get
 * body: 000fabf4-000fac33
 * ============================================================ */

undefined4 hash_result_get(int param_1)

{
  if (param_1 == DAT_000fac34) {
    return 0x8502;
  }
  if (param_1 < DAT_000fac34) {
    if (param_1 == 0) {
      return 0;
    }
    if (param_1 + DAT_000fac38 == 0) {
      return 0x8501;
    }
    if (param_1 + DAT_000fac38 == 1) {
      return 0x8503;
    }
  }
  else if ((param_1 - DAT_000fac34 != 10) && (param_1 - DAT_000fac34 == 0xd)) {
    return 0x8503;
  }
  return 0x8516;
}



/* ============================================================
 * entry: 000fac3c
 * name: image_copy
 * body: 000fac3c-000facc7
 * ============================================================ */

int image_copy(int param_1,int param_2,int param_3,uint param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;

  if (param_2 != param_1) {
    uVar3 = (uint)(param_2 - param_1) >> 0xc;
    uVar4 = param_3 + 0xfffU >> 0xc;
    nrf_bootloader_wdt_init();
    if (param_4 < uVar3) {
      uVar3 = param_4;
    }
    while (param_3 != 0) {
      iVar2 = param_3;
      uVar5 = uVar4;
      if (uVar3 < uVar4) {
        iVar2 = uVar3 << 0xc;
        uVar5 = uVar3;
      }
      iVar1 = nrf_dfu_flash_erase(param_1,uVar5,0);
      if (iVar1 != 0) {
        return iVar1;
      }
      iVar1 = nrf_dfu_flash_store(param_1,param_2,(iVar2 - (iVar2 - 1U & 3)) + 3,0);
      if (iVar1 != 0) {
        return iVar1;
      }
      uVar4 = uVar4 - uVar5;
      param_3 = param_3 - iVar2;
      param_1 = param_1 + iVar2;
      *(int *)(DAT_000facc8 + 0x30) = *(int *)(DAT_000facc8 + 0x30) + iVar2;
      param_2 = param_2 + iVar2;
      iVar2 = nrf_dfu_settings_write_and_backup(0);
      if (iVar2 != 0) {
        return iVar2;
      }
    }
  }
  return 0;
}



/* ============================================================
 * entry: 000facd4
 * name: nrf_fstorage_nvmc_init
 * body: 000facd4-000facdb
 * ============================================================ */

undefined4 nrf_fstorage_nvmc_init(int param_1)

{
  *(undefined4 *)(param_1 + 4) = DAT_000facdc;
  return 0;
}



/* ============================================================
 * entry: 000face0
 * name: nrf_fstorage_sd_init
 * body: 000face0-000fad0d
 * ============================================================ */

undefined4 nrf_fstorage_sd_init(int param_1)

{
  undefined1 uVar1;
  int iVar2;

  *(int *)(param_1 + 4) = DAT_000fad10;
  iVar2 = nrf_atomic_u32_fetch_or(DAT_000fad14);
  if (iVar2 == 0) {
    uVar1 = nrf_sdh_is_enabled();
    iVar2 = DAT_000fad14;
    *(undefined1 *)(DAT_000fad14 + 0x10) = uVar1;
    nrf_atfifo_init(*(undefined4 *)(DAT_000fad10 + -4),iVar2 + -0x1dc,0x1dc,0x1c);
  }
  return 0;
}



/* ============================================================
 * entry: 000fad18
 * name: nrf_fstorage_nvmc_is_busy
 * body: 000fad18-000fad23
 * ============================================================ */

bool nrf_fstorage_nvmc_is_busy(void)

{
  return *DAT_000fad24 != 0;
}



/* ============================================================
 * entry: 000fad28
 * name: nrf_fstorage_sd_is_busy
 * body: 000fad28-000fad33
 * ============================================================ */

bool nrf_fstorage_sd_is_busy(void)

{
  return *(char *)(DAT_000fad34 + 8) != '\0';
}



/* ============================================================
 * entry: 000fad38
 * name: is_major_softdevice_update
 * body: 000fad38-000fad8f
 * ============================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 is_major_softdevice_update(int param_1)

{
  uint uVar1;
  uint uVar2;
  undefined4 uVar3;

  if ((_DAT_00003004 == DAT_000fad90) || (*(int *)(param_1 + 0x2004) != DAT_000fad90)) {
    uVar3 = 0;
  }
  else {
    uVar3 = 1;
  }
  if ((_DAT_00003004 == DAT_000fad90) && (*(int *)(param_1 + 0x2004) == DAT_000fad90)) {
    uVar2 = _DAT_00003014;
    if (DAT_00003000 < 0x15) {
      uVar2 = 0;
    }
    if (*(byte *)(param_1 + 0x2000) < 0x15) {
      uVar1 = 0;
    }
    else {
      uVar1 = *(uint *)(param_1 + 0x2014);
    }
    if (uVar2 / DAT_000fad94 == uVar1 / DAT_000fad94) {
      uVar3 = 0;
    }
    else {
      uVar3 = 1;
    }
  }
  return uVar3;
}



/* ============================================================
 * entry: 000fad98
 * name: iter_from_extension
 * body: 000fad98-000fadc5
 * ============================================================ */

void iter_from_extension(int param_1,int *param_2)

{
  int iVar1;

  iVar1 = *(int *)(*param_2 + 8);
  pb_field_iter_begin(param_1,iVar1,param_2[1]);
  *(int *)(param_1 + 0x10) = param_2[1];
  *(int **)(param_1 + 0x14) = param_2 + 3;
  if (*(byte *)(iVar1 + 2) >> 6 == 2) {
    *(int **)(param_1 + 0x10) = param_2 + 1;
  }
  return;
}



/* ============================================================
 * entry: 000fadc8
 * name: main
 * body: 000fadc8-000fadf7
 * ============================================================ */

undefined4 main(void)

{
  int iVar1;
  undefined2 *puVar2;

  nrf_bootloader_mbr_addrs_populate();
  iVar1 = nrf_bootloader_acl_add(0,0x1000);
  if ((iVar1 == 0) &&
     (iVar1 = nrf_bootloader_acl_add(iRam000fadf0,0xfe000 - iRam000fadf0), iVar1 == 0)) {
    nrf_bootloader_init(uRam000fadf4);
  }
  puVar2 = (undefined2 *)app_error_fault_handler();
  *puVar2 = (short)puVar2;
  iVar1 = nrf_atfifo_space_clear(puVar2,&stack0x00000014);
  if (iVar1 != 0) {
    return 0;
  }
  return 0x11;
}



/* ============================================================
 * entry: 000fadf8
 * name: nrf_atfifo_clear
 * body: 000fadf8-000fae07
 * ============================================================ */

undefined4 nrf_atfifo_clear(void)

{
  int iVar1;

  iVar1 = nrf_atfifo_space_clear();
  if (iVar1 != 0) {
    return 0;
  }
  return 0x11;
}



/* ============================================================
 * entry: 000fae08
 * name: nrf_atfifo_init
 * body: 000fae08-000fae2d
 * ============================================================ */

undefined4 nrf_atfifo_init(int *param_1,int param_2,uint param_3,uint param_4)

{
  if (param_2 == 0) {
    return 0xe;
  }
  if (param_3 != param_4 * (param_3 / param_4)) {
    return 9;
  }
  *param_1 = param_2;
  param_1[1] = 0;
  param_1[2] = 0;
  *(short *)(param_1 + 3) = (short)param_3;
  *(short *)((int)param_1 + 0xe) = (short)param_4;
  return 0;
}



/* ============================================================
 * entry: 000fae2e
 * name: nrf_atfifo_item_alloc
 * body: 000fae2e-000fae43
 * ============================================================ */

int nrf_atfifo_item_alloc(int *param_1,ushort *param_2)

{
  int iVar1;
  int iVar2;

  iVar1 = nrf_atfifo_wspace_req();
  iVar2 = 0;
  if (iVar1 != 0) {
    iVar2 = *param_1 + (uint)*param_2;
  }
  return iVar2;
}



/* ============================================================
 * entry: 000fae44
 * name: nrf_atfifo_item_free
 * body: 000fae44-000fae59
 * ============================================================ */

undefined4 nrf_atfifo_item_free(undefined4 param_1,short *param_2)

{
  if (*param_2 == param_2[1]) {
    nrf_atfifo_rspace_close();
    return 1;
  }
  return 0;
}



/* ============================================================
 * entry: 000fae5a
 * name: nrf_atfifo_item_get
 * body: 000fae5a-000fae6f
 * ============================================================ */

int nrf_atfifo_item_get(int *param_1,int param_2)

{
  int iVar1;
  int iVar2;

  iVar1 = nrf_atfifo_rspace_req();
  iVar2 = 0;
  if (iVar1 != 0) {
    iVar2 = *param_1 + (uint)*(ushort *)(param_2 + 2);
  }
  return iVar2;
}



/* ============================================================
 * entry: 000fae70
 * name: nrf_atfifo_item_put
 * body: 000fae70-000fae85
 * ============================================================ */

undefined4 nrf_atfifo_item_put(undefined4 param_1,short *param_2)

{
  if (*param_2 == param_2[1]) {
    nrf_atfifo_wspace_close();
    return 1;
  }
  return 0;
}



/* ============================================================
 * entry: 000fae86
 * name: nrf_atomic_flag_clear
 * body: 000fae86-000fae8b;000fae92-000fae9d
 * ============================================================ */

undefined4
nrf_atomic_flag_clear(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 local_8;

  local_8 = param_4;
  nrf_atomic_internal_and(param_1,0,&local_8);
  return local_8;
}



/* ============================================================
 * entry: 000fae8c
 * name: nrf_atomic_u32_fetch_or
 * body: 000fae8c-000fae91;000fae9e-000faea7
 * ============================================================ */

void nrf_atomic_u32_fetch_or
               (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uStack_8;

  uStack_8 = param_4;
  nrf_atomic_internal_orr(param_1,1,&uStack_8);
  return;
}



/* ============================================================
 * entry: 000faea8
 * name: nrf_atomic_u32_fetch_store
 * body: 000faea8-000faeb1
 * ============================================================ */

void nrf_atomic_u32_fetch_store
               (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uStack_8;

  uStack_8 = param_4;
  nrf_atomic_internal_mov(param_1,param_2,&uStack_8);
  return;
}



/* ============================================================
 * entry: 000faeb2
 * name: nrf_balloc_alloc
 * body: 000faeb2-000faef5
 * ============================================================ */

int nrf_balloc_alloc(int *param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  uint uVar1;
  byte *pbVar2;
  int iVar3;
  uint local_10;

  iVar3 = 0;
  local_10 = param_4 & 0xffffff00;
  app_util_critical_region_enter(&local_10);
  uVar1 = *(uint *)*param_1;
  if ((uint)param_1[1] < uVar1) {
    pbVar2 = (byte *)(uVar1 - 1);
    *(uint *)*param_1 = (uint)pbVar2;
    iVar3 = (uint)*pbVar2 * (uint)*(ushort *)(param_1 + 4) + param_1[3];
    if ((uint)*(byte *)(*param_1 + 4) < ((uint)*(byte *)(param_1 + 2) - (int)pbVar2 & 0xff)) {
      *(char *)(*param_1 + 4) = (char)((uint)*(byte *)(param_1 + 2) - (int)pbVar2);
    }
  }
  app_util_critical_region_exit(local_10 & 0xff);
  return iVar3;
}



/* ============================================================
 * entry: 000faef6
 * name: nrf_balloc_free
 * body: 000faef6-000faf25
 * ============================================================ */

void nrf_balloc_free(undefined4 *param_1,int param_2,undefined4 param_3,uint param_4)

{
  ushort uVar1;
  int iVar2;
  undefined1 *puVar3;
  uint local_10;

  local_10 = param_4 & 0xffffff00;
  app_util_critical_region_enter(&local_10);
  iVar2 = param_1[3];
  uVar1 = *(ushort *)(param_1 + 4);
  puVar3 = *(undefined1 **)*param_1;
  *(undefined1 **)*param_1 = puVar3 + 1;
  *puVar3 = (char)((uint)(param_2 - iVar2) / (uint)uVar1);
  app_util_critical_region_exit(local_10 & 0xff);
  return;
}



/* ============================================================
 * entry: 000faf26
 * name: nrf_balloc_init
 * body: 000faf26-000faf55
 * ============================================================ */

undefined4 nrf_balloc_init(int *param_1)

{
  byte bVar1;
  uint uVar2;
  byte *pbVar3;
  bool bVar4;

  if (param_1 != (int *)0x0) {
    uVar2 = (uint)*(byte *)(param_1 + 2) - param_1[1] & 0xff;
    *(int *)*param_1 = param_1[1];
    while( true ) {
      bVar4 = uVar2 == 0;
      bVar1 = (char)uVar2 - 1;
      uVar2 = (uint)bVar1;
      if (bVar4) break;
      pbVar3 = *(byte **)*param_1;
      *(byte **)*param_1 = pbVar3 + 1;
      *pbVar3 = bVar1;
    }
    *(undefined1 *)(*param_1 + 4) = 0;
    return 0;
  }
  return 0xe;
}



/* ============================================================
 * entry: 000faf56
 * name: nrf_bootloader_app_start_final
 * body: 000faf56-000faf79;000faf7c-000fafd3
 * ============================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void nrf_bootloader_app_start_final(void)

{
  bool bVar1;
  char cVar2;
  int iVar3;
  uint uVar4;
  undefined4 extraout_r3;
  undefined4 unaff_r4;
  undefined4 unaff_lr;

  _DAT_e000e180 = 0xffffffff;
  _DAT_e000e280 = 0xffffffff;
  nrf_dfu_mbr_irq_forward_address_set();
  iVar3 = nrf_bootloader_acl_add(DAT_000fafd4,0xff000 - DAT_000fafd4);
  if (iVar3 != 0) {
    app_error_handler_bare();
  }
  iVar3 = nrf_dfu_bank0_start_addr();
  uVar4 = *(int *)(DAT_000fafd8 + 0x18) - 1U & 0xfff;
  iVar3 = nrf_bootloader_acl_add
                    (0,iVar3 + (*(int *)(DAT_000fafd8 + 0x18) - uVar4) + 0xfff,uVar4,extraout_r3,
                     unaff_r4,unaff_lr);
  if (iVar3 != 0) {
    app_error_handler_bare();
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setThreadModePrivileged(1);
    bVar1 = (bool)isThreadMode();
    if (bVar1) {
      cVar2 = isUsingMainStack();
      setStackMode(cVar2 == '\x01');
    }
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts(0);
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setBasePriority(0);
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableFIQinterrupts(0);
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setMainStackPointer(_DAT_00001000);
  }
                    /* WARNING: Could not recover jumptable at 0x000fafd2. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*_DAT_00001004)(_DAT_00001000,_DAT_00001004,0);
  return;
}



/* ============================================================
 * entry: 000fafdc
 * name: nrf_bootloader_dfu_inactivity_timer_restart
 * body: 000fafdc-000faffd
 * ============================================================ */

void nrf_bootloader_dfu_inactivity_timer_restart(int param_1,undefined4 param_2)

{
  int iVar1;

  iVar1 = DAT_000fb000;
  timer_stop(*(undefined4 *)(DAT_000fb000 + 4));
  if (param_1 != 0) {
    timer_start(*(undefined4 *)(iVar1 + 4),param_1,param_2);
    return;
  }
  return;
}



/* ============================================================
 * entry: 000fb004
 * name: nrf_bootloader_acl_add
 * body: 000fb004-000fb03b
 * ============================================================ */

undefined4 nrf_bootloader_acl_add(uint param_1,uint param_2)

{
  uint *puVar1;
  uint uVar2;
  int iVar3;

  puVar1 = DAT_000fb03c;
  if (((param_2 & 0xfff) == 0) && (param_1 < 0xff001)) {
    uVar2 = *DAT_000fb03c;
    if (7 < uVar2) {
      return 4;
    }
    iVar3 = DAT_000fb040 + uVar2 * 0x10;
    *(uint *)(iVar3 + 0x800) = param_1;
    *(uint *)(iVar3 + 0x804) = param_2;
    *(undefined4 *)(iVar3 + 0x808) = 2;
    *puVar1 = uVar2 + 1;
    return 0;
  }
  return 7;
}



/* ============================================================
 * entry: 000fb044
 * name: nrf_bootloader_fw_activate
 * body: 000fb044-000fb0a9
 * ============================================================ */

undefined4 nrf_bootloader_fw_activate(void)

{
  bool bVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;

  bVar1 = false;
  iVar2 = *(int *)(DAT_000fb0ac + 0x2c);
  iVar4 = DAT_000fb0ac + 0x24;
  if (iVar2 == 1) {
    nrf_bootloader_app_activate();
  }
  else {
    if (iVar2 == 0xa5) {
      nrf_bootloader_sd_activate();
    }
    else {
      if (iVar2 == 0xaa) {
        nrf_bootloader_bl_activate();
        goto LAB_000fb080;
      }
      if (iVar2 != 0xac) {
        return 0;
      }
      iVar2 = nrf_bootloader_sd_activate();
      if (iVar2 == 0) {
        nrf_bootloader_bl_activate();
      }
    }
    bVar1 = true;
  }
LAB_000fb080:
  nrf_dfu_bank_invalidate(iVar4);
  *DAT_000fb0b0 = 0;
  iVar2 = nrf_dfu_settings_write_and_backup(DAT_000fb0b4);
  if (iVar2 == 0) {
    uVar3 = 1;
    if ((bVar1) && (*(int *)(DAT_000fb0ac + 0x20) == 1)) {
      return 2;
    }
  }
  else {
    uVar3 = 3;
  }
  return uVar3;
}



/* ============================================================
 * entry: 000fb0b8
 * name: nrf_bootloader_init
 * body: 000fb0b8-000fb14d
 * ============================================================ */

undefined4 nrf_bootloader_init(undefined4 param_1)

{
  undefined1 *puVar1;
  int iVar2;

  puVar1 = DAT_000fb150;
  *(undefined4 *)(DAT_000fb150 + 4) = param_1;
  iVar2 = nrf_dfu_settings_init(0);
  if (iVar2 != 0) {
    return 3;
  }
  iVar2 = nrf_bootloader_fw_activate();
  if (iVar2 == 0) {
    iVar2 = nrf_bootloader_app_is_valid();
    if (iVar2 == 0) {
      iVar2 = nrf_dfu_settings_additional_erase();
      if (iVar2 != 0) {
        return 3;
      }
      *puVar1 = 0;
      nrf_dfu_settings_backup(DAT_000fb164);
      nrf_bootloader_app_start_final();
      return 3;
    }
  }
  else {
    if (iVar2 == 1) {
      bootloader_reset(1);
      return 3;
    }
    if (iVar2 != 2) {
      return 3;
    }
  }
  nrf_bootloader_wdt_init();
  iVar2 = app_sched_init(0x18,0x20,DAT_000fb154);
  if (iVar2 != 0) {
    app_error_handler_bare();
  }
  if ((*DAT_000fb158 & 0xf9) == 0xb1) {
    *DAT_000fb158 = *DAT_000fb158 & 0x4e;
  }
  iVar2 = nrf_dfu_init_user();
  if (iVar2 == 0) {
    nrf_bootloader_dfu_inactivity_timer_restart(0x3c0000,DAT_000fb15c);
    iVar2 = nrf_dfu_init(DAT_000fb160);
    if (iVar2 == 0) {
      do {
        nrf_bootloader_wdt_feed();
        app_sched_execute();
        software_interrupt(0x41);
      } while( true );
    }
  }
  return 3;
}



/* ============================================================
 * entry: 000fb168
 * name: nrf_bootloader_mbr_addrs_populate
 * body: 000fb168-000fb191
 * ============================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void nrf_bootloader_mbr_addrs_populate(void)

{
  if (_DAT_00000ff8 == -1) {
    nrf_nvmc_write_word(0xff8,DAT_000fb194);
  }
  if (_DAT_00000ffc == -1) {
    nrf_nvmc_write_word(0xffc,0xfe000);
    return;
  }
  return;
}



/* ============================================================
 * entry: 000fb198
 * name: nrf_bootloader_wdt_feed
 * body: 000fb198-000fb1ab
 * ============================================================ */

void nrf_bootloader_wdt_feed(void)

{
  int iVar1;

  iVar1 = nrf_wdt_started();
  if (iVar1 != 0) {
    wdt_feed();
    return;
  }
  return;
}



/* ============================================================
 * entry: 000fb1ac
 * name: nrf_bootloader_wdt_feed_timer_start
 * body: 000fb1ac-000fb1bb
 * ============================================================ */

void nrf_bootloader_wdt_feed_timer_start(undefined4 param_1,undefined4 param_2)

{
  int iVar1;

  iVar1 = *(int *)(DAT_000fb1bc + 8);
  *(undefined4 *)(iVar1 + 8) = param_1;
  timer_start(iVar1,param_1,param_2);
  return;
}



/* ============================================================
 * entry: 000fb1c0
 * name: nrf_bootloader_wdt_init
 * body: 000fb1c0-000fb1fb
 * ============================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void nrf_bootloader_wdt_init(void)

{
  char *pcVar1;
  int iVar2;

  pcVar1 = DAT_000fb1fc;
  if (*DAT_000fb1fc == '\0') {
    iVar2 = nrf_wdt_started();
    if (iVar2 != 0) {
      iVar2 = *DAT_000fb200 + -0xc80;
      if (iVar2 < 0x96) {
        iVar2 = 0x96;
      }
      wdt_feed();
      nrf_bootloader_wdt_feed_timer_start(iVar2,DAT_000fb204);
      _DAT_e000e100 = 0x10000;
    }
    *pcVar1 = '\x01';
  }
  return;
}



/* ============================================================
 * entry: 000fb208
 * name: nrf_crypto_backend_secp256r1_public_key_from_raw
 * body: 000fb208-000fb227
 * ============================================================ */

undefined4 nrf_crypto_backend_secp256r1_public_key_from_raw(int param_1,int param_2)

{
  memmove(param_1 + 8,param_2,0x20);
  memmove(param_1 + 0x28,param_2 + 0x20,0x20);
  return 0;
}



/* ============================================================
 * entry: 000fb228
 * name: nrf_crypto_backend_secp256r1_verify
 * body: 000fb228-000fb28b
 * ============================================================ */

undefined4
nrf_crypto_backend_secp256r1_verify
          (undefined4 *param_1,int param_2,undefined4 param_3,undefined4 param_4,undefined4 param_5)

{
  int iVar1;
  undefined4 uVar2;

  *param_1 = DAT_000fb28c;
  iVar1 = nrf_atomic_u32_fetch_store(DAT_000fb290,1,param_3,param_4,param_4);
  DataMemoryBarrier(0x1f);
  if (iVar1 == 0) {
    cc310_bl_backend_enable();
    iVar1 = nrf_cc310_bl_ecdsa_verify_hash_secp256r1(param_1,param_2 + 8,param_5,param_3,param_4);
    cc310_bl_backend_disable();
    DataMemoryBarrier(0x1f);
    *DAT_000fb290 = 0;
    uVar2 = 0;
    if (iVar1 != 0) {
      if (iVar1 + DAT_000fb294 == 0) {
        uVar2 = 0x8542;
      }
      else {
        uVar2 = 0x8516;
      }
    }
  }
  else {
    uVar2 = 0x8504;
  }
  return uVar2;
}



/* ============================================================
 * entry: 000fb298
 * name: nrf_crypto_ecc_public_key_from_raw
 * body: 000fb298-000fb2c7
 * ============================================================ */

void nrf_crypto_ecc_public_key_from_raw(int param_1,undefined4 *param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 extraout_r3;

  iVar1 = nrf_crypto_internal_ecc_key_output_prepare();
  if (((iVar1 == 0) &&
      (iVar1 = nrf_crypto_internal_ecc_raw_input_check
                         (param_3,extraout_r3,*(undefined1 *)(param_1 + 6)), iVar1 == 0)) &&
     (iVar1 = nrf_crypto_backend_secp256r1_public_key_from_raw(param_2,param_3), iVar1 == 0)) {
    *param_2 = DAT_000fb2c8;
  }
  return;
}



/* ============================================================
 * entry: 000fb2cc
 * name: nrf_crypto_ecdsa_verify
 * body: 000fb2cc-000fb31b
 * ============================================================ */

int nrf_crypto_ecdsa_verify
              (int param_1,int param_2,int param_3,undefined4 param_4,undefined4 param_5,
              undefined4 param_6)

{
  int iVar1;

  iVar1 = nrf_crypto_internal_ecc_key_input_check(param_2,DAT_000fb31c,param_3,param_4,param_4);
  if ((iVar1 == 0) &&
     (iVar1 = nrf_crypto_internal_ecc_raw_input_check
                        (param_5,param_6,(uint)*(byte *)(*(int *)(param_2 + 4) + 5) << 1),
     iVar1 == 0)) {
    if (param_3 == 0) {
      iVar1 = 0x8510;
    }
    else if (param_1 == 0) {
      iVar1 = 0x8515;
    }
    else {
      iVar1 = nrf_crypto_backend_secp256r1_verify(param_1,param_2,param_3,param_4,param_5);
    }
  }
  return iVar1;
}



/* ============================================================
 * entry: 000fb320
 * name: nrf_crypto_hash_finalize
 * body: 000fb320-000fb38b
 * ============================================================ */

int nrf_crypto_hash_finalize
              (int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,int param_5,
              uint *param_6)

{
  int iVar1;

  iVar1 = nrf_crypto_hash_init();
  if ((iVar1 != 0) || (iVar1 = nrf_crypto_hash_update(param_1,param_3,param_4), iVar1 != 0)) {
    return iVar1;
  }
  iVar1 = verify_context();
  if (iVar1 == 0) {
    if (param_5 == 0) {
      return 0x8513;
    }
    if (*(uint *)(*(int *)(param_1 + 4) + 0xc) <= *param_6) {
                    /* WARNING: Could not recover jumptable at 0x000fb38a. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      iVar1 = (**(code **)(*(int *)(param_1 + 4) + 8))(param_1,param_5,param_6);
      return iVar1;
    }
    iVar1 = 0x8514;
  }
  return iVar1;
}



/* ============================================================
 * entry: 000fb38c
 * name: nrf_crypto_hash_init
 * body: 000fb38c-000fb3b1
 * ============================================================ */

int nrf_crypto_hash_init(undefined4 *param_1,undefined4 *param_2)

{
  int iVar1;

  if (param_1 == (undefined4 *)0x0) {
    return 0x8501;
  }
  if (param_2 != (undefined4 *)0x0) {
    param_1[1] = param_2;
    iVar1 = (*(code *)*param_2)();
    if (iVar1 == 0) {
      *param_1 = DAT_000fb3b4;
      iVar1 = 0;
    }
    return iVar1;
  }
  return 0x8510;
}



/* ============================================================
 * entry: 000fb3b8
 * name: nrf_crypto_hash_update
 * body: 000fb3b8-000fb3e5
 * ============================================================ */

int nrf_crypto_hash_update(int param_1,int param_2,int param_3)

{
  int iVar1;

  iVar1 = verify_context();
  if (iVar1 == 0) {
    if (param_2 != 0) {
      if (param_3 != 0) {
                    /* WARNING: Could not recover jumptable at 0x000fb3da. Too many branches */
                    /* WARNING: Treating indirect jump as call */
        iVar1 = (**(code **)(*(int *)(param_1 + 4) + 4))(param_1,param_2,param_3);
        return iVar1;
      }
      return 0;
    }
    iVar1 = 0x8510;
  }
  return iVar1;
}



/* ============================================================
 * entry: 000fb3e8
 * name: nrf_crypto_init
 * body: 000fb3e8-000fb3fd;000fb400-000fb419
 * ============================================================ */

int nrf_crypto_init(void)

{
  int iVar1;
  undefined1 *puVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;

  puVar2 = DAT_000fb424;
  iVar1 = DAT_000fb420;
  uVar3 = DAT_000fb41c - DAT_000fb420;
  *DAT_000fb424 = 1;
  uVar5 = 0;
  while( true ) {
    if (uVar3 >> 3 <= uVar5) {
      *puVar2 = 2;
      return 0;
    }
    iVar4 = (**(code **)(iVar1 + uVar5 * 8))();
    if (iVar4 != 0) break;
    uVar5 = uVar5 + 1;
  }
  return iVar4;
}



/* ============================================================
 * entry: 000fb428
 * name: nrf_crypto_internal_double_swap_endian
 * body: 000fb428-000fb441
 * ============================================================ */

void nrf_crypto_internal_double_swap_endian(int param_1,int param_2,int param_3)

{
  nrf_crypto_internal_swap_endian();
  nrf_crypto_internal_swap_endian(param_1 + param_3,param_2 + param_3,param_3);
  return;
}



/* ============================================================
 * entry: 000fb442
 * name: nrf_crypto_internal_double_swap_endian_in_place
 * body: 000fb442-000fb457
 * ============================================================ */

void nrf_crypto_internal_double_swap_endian_in_place(int param_1,int param_2)

{
  nrf_crypto_internal_swap_endian_in_place();
  nrf_crypto_internal_swap_endian_in_place(param_1 + param_2,param_2);
  return;
}



/* ============================================================
 * entry: 000fb458
 * name: nrf_crypto_internal_ecc_key_input_check
 * body: 000fb458-000fb46f
 * ============================================================ */

undefined4 nrf_crypto_internal_ecc_key_input_check(int *param_1,int param_2)

{
  if (param_1 == (int *)0x0) {
    return 0x8510;
  }
  if (*param_1 != param_2) {
    return 0x8540;
  }
  return 0;
}



/* ============================================================
 * entry: 000fb470
 * name: nrf_crypto_internal_ecc_key_output_prepare
 * body: 000fb470-000fb489
 * ============================================================ */

undefined4 nrf_crypto_internal_ecc_key_output_prepare(int param_1,undefined4 *param_2)

{
  if (param_1 == 0) {
    return 0x8510;
  }
  if (param_2 != (undefined4 *)0x0) {
    *param_2 = 0;
    param_2[1] = param_1;
    return 0;
  }
  return 0x8513;
}



/* ============================================================
 * entry: 000fb48a
 * name: nrf_crypto_internal_ecc_raw_input_check
 * body: 000fb48a-000fb49f
 * ============================================================ */

undefined4 nrf_crypto_internal_ecc_raw_input_check(int param_1,int param_2,int param_3)

{
  if (param_1 == 0) {
    return 0x8510;
  }
  if (param_2 != param_3) {
    return 0x8511;
  }
  return 0;
}



/* ============================================================
 * entry: 000fb4a0
 * name: nrf_crypto_internal_swap_endian
 * body: 000fb4a0-000fb4a5;000fb4a8-000fb4b5
 * ============================================================ */

void nrf_crypto_internal_swap_endian(undefined1 *param_1,undefined1 *param_2,int param_3)

{
  undefined1 *puVar1;

  puVar1 = param_1 + param_3;
  while (puVar1 = puVar1 + -1, param_1 <= puVar1) {
    *puVar1 = *param_2;
    param_2 = param_2 + 1;
  }
  return;
}



/* ============================================================
 * entry: 000fb4b6
 * name: nrf_crypto_internal_swap_endian_in_place
 * body: 000fb4b6-000fb4cd
 * ============================================================ */

void nrf_crypto_internal_swap_endian_in_place(undefined1 *param_1,int param_2)

{
  undefined1 uVar1;
  undefined1 *puVar2;

  puVar2 = param_1 + param_2;
  for (; puVar2 = puVar2 + -1, param_1 <= puVar2; param_1 = param_1 + 1) {
    uVar1 = *param_1;
    *param_1 = *puVar2;
    *puVar2 = uVar1;
  }
  return;
}



/* ============================================================
 * entry: 000fb4d0
 * name: nrf_dfu_bank0_start_addr
 * body: 000fb4d0-000fb4f1
 * ============================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int nrf_dfu_bank0_start_addr(void)

{
  if (_DAT_00003004 == DAT_000fb4f4) {
    return (_DAT_00003008 - (_DAT_00003008 - 1U & 0xfff)) + 0xfff;
  }
  return 0x1000;
}



/* ============================================================
 * entry: 000fb4f8
 * name: nrf_dfu_bank1_start_addr
 * body: 000fb4f8-000fb513
 * ============================================================ */

int nrf_dfu_bank1_start_addr(void)

{
  int iVar1;

  iVar1 = nrf_dfu_bank0_start_addr();
  return ((*(int *)(DAT_000fb514 + 0x18) + iVar1) -
         (iVar1 + -1 + *(int *)(DAT_000fb514 + 0x18) & 0xfffU)) + 0xfff;
}



/* ============================================================
 * entry: 000fb518
 * name: nrf_dfu_bank_invalidate
 * body: 000fb518-000fb525
 * ============================================================ */

void nrf_dfu_bank_invalidate(undefined4 *param_1)

{
  *param_1 = 0;
  param_1[1] = 0;
  param_1[2] = 0;
  *(undefined4 *)(DAT_000fb528 + 0x30) = 0;
  return;
}



/* ============================================================
 * entry: 000fb52c
 * name: nrf_dfu_cache_prepare
 * body: 000fb52c-000fb5b7
 * ============================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 nrf_dfu_cache_prepare(uint param_1,uint param_2,int param_3,int param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint extraout_r3;
  uint extraout_r3_00;

  iVar1 = DAT_000fb5b8;
  uVar6 = 0;
  do {
    uVar4 = 1;
    if (uVar6 == 0) {
      iVar2 = nrf_dfu_bank1_start_addr();
      uVar6 = extraout_r3;
      if ((param_3 == 0) || (uVar4 = 1, *(int *)(DAT_000fb5bc + 0x20) != 1)) {
LAB_000fb582:
        uVar4 = 0;
      }
    }
    else if (uVar6 == 1) {
      iVar2 = nrf_dfu_bank0_start_addr();
      uVar6 = extraout_r3_00;
      if ((param_4 == 0) && (_DAT_00003004 == DAT_000fb5c0)) goto LAB_000fb582;
      uVar4 = 1;
    }
    else if (uVar6 == 2) {
      iVar2 = 0x1000;
    }
    else {
      iVar2 = 0;
    }
    uVar5 = (uint)((iVar1 - iVar2) - 0x24000U < param_1);
    if (((((uVar5 | param_2) & ~uVar4) == 0) || (1 < uVar6)) ||
       (uVar6 = uVar6 + 1 & 0xff, 2 < uVar6)) {
      if (uVar5 == 0) {
        if (uVar6 != 0) {
          nrf_dfu_bank_invalidate(DAT_000fb5bc + 0x18);
        }
        uVar3 = 0;
      }
      else {
        uVar3 = 4;
      }
      return uVar3;
    }
  } while( true );
}



/* ============================================================
 * entry: 000fb5c4
 * name: nrf_dfu_command_req
 * body: 000fb5c4-000fb5d1;000fb5dc-000fb651
 * ============================================================ */

void nrf_dfu_command_req(undefined1 *param_1,int param_2)

{
  undefined1 uVar1;
  int iVar2;

  switch(*param_1) {
  case 1:
    (**(code **)(DAT_000fb654 + 0xc))(3);
    nrf_dfu_validation_init_cmd_create(*(undefined4 *)(param_1 + 0x14));
    uVar1 = ext_err_code_handle();
    *(undefined1 *)(param_2 + 1) = uVar1;
    break;
  case 3:
    goto LAB_000fb64a;
  case 4:
    nrf_dfu_validation_init_cmd_execute(DAT_000fb654 + 4);
    iVar2 = ext_err_code_handle();
    *(char *)(param_2 + 1) = (char)iVar2;
    if ((iVar2 == 1) && (iVar2 = nrf_dfu_settings_write_and_backup(0), iVar2 != 0)) {
      *(undefined1 *)(param_2 + 1) = 10;
      return;
    }
    break;
  case 6:
    *(undefined4 *)(param_2 + 0xc) = 0x200;
LAB_000fb64a:
    cmd_response_offset_and_crc_set(param_2);
    return;
  case 8:
    nrf_dfu_validation_init_cmd_append
              (*(undefined4 *)(param_1 + 0x10),*(undefined2 *)(param_1 + 0x14));
    uVar1 = ext_err_code_handle();
    *(undefined1 *)(param_2 + 1) = uVar1;
    cmd_response_offset_and_crc_set(param_2);
    if (*(code **)(param_1 + 0xc) != (code *)0x0) {
                    /* WARNING: Could not recover jumptable at 0x000fb61a. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      (**(code **)(param_1 + 0xc))(*(undefined4 *)(param_1 + 0x10));
      return;
    }
  }
  return;
}



/* ============================================================
 * entry: 000fb658
 * name: nrf_dfu_data_req
 * body: 000fb658-000fb669;000fb674-000fb6c3
 * ============================================================ */

undefined4 nrf_dfu_data_req(undefined1 *param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;

  iVar1 = DAT_000fb6c4;
  uVar3 = 1;
  uVar2 = *(undefined4 *)(DAT_000fb6c4 + 0x48);
  switch(*param_1) {
  case 1:
    nrf_dfu_data_object_create();
    break;
  case 3:
    *(undefined4 *)(param_2 + 8) = uVar2;
    *(undefined4 *)(param_2 + 4) = *(undefined4 *)(iVar1 + 0x50);
    break;
  case 4:
    if (*(int *)(DAT_000fb6c4 + 0x44) ==
        *(int *)(DAT_000fb6c4 + 0x50) - *(int *)(DAT_000fb6c4 + 0x54)) {
      uVar3 = 0;
      *(int *)(DAT_000fb6c4 + 0x54) = *(int *)(DAT_000fb6c4 + 0x50);
      *(undefined4 *)(iVar1 + 0x44) = 0;
      *(undefined4 *)(iVar1 + 0x4c) = uVar2;
      on_data_obj_execute_request_sched(param_1,0);
      (**(code **)(DAT_000fb6c8 + 0xc))(4);
    }
    else {
      *(undefined1 *)(param_2 + 1) = 8;
      uVar3 = 1;
    }
    break;
  case 6:
    *(undefined4 *)(param_2 + 8) = uVar2;
    *(undefined4 *)(param_2 + 4) = *(undefined4 *)(iVar1 + 0x50);
    *(undefined4 *)(param_2 + 0xc) = 0x1000;
    break;
  case 8:
    nrf_dfu_data_object_write();
  }
  return uVar3;
}



/* ============================================================
 * entry: 000fb6cc
 * name: nrf_dfu_flash_erase
 * body: 000fb6cc-000fb6d7
 * ============================================================ */

void nrf_dfu_flash_erase(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  nrf_fstorage_erase(DAT_000fb6d8,param_1,param_2,param_3);
  return;
}



/* ============================================================
 * entry: 000fb6dc
 * name: nrf_dfu_flash_init
 * body: 000fb6dc-000fb6eb
 * ============================================================ */

void nrf_dfu_flash_init(int param_1)

{
  undefined4 uVar1;

  uVar1 = DAT_000fb6f0;
  if (param_1 != 0) {
    uVar1 = DAT_000fb6ec;
  }
  nrf_fstorage_init(DAT_000fb6f4,uVar1,0);
  return;
}



/* ============================================================
 * entry: 000fb6f8
 * name: nrf_dfu_flash_store
 * body: 000fb6f8-000fb709
 * ============================================================ */

void nrf_dfu_flash_store(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4
                        )

{
  nrf_fstorage_write(DAT_000fb70c,param_1,param_2,param_3,param_4);
  return;
}



/* ============================================================
 * entry: 000fb710
 * name: nrf_dfu_init
 * body: 000fb710-000fb731;000fb77c-000fb7b9
 * ============================================================ */

int nrf_dfu_init(undefined4 param_1)

{
  int iVar1;
  int iVar2;

  *DAT_000fb734 = param_1;
  nrf_dfu_observer(0);
  iVar2 = nrf_dfu_transports_init(DAT_000fb738);
  iVar1 = DAT_000fb738;
  if (iVar2 != 0) {
    return iVar2;
  }
  if (DAT_000fb738 != 0) {
    iVar2 = nrf_dfu_flash_init(1);
    if (iVar2 == 0) {
      nrf_dfu_validation_init();
      iVar2 = nrf_dfu_validation_init_cmd_present();
      if ((iVar2 == 0) ||
         (iVar2 = nrf_dfu_validation_init_cmd_execute(DAT_000fb7bc + -4), iVar2 == 1)) {
        *(int *)(DAT_000fb7bc + 4) = iVar1;
        ext_error_set(0);
        return 0;
      }
      iVar2 = 3;
    }
    return iVar2;
  }
  return 7;
}



/* ============================================================
 * entry: 000fb73c
 * name: nrf_dfu_init_user
 * body: 000fb73c-000fb73f
 * ============================================================ */

undefined4 nrf_dfu_init_user(void)

{
  return 0;
}



/* ============================================================
 * entry: 000fb740
 * name: nrf_dfu_mbr_copy_bl
 * body: 000fb740-000fb755
 * ============================================================ */

undefined1 * nrf_dfu_mbr_copy_bl(void)

{
  undefined1 local_18 [16];

  software_interrupt(0x18);
  return local_18;
}



/* ============================================================
 * entry: 000fb758
 * name: nrf_dfu_mbr_init_sd
 * body: 000fb758-000fb769
 * ============================================================ */

undefined1 * nrf_dfu_mbr_init_sd(void)

{
  undefined1 local_18 [16];

  software_interrupt(0x18);
  return local_18;
}



/* ============================================================
 * entry: 000fb770
 * name: nrf_dfu_mbr_irq_forward_address_set
 * body: 000fb770-000fb77b
 * ============================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 nrf_dfu_mbr_irq_forward_address_set(void)

{
  _DAT_20000000 = 0x1000;
  return 0;
}



/* ============================================================
 * entry: 000fb7c0
 * name: nrf_dfu_req_handler_on_req
 * body: 000fb7c0-000fb7cf
 * ============================================================ */

undefined4 nrf_dfu_req_handler_on_req(int param_1)

{
  undefined4 uVar1;

  if (*(int *)(param_1 + 8) != 0) {
    uVar1 = app_sched_event_put(param_1,0x18,DAT_000fb7d0);
    return uVar1;
  }
  return 7;
}



/* ============================================================
 * entry: 000fb7d8
 * name: nrf_dfu_req_handler_req_process
 * body: 000fb7d8-000fb7f9;000fb808-000fb85f
 * ============================================================ */

void nrf_dfu_req_handler_req_process(byte *param_1)

{
  byte bVar1;
  byte *pbVar2;
  int iVar3;
  byte local_28;
  char local_27;

  memmove(&local_28,DAT_000fb860,0x18);
  pbVar2 = DAT_000fb864;
  local_28 = *param_1;
  bVar1 = *param_1;
  switch(bVar1) {
  default:
    local_27 = '\x02';
    break;
  case 1:
  case 3:
  case 4:
  case 6:
  case 8:
    if ((bVar1 == 6) || (bVar1 == 1)) {
      *DAT_000fb864 = param_1[0x10];
    }
    if (*pbVar2 == 1) {
      nrf_dfu_command_req(param_1,&local_28);
    }
    else if (*pbVar2 == 2) {
      iVar3 = nrf_dfu_data_req();
      if (iVar3 == 0) {
        return;
      }
    }
    else {
      *pbVar2 = 0;
      local_27 = '\x05';
    }
    break;
  case 2:
    break;
  case 0xc:
    (**(code **)(DAT_000fb864 + 0xc))(7);
  }
  (**(code **)(param_1 + 8))(&local_28,*(undefined4 *)(param_1 + 4));
  if (local_27 != '\x01') {
    (**(code **)(pbVar2 + 0xc))(5);
  }
  return;
}



/* ============================================================
 * entry: 000fb868
 * name: nrf_dfu_set_adv_name_handler
 * body: 000fb868-000fb87d
 * ============================================================ */

undefined4 nrf_dfu_set_adv_name_handler(undefined4 *param_1)

{
  if (param_1 != (undefined4 *)0x0) {
    *param_1 = DAT_000fb880;
    param_1[1] = DAT_000fb884;
    *(undefined1 *)(param_1 + 2) = 1;
    return 0;
  }
  return 0xe;
}



/* ============================================================
 * entry: 000fb8e4
 * name: nrf_dfu_settings_additional_erase
 * body: 000fb8e4-000fb911
 * ============================================================ */

undefined4 nrf_dfu_settings_additional_erase(void)

{
  if ((*(int *)(DAT_000fb914 + 0x324) != -1) || (*(int *)(DAT_000fb914 + 0x364) != -1)) {
    nrf_nvmc_page_erase(0xff000);
    nrf_nvmc_write_words(0xff000,DAT_000fb914,0xc9);
  }
  return 0;
}



/* ============================================================
 * entry: 000fb918
 * name: nrf_dfu_settings_adv_name_copy
 * body: 000fb918-000fb92b
 * ============================================================ */

undefined4 nrf_dfu_settings_adv_name_copy(int param_1)

{
  if (param_1 != 0) {
    memmove(param_1,DAT_000fb92c,0x1c);
    return 0;
  }
  return 0xe;
}



/* ============================================================
 * entry: 000fb930
 * name: bootloader_adv_name_record_valid
 * body: 000fb930-000fb94b
 * ============================================================ */

undefined4 bootloader_adv_name_record_valid(void)

{
  int *piVar1;
  int iVar2;

  piVar1 = DAT_000fb94c;
  iVar2 = crc32_compute(DAT_000fb94c + 1,0x18,0);
  if (*piVar1 == iVar2) {
    return 1;
  }
  return 0;
}



/* ============================================================
 * entry: 000fb950
 * name: nrf_dfu_settings_adv_name_write
 * body: 000fb950-000fb981
 * ============================================================ */

undefined8 nrf_dfu_settings_adv_name_write(undefined4 *param_1,undefined4 param_2)

{
  undefined4 uVar1;
  int iVar2;

  iVar2 = DAT_000fb984 + 0x364;
  if (param_1 == (undefined4 *)0x0) {
    return CONCAT44(param_2,0xe);
  }
  if (*(int *)(DAT_000fb984 + 0x364) != -1) {
    return CONCAT44(param_2,8);
  }
  uVar1 = crc32_compute(param_1 + 1,0x18,0);
  *param_1 = uVar1;
  software_interrupt(0x29);
  return CONCAT44(param_1,iVar2);
}



/* ============================================================
 * entry: 000fb988
 * name: nrf_dfu_settings_backup
 * body: 000fb988-000fb98d
 * ============================================================ */

void nrf_dfu_settings_backup(undefined4 param_1)

{
  settings_backup(param_1,DAT_000fb990);
  return;
}



/* ============================================================
 * entry: 000fb994
 * name: nrf_dfu_settings_init
 * body: 000fb994-000fb9ad
 * ============================================================ */

undefined4 nrf_dfu_settings_init(void)

{
  int iVar1;

  iVar1 = nrf_dfu_flash_init();
  if (iVar1 == 0) {
    nrf_dfu_settings_reinit();
    iVar1 = nrf_dfu_settings_write_and_backup(0);
    if (iVar1 == 0) {
      return 0;
    }
  }
  return 3;
}



/* ============================================================
 * entry: 000fb9b0
 * name: nrf_dfu_settings_progress_reset
 * body: 000fb9b0-000fb9d1
 * ============================================================ */

void nrf_dfu_settings_progress_reset(void)

{
  armcc_memset_core(DAT_000fb9d4,0x200,0xff);
  armcc_memclr(DAT_000fb9d4 + -0x24,0x20);
  *(undefined4 *)(DAT_000fb9d4 + -0x2c) = 0;
  return;
}



/* ============================================================
 * entry: 000fb9d8
 * name: nrf_dfu_settings_reinit
 * body: 000fb9d8-000fba95
 * ============================================================ */

void nrf_dfu_settings_reinit(void)

{
  bool bVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;

  iVar3 = crc_ok(DAT_000fba98);
  piVar2 = DAT_000fba9c;
  iVar6 = *DAT_000fba9c;
  iVar4 = crc_ok(iVar6);
  if ((iVar4 == 0) ||
     ((*(int *)(iVar6 + 4) != 1 &&
      (iVar4 = boot_validation_crc(iVar6), iVar4 != *(int *)(iVar6 + 0x25c))))) {
    bVar1 = false;
  }
  else {
    bVar1 = true;
  }
  iVar4 = DAT_000fbaa0;
  if (iVar3 == 0) {
    if (!bVar1) {
      armcc_memclr(DAT_000fbaa0);
      goto LAB_000fba86;
    }
    uVar5 = 0x380;
    iVar6 = *piVar2;
    iVar3 = DAT_000fbaa0;
LAB_000fba4e:
    memmove(iVar3,iVar6,uVar5);
  }
  else {
    memmove(DAT_000fbaa0,DAT_000fba98,0x380);
    if (bVar1) {
      iVar6 = *piVar2;
      memmove(iVar4 + 4,iVar6 + 4,0x54);
      uVar5 = 0x2c8;
      iVar6 = iVar6 + 0x5c;
      iVar3 = iVar4 + 0x5c;
      goto LAB_000fba4e;
    }
  }
  if (*(int *)(iVar4 + 4) != 1) {
    return;
  }
  memmove(DAT_000fbaa4 + 0x1c8,DAT_000fbaa4,0x40);
  memmove(DAT_000fbaa4 + 0x208,DAT_000fbaa4 + 0x40,0x1c);
  *(undefined1 *)(iVar4 + 0x260) = 0;
  *(undefined1 *)(iVar4 + 0x2a1) = 1;
  iVar3 = DAT_000fbaa8;
  *(undefined1 *)(iVar4 + 0x2e2) = 0;
  *(undefined4 *)(iVar3 + 0x22) = *(undefined4 *)(iVar4 + 0x1c);
LAB_000fba86:
  *(undefined4 *)(iVar4 + 4) = 2;
  return;
}



/* ============================================================
 * entry: 000fbaac
 * name: nrf_dfu_settings_write
 * body: 000fbaac-000fbad5
 * ============================================================ */

void nrf_dfu_settings_write(undefined4 param_1)

{
  undefined4 *puVar1;
  undefined4 uVar2;

  uVar2 = settings_crc_get(DAT_000fbad8);
  puVar1 = DAT_000fbad8;
  *DAT_000fbad8 = uVar2;
  uVar2 = boot_validation_crc(puVar1);
  puVar1[0x97] = uVar2;
  settings_write(DAT_000fbadc,puVar1,param_1,puVar1 + -0x1c0);
  return;
}



/* ============================================================
 * entry: 000fbae0
 * name: nrf_dfu_settings_write_and_backup
 * body: 000fbae0-000fbaf9
 * ============================================================ */

int nrf_dfu_settings_write_and_backup(undefined4 param_1)

{
  int iVar1;

  iVar1 = nrf_dfu_settings_write(0);
  if (iVar1 == 0) {
    settings_backup(param_1,DAT_000fbafc);
  }
  return iVar1;
}



/* ============================================================
 * entry: 000fbb00
 * name: nrf_dfu_softdevice_start_address
 * body: 000fbb00-000fbb05
 * ============================================================ */

undefined4 nrf_dfu_softdevice_start_address(void)

{
  return 0x1000;
}



/* ============================================================
 * entry: 000fbb08
 * name: nrf_dfu_transports_close
 * body: 000fbb08-000fbb33
 * ============================================================ */

void nrf_dfu_transports_close(undefined4 param_1)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;

  iVar1 = DAT_000fbb38;
  uVar2 = DAT_000fbb34 - DAT_000fbb38;
  uVar4 = 0;
  while ((uVar4 < uVar2 >> 3 && (iVar3 = (**(code **)(iVar1 + uVar4 * 8 + 4))(param_1), iVar3 == 0))
        ) {
    uVar4 = uVar4 + 1;
  }
  return;
}



/* ============================================================
 * entry: 000fbb3c
 * name: nrf_dfu_transports_init
 * body: 000fbb3c-000fbb65
 * ============================================================ */

void nrf_dfu_transports_init(undefined4 param_1)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;

  iVar1 = DAT_000fbb6c;
  uVar2 = DAT_000fbb68 - DAT_000fbb6c;
  uVar4 = 0;
  while ((uVar4 < uVar2 >> 3 && (iVar3 = (**(code **)(iVar1 + uVar4 * 8))(param_1), iVar3 == 0))) {
    uVar4 = uVar4 + 1;
  }
  return;
}



/* ============================================================
 * entry: 000fbb70
 * name: nrf_dfu_validation_postvalidate
 * body: 000fbb70-000fbb75
 * ============================================================ */

void nrf_dfu_validation_postvalidate(undefined4 param_1,undefined4 param_2)

{
  nrf_dfu_validation_postvalidate_impl(param_1,param_2,1);
  return;
}



/* ============================================================
 * entry: 000fbb76
 * name: nrf_dfu_validation_boot_validate
 * body: 000fbb76-000fbc1d
 * ============================================================ */

/* WARNING: Removing unreachable block (ram,0x000fbbe6) */

undefined4 nrf_dfu_validation_boot_validate(char *param_1,undefined4 param_2,undefined4 param_3)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_b8 [156];
  undefined4 local_1c [3];

  cVar1 = *param_1;
  if (cVar1 != '\0') {
    if (cVar1 == '\x01') {
      crc32_compute(param_2,param_3,0);
    }
    else {
      if (cVar1 == '\x02') {
        local_1c[0] = 0x20;
        uVar3 = 1;
        armcc_memclr(auStack_b8,0x7c);
        crypto_init();
        iVar2 = nrf_crypto_hash_finalize
                          (auStack_b8,DAT_000fbc24,param_2,param_3,DAT_000fbc20,local_1c);
        if ((iVar2 != 0) || (iVar2 = memcmp(DAT_000fbc20,param_1 + 1,0x20), iVar2 != 0)) {
          uVar3 = 0;
        }
        return uVar3;
      }
      if ((cVar1 != '\x03') ||
         (iVar2 = nrf_dfu_validation_signature_check(0,param_1 + 1,0x40), iVar2 != 1)) {
        return 0;
      }
    }
  }
  return 1;
}



/* ============================================================
 * entry: 000fbc28
 * name: nrf_dfu_validation_init
 * body: 000fbc28-000fbc41
 * ============================================================ */

void nrf_dfu_validation_init(void)

{
  undefined1 *puVar1;
  undefined1 uVar2;
  int iVar3;

  puVar1 = DAT_000fbc48;
  if ((*(int *)(DAT_000fbc44 + 0x38) == 0) || (iVar3 = stored_init_cmd_decode(), iVar3 == 0)) {
    uVar2 = 0;
  }
  else {
    uVar2 = 1;
  }
  *puVar1 = uVar2;
  return;
}



/* ============================================================
 * entry: 000fbc4c
 * name: nrf_dfu_validation_init_cmd_append
 * body: 000fbc4c-000fbc8d
 * ============================================================ */

undefined4 nrf_dfu_validation_init_cmd_append(undefined4 param_1,int param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;

  iVar1 = DAT_000fbc90;
  uVar4 = 1;
  if (*(uint *)(DAT_000fbc90 + 0x38) < (uint)(*(int *)(DAT_000fbc90 + 0x3c) + param_2)) {
    uVar4 = 3;
  }
  else {
    memmove(*(int *)(DAT_000fbc90 + 0x3c) + DAT_000fbc90 + 0x5c,param_1,param_2);
    iVar2 = DAT_000fbc90;
    *(int *)(iVar1 + 0x3c) = *(int *)(iVar1 + 0x3c) + param_2;
    uVar3 = crc32_compute(param_1,param_2,iVar2 + 0x40);
    *(undefined4 *)(iVar1 + 0x40) = uVar3;
  }
  return uVar4;
}



/* ============================================================
 * entry: 000fbc94
 * name: nrf_dfu_validation_init_cmd_create
 * body: 000fbc94-000fbcbd
 * ============================================================ */

undefined4 nrf_dfu_validation_init_cmd_create(uint param_1)

{
  undefined4 uVar1;

  uVar1 = 1;
  if (param_1 == 0) {
    uVar1 = 3;
  }
  else if (param_1 < 0x201) {
    *DAT_000fbcc0 = 0;
    nrf_dfu_settings_progress_reset();
    *(uint *)(DAT_000fbcc4 + 0x38) = param_1;
  }
  else {
    uVar1 = 4;
  }
  return uVar1;
}



/* ============================================================
 * entry: 000fbcc8
 * name: nrf_dfu_validation_init_cmd_execute
 * body: 000fbcc8-000fbd51
 * ============================================================ */

int nrf_dfu_validation_init_cmd_execute(undefined4 *param_1,undefined4 *param_2)

{
  char *pcVar1;
  undefined4 uVar2;
  int iVar3;

  pcVar1 = DAT_000fbd58;
  if (*(int *)(DAT_000fbd54 + 0x3c) == *(int *)(DAT_000fbd54 + 0x38)) {
    if (*DAT_000fbd58 == '\0') {
      iVar3 = stored_init_cmd_decode();
      if (iVar3 == 0) {
        iVar3 = 5;
      }
      else {
        iVar3 = nrf_dfu_validation_prevalidate();
        *param_1 = 0;
        *param_2 = 0;
        if ((iVar3 == 1) &&
           (iVar3 = update_data_size_get(*(undefined4 *)(pcVar1 + 0xc),param_2), iVar3 == 1)) {
          uVar2 = 0;
          if ((*(char *)(*(int *)(pcVar1 + 0xc) + 0x55) == '\0') ||
             (*(char *)(*(int *)(pcVar1 + 0xc) + 0x55) == '\x01')) {
            uVar2 = 1;
          }
          iVar3 = nrf_dfu_cache_prepare(*param_2,uVar2,0,1);
          if (iVar3 == 0) {
            uVar2 = nrf_dfu_bank1_start_addr();
            *param_1 = uVar2;
            *pcVar1 = '\x01';
            return 1;
          }
          iVar3 = 4;
        }
        nrf_dfu_settings_progress_reset();
      }
    }
    else {
      uVar2 = nrf_dfu_bank1_start_addr();
      *param_1 = uVar2;
      iVar3 = update_data_size_get(*(undefined4 *)(pcVar1 + 0xc),param_2);
    }
  }
  else {
    iVar3 = 8;
  }
  return iVar3;
}



/* ============================================================
 * entry: 000fbd5c
 * name: nrf_dfu_validation_init_cmd_present
 * body: 000fbd5c-000fbd61
 * ============================================================ */

undefined1 nrf_dfu_validation_init_cmd_present(void)

{
  return *DAT_000fbd64;
}



/* ============================================================
 * entry: 000fbd68
 * name: nrf_dfu_validation_prevalidate
 * body: 000fbd68-000fbda5
 * ============================================================ */

void nrf_dfu_validation_prevalidate(void)

{
  undefined1 uVar1;
  int iVar2;
  undefined2 uVar3;
  int iVar4;

  iVar4 = DAT_000fbda8 + 4;
  uVar1 = 0;
  iVar2 = 0;
  uVar3 = 0;
  if (*(char *)(DAT_000fbda8 + 0x16c) != '\0') {
    uVar1 = *(undefined1 *)(DAT_000fbda8 + 0x2d8);
    uVar3 = *(undefined2 *)(DAT_000fbda8 + 0x2da);
    iVar4 = DAT_000fbda8 + 0x170;
    iVar2 = DAT_000fbda8 + 0x2dc;
  }
  iVar2 = nrf_dfu_validation_signature_check(uVar1,iVar2,uVar3,*(undefined4 *)(DAT_000fbdac + 4));
  if (iVar2 == 1) {
    nrf_dfu_ver_validation_check(iVar4 + 4);
    return;
  }
  return;
}



/* ============================================================
 * entry: 000fbdb0
 * name: nrf_dfu_validation_signature_check
 * body: 000fbdb0-000fbe3f
 * ============================================================ */

undefined4
nrf_dfu_validation_signature_check
          (int param_1,int param_2,int param_3,undefined4 param_4,undefined4 param_5)

{
  undefined4 uVar1;
  int iVar2;
  undefined1 auStack_140 [164];
  undefined1 auStack_9c [124];
  undefined4 local_20 [2];

  local_20[0] = 0x20;
  armcc_memclr(auStack_9c,0x7c);
  armcc_memclr(auStack_140,0xa4);
  crypto_init();
  if (param_2 == 0) {
    uVar1 = 0x13;
  }
  else if (param_1 == 0) {
    iVar2 = nrf_crypto_hash_finalize(auStack_9c,DAT_000fbe44,param_4,param_5,DAT_000fbe40,local_20);
    if ((iVar2 == 0) && (param_3 == 0x40)) {
      memmove(DAT_000fbe40 + -0x40,param_2,0x40);
      nrf_crypto_internal_double_swap_endian_in_place(DAT_000fbe40 + -0x40,0x20);
      iVar2 = nrf_crypto_ecdsa_verify
                        (auStack_140,DAT_000fbe40 + -0x88,DAT_000fbe40,local_20[0],
                         DAT_000fbe40 + -0x40,0x40);
      if (iVar2 == 0) {
        uVar1 = 1;
      }
      else {
        uVar1 = 5;
      }
    }
    else {
      uVar1 = 10;
    }
  }
  else {
    uVar1 = 0x16;
  }
  return uVar1;
}



/* ============================================================
 * entry: 000fbe48
 * name: nrf_dfu_ver_validation_check
 * body: 000fbe48-000fbecd
 * ============================================================ */

undefined4 nrf_dfu_ver_validation_check(char *param_1)

{
  char cVar1;
  int iVar2;

  if ((param_1[0x54] != '\0') &&
     ((((cVar1 = param_1[0x55], cVar1 == '\0' || (cVar1 == '\x01')) || (cVar1 == '\x02')) ||
      (cVar1 == '\x03')))) {
    if (param_1[0x6e] != '\x03') {
      return 0x14;
    }
    if ((param_1[0x92] != '\0') && (param_1[0x93] != '\0')) {
      return 1;
    }
    if (param_1[8] != '\0') {
      if (*(int *)(param_1 + 0xc) != 0x34) {
        return 0x11;
      }
      iVar2 = sd_req_ok(param_1);
      if (iVar2 == 0) {
        return 0x12;
      }
      if (*param_1 != '\0') {
        if ((param_1[0x55] == '\0') || (param_1[0x55] == '\x01')) {
          if (*(uint *)(DAT_000fbed0 + 8) <= *(uint *)(param_1 + 4)) {
            return 1;
          }
        }
        else if (*(uint *)(DAT_000fbed0 + 0xc) < *(uint *)(param_1 + 4)) {
          return 1;
        }
        return 0x10;
      }
      if (param_1[0x55] == '\x01') {
        return 1;
      }
    }
  }
  return 0xf;
}



/* ============================================================
 * entry: 000fbed4
 * name: nrf_fstorage_erase
 * body: 000fbed4-000fbeff
 * ============================================================ */

void nrf_fstorage_erase(int *param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  addr_is_within_bounds(param_1,param_2,param_3 * *(int *)param_1[1]);
                    /* WARNING: Could not recover jumptable at 0x000fbefe. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (**(code **)(*param_1 + 0x10))(param_1,param_2,param_3,param_4);
  return;
}



/* ============================================================
 * entry: 000fbf00
 * name: nrf_fstorage_init
 * body: 000fbf00-000fbf07
 * ============================================================ */

void nrf_fstorage_init(undefined4 *param_1,undefined4 *param_2,undefined4 param_3)

{
  *param_1 = param_2;
                    /* WARNING: Could not recover jumptable at 0x000fbf06. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)*param_2)(param_1,param_3);
  return;
}



/* ============================================================
 * entry: 000fbf08
 * name: nrf_fstorage_is_busy
 * body: 000fbf08-000fbf25;000fbf28-000fbf4d
 * ============================================================ */

undefined4 nrf_fstorage_is_busy(int *param_1)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;

  iVar1 = DAT_000fbf50;
  if ((param_1 != (int *)0x0) && (*param_1 != 0)) {
                    /* WARNING: Could not recover jumptable at 0x000fbf18. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    uVar2 = (**(code **)(*param_1 + 0x1c))();
    return uVar2;
  }
  uVar4 = 0;
  uVar5 = DAT_000fbf54 - DAT_000fbf50;
  while( true ) {
    if (uVar5 / 0x14 <= uVar4) {
      return 0;
    }
    iVar3 = *(int *)(iVar1 + uVar4 * 0x14);
    if ((iVar3 != 0) && (iVar3 = (**(code **)(iVar3 + 0x1c))(), iVar3 != 0)) break;
    uVar4 = uVar4 + 1;
  }
  return 1;
}



/* ============================================================
 * entry: 000fbf90
 * name: nrf_fstorage_sys_evt_handler
 * body: 000fbf90-000fc025
 * ============================================================ */

void nrf_fstorage_sys_evt_handler(int param_1)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;

  iVar2 = DAT_000fc028;
  if (((param_1 != 2) && (param_1 != 3)) || (cVar1 = *(char *)(DAT_000fc028 + 8), cVar1 == '\0')) {
    return;
  }
  if ((cVar1 == '\x01') || (cVar1 != '\x02')) goto LAB_000fc00c;
  iVar3 = *DAT_000fc02c;
  if (param_1 == 2) {
    *(undefined4 *)(DAT_000fc028 + 0xc) = 0;
    if (*(char *)(iVar3 + 4) == '\0') {
      uVar6 = *(int *)(iVar3 + 0x14) - *(int *)(iVar3 + 0x18);
      if (0x13 < uVar6) {
        uVar6 = 0x14;
      }
      iVar4 = uVar6 + *(int *)(iVar3 + 0x18);
      *(int *)(iVar3 + 0x18) = iVar4;
      if (iVar4 != *(int *)(iVar3 + 0x14)) goto LAB_000fc00c;
      goto LAB_000fbffc;
    }
    if ((*(char *)(iVar3 + 4) != '\x01') ||
       (iVar4 = *(int *)(iVar3 + 0x10) + 1, *(int *)(iVar3 + 0x10) = iVar4,
       iVar4 != *(int *)(iVar3 + 0x14))) goto LAB_000fc00c;
    *(undefined1 *)(iVar2 + 8) = 0;
LAB_000fc018:
    uVar5 = 0;
  }
  else {
    if ((param_1 != 3) ||
       (uVar6 = *(int *)(DAT_000fc028 + 0xc) + 1, *(uint *)(DAT_000fc028 + 0xc) = uVar6, uVar6 < 9))
    goto LAB_000fc00c;
    *(undefined4 *)(iVar2 + 0xc) = 0;
LAB_000fbffc:
    *(undefined1 *)(iVar2 + 8) = 0;
    if (param_1 == 2) goto LAB_000fc018;
    uVar5 = 0xd;
  }
  event_send(iVar3,uVar5);
  queue_free();
LAB_000fc00c:
  if (*(char *)(iVar2 + 0x11) == '\0') {
    queue_process();
    return;
  }
  nrf_sdh_request_continue();
  return;
}



/* ============================================================
 * entry: 000fc030
 * name: nrf_fstorage_write
 * body: 000fc030-000fc06d
 * ============================================================ */

void nrf_fstorage_write(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                       undefined4 param_5)

{
  addr_is_aligned32(param_2);
  addr_is_aligned32(param_3);
  addr_is_within_bounds(param_1,param_2,param_4);
  (**(code **)(*param_1 + 0xc))(param_1,param_2,param_3,param_4,param_5);
  return;
}



/* ============================================================
 * entry: 000fc070
 * name: nrf_nvmc_page_erase
 * body: 000fc070-000fc097
 * ============================================================ */

void nrf_nvmc_page_erase(undefined4 param_1)

{
  undefined4 *puVar1;

  puVar1 = DAT_000fc098;
  *DAT_000fc098 = 2;
  InstructionSynchronizationBarrier(0xf);
  DataSynchronizationBarrier(0xf);
  puVar1[1] = param_1;
  do {
  } while (*DAT_000fc09c == 0);
  *puVar1 = 0;
  InstructionSynchronizationBarrier(0xf);
  DataSynchronizationBarrier(0xf);
  return;
}



/* ============================================================
 * entry: 000fc0a0
 * name: nrf_nvmc_write_word
 * body: 000fc0a0-000fc0c5
 * ============================================================ */

void nrf_nvmc_write_word(undefined4 *param_1,undefined4 param_2)

{
  undefined4 *puVar1;

  puVar1 = DAT_000fc0c8;
  *DAT_000fc0c8 = 1;
  InstructionSynchronizationBarrier(0xf);
  DataSynchronizationBarrier(0xf);
  *param_1 = param_2;
  do {
  } while (*DAT_000fc0cc == 0);
  *puVar1 = 0;
  InstructionSynchronizationBarrier(0xf);
  DataSynchronizationBarrier(0xf);
  return;
}



/* ============================================================
 * entry: 000fc0d0
 * name: nrf_nvmc_write_words
 * body: 000fc0d0-000fc0e5;000fc0e8-000fc109
 * ============================================================ */

void nrf_nvmc_write_words(int param_1,int param_2,uint param_3)

{
  undefined4 *puVar1;
  int *piVar2;
  uint uVar3;

  puVar1 = DAT_000fc10c;
  *DAT_000fc10c = 1;
  piVar2 = DAT_000fc110;
  InstructionSynchronizationBarrier(0xf);
  DataSynchronizationBarrier(0xf);
  for (uVar3 = 0; uVar3 < param_3; uVar3 = uVar3 + 1) {
    *(undefined4 *)(param_1 + uVar3 * 4) = *(undefined4 *)(param_2 + uVar3 * 4);
    do {
    } while (*piVar2 == 0);
  }
  *puVar1 = 0;
  InstructionSynchronizationBarrier(0xf);
  DataSynchronizationBarrier(0xf);
  return;
}



/* ============================================================
 * entry: 000fc114
 * name: nrf_rtc_event_clear
 * body: 000fc114-000fc11f
 * ============================================================ */

void nrf_rtc_event_clear(int param_1,int param_2)

{
  *(undefined4 *)(param_1 + param_2) = 0;
  return;
}



/* ============================================================
 * entry: 000fc120
 * name: nrf_sdh_ble_app_ram_start_get
 * body: 000fc120-000fc12f
 * ============================================================ */

undefined4 nrf_sdh_ble_app_ram_start_get(undefined4 *param_1)

{
  if (param_1 != (undefined4 *)0x0) {
    *param_1 = *DAT_000fc130;
    return 0;
  }
  return 0xe;
}



/* ============================================================
 * entry: 000fc134
 * name: nrf_sdh_ble_default_cfg_set
 * body: 000fc134-000fc1cf
 * ============================================================ */

undefined8 nrf_sdh_ble_default_cfg_set(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 local_20;

  iVar1 = nrf_sdh_ble_app_ram_start_get(param_2);
  local_20 = param_2;
  if (iVar1 == 0) {
    software_interrupt(0x69);
    software_interrupt(0x69);
    software_interrupt(0x69);
    software_interrupt(0x69);
    software_interrupt(0x69);
    local_20 = 0;
    software_interrupt(0x69);
    iVar1 = 0;
  }
  return CONCAT44(local_20,iVar1);
}



/* ============================================================
 * entry: 000fc1d0
 * name: nrf_sdh_ble_enable
 * body: 000fc1d0-000fc1dd
 * ============================================================ */

void nrf_sdh_ble_enable(int param_1)

{
  software_interrupt(0x60);
  if (param_1 == 0) {
    *DAT_000fc1e0 = 1;
  }
  return;
}



/* ============================================================
 * entry: 000fc1e4
 * name: nrf_sdh_soc_evts_poll
 * body: 000fc1e4-000fc23b
 * ============================================================ */

void nrf_sdh_soc_evts_poll(void)

{
  undefined1 auStack_210 [508];
  undefined4 *local_14;
  undefined2 local_10 [2];

  if (*DAT_000fc23c != '\0') {
    while( true ) {
      local_10[0] = 500;
      software_interrupt(0x61);
      if (&stack0x00000000 != (undefined1 *)0x210) break;
      nrf_section_iter_init(500,DAT_000fc240);
      while (local_14 != (undefined4 *)0x0) {
        (*(code *)*local_14)(0,local_14[1]);
        nrf_section_iter_next(500);
      }
    }
    if (&stack0x00000000 != (undefined1 *)0x215) {
      app_error_handler_bare(auStack_210,local_10);
      return;
    }
  }
  return;
}



/* ============================================================
 * entry: 000fc244
 * name: nrf_sdh_disable_request
 * body: 000fc244-000fc293
 * ============================================================ */

int nrf_sdh_disable_request(void)

{
  char *pcVar1;
  int iVar2;
  uint in_r3;
  uint local_18;

  pcVar1 = DAT_000fc294;
  if (*DAT_000fc294 == '\0') {
    return 8;
  }
  DAT_000fc294[2] = '\x01';
  local_18 = in_r3;
  iVar2 = sdh_request_observer_notify();
  if (iVar2 != 0x11) {
    sdh_state_observer_notify(2);
    local_18 = local_18 & 0xffffff00;
    iVar2 = app_util_critical_region_enter(&local_18);
    software_interrupt(0x11);
    *pcVar1 = '\0';
    app_util_critical_region_exit(local_18 & 0xff);
    if (iVar2 != 0) {
      return iVar2;
    }
    pcVar1[2] = '\0';
    softdevice_evt_irq_disable();
    sdh_state_observer_notify(3);
  }
  return 0;
}



/* ============================================================
 * entry: 000fc298
 * name: nrf_sdh_enable_request
 * body: 000fc298-000fc2fd
 * ============================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 *
nrf_sdh_enable_request(undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  char *pcVar1;
  undefined4 uVar2;
  int iVar3;
  uint local_18;
  undefined4 local_14;

  pcVar1 = _DAT_000fc300;
  if (*_DAT_000fc300 != '\0') {
    return (undefined4 *)&NMI;
  }
  _DAT_000fc300[2] = '\x01';
  local_18 = param_3;
  local_14 = param_4;
  iVar3 = sdh_request_observer_notify(0);
  if (iVar3 != 0x11) {
    sdh_state_observer_notify(0);
    local_14 = *_DAT_000fc304;
    local_18 = local_18 & 0xffffff00;
    app_util_critical_region_enter(&local_18);
    uVar2 = _DAT_000fc308;
    software_interrupt(0x10);
    *pcVar1 = &local_14 == (undefined4 *)0x0;
    app_util_critical_region_exit(local_18 & 0xff,uVar2);
    if (&local_14 != (undefined4 *)0x0) {
      return &local_14;
    }
    pcVar1[2] = '\0';
    pcVar1[1] = '\0';
    softdevices_evt_irq_enable();
    sdh_state_observer_notify(1);
  }
  return (undefined4 *)0x0;
}



/* ============================================================
 * entry: 000fc30c
 * name: SWI2_EGU2_IRQHandler
 * body: 000fc30c-000fc32b
 * ============================================================ */

void SWI2_EGU2_IRQHandler
               (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 *param_4)

{
  undefined4 uStack_10;
  undefined4 uStack_c;
  undefined4 *local_8;

  uStack_10 = param_2;
  uStack_c = param_3;
  local_8 = param_4;
  nrf_section_iter_init(&uStack_10,DAT_000fc32c);
  while (local_8 != (undefined4 *)0x0) {
    (*(code *)*local_8)(local_8[1]);
    nrf_section_iter_next(&uStack_10);
  }
  return;
}



/* ============================================================
 * entry: 000fc330
 * name: nrf_sdh_is_enabled
 * body: 000fc330-000fc335
 * ============================================================ */

undefined1 nrf_sdh_is_enabled(void)

{
  return *DAT_000fc338;
}



/* ============================================================
 * entry: 000fc33c
 * name: nrf_sdh_request_continue
 * body: 000fc33c-000fc351
 * ============================================================ */

undefined4 nrf_sdh_request_continue(void)

{
  undefined4 uVar1;

  if (DAT_000fc354[2] == '\0') {
    return 8;
  }
  if (*DAT_000fc354 != '\0') {
    uVar1 = nrf_sdh_disable_request();
    return uVar1;
  }
  uVar1 = nrf_sdh_enable_request();
  return uVar1;
}



/* ============================================================
 * entry: 000fc394
 * name: nrf_section_iter_init
 * body: 000fc394-000fc3c1
 * ============================================================ */

void nrf_section_iter_init(int *param_1,int *param_2)

{
  int *piVar1;
  int iVar2;

  *param_1 = (int)param_2;
  param_1[1] = *param_2;
  piVar1 = (int *)param_1[1];
  while (piVar1 != *(int **)(*param_1 + 4)) {
    iVar2 = *piVar1;
    if (iVar2 != piVar1[1]) goto LAB_000fc3b8;
    piVar1 = piVar1 + 2;
    param_1[1] = (int)piVar1;
  }
  iVar2 = 0;
LAB_000fc3b8:
  param_1[2] = iVar2;
  return;
}



/* ============================================================
 * entry: 000fc3c2
 * name: nrf_section_iter_next
 * body: 000fc3c2-000fc3e1
 * ============================================================ */

void nrf_section_iter_next(int *param_1)

{
  int *piVar1;
  int iVar2;

  if (param_1[2] != 0) {
    iVar2 = *(int *)(*param_1 + 8) + param_1[2];
    param_1[2] = iVar2;
    if (iVar2 == *(int *)(param_1[1] + 4)) {
      param_1[1] = param_1[1] + 8;
      piVar1 = (int *)param_1[1];
      while (piVar1 != *(int **)(*param_1 + 4)) {
        iVar2 = *piVar1;
        if (iVar2 != piVar1[1]) goto LAB_000fc3b8;
        piVar1 = piVar1 + 2;
        param_1[1] = (int)piVar1;
      }
      iVar2 = 0;
LAB_000fc3b8:
      param_1[2] = iVar2;
      return;
    }
  }
  return;
}



/* ============================================================
 * entry: 000fc3e4
 * name: nrf_svc_handler_c
 * body: 000fc3e4-000fc437
 * ============================================================ */

void nrf_svc_handler_c(undefined4 *param_1)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  uint *puVar4;

  uVar3 = 0xffffffff;
  if (*(byte *)(param_1[6] + -2) == 0) {
    uVar3 = param_1[4];
  }
  uVar1 = 0;
  do {
    if ((uint)(DAT_000fc438 - DAT_000fc43c) / 0xc <= uVar1) {
      uVar2 = 1;
LAB_000fc432:
      *param_1 = uVar2;
      return;
    }
    puVar4 = (uint *)(DAT_000fc43c + uVar1 * 0xc);
    if ((*puVar4 == (uint)*(byte *)(param_1[6] + -2)) &&
       ((uVar3 == 0xffffffff || (puVar4[1] == uVar3)))) {
      uVar2 = (*(code *)puVar4[2])(*param_1,param_1[1],param_1[2],param_1[3]);
      goto LAB_000fc432;
    }
    uVar1 = uVar1 + 1;
  } while( true );
}



/* ============================================================
 * entry: 000fc440
 * name: nrf_wdt_started
 * body: 000fc440-000fc44b
 * ============================================================ */

bool nrf_wdt_started(void)

{
  return *DAT_000fc44c != 0;
}



/* ============================================================
 * entry: 000fc450
 * name: nvmc_wait
 * body: 000fc450-000fc45d
 * ============================================================ */

void nvmc_wait(undefined4 param_1)

{
  *DAT_000fc460 = param_1;
  do {
  } while (*DAT_000fc464 == 0);
  return;
}



/* ============================================================
 * entry: 000fc468
 * name: on_ctrl_pt_write
 * body: 000fc468-000fc4cd
 * ============================================================ */

void on_ctrl_pt_write(undefined4 param_1,int param_2)

{
  undefined2 uVar1;
  int iVar2;
  char local_28 [4];
  undefined4 local_24;
  uint local_18;
  undefined4 local_14;

  memmove(local_28,DAT_000fc4d0,0x18);
  iVar2 = DAT_000fc4d4;
  local_28[0] = *(char *)(param_2 + 0xc);
  local_24 = param_1;
  if (local_28[0] == '\x01') {
    *(undefined2 *)(DAT_000fc4d4 + 6) = *(undefined2 *)(DAT_000fc4d4 + 4);
    local_18 = (uint)*(byte *)(param_2 + 0xd);
    local_14 = *(undefined4 *)(param_2 + 0xe);
    if (local_18 == 1) {
      nrf_dfu_transports_close(DAT_000fc4d8);
    }
  }
  else if (local_28[0] == '\x02') {
    uVar1 = *(undefined2 *)(param_2 + 0xd);
    *(undefined2 *)(DAT_000fc4d4 + 4) = uVar1;
    *(undefined2 *)(iVar2 + 6) = uVar1;
  }
  else if (local_28[0] == '\x06') {
    local_18 = (uint)*(byte *)(param_2 + 0xd);
  }
  nrf_dfu_req_handler_on_req(local_28);
  return;
}



/* ============================================================
 * entry: 000fc4dc
 * name: nrf_dfu_data_object_create
 * body: 000fc4dc-000fc547
 * ============================================================ */

void nrf_dfu_data_object_create(int param_1,int param_2)

{
  int iVar1;
  undefined1 uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;

  iVar3 = nrf_dfu_validation_init_cmd_present();
  iVar1 = DAT_000fc54c;
  iVar4 = DAT_000fc548;
  if (iVar3 == 0) {
LAB_000fc51c:
    *(undefined1 *)(param_2 + 1) = 8;
  }
  else {
    uVar5 = *(uint *)(param_1 + 0x14);
    uVar2 = 3;
    if ((uVar5 != 0) &&
       (((uVar5 & 0xfff) == 0 ||
        (*(int *)(DAT_000fc548 + 0x54) + uVar5 == *(int *)(DAT_000fc54c + 8))))) {
      if (uVar5 < 0x1001) {
        iVar3 = *(int *)(DAT_000fc548 + 0x54);
        if (*(uint *)(DAT_000fc54c + 8) < iVar3 + uVar5) goto LAB_000fc51c;
        *(uint *)(DAT_000fc548 + 0x44) = uVar5;
        *(int *)(iVar4 + 0x50) = iVar3;
        *(undefined4 *)(iVar4 + 0x48) = *(undefined4 *)(iVar4 + 0x4c);
        *(int *)(iVar4 + 0x30) = iVar3;
        iVar4 = nrf_dfu_flash_erase(iVar3 + *(int *)(iVar1 + 4),
                                    *(int *)(param_1 + 0x14) + 0xfffU >> 0xc,0);
        if (iVar4 == 0) {
          return;
        }
        uVar2 = 5;
      }
      else {
        uVar2 = 4;
      }
    }
    *(undefined1 *)(param_2 + 1) = uVar2;
  }
  return;
}



/* ============================================================
 * entry: 000fc550
 * name: on_data_obj_execute_request_sched
 * body: 000fc550-000fc5b3
 * ============================================================ */

void on_data_obj_execute_request_sched(int param_1)

{
  int iVar1;
  undefined1 uStack_20;
  undefined1 local_1f;

  iVar1 = nrf_fstorage_is_busy(0);
  if (iVar1 == 0) {
    memmove(&uStack_20,DAT_000fc5b8,0x18);
    if (*(int *)(DAT_000fc5bc + 0x50) == *(int *)(DAT_000fc5c0 + 8)) {
      local_1f = nrf_dfu_validation_postvalidate(*(undefined4 *)(DAT_000fc5c0 + 4));
      local_1f = ext_err_code_handle();
      (**(code **)(param_1 + 8))(&uStack_20,*(undefined4 *)(param_1 + 4));
      nrf_dfu_settings_write_and_backup(DAT_000fc5c4);
    }
    else {
      local_1f = 1;
      (**(code **)(param_1 + 8))(&uStack_20,*(undefined4 *)(param_1 + 4));
    }
  }
  else {
    app_sched_event_put(param_1,0x18,DAT_000fc5b4);
  }
  return;
}



/* ============================================================
 * entry: 000fc5c8
 * name: nrf_dfu_data_object_write
 * body: 000fc5c8-000fc63d
 * ============================================================ */

void nrf_dfu_data_object_write(int param_1,int param_2)

{
  ushort uVar1;
  int iVar2;
  undefined1 uVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;

  iVar4 = nrf_dfu_validation_init_cmd_present();
  iVar2 = DAT_000fc640;
  if (iVar4 == 0) {
    uVar3 = 8;
  }
  else {
    if ((*(int *)(DAT_000fc640 + 0x50) - *(int *)(DAT_000fc640 + 0x54)) +
        (uint)*(ushort *)(param_1 + 0x14) <= *(uint *)(DAT_000fc640 + 0x44)) {
      iVar4 = *(int *)(DAT_000fc640 + 0x30);
      iVar6 = *(int *)(DAT_000fc644 + 4);
      uVar5 = crc32_compute(*(undefined4 *)(param_1 + 0x10),(uint)*(ushort *)(param_1 + 0x14),
                            DAT_000fc640 + 0x48);
      iVar4 = nrf_dfu_flash_store(iVar4 + iVar6,*(undefined4 *)(param_1 + 0x10),
                                  *(undefined2 *)(param_1 + 0x14),*(undefined4 *)(param_1 + 0xc));
      if (iVar4 == 0) {
        *(uint *)(iVar2 + 0x30) = *(int *)(iVar2 + 0x30) + (uint)*(ushort *)(param_1 + 0x14);
        uVar1 = *(ushort *)(param_1 + 0x14);
        *(undefined4 *)(iVar2 + 0x48) = uVar5;
        *(uint *)(iVar2 + 0x50) = *(int *)(iVar2 + 0x50) + (uint)uVar1;
        *(undefined4 *)(param_2 + 8) = uVar5;
        *(undefined4 *)(param_2 + 4) = *(undefined4 *)(iVar2 + 0x50);
        return;
      }
                    /* WARNING: Could not recover jumptable at 0x000fc61e. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      (**(code **)(param_1 + 0xc))(*(undefined4 *)(param_1 + 0x10));
      return;
    }
    uVar3 = 3;
  }
  *(undefined1 *)(param_2 + 1) = uVar3;
  return;
}



/* ============================================================
 * entry: 000fc654
 * name: app_error_fault_handler
 * body: 000fc654-000fc679
 * ============================================================ */

void app_error_fault_handler(void)

{
  if ((*DAT_000fc67c & 1) != 0) {
    software_bkpt(0);
  }
  DataSynchronizationBarrier(0xf);
  DAT_000fc67c[-0x39] = DAT_000fc67c[-0x39] & 0x700 | DAT_000fc680;
  DataSynchronizationBarrier(0xf);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* ============================================================
 * entry: 000fc684
 * name: on_flash_write
 * body: 000fc684-000fc68b
 * ============================================================ */

void on_flash_write(undefined4 param_1)

{
  nrf_balloc_free(DAT_000fc68c,param_1);
  return;
}



/* ============================================================
 * entry: 000fc690
 * name: on_rw_authorize_req
 * body: 000fc690-000fc70f
 * ============================================================ */

undefined8 on_rw_authorize_req(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 *puVar4;
  undefined1 auStack_28 [4];
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  int local_18;
  undefined4 local_14;
  undefined1 *local_10;

  iVar1 = DAT_000fc714;
  puVar4 = (undefined4 *)(param_2 + 8);
  local_10 = auStack_28;
  if (((*(char *)(param_2 + 6) == '\x02') && (*(short *)(param_2 + 8) == *(short *)(param_1 + 0xc)))
     && (*(char *)(param_2 + 0xe) == '\x01')) {
    local_24 = *DAT_000fc710;
    local_20 = DAT_000fc710[1];
    local_1c = *(undefined4 *)(param_2 + 0x10);
    local_18 = param_2 + 0x14;
    local_14 = DAT_000fc710[-0x18];
    software_interrupt(0xad);
    if ((*(short *)(DAT_000fc714 + 2) == 0) &&
       (iVar2 = ble_srv_is_notification_enabled
                          (auStack_28,*(undefined2 *)(param_1 + 0x10),&local_14), iVar2 == 0)) {
      puVar4 = &local_24;
      software_interrupt(0xb0);
    }
    else {
      puVar4 = &local_24;
      software_interrupt(0xb0);
      if (*(short *)(iVar1 + 2) == 0) {
        uVar3 = 1;
        goto LAB_000fc708;
      }
    }
  }
  uVar3 = 0;
LAB_000fc708:
  return CONCAT44(puVar4,uVar3);
}



/* ============================================================
 * entry: 000fc718
 * name: pb_dec_bytes
 * body: 000fc718-000fc759
 * ============================================================ */

undefined4 pb_dec_bytes(undefined4 param_1,int param_2,undefined2 *param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint local_18;

  local_18 = param_4;
  iVar1 = pb_decode_varint32(param_1,&local_18);
  if ((((iVar1 != 0) && (local_18 < 0x10000)) && (local_18 <= local_18 + 2)) &&
     ((*(byte *)(param_2 + 2) >> 6 != 2 && (local_18 + 2 <= (uint)*(ushort *)(param_2 + 8))))) {
    *param_3 = (short)local_18;
    uVar2 = pb_read(param_1,param_3 + 1,local_18);
    return uVar2;
  }
  return 0;
}



/* ============================================================
 * entry: 000fc75a
 * name: pb_dec_fixed32
 * body: 000fc75a-000fc75f
 * ============================================================ */

void pb_dec_fixed32(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  pb_decode_fixed32(param_1,param_3);
  return;
}



/* ============================================================
 * entry: 000fc760
 * name: pb_dec_fixed64
 * body: 000fc760-000fc765
 * ============================================================ */

void pb_dec_fixed64(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  pb_decode_fixed64(param_1,param_3);
  return;
}



/* ============================================================
 * entry: 000fc766
 * name: pb_dec_string
 * body: 000fc766-000fc7a3
 * ============================================================ */

undefined4 pb_dec_string(undefined4 param_1,int param_2,int param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint local_18;

  local_18 = param_4;
  iVar1 = pb_decode_varint32(param_1,&local_18);
  if ((((iVar1 != 0) && (local_18 <= local_18 + 1)) && (*(byte *)(param_2 + 2) >> 6 != 2)) &&
     (local_18 + 1 <= (uint)*(ushort *)(param_2 + 8))) {
    uVar2 = pb_read(param_1,param_3);
    *(undefined1 *)(param_3 + local_18) = 0;
    return uVar2;
  }
  return 0;
}



/* ============================================================
 * entry: 000fc7a4
 * name: pb_dec_submessage
 * body: 000fc7a4-000fc7e3
 * ============================================================ */

void pb_dec_submessage(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iStack_28;
  int local_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;

  uVar2 = *(undefined4 *)(param_2 + 0xc);
  iStack_28 = param_1;
  local_24 = param_2;
  uStack_20 = param_3;
  uStack_1c = param_4;
  iVar1 = pb_make_string_substream(param_1,&iStack_28);
  if ((iVar1 != 0) && (*(int *)(param_2 + 0xc) != 0)) {
    if ((*(byte *)(param_2 + 2) & 0x3f) >> 4 == 2) {
      pb_decode(&iStack_28,uVar2,param_3);
    }
    else {
      pb_decode_noinit();
    }
    *(int *)(param_1 + 4) = local_24;
  }
  return;
}



/* ============================================================
 * entry: 000fc7e4
 * name: pb_dec_svarint
 * body: 000fc7e4-000fc83b
 * ============================================================ */

undefined4 pb_dec_svarint(undefined4 param_1,int param_2,short *param_3,int param_4)

{
  short sVar1;
  int iVar2;
  short *psVar3;
  short *local_18;
  int iStack_14;

  local_18 = param_3;
  iStack_14 = param_4;
  iVar2 = pb_decode_svarint(param_1,&local_18);
  if (iVar2 != 0) {
    sVar1 = *(short *)(param_2 + 8);
    psVar3 = local_18;
    if (sVar1 == 8) {
      *(short **)param_3 = local_18;
      *(int *)(param_3 + 2) = iStack_14;
      iVar2 = iStack_14;
    }
    else {
      if (sVar1 == 4) {
        *(short **)param_3 = local_18;
      }
      else if (sVar1 == 2) {
        *param_3 = (short)local_18;
        psVar3 = (short *)(int)(short)local_18;
      }
      else {
        if (sVar1 != 1) {
          return 0;
        }
        *(char *)param_3 = (char)local_18;
        psVar3 = (short *)(int)(char)local_18;
      }
      iVar2 = (int)psVar3 >> 0x1f;
    }
    if (psVar3 == local_18 && iVar2 == iStack_14) {
      return 1;
    }
  }
  return 0;
}



/* ============================================================
 * entry: 000fc83c
 * name: pb_dec_uvarint
 * body: 000fc83c-000fc893
 * ============================================================ */

undefined4 pb_dec_uvarint(undefined4 param_1,int param_2,undefined4 *param_3,int param_4)

{
  short sVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 *local_18;
  int iStack_14;

  local_18 = param_3;
  iStack_14 = param_4;
  iVar2 = pb_decode_varint(param_1,&local_18);
  if (iVar2 != 0) {
    sVar1 = *(short *)(param_2 + 8);
    puVar3 = local_18;
    if (sVar1 == 8) {
      *param_3 = local_18;
      param_3[1] = iStack_14;
      iVar2 = iStack_14;
    }
    else {
      iVar2 = 0;
      if (sVar1 == 4) {
        *param_3 = local_18;
      }
      else if (sVar1 == 2) {
        *(short *)param_3 = (short)local_18;
        puVar3 = (undefined4 *)((uint)local_18 & 0xffff);
      }
      else {
        if (sVar1 != 1) {
          return 0;
        }
        *(char *)param_3 = (char)local_18;
        puVar3 = (undefined4 *)((uint)local_18 & 0xff);
      }
    }
    if (puVar3 == local_18 && iVar2 == iStack_14) {
      return 1;
    }
  }
  return 0;
}



/* ============================================================
 * entry: 000fc894
 * name: pb_dec_varint
 * body: 000fc894-000fc8eb
 * ============================================================ */

undefined4 pb_dec_varint(undefined4 param_1,int param_2,short *param_3,int param_4)

{
  short sVar1;
  int iVar2;
  short *psVar3;
  short *local_18;
  int iStack_14;

  local_18 = param_3;
  iStack_14 = param_4;
  iVar2 = pb_decode_varint(param_1,&local_18);
  if (iVar2 != 0) {
    sVar1 = *(short *)(param_2 + 8);
    psVar3 = local_18;
    if (sVar1 == 8) {
      *(short **)param_3 = local_18;
      *(int *)(param_3 + 2) = iStack_14;
      iVar2 = iStack_14;
    }
    else {
      iStack_14 = (int)local_18 >> 0x1f;
      if (sVar1 == 4) {
        *(short **)param_3 = local_18;
      }
      else if (sVar1 == 2) {
        *param_3 = (short)local_18;
        psVar3 = (short *)(int)(short)local_18;
      }
      else {
        if (sVar1 != 1) {
          return 0;
        }
        *(char *)param_3 = (char)local_18;
        psVar3 = (short *)(int)(char)local_18;
      }
      iVar2 = (int)psVar3 >> 0x1f;
    }
    if (psVar3 == local_18 && iVar2 == iStack_14) {
      return 1;
    }
  }
  return 0;
}



/* ============================================================
 * entry: 000fc8ec
 * name: pb_decode
 * body: 000fc8ec-000fc909
 * ============================================================ */

void pb_decode(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  pb_message_set_to_defaults(param_2,param_3);
  pb_decode_noinit(param_1,param_2,param_3);
  return;
}



/* ============================================================
 * entry: 000fc90a
 * name: pb_decode_fixed32
 * body: 000fc90a-000fc933
 * ============================================================ */

bool pb_decode_fixed32(undefined4 param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;

  local_10 = param_4;
  iVar1 = pb_read(param_1,&local_10,4);
  if (iVar1 != 0) {
    *param_2 = local_10;
  }
  return iVar1 != 0;
}



/* ============================================================
 * entry: 000fc934
 * name: pb_decode_fixed64
 * body: 000fc934-000fc98f
 * ============================================================ */

bool pb_decode_fixed64(undefined4 param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 local_c;

  local_10 = param_3;
  local_c = param_4;
  iVar1 = pb_read(param_1,&local_10,8);
  if (iVar1 != 0) {
    *param_2 = local_10;
    param_2[1] = local_c;
  }
  return iVar1 != 0;
}



/* ============================================================
 * entry: 000fc990
 * name: pb_decode_noinit
 * body: 000fc990-000fcae9;000fcaec-000fcb19
 * ============================================================ */

undefined4 pb_decode_noinit(int param_1)

{
  ushort uVar1;
  ushort *puVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int *piVar6;
  uint uVar7;
  uint local_98;
  undefined1 auStack_94 [4];
  ushort *local_90;
  uint local_8c;
  undefined4 *local_84;
  uint local_7c;
  byte local_6c [12];
  uint local_60;
  uint local_5c [3];
  char local_50 [20];
  undefined1 auStack_3c [24];

  local_5c[0] = 0;
  uVar7 = 0;
  local_5c[1] = 0;
  pb_field_iter_begin(auStack_94);
LAB_000fcabc:
  do {
    if (*(int *)(param_1 + 8) == 0) {
LAB_000fcac4:
      do {
        uVar7 = local_8c;
        uVar1 = local_90[1];
        iVar4 = pb_field_iter_next(auStack_94);
      } while (iVar4 != 0);
      if (((uVar1 & 0x30) == 0) && (*local_90 != 0)) {
        uVar7 = uVar7 + 1;
      }
      if (uVar7 != 0) {
        for (uVar5 = 0; uVar5 < uVar7 >> 5; uVar5 = uVar5 + 1) {
          if (local_5c[uVar5] != 0xffffffff) {
            return 0;
          }
        }
        if (local_5c[uVar7 >> 5] != 0xffffffffU >> (0x20 - (uVar7 & 0x1f) & 0xff)) {
          return 0;
        }
      }
      return 1;
    }
    iVar4 = pb_decode_tag(param_1,local_6c,&local_98,local_50);
    if (iVar4 == 0) {
      if (local_50[0] == '\0') {
        return 0;
      }
      goto LAB_000fcac4;
    }
    iVar4 = pb_field_iter_find(auStack_94,local_98);
    puVar2 = local_90;
    if (iVar4 == 0) {
      if (uVar7 <= local_98) {
        do {
          if ((local_90[1] & 0xf) == 8) {
            uVar7 = (uint)*local_90;
            goto LAB_000fca0a;
          }
          pb_field_iter_next(auStack_94);
        } while (local_90 != puVar2);
        uVar7 = 0xffffffff;
LAB_000fca0a:
        if (uVar7 <= local_98) {
          iVar4 = *(int *)(param_1 + 8);
          local_7c = local_98;
          local_60 = (uint)local_6c[0];
          piVar6 = (int *)*local_84;
          while ((uVar5 = local_60, piVar6 != (int *)0x0 && (*(int *)(param_1 + 8) == iVar4))) {
            if (*(code **)*piVar6 == (code *)0x0) {
              local_5c[2] = param_1;
              if (**(ushort **)(*piVar6 + 8) == local_7c) {
                iter_from_extension(auStack_3c,piVar6);
                *(undefined1 *)(piVar6 + 3) = 1;
                iVar3 = nanopb_decode_field(local_5c[2],uVar5,auStack_3c);
                goto LAB_000fca60;
              }
            }
            else {
              iVar3 = (**(code **)*piVar6)(param_1,piVar6,local_7c,local_60);
LAB_000fca60:
              if (iVar3 == 0) {
                return 0;
              }
            }
            piVar6 = (int *)piVar6[2];
          }
          if (*(int *)(param_1 + 8) != iVar4) goto LAB_000fcabc;
        }
      }
      iVar4 = pb_skip_field(param_1,local_6c[0]);
    }
    else {
      if (((local_90[1] & 0x30) == 0) && (local_8c < 0x40)) {
        local_5c[local_8c >> 5] = local_5c[local_8c >> 5] | 1 << (local_8c & 0x1f);
      }
      if (*(code **)(param_1 + 0xc) != (code *)0x0) {
        (**(code **)(param_1 + 0xc))(param_1,local_98,local_6c[0],auStack_94);
      }
      iVar4 = nanopb_decode_field(param_1,local_6c[0],auStack_94);
    }
    if (iVar4 == 0) {
      return 0;
    }
  } while( true );
}



/* ============================================================
 * entry: 000fcb1a
 * name: pb_decode_svarint
 * body: 000fcb1a-000fcb53
 * ============================================================ */

undefined4 pb_decode_svarint(undefined4 param_1,uint *param_2,uint param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint local_10;
  uint uStack_c;

  local_10 = param_3;
  uStack_c = param_4;
  iVar1 = pb_decode_varint(param_1,&local_10);
  uVar2 = 0;
  if (iVar1 != 0) {
    if ((local_10 & 1) == 0) {
      *param_2 = (uint)((uStack_c & 1) != 0) << 0x1f | local_10 >> 1;
      param_2[1] = uStack_c >> 1;
    }
    else {
      *param_2 = ~((uint)((uStack_c & 1) != 0) << 0x1f | local_10 >> 1);
      param_2[1] = ~(uStack_c >> 1);
    }
    uVar2 = 1;
  }
  return uVar2;
}



/* ============================================================
 * entry: 000fcb54
 * name: pb_decode_tag
 * body: 000fcb54-000fcb95
 * ============================================================ */

undefined4 pb_decode_tag(int param_1,byte *param_2,uint *param_3,undefined1 *param_4)

{
  int iVar1;
  undefined1 *local_18;

  *param_4 = 0;
  *param_2 = 0;
  *param_3 = 0;
  local_18 = param_4;
  iVar1 = pb_decode_varint32(param_1,&local_18);
  if (iVar1 == 0) {
    if (*(int *)(param_1 + 8) != 0) {
      return 0;
    }
  }
  else if (local_18 != (undefined1 *)0x0) {
    *param_3 = (uint)local_18 >> 3;
    *param_2 = (byte)local_18 & 7;
    return 1;
  }
  *param_4 = 1;
  return 0;
}



/* ============================================================
 * entry: 000fcb96
 * name: pb_decode_varint
 * body: 000fcb96-000fcbdf
 * ============================================================ */

undefined4 pb_decode_varint(undefined4 param_1,uint *param_2,undefined4 param_3,uint param_4)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  undefined8 uVar6;
  uint local_20;

  uVar5 = 0;
  uVar3 = 0;
  uVar4 = 0;
  local_20 = param_4;
  while( true ) {
    iVar2 = pb_readbyte(param_1,&local_20);
    uVar1 = local_20;
    if (iVar2 == 0) {
      return 0;
    }
    uVar6 = armcc_runtime_lsl64(local_20 & 0x7f,0,uVar5);
    uVar4 = (uint)((ulonglong)uVar6 >> 0x20) | uVar4;
    uVar3 = uVar3 | (uint)uVar6;
    uVar5 = uVar5 + 7;
    if (-1 < (int)(uVar1 << 0x18)) break;
    if (0x3f < uVar5) {
      return 0;
    }
  }
  *param_2 = uVar3;
  param_2[1] = uVar4;
  return 1;
}



/* ============================================================
 * entry: 000fcbe0
 * name: pb_decode_varint32
 * body: 000fcbe0-000fcc2b
 * ============================================================ */

undefined4 pb_decode_varint32(undefined4 param_1,uint *param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint local_18;

  local_18 = param_4;
  iVar1 = pb_readbyte(param_1,&local_18);
  if (iVar1 != 0) {
    uVar2 = local_18 & 0xff;
    if (-1 < (int)(local_18 << 0x18)) {
LAB_000fcc26:
      *param_2 = uVar2;
      return 1;
    }
    uVar3 = 7;
    uVar2 = local_18 & 0x7f;
    do {
      iVar1 = pb_readbyte(param_1,&local_18);
      if (iVar1 == 0) {
        return 0;
      }
      uVar2 = uVar2 | (local_18 & 0x7f) << (uVar3 & 0xff);
      uVar3 = uVar3 + 7;
      if (-1 < (int)(local_18 << 0x18)) goto LAB_000fcc26;
    } while (uVar3 < 0x20);
  }
  return 0;
}



/* ============================================================
 * entry: 000fcc2c
 * name: nrf_dfu_init_command_decode_callback
 * body: 000fcc2c-000fcc5f
 * ============================================================ */

void nrf_dfu_init_command_decode_callback
               (int param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  byte bVar1;
  int iVar2;
  undefined1 uVar3;
  int iVar4;
  byte *pbVar5;
  byte *pbVar6;

  iVar2 = DAT_000fcc64;
  if (*(int *)(*(int *)(param_4 + 4) + 0xc) == DAT_000fcc60) {
    iVar4 = *(int *)(param_1 + 8);
    pbVar6 = *(byte **)(param_1 + 4);
    if (*(int *)(DAT_000fcc64 + 4) == 0 && *(int *)(DAT_000fcc64 + 8) == 0) {
      do {
        pbVar5 = pbVar6 + 1;
        bVar1 = *pbVar6;
        iVar4 = iVar4 + -1;
        pbVar6 = pbVar5;
      } while ((int)((uint)bVar1 << 0x18) < 0);
      *(byte **)(DAT_000fcc64 + 4) = pbVar5;
      *(int *)(iVar2 + 8) = iVar4;
      uVar3 = 1;
    }
    else {
      uVar3 = 0;
    }
    *(undefined1 *)(iVar2 + 2) = uVar3;
  }
  return;
}



/* ============================================================
 * entry: 000fcc68
 * name: pb_field_iter_begin
 * body: 000fcc68-000fcc89
 * ============================================================ */

bool pb_field_iter_begin(undefined4 *param_1,short *param_2,int param_3)

{
  ushort uVar1;

  param_1[3] = param_3;
  *param_1 = param_2;
  param_1[1] = param_2;
  param_1[2] = 0;
  uVar1 = param_2[2];
  param_1[4] = param_3 + (uint)uVar1;
  param_1[5] = param_3 + (uint)uVar1 + (int)param_2[3];
  return *param_2 != 0;
}



/* ============================================================
 * entry: 000fcc8a
 * name: pb_field_iter_find
 * body: 000fcc8a-000fccb7
 * ============================================================ */

undefined4 pb_field_iter_find(int param_1,uint param_2)

{
  int iVar1;

  iVar1 = *(int *)(param_1 + 4);
  while( true ) {
    if ((**(ushort **)(param_1 + 4) == param_2) && (((*(ushort **)(param_1 + 4))[1] & 0xf) != 8))
    break;
    pb_field_iter_next(param_1);
    if (*(int *)(param_1 + 4) == iVar1) {
      return 0;
    }
  }
  return 1;
}



/* ============================================================
 * entry: 000fccb8
 * name: pb_field_iter_next
 * body: 000fccb8-000fcd35
 * ============================================================ */

undefined4 pb_field_iter_next(undefined4 *param_1)

{
  byte bVar1;
  short *psVar2;
  int iVar3;
  uint uVar4;

  psVar2 = (short *)param_1[1];
  if (*psVar2 != 0) {
    param_1[1] = psVar2 + 8;
    if (psVar2[8] != 0) {
      bVar1 = *(byte *)(psVar2 + 1);
      uVar4 = (uint)(ushort)psVar2[4];
      if (((bVar1 & 0x3f) >> 4 == 3) && ((*(byte *)(psVar2 + 9) & 0x3f) >> 4 == 3)) {
        uVar4 = 0;
        param_1[4] = param_1[4] - (uint)(ushort)psVar2[2];
      }
      else if (bVar1 >> 4 == 2) {
        uVar4 = (ushort)psVar2[5] * uVar4;
      }
      else if (bVar1 >> 6 == 2) {
        uVar4 = 4;
      }
      if ((*(byte *)(psVar2 + 1) & 0x30) == 0) {
        param_1[2] = param_1[2] + 1;
      }
      iVar3 = param_1[4] + (uint)(ushort)psVar2[10] + uVar4;
      param_1[4] = iVar3;
      param_1[5] = iVar3 + psVar2[0xb];
      return 1;
    }
    pb_field_iter_begin(param_1,*param_1,param_1[3]);
  }
  return 0;
}



/* ============================================================
 * entry: 000fcd36
 * name: pb_field_set_to_default
 * body: 000fcd36-000fcdd9
 * ============================================================ */

void pb_field_set_to_default(int param_1)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  undefined1 auStack_28 [28];

  bVar1 = *(byte *)(*(int *)(param_1 + 4) + 2);
  uVar2 = (uint)bVar1;
  if ((uVar2 & 0xf) == 8) {
    for (iVar3 = **(int **)(param_1 + 0x10); iVar3 != 0; iVar3 = *(int *)(iVar3 + 8)) {
      *(undefined1 *)(iVar3 + 0xc) = 0;
      iter_from_extension(auStack_28,iVar3);
      pb_field_set_to_default(auStack_28);
    }
    return;
  }
  if (bVar1 >> 6 != 0) {
    if (bVar1 >> 6 != 2) {
      return;
    }
    uVar2 = (uVar2 & 0x3f) >> 4;
    **(undefined4 **)(param_1 + 0x10) = 0;
    if ((uVar2 != 2) && (uVar2 != 3)) {
      return;
    }
LAB_000fcd64:
    **(undefined2 **)(param_1 + 0x14) = 0;
    return;
  }
  uVar2 = (uVar2 & 0x3f) >> 4;
  if (uVar2 == 1) {
    **(undefined1 **)(param_1 + 0x14) = 0;
  }
  else if ((uVar2 == 2) || (uVar2 == 3)) goto LAB_000fcd64;
  iVar3 = *(int *)(param_1 + 4);
  if ((*(byte *)(iVar3 + 2) & 0xf) == 7) {
    pb_message_set_to_defaults(*(undefined4 *)(iVar3 + 0xc),*(undefined4 *)(param_1 + 0x10));
    return;
  }
  if (*(int *)(iVar3 + 0xc) != 0) {
    memmove(*(undefined4 *)(param_1 + 0x10),*(int *)(iVar3 + 0xc),*(undefined2 *)(iVar3 + 8));
    return;
  }
  armcc_memclr(*(undefined4 *)(param_1 + 0x10),*(undefined2 *)(iVar3 + 8));
  return;
}



/* ============================================================
 * entry: 000fcddc
 * name: pb_istream_from_buffer
 * body: 000fcddc-000fcde9
 * ============================================================ */

void pb_istream_from_buffer(undefined4 *param_1,undefined4 param_2,undefined4 param_3)

{
  *param_1 = DAT_000fcdec;
  param_1[1] = param_2;
  param_1[2] = param_3;
  param_1[3] = 0;
  return;
}



/* ============================================================
 * entry: 000fcdf0
 * name: pb_make_string_substream
 * body: 000fcdf0-000fce25
 * ============================================================ */

undefined4
pb_make_string_substream(undefined4 *param_1,undefined4 *param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  uint local_10;

  local_10 = param_4;
  iVar1 = pb_decode_varint32(param_1,&local_10);
  if (iVar1 != 0) {
    uVar3 = param_1[1];
    uVar2 = param_1[2];
    uVar4 = param_1[3];
    *param_2 = *param_1;
    param_2[1] = uVar3;
    param_2[2] = uVar2;
    param_2[3] = uVar4;
    if (local_10 <= uVar2) {
      param_2[2] = local_10;
      param_1[2] = param_1[2] - local_10;
      return 1;
    }
  }
  return 0;
}



/* ============================================================
 * entry: 000fce26
 * name: pb_message_set_to_defaults
 * body: 000fce26-000fce4b
 * ============================================================ */

void pb_message_set_to_defaults(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined1 auStack_20 [28];

  iVar1 = pb_field_iter_begin(auStack_20,param_1,param_2);
  while (iVar1 != 0) {
    pb_field_set_to_default(auStack_20);
    iVar1 = pb_field_iter_next(auStack_20);
  }
  return;
}



/* ============================================================
 * entry: 000fce4c
 * name: pb_read
 * body: 000fce4c-000fce9f
 * ============================================================ */

undefined4 pb_read(int *param_1,int param_2,uint param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int *piStack_20;
  int iStack_1c;
  uint uStack_18;
  undefined4 uStack_14;

  piStack_20 = param_1;
  uStack_18 = param_3;
  uStack_14 = param_4;
  if ((param_2 == 0) && (iStack_1c = 0, *param_1 != DAT_000fcea0)) {
    for (; 0x10 < param_3; param_3 = param_3 - 0x10) {
      iVar2 = pb_read(param_1,&piStack_20,0x10);
      if (iVar2 == 0) {
        return 0;
      }
    }
    uVar1 = pb_read(param_1,&piStack_20,param_3);
  }
  else if ((uint)param_1[2] < param_3) {
    uVar1 = 0;
  }
  else {
    iStack_1c = param_2;
    iVar2 = (*(code *)*param_1)(param_1,param_2,param_3);
    uVar1 = 0;
    if (iVar2 != 0) {
      param_1[2] = param_1[2] - param_3;
      uVar1 = 1;
    }
  }
  return uVar1;
}



/* ============================================================
 * entry: 000fcea4
 * name: pb_readbyte
 * body: 000fcea4-000fcec3
 * ============================================================ */

undefined4 pb_readbyte(undefined4 *param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;

  uVar2 = 0;
  if ((param_1[2] != 0) && (iVar1 = (*(code *)*param_1)(param_1,param_2,1), uVar2 = 0, iVar1 != 0))
  {
    param_1[2] = param_1[2] + -1;
    uVar2 = 1;
  }
  return uVar2;
}



/* ============================================================
 * entry: 000fcec4
 * name: pb_skip_field
 * body: 000fcec4-000fcf1d
 * ============================================================ */

undefined4 pb_skip_field(undefined4 param_1,int param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  undefined4 uVar2;
  int local_10;

  local_10 = param_4;
  if (param_2 == 0) {
    do {
      iVar1 = pb_read(param_1,&local_10,1);
      if (iVar1 == 0) {
        return 0;
      }
    } while (local_10 << 0x18 < 0);
    return 1;
  }
  if (param_2 == 1) {
    uVar2 = 8;
  }
  else {
    if (param_2 == 2) {
      iVar1 = pb_decode_varint32(param_1,&local_10);
      if (iVar1 == 0) {
        return 0;
      }
      uVar2 = pb_read(param_1,0,local_10);
      return uVar2;
    }
    if (param_2 != 5) {
      return 0;
    }
    uVar2 = 4;
  }
  uVar2 = pb_read(param_1,0,uVar2,param_4);
  return uVar2;
}



/* ============================================================
 * entry: 000fcf20
 * name: nrf_dfu_validation_postvalidate_impl
 * body: 000fcf20-000fcfe3
 * ============================================================ */

int nrf_dfu_validation_postvalidate_impl(undefined4 param_1,undefined4 param_2,int param_3)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  undefined1 auStack_68 [68];

  iVar5 = *(int *)(DAT_000fcfe4 + 0xc);
  iVar6 = 1;
  iVar2 = fw_hash_ok(iVar5,param_1,param_2);
  iVar1 = DAT_000fcfe8;
  if (iVar2 == 0) {
    iVar6 = 0x17;
LAB_000fcfa6:
    if (param_3 == 0) {
      if (iVar6 != 1) {
        nrf_dfu_settings_progress_reset();
        return iVar6;
      }
LAB_000fcfce:
      *(undefined4 *)(iVar1 + 0x14) = 1;
      return 1;
    }
    if (iVar6 != 1) {
      nrf_dfu_bank_invalidate(DAT_000fcfe8 + 0x24);
      goto LAB_000fcfb4;
    }
  }
  else {
    uVar3 = (uint)*(byte *)(iVar5 + 0x55);
    if (uVar3 != 0) {
      iVar2 = postvalidate(iVar5,uVar3 & 1,(uVar3 & 3) >> 1,param_1,param_2,param_3);
      if (iVar2 == 0) goto LAB_000fcfa4;
      goto LAB_000fcfa6;
    }
    iVar2 = boot_validation_extract(auStack_68,iVar5,0,param_1,param_2,1);
    if (iVar2 == 0) {
LAB_000fcfa4:
      iVar6 = 5;
      goto LAB_000fcfa6;
    }
    if (param_3 == 0) goto LAB_000fcfce;
    memmove(DAT_000fcfec,auStack_68,0x41);
    *(undefined4 *)(iVar1 + 0x20) = 0;
    *(undefined4 *)(iVar1 + 0x2c) = 1;
    if ((*(char *)(iVar5 + 0x92) == '\0') || (*(char *)(iVar5 + 0x93) == '\0')) {
      *(undefined4 *)(iVar1 + 8) = *(undefined4 *)(iVar5 + 4);
    }
  }
  uVar4 = crc32_compute(param_1,param_2,0);
  *(undefined4 *)(iVar1 + 0x24) = param_2;
  *(undefined4 *)(iVar1 + 0x28) = uVar4;
LAB_000fcfb4:
  nrf_dfu_settings_progress_reset();
  *(undefined4 *)(iVar1 + 0x48) = param_1;
  return iVar6;
}



/* ============================================================
 * entry: 000fcff0
 * name: postvalidate
 * body: 000fcff0-000fd0e3
 * ============================================================ */

undefined4 postvalidate(int param_1,int param_2,int param_3,int param_4,int param_5,int param_6)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_a8 [68];
  undefined1 auStack_64 [68];

  armcc_memclr(auStack_a8,0x44);
  armcc_memclr(auStack_64,0x44);
  iVar1 = param_4;
  if (param_2 != 0) {
    if (((*(int *)(param_4 + 0x2004) != DAT_000fd0e4) ||
        (*(uint *)(param_4 + 0x2008) <
         (*(int *)(param_1 + 0x58) - (*(int *)(param_1 + 0x58) - 1U & 0xfff)) + 0x1fff)) ||
       ((iVar1 = is_major_softdevice_update(param_4), iVar1 != 0 && (param_3 == 0)))) {
      return 0;
    }
    iVar1 = boot_validation_extract(auStack_a8,param_1,0,param_4,*(undefined4 *)(param_1 + 0x58),1);
    if (iVar1 == 0) {
      return 0;
    }
    iVar1 = param_4 + *(int *)(param_1 + 0x58);
    param_5 = param_5 - *(int *)(param_1 + 0x58);
  }
  if ((param_3 != 0) &&
     (iVar1 = boot_validation_extract(auStack_64,param_1,param_2,iVar1,param_5,0), iVar1 == 0)) {
    return 0;
  }
  iVar1 = DAT_000fd0e8;
  if (param_6 != 0) {
    if (param_2 == 0) {
      *(undefined4 *)(DAT_000fd0e8 + 0x2c) = 0xaa;
    }
    else {
      iVar2 = is_major_softdevice_update(param_4);
      if (iVar2 != 0) {
        nrf_dfu_bank_invalidate(iVar1 + 0x18);
      }
      memmove(DAT_000fd0ec,auStack_a8,0x41);
      if (param_3 == 0) {
        uVar3 = 0xa5;
      }
      else {
        uVar3 = 0xac;
      }
      *(undefined4 *)(iVar1 + 0x2c) = uVar3;
      *(undefined4 *)(iVar1 + 0x34) = *(undefined4 *)(param_1 + 0x58);
    }
    if ((param_3 != 0) &&
       ((memmove(DAT_000fd0ec + 0x82,auStack_64,0x41), *(char *)(param_1 + 0x92) == '\0' ||
        (*(char *)(param_1 + 0x93) == '\0')))) {
      *(undefined4 *)(iVar1 + 0xc) = *(undefined4 *)(param_1 + 4);
    }
  }
  return 1;
}



/* ============================================================
 * entry: 000fd0f0
 * name: queue_free
 * body: 000fd0f0-000fd0f9
 * ============================================================ */

void queue_free(void)

{
  nrf_atfifo_item_free(*DAT_000fd100,DAT_000fd0fc);
  return;
}



/* ============================================================
 * entry: 000fd104
 * name: queue_process
 * body: 000fd104-000fd193
 * ============================================================ */

void queue_process(void)

{
  int iVar1;
  int *piVar2;
  int iVar3;

  piVar2 = DAT_000fd198;
  iVar1 = DAT_000fd194;
  if (*(char *)(DAT_000fd194 + 8) == '\0') {
    iVar3 = nrf_atfifo_item_get(*DAT_000fd19c,DAT_000fd198 + 1);
    *piVar2 = iVar3;
    if (iVar3 == 0) {
      *(undefined4 *)(iVar1 + 4) = 0;
      return;
    }
  }
  *(undefined1 *)(iVar1 + 8) = 2;
  iVar3 = *piVar2;
  if (*(char *)(iVar3 + 4) == '\0') {
    iVar3 = *(int *)(iVar3 + 0x10) + *(int *)(iVar3 + 0x18);
    software_interrupt(0x29);
  }
  else {
    if (*(char *)(iVar3 + 4) != '\x01') goto LAB_000fd16a;
    iVar3 = *(int *)(iVar3 + 0xc) + *(int *)(iVar3 + 0x10);
    software_interrupt(0x28);
  }
  if (iVar3 == 0) {
    if (*(char *)(iVar1 + 0x10) == '\0') {
      nrf_fstorage_sys_evt_handler(2,0);
      return;
    }
  }
  else {
    if (iVar3 != 0x11) {
LAB_000fd16a:
      event_send(*piVar2,3);
      *(undefined1 *)(iVar1 + 8) = 0;
      *(undefined4 *)(iVar1 + 4) = 0;
      queue_free();
      return;
    }
    *(undefined1 *)(iVar1 + 8) = 1;
  }
  return;
}



/* ============================================================
 * entry: 000fd1a0
 * name: queue_start
 * body: 000fd1a0-000fd1bd
 * ============================================================ */

void queue_start(void)

{
  int iVar1;
  int iVar2;

  iVar1 = DAT_000fd1c0;
  iVar2 = nrf_atomic_u32_fetch_or(DAT_000fd1c0 + 4);
  if ((iVar2 == 0) && (*(char *)(iVar1 + 0x11) == '\0')) {
    queue_process();
    return;
  }
  return;
}



/* ============================================================
 * entry: 000fd1c4
 * name: nrf_fstorage_nvmc_read
 * body: 000fd1c4-000fd1d1
 * ============================================================ */

undefined4
nrf_fstorage_nvmc_read(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  memmove(param_3,param_2,param_4);
  return 0;
}



/* ============================================================
 * entry: 000fd1d2
 * name: nrf_fstorage_sd_read
 * body: 000fd1d2-000fd1df
 * ============================================================ */

undefined4
nrf_fstorage_sd_read(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  memmove(param_3,param_2,param_4);
  return 0;
}



/* ============================================================
 * entry: 000fd1e0
 * name: read_raw_value
 * body: 000fd1e0-000fd241
 * ============================================================ */

undefined4 read_raw_value(undefined4 param_1,int param_2,byte *param_3,uint *param_4)

{
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;

  uVar4 = *param_4;
  if (param_2 == 0) {
    uVar1 = 0;
    *param_4 = 0;
    while( true ) {
      *param_4 = uVar1 + 1;
      if (uVar4 < uVar1 + 1) {
        return 0;
      }
      iVar2 = pb_read(param_1,param_3,1);
      if (iVar2 == 0) break;
      if (-1 < (int)((uint)*param_3 << 0x18)) {
        return 1;
      }
      uVar1 = *param_4;
      param_3 = param_3 + 1;
    }
    return 0;
  }
  if (param_2 == 1) {
    uVar3 = 8;
    *param_4 = 8;
  }
  else {
    if (param_2 != 5) {
      return 0;
    }
    uVar3 = 4;
    *param_4 = 4;
  }
  uVar3 = pb_read(param_1,param_3,uVar3);
  return uVar3;
}



/* ============================================================
 * entry: 000fd242
 * name: response_crc_add
 * body: 000fd242-000fd261
 * ============================================================ */

int response_crc_add(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;

  iVar1 = uint32_encode(param_2,param_1 + 3);
  iVar2 = uint32_encode(param_3,param_1 + iVar1 + 3);
  return iVar2 + iVar1;
}



/* ============================================================
 * entry: 000fd264
 * name: response_send
 * body: 000fd264-000fd28b
 * ============================================================ */

undefined8 response_send(void)

{
  undefined1 local_20 [28];

  software_interrupt(0xae);
  return CONCAT44(local_20,(uint)*(ushort *)(DAT_000fd294 + 2));
}



/* ============================================================
 * entry: 000fd298
 * name: nrf_fstorage_nvmc_rmap
 * body: 000fd298-000fd29b
 * ============================================================ */

undefined4 nrf_fstorage_nvmc_rmap(undefined4 param_1,undefined4 param_2)

{
  return param_2;
}



/* ============================================================
 * entry: 000fd29c
 * name: nrf_fstorage_sd_rmap
 * body: 000fd29c-000fd29f
 * ============================================================ */

undefined4 nrf_fstorage_sd_rmap(undefined4 param_1,undefined4 param_2)

{
  return param_2;
}



/* ============================================================
 * entry: 000fd2a0
 * name: nrf_bootloader_sd_activate
 * body: 000fd2a0-000fd2e9
 * ============================================================ */

int nrf_bootloader_sd_activate(void)

{
  int iVar1;
  int iVar2;
  int iVar3;

  iVar1 = nrf_dfu_softdevice_start_address();
  iVar3 = *(int *)(DAT_000fd2ec + 0x30);
  iVar2 = *(int *)(DAT_000fd2ec + 0x34) - iVar3;
  if (*(int *)(*(int *)(DAT_000fd2ec + 0x48) + 0x2004) != DAT_000fd2f0) {
    return 3;
  }
  if (iVar3 == *(int *)(DAT_000fd2ec + 0x34)) {
    iVar1 = 0;
  }
  else {
    iVar1 = image_copy(iVar1 + iVar3,*(int *)(DAT_000fd2ec + 0x48) + iVar3,
                       (iVar2 - (iVar2 - 1U & 0xfff)) + 0xfff,8);
    if (iVar1 == 0) {
      iVar1 = nrf_dfu_settings_write_and_backup();
      return iVar1;
    }
  }
  return iVar1;
}



/* ============================================================
 * entry: 000fd2f4
 * name: sd_req_check
 * body: 000fd2f4-000fd333
 * ============================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 sd_req_check(int param_1,uint param_2,int param_3)

{
  uint uVar1;

  uVar1 = 0;
  while( true ) {
    if (param_2 <= uVar1) {
      return 0;
    }
    if (((_DAT_00003004 == DAT_000fd334) && (*(uint *)(param_1 + uVar1 * 4) == (uint)_DAT_0000300c))
       || ((param_3 != 0 && (*(int *)(param_1 + uVar1 * 4) == 0xfffe)))) break;
    uVar1 = uVar1 + 1 & 0xff;
  }
  return 1;
}



/* ============================================================
 * entry: 000fd338
 * name: sd_req_ok
 * body: 000fd338-000fd39b
 * ============================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 sd_req_ok(char *param_1)

{
  ushort uVar1;
  char cVar2;
  undefined4 uVar3;

  uVar1 = *(ushort *)(param_1 + 0x10);
  if (_DAT_00003004 == DAT_000fd39c) {
    if (uVar1 != 0) {
      cVar2 = param_1[0x55];
      if (*(int *)(param_1 + 0x14) != 0) {
        uVar3 = sd_req_check(param_1 + 0x14,uVar1 & 0xff,cVar2 == '\x04');
        return uVar3;
      }
      if (cVar2 == '\0') {
        if (uVar1 < 2) {
          return 1;
        }
        sd_req_check(param_1 + 0x14,uVar1 & 0xff,0);
      }
      else if (cVar2 != '\x01') {
        return 1;
      }
    }
  }
  else if ((uVar1 == 0) || (*(int *)(param_1 + 0x14) == 0)) {
    if (*param_1 != '\0') {
      return 1;
    }
    return 0;
  }
  return 0;
}



/* ============================================================
 * entry: 000fd3a0
 * name: sdh_request_observer_notify
 * body: 000fd3a0-000fd3ad;000fd3b0-000fd3cb
 * ============================================================ */

longlong sdh_request_observer_notify
                   (undefined4 param_1,uint param_2,undefined4 param_3,undefined4 *param_4)

{
  int iVar1;
  uint uStack_18;
  undefined4 uStack_14;
  undefined4 *local_10;

  uStack_18 = param_2;
  uStack_14 = param_3;
  local_10 = param_4;
  nrf_section_iter_init(&uStack_18,DAT_000fd3cc);
  while( true ) {
    if (local_10 == (undefined4 *)0x0) {
      return (ulonglong)uStack_18 << 0x20;
    }
    iVar1 = (*(code *)*local_10)(param_1,local_10[1]);
    if (iVar1 == 0) break;
    nrf_section_iter_next(&uStack_18);
  }
  return CONCAT44(uStack_18,0x11);
}



/* ============================================================
 * entry: 000fd3d0
 * name: sdh_state_observer_notify
 * body: 000fd3d0-000fd3dd;000fd3e0-000fd3f5
 * ============================================================ */

void sdh_state_observer_notify
               (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 *param_4)

{
  undefined4 uStack_18;
  undefined4 uStack_14;
  undefined4 *local_10;

  uStack_18 = param_2;
  uStack_14 = param_3;
  local_10 = param_4;
  nrf_section_iter_init(&uStack_18,DAT_000fd3f8);
  while (local_10 != (undefined4 *)0x0) {
    (*(code *)*local_10)(param_1,local_10[1]);
    nrf_section_iter_next(&uStack_18);
  }
  return;
}



/* ============================================================
 * entry: 000fd3fc
 * name: settings_backup
 * body: 000fd3fc-000fd407
 * ============================================================ */

void settings_backup(undefined4 param_1,undefined4 param_2)

{
  settings_write(*DAT_000fd40c,param_2,param_1,DAT_000fd408);
  return;
}



/* ============================================================
 * entry: 000fd410
 * name: settings_crc_get
 * body: 000fd410-000fd419
 * ============================================================ */

void settings_crc_get(int param_1)

{
  crc32_compute(param_1 + 4,0x58,0);
  return;
}



/* ============================================================
 * entry: 000fd41a
 * name: settings_write
 * body: 000fd41a-000fd469
 * ============================================================ */

undefined4 settings_write(undefined4 param_1,undefined4 param_2,code *param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;

  iVar1 = memcmp(param_1,param_2,0x380);
  if (iVar1 == 0) {
    if (param_3 != (code *)0x0) {
      (*param_3)(0);
    }
    uVar2 = 0;
  }
  else {
    iVar1 = nrf_dfu_flash_erase(param_1,1,0);
    if (iVar1 == 0) {
      memmove(param_4,param_2,0x380);
      iVar1 = nrf_dfu_flash_store(param_1,param_4,0x380,param_3);
      if (iVar1 == 0) {
        return 0;
      }
    }
    uVar2 = 3;
  }
  return uVar2;
}



/* ============================================================
 * entry: 000fd46c
 * name: softdevice_evt_irq_disable
 * body: 000fd46c-000fd4a7
 * ============================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void softdevice_evt_irq_disable(void)

{
  int iVar1;

  iVar1 = __sd_nvic_app_accessible_irq(0x16);
  if (iVar1 == 0) {
    app_error_handler_bare(0x2001);
    return;
  }
  if (DAT_000fd4a8[2] != 0) {
    *DAT_000fd4a8 = *DAT_000fd4a8 & 0xffbfffff;
    return;
  }
  _DAT_e000e180 = 0x400000;
  DataSynchronizationBarrier(0xf);
  InstructionSynchronizationBarrier(0xf);
  return;
}



/* ============================================================
 * entry: 000fd4ac
 * name: softdevices_evt_irq_enable
 * body: 000fd4ac-000fd4fb
 * ============================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void softdevices_evt_irq_enable(void)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;

  iVar1 = __sd_nvic_app_accessible_irq(0x16);
  if (iVar1 == 0) {
    uVar3 = 0x2001;
  }
  else {
    uVar2 = (uint)(*(byte *)(DAT_000fd4fc + 0x400) >> 5);
    if ((uVar2 < 8) && ((1 << uVar2 & 0xecU) != 0)) {
      if (DAT_000fd500[2] != 0) {
        *DAT_000fd500 = *DAT_000fd500 | 0x400000;
        return;
      }
      _DAT_e000e100 = 0x400000;
      return;
    }
    uVar3 = 0x2002;
  }
  app_error_handler_bare(uVar3);
  return;
}



/* ============================================================
 * entry: 000fd504
 * name: stored_init_cmd_decode
 * body: 000fd504-000fd5af
 * ============================================================ */

undefined4
stored_init_cmd_decode(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 local_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;

  local_20 = param_1;
  uStack_1c = param_2;
  uStack_18 = param_3;
  uStack_14 = param_4;
  pb_istream_from_buffer(&local_20,DAT_000fd5b0 + 0x5c,*(undefined4 *)(DAT_000fd5b0 + 0x38));
  iVar1 = DAT_000fd5bc;
  iVar3 = DAT_000fd5b4;
  *(undefined4 *)(DAT_000fd5b4 + 0x1c) = local_20;
  *(undefined4 *)(iVar3 + 0x20) = uStack_1c;
  *(undefined4 *)(iVar3 + 0x24) = uStack_18;
  *(undefined4 *)(iVar3 + 0x28) = DAT_000fd5b8;
  *(undefined1 *)(iVar1 + 2) = 0;
  *(undefined4 *)(iVar1 + 4) = 0;
  *(undefined4 *)(iVar1 + 8) = 0;
  armcc_memclr(iVar3 + -0x300,0x31c);
  iVar2 = pb_decode(iVar3 + 0x1c,DAT_000fd5c0);
  if (iVar2 == 0) {
    return 0;
  }
  if (*(char *)(iVar1 + 2) == '\0') {
LAB_000fd5ac:
    uVar4 = 0;
  }
  else {
    if (*(char *)(iVar3 + -0x194) == '\0') {
      if ((*(char *)(iVar3 + -0x300) == '\0') ||
         (iVar2 = DAT_000fd5c8, *(char *)(iVar3 + -0x2fa) == '\0')) goto LAB_000fd5ac;
    }
    else {
      if ((*(char *)(iVar3 + -0x300) != '\0') || (*(char *)(iVar3 + -0x18e) == '\0'))
      goto LAB_000fd5ac;
      iVar2 = iVar3 + -0x18c;
      pb_istream_from_buffer(&local_20,*(undefined4 *)(iVar1 + 4),*(undefined4 *)(iVar1 + 8));
      *(undefined4 *)(iVar3 + 0x1c) = local_20;
      *(undefined4 *)(iVar3 + 0x20) = uStack_1c;
      *(undefined4 *)(iVar3 + 0x24) = uStack_18;
      *(undefined4 *)(iVar3 + 0x28) = uStack_14;
      armcc_memclr(iVar2,0x164);
      iVar3 = pb_decode((undefined4 *)(iVar3 + 0x1c),DAT_000fd5c4,iVar2);
      if (iVar3 == 0) {
        return 0;
      }
    }
    uVar4 = 1;
    *(int *)(iVar1 + 0xc) = iVar2;
  }
  return uVar4;
}



/* ============================================================
 * entry: 000fd5cc
 * name: timer_activate
 * body: 000fd5cc-000fd621
 * ============================================================ */

void timer_activate(int param_1,uint param_2)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;

  iVar1 = DAT_000fd624;
  uVar3 = 0xffffff;
  if (param_2 < 0xffffff) {
    uVar3 = param_2;
  }
  iVar2 = param_2 - uVar3;
  uVar3 = *(int *)(DAT_000fd624 + 0x504) + uVar3 & 0xffffff;
  *(int *)(param_1 + 4) = iVar2;
  if (iVar2 - 1U < 0x95) {
    uVar3 = uVar3 - 0x96;
    *(int *)(param_1 + 4) = iVar2 + 0x96;
  }
  uVar4 = (uint)*(byte *)(param_1 + 0xc);
  *(uint *)(iVar1 + uVar4 * 4 + 0x540) = uVar3;
  (*DAT_000fd628)(0x7c0);
  nrf_rtc_event_clear(iVar1,uVar4 * 4 + 0x140);
  *(int *)(iVar1 + 0x304) = 0x10000 << uVar4;
  return;
}



/* ============================================================
 * entry: 000fd62c
 * name: timer_init
 * body: 000fd62c-000fd68b
 * ============================================================ */

void timer_init(void)

{
  char *pcVar1;
  undefined4 *puVar2;

  pcVar1 = DAT_000fd68c;
  if (*DAT_000fd68c == '\0') {
    if (-1 < *DAT_000fd690 << 0xf) {
      *DAT_000fd694 = 1;
    }
    puVar2 = DAT_000fd698;
    nrf_rtc_event_clear(DAT_000fd698,0x100);
    nrf_rtc_event_clear(puVar2,0x140);
    nrf_rtc_event_clear(puVar2,0x144);
    *(undefined1 *)(DAT_000fd69c + 0x400) = 0xa0;
    *(undefined4 *)(DAT_000fd69c + 0xe0) = 0x10;
    puVar2[0x142] = 0;
    puVar2[2] = 1;
    *puVar2 = 1;
    puVar2[0xc1] = 2;
    *pcVar1 = '\x01';
  }
  return;
}



/* ============================================================
 * entry: 000fd6a0
 * name: timer_start
 * body: 000fd6a0-000fd6b9
 * ============================================================ */

void timer_start(undefined4 *param_1,undefined4 param_2,undefined4 param_3)

{
  timer_init();
  *param_1 = param_3;
  timer_activate(param_1,param_2);
  return;
}



/* ============================================================
 * entry: 000fd6bc
 * name: timer_stop
 * body: 000fd6bc-000fd6cb
 * ============================================================ */

void timer_stop(int param_1)

{
  *(int *)(DAT_000fd6cc + 0x308) = 0x10000 << *(sbyte *)(param_1 + 0xc);
  return;
}



/* ============================================================
 * entry: 000fd6d0
 * name: uint32_encode
 * body: 000fd6d0-000fd6e1
 * ============================================================ */

undefined4 uint32_encode(undefined4 param_1,undefined1 *param_2)

{
  *param_2 = (char)param_1;
  param_2[1] = (char)((uint)param_1 >> 8);
  param_2[2] = (char)((uint)param_1 >> 0x10);
  param_2[3] = (char)((uint)param_1 >> 0x18);
  return 4;
}



/* ============================================================
 * entry: 000fd6e4
 * name: nrf_fstorage_nvmc_uninit
 * body: 000fd6e4-000fd6ef
 * ============================================================ */

undefined4 nrf_fstorage_nvmc_uninit(void)

{
  nrf_atomic_flag_clear(DAT_000fd6f0);
  return 0;
}



/* ============================================================
 * entry: 000fd6f4
 * name: nrf_fstorage_sd_uninit
 * body: 000fd6f4-000fd709
 * ============================================================ */

undefined4 nrf_fstorage_sd_uninit(void)

{
  armcc_memclr(DAT_000fd70c,0x14);
  nrf_atfifo_clear(*DAT_000fd710);
  return 0;
}



/* ============================================================
 * entry: 000fd714
 * name: update_data_size_get
 * body: 000fd714-000fd767
 * ============================================================ */

undefined4 update_data_size_get(int param_1,int *param_2)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;

  uVar3 = 0xf;
  uVar2 = (uint)*(byte *)(param_1 + 0x55);
  iVar1 = 0;
  if (((uVar2 == 0) || (uVar2 == 4)) && (*(char *)(param_1 + 100) == '\x01')) {
    iVar1 = *(int *)(param_1 + 0x68);
  }
  else {
    if (((*(byte *)(param_1 + 0x55) & 1) != 0) && (*(char *)(param_1 + 0x56) == '\x01')) {
      iVar1 = *(int *)(param_1 + 0x58);
    }
    if (((int)(uVar2 << 0x1e) < 0) && (*(char *)(param_1 + 0x5c) == '\x01')) {
      if (0xfe000U - DAT_000fd768 < *(uint *)(param_1 + 0x60)) {
        return 4;
      }
      iVar1 = iVar1 + *(uint *)(param_1 + 0x60);
    }
  }
  if (iVar1 != 0) {
    uVar3 = 1;
    *param_2 = iVar1;
  }
  return uVar3;
}



/* ============================================================
 * entry: 000fd76c
 * name: verify_context
 * body: 000fd76c-000fd785
 * ============================================================ */

undefined4 verify_context(int *param_1)

{
  if (param_1 == (int *)0x0) {
    return 0x8501;
  }
  if (*param_1 != DAT_000fd788) {
    return 0x8502;
  }
  return 0;
}



/* ============================================================
 * entry: 000fd78c
 * name: wdt_feed
 * body: 000fd78c-000fd7bb
 * ============================================================ */

void wdt_feed(void)

{
  uint *puVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;

  iVar4 = nrf_wdt_started();
  iVar3 = DAT_000fd7c4;
  uVar2 = DAT_000fd7c0;
  puVar1 = DAT_000fd7bc;
  if (iVar4 != 0) {
    uVar5 = 0;
    do {
      if ((*puVar1 & 1 << uVar5) != 0) {
        *(undefined4 *)(iVar3 + uVar5 * 4 + 0x600) = uVar2;
      }
      uVar5 = uVar5 + 1 & 0xff;
    } while (uVar5 < 7);
  }
  return;
}



/* ============================================================
 * entry: 000fd7c8
 * name: wdt_feed_timer_handler
 * body: 000fd7c8-000fd7cb
 * ============================================================ */

void wdt_feed_timer_handler(void)

{
  uint *puVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;

  iVar4 = nrf_wdt_started();
  iVar3 = DAT_000fd7c4;
  uVar2 = DAT_000fd7c0;
  puVar1 = DAT_000fd7bc;
  if (iVar4 != 0) {
    uVar5 = 0;
    do {
      if ((*puVar1 & 1 << uVar5) != 0) {
        *(undefined4 *)(iVar3 + uVar5 * 4 + 0x600) = uVar2;
      }
      uVar5 = uVar5 + 1 & 0xff;
    } while (uVar5 < 7);
  }
  return;
}



/* ============================================================
 * entry: 000fd7cc
 * name: nrf_fstorage_nvmc_wmap
 * body: 000fd7cc-000fd7cf
 * ============================================================ */

undefined4 nrf_fstorage_nvmc_wmap(void)

{
  return 0;
}



/* ============================================================
 * entry: 000fd7d0
 * name: nrf_fstorage_sd_wmap
 * body: 000fd7d0-000fd7d3
 * ============================================================ */

undefined4 nrf_fstorage_sd_wmap(void)

{
  return 0;
}



/* ============================================================
 * entry: 000fd7d4
 * name: nrf_fstorage_nvmc_write
 * body: 000fd7d4-000fd813
 * ============================================================ */

undefined4
nrf_fstorage_nvmc_write
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,uint param_4,undefined4 param_5)

{
  int iVar1;
  undefined4 uVar2;

  iVar1 = nrf_atomic_u32_fetch_or(DAT_000fd814);
  if (iVar1 == 0) {
    nrf_nvmc_write_words(param_2,param_3,param_4 >> 2);
    nrf_atomic_flag_clear(DAT_000fd814);
    nrf_fstorage_nvmc_event_send(param_1,1,param_3,param_2,param_4,param_5);
    uVar2 = 0;
  }
  else {
    uVar2 = 0x11;
  }
  return uVar2;
}



/* ============================================================
 * entry: 000fd818
 * name: nrf_fstorage_sd_write
 * body: 000fd818-000fd861
 * ============================================================ */

undefined4
nrf_fstorage_sd_write
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
          undefined4 param_5)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  undefined4 uStack_28;

  puVar1 = DAT_000fd864;
  uStack_28 = param_4;
  puVar2 = (undefined4 *)nrf_atfifo_item_alloc(*DAT_000fd864,&uStack_28);
  if (puVar2 == (undefined4 *)0x0) {
    uVar3 = 4;
  }
  else {
    armcc_memclr(puVar2,0x1c);
    *(undefined1 *)(puVar2 + 1) = 0;
    *puVar2 = param_1;
    puVar2[4] = param_2;
    puVar2[5] = param_4;
    puVar2[2] = param_5;
    puVar2[3] = param_3;
    nrf_atfifo_item_put(*puVar1,&uStack_28);
    queue_start();
    uVar3 = 0;
  }
  return uVar3;
}



/* ============================================================
 * entry: 000fd8b0
 * name: nrfx_coredep_delay_machine_code_dfu_timers
 * body: 000fd8b0-000fd8b5
 * ============================================================ */

void nrfx_coredep_delay_machine_code_dfu_timers(uint param_1)

{
  bool bVar1;

  do {
    bVar1 = 2 < param_1;
    param_1 = param_1 - 3;
  } while (bVar1 && param_1 != 0);
  return;
}



/* ============================================================
 * entry: 000fdaa0
 * name: nrfx_coredep_delay_machine_code_ble_dfu
 * body: 000fdaa0-000fdaa5
 * ============================================================ */

void nrfx_coredep_delay_machine_code_ble_dfu(uint param_1)

{
  bool bVar1;

  do {
    bVar1 = 2 < param_1;
    param_1 = param_1 - 3;
  } while (bVar1 && param_1 != 0);
  return;
}


