/*
 * Machine-generated Ghidra C-like decompilation. This is analysis output, not
 * recovered original source. Types, names, volatile qualifiers, inline boundaries,
 * and undefined-behavior assumptions require manual validation before semantic use.
 */


/* ================================================================
 * entry: 0x000f8208
 * end:   0x000f820b
 * size:  4 bytes
 * name:  thunk_FUN_000fadc8
 * ================================================================ */

void thunk_FUN_000fadc8(void)

{
  (*DAT_000f820c)();
  return;
}



/* ================================================================
 * entry: 0x000f8218
 * end:   0x000f824f
 * size:  56 bytes
 * name:  FUN_000f8218
 * ================================================================ */

undefined4 FUN_000f8218(int param_1,uint *param_2)

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



/* ================================================================
 * entry: 0x000f8250
 * end:   0x000f8261
 * size:  18 bytes
 * name:  FUN_000f8250
 * ================================================================ */

void FUN_000f8250(int param_1)

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



/* ================================================================
 * entry: 0x000f8262
 * end:   0x000f829b
 * size:  58 bytes
 * name:  FUN_000f8262
 * ================================================================ */

undefined4 FUN_000f8262(int param_1,uint *param_2)

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



/* ================================================================
 * entry: 0x000f829c
 * end:   0x000f82ad
 * size:  18 bytes
 * name:  FUN_000f829c
 * ================================================================ */

void FUN_000f829c(int param_1)

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



/* ================================================================
 * entry: 0x000f82ae
 * end:   0x000f82df
 * size:  50 bytes
 * name:  FUN_000f82ae
 * ================================================================ */

undefined4 FUN_000f82ae(int param_1)

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



/* ================================================================
 * entry: 0x000f82e0
 * end:   0x000f82f7
 * size:  24 bytes
 * name:  FUN_000f82e0
 * ================================================================ */

undefined4 FUN_000f82e0(undefined4 *param_1,undefined4 param_2,undefined4 *param_3)

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



/* ================================================================
 * entry: 0x000f82f8
 * end:   0x000f8311
 * size:  26 bytes
 * name:  FUN_000f82f8
 * ================================================================ */

void FUN_000f82f8(uint *param_1,uint param_2,uint *param_3)

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



/* ================================================================
 * entry: 0x000f8312
 * end:   0x000f832b
 * size:  26 bytes
 * name:  FUN_000f8312
 * ================================================================ */

void FUN_000f8312(uint *param_1,uint param_2,uint *param_3)

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



/* ================================================================
 * entry: 0x000f832c
 * end:   0x000f8345
 * size:  26 bytes
 * name:  FUN_000f832c
 * ================================================================ */

void FUN_000f832c(uint *param_1,uint param_2,uint *param_3)

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



/* ================================================================
 * entry: 0x000f8346
 * end:   0x000f835f
 * size:  26 bytes
 * name:  FUN_000f8346
 * ================================================================ */

void FUN_000f8346(int *param_1,int param_2,int *param_3)

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



/* ================================================================
 * entry: 0x000f8360
 * end:   0x000f8379
 * size:  26 bytes
 * name:  FUN_000f8360
 * ================================================================ */

void FUN_000f8360(int *param_1,int param_2,int *param_3)

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



/* ================================================================
 * entry: 0x000f837a
 * end:   0x000f83a3
 * size:  42 bytes
 * name:  FUN_000f837a
 * ================================================================ */

undefined4 FUN_000f837a(int *param_1,int *param_2,int param_3,int param_4)

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



/* ================================================================
 * entry: 0x000f83a4
 * end:   0x000f83c1
 * size:  30 bytes
 * name:  FUN_000f83a4
 * ================================================================ */

void FUN_000f83a4(uint *param_1,uint param_2,uint *param_3)

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



/* ================================================================
 * entry: 0x000f83c4
 * end:   0x000f83d5
 * size:  18 bytes
 * name:  hardfault_exception_entry
 * ================================================================ */

void hardfault_exception_entry(void)

{
  undefined4 uVar1;
  uint unaff_lr;

  if ((unaff_lr & 4) == 0) {
    uVar1 = getMainStackPointer();
  }
  else {
    uVar1 = getProcessStackPointer();
  }
  hardfault_c_handler(uVar1);
  return;
}



/* ================================================================
 * entry: 0x000f83d8
 * end:   0x000f83df
 * size:  8 bytes
 * name:  reset_handler
 * ================================================================ */

void reset_handler(void)

{
  (*DAT_000f83f4)();
                    /* WARNING: Could not recover jumptable at 0x000f83de. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*DAT_000f83f8)();
  return;
}



/* ================================================================
 * entry: 0x000f83e0
 * end:   0x000f83e1
 * size:  2 bytes
 * name:  FUN_000f83e0
 * ================================================================ */

void FUN_000f83e0(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* ================================================================
 * entry: 0x000f83e2
 * end:   0x000f83e3
 * size:  2 bytes
 * name:  FUN_000f83e2
 * ================================================================ */

void FUN_000f83e2(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* ================================================================
 * entry: 0x000f83e4
 * end:   0x000f83e5
 * size:  2 bytes
 * name:  FUN_000f83e4
 * ================================================================ */

void FUN_000f83e4(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* ================================================================
 * entry: 0x000f83e6
 * end:   0x000f83e7
 * size:  2 bytes
 * name:  FUN_000f83e6
 * ================================================================ */

void FUN_000f83e6(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* ================================================================
 * entry: 0x000f83e8
 * end:   0x000f83e9
 * size:  2 bytes
 * name:  FUN_000f83e8
 * ================================================================ */

void FUN_000f83e8(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* ================================================================
 * entry: 0x000f83ec
 * end:   0x000f83ed
 * size:  2 bytes
 * name:  FUN_000f83ec
 * ================================================================ */

void FUN_000f83ec(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* ================================================================
 * entry: 0x000f83ee
 * end:   0x000f83ef
 * size:  2 bytes
 * name:  FUN_000f83ee
 * ================================================================ */

void FUN_000f83ee(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* ================================================================
 * entry: 0x000f83f0
 * end:   0x000f83f1
 * size:  2 bytes
 * name:  FUN_000f83f0
 * ================================================================ */

void FUN_000f83f0(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* ================================================================
 * entry: 0x000f83f2
 * end:   0x000f83f3
 * size:  2 bytes
 * name:  FUN_000f83f2
 * ================================================================ */

void FUN_000f83f2(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* ================================================================
 * entry: 0x000f83fc
 * end:   0x000f8419
 * size:  30 bytes
 * name:  FUN_000f83fc
 * ================================================================ */

longlong FUN_000f83fc(uint param_1,int param_2,uint param_3)

{
  if (0x1f < (int)param_3) {
    return (ulonglong)(param_1 << (param_3 - 0x20 & 0xff)) << 0x20;
  }
  return CONCAT44(param_2 << (param_3 & 0xff) | param_1 >> (0x20 - param_3 & 0xff),
                  param_1 << (param_3 & 0xff));
}



/* ================================================================
 * entry: 0x000f841a
 * end:   0x000f845b
 * size:  66 bytes
 * name:  FUN_000f841a
 * ================================================================ */

void FUN_000f841a(undefined4 *param_1,undefined4 *param_2,uint param_3)

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



/* ================================================================
 * entry: 0x000f845c
 * end:   0x000f8469
 * size:  14 bytes
 * name:  FUN_000f845c
 * ================================================================ */

void FUN_000f845c(undefined1 *param_1,int param_2,undefined1 param_3)

{
  bool bVar1;

  while (bVar1 = param_2 != 0, param_2 = param_2 + -1, bVar1) {
    *param_1 = param_3;
    param_1 = param_1 + 1;
  }
  return;
}



/* ================================================================
 * entry: 0x000f846a
 * end:   0x000f846d
 * size:  4 bytes
 * name:  FUN_000f846a
 * ================================================================ */

void FUN_000f846a(undefined4 param_1,undefined4 param_2)

{
  FUN_000f845c(param_1,param_2,0);
  return;
}



/* ================================================================
 * entry: 0x000f846e
 * end:   0x000f847f
 * size:  18 bytes
 * name:  FUN_000f846e
 * ================================================================ */

undefined4 FUN_000f846e(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  FUN_000f845c(param_1,param_3,param_2);
  return param_1;
}



/* ================================================================
 * entry: 0x000f8480
 * end:   0x000f848d
 * size:  14 bytes
 * name:  FUN_000f8480
 * ================================================================ */

int FUN_000f8480(char *param_1)

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



/* ================================================================
 * entry: 0x000f848e
 * end:   0x000f84a7
 * size:  26 bytes
 * name:  FUN_000f848e
 * ================================================================ */

void FUN_000f848e(int param_1,int param_2,uint param_3)

{
  uint uVar1;

  for (uVar1 = 0; (uVar1 < param_3 && (*(char *)(param_1 + uVar1) == *(char *)(param_2 + uVar1)));
      uVar1 = uVar1 + 1) {
  }
  return;
}



/* ================================================================
 * entry: 0x000f84a8
 * end:   0x000f84c5
 * size:  30 bytes
 * name:  FUN_000f84a8
 * ================================================================ */

void FUN_000f84a8(int param_1,int param_2,uint param_3)

{
  uint uVar1;

  for (uVar1 = 0;
      ((uVar1 < param_3 && (*(char *)(param_1 + uVar1) == *(char *)(param_2 + uVar1))) &&
      (*(char *)(param_1 + uVar1) != '\0')); uVar1 = uVar1 + 1) {
  }
  return;
}



/* ================================================================
 * entry: 0x000f84c8
 * end:   0x000f84e5
 * size:  30 bytes
 * name:  FUN_000f84c8
 * ================================================================ */

void FUN_000f84c8(void)

{
  code *pcVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;

  puVar2 = DAT_000f84e8;
  for (puVar3 = puRam000f84e4; puVar3 < puVar2; puVar3 = puVar3 + 4) {
    (*(code *)puVar3[3])(*puVar3,puVar3[1],puVar3[2]);
  }
  thunk_FUN_000fadc8();
                    /* WARNING: Does not return */
  pcVar1 = (code *)software_udf(0x1c,0xf84e4);
  (*pcVar1)();
}



/* ================================================================
 * entry: 0x000f84ec
 * end:   0x000f8503
 * size:  24 bytes
 * name:  FUN_000f84ec
 * ================================================================ */

void FUN_000f84ec(void)

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



/* ================================================================
 * entry: 0x000f8510
 * end:   0x000f8529
 * size:  26 bytes
 * name:  FUN_000f8510
 * ================================================================ */

undefined4 FUN_000f8510(int param_1,uint *param_2,int param_3)

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



/* ================================================================
 * entry: 0x000f852c
 * end:   0x000f8603
 * size:  216 bytes
 * name:  FUN_000f852c
 * ================================================================ */

void FUN_000f852c(void)

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
  FUN_000f9124(0,0xe,0xf,0xd);
  return;
}



/* ================================================================
 * entry: 0x000f8640
 * end:   0x000f8781
 * size:  322 bytes
 * name:  FUN_000f8640
 * ================================================================ */

void FUN_000f8640(int param_1,int param_2)

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



/* ================================================================
 * entry: 0x000f87d4
 * end:   0x000f88fb
 * size:  296 bytes
 * name:  FUN_000f87d4
 * ================================================================ */

void FUN_000f87d4(int param_1,uint param_2,int param_3)

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



/* ================================================================
 * entry: 0x000f8914
 * end:   0x000f89bd
 * size:  170 bytes
 * name:  FUN_000f8914
 * ================================================================ */

void FUN_000f8914(int param_1,int param_2,undefined4 *param_3,uint param_4)

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



/* ================================================================
 * entry: 0x000f89d0
 * end:   0x000f8af7
 * size:  296 bytes
 * name:  FUN_000f89d0
 * ================================================================ */

void FUN_000f89d0(void)

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



/* ================================================================
 * entry: 0x000f8b48
 * end:   0x000f8c99
 * size:  338 bytes
 * name:  FUN_000f8b48
 * ================================================================ */

void FUN_000f8b48(void)

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



/* ================================================================
 * entry: 0x000f8cf4
 * end:   0x000f8f05
 * size:  530 bytes
 * name:  FUN_000f8cf4
 * ================================================================ */

int FUN_000f8cf4(void)

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
      iVar7 = FUN_000f9258();
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



/* ================================================================
 * entry: 0x000f8f80
 * end:   0x000f8f9d
 * size:  30 bytes
 * name:  FUN_000f8f80
 * ================================================================ */

void FUN_000f8f80(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  if (param_1 != 0) {
    if (0x1f < param_1) {
      param_1 = 0x20;
    }
    FUN_000f87d4(0,param_1,7,param_4,param_4);
  }
  *DAT_000f8fa0 = 0;
  return;
}



/* ================================================================
 * entry: 0x000f8fa4
 * end:   0x000f900b
 * size:  104 bytes
 * name:  FUN_000f8fa4
 * ================================================================ */

uint FUN_000f8fa4(int param_1,uint param_2,uint *param_3,int *param_4)

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



/* ================================================================
 * entry: 0x000f9018
 * end:   0x000f9097
 * size:  128 bytes
 * name:  FUN_000f9018
 * ================================================================ */

void FUN_000f9018(int param_1)

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



/* ================================================================
 * entry: 0x000f90a8
 * end:   0x000f911b
 * size:  116 bytes
 * name:  FUN_000f90a8
 * ================================================================ */

/* WARNING: Removing unreachable block (ram,0x000f90de) */
/* WARNING: Removing unreachable block (ram,0x000f90e2) */

undefined4 FUN_000f90a8(uint param_1,uint *param_2,undefined4 param_3,undefined4 param_4)

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
    FUN_000f91d4(uVar3,iVar4,1,puVar1,param_4);
    FUN_000f921c(param_1,iVar4);
    uVar2 = 0;
  }
  return uVar2;
}



/* ================================================================
 * entry: 0x000f9124
 * end:   0x000f91bf
 * size:  156 bytes
 * name:  FUN_000f9124
 * ================================================================ */

void FUN_000f9124(undefined4 param_1,int param_2,int param_3,int param_4)

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



/* ================================================================
 * entry: 0x000f91d4
 * end:   0x000f920d
 * size:  58 bytes
 * name:  FUN_000f91d4
 * ================================================================ */

void FUN_000f91d4(int param_1,int param_2)

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



/* ================================================================
 * entry: 0x000f921c
 * end:   0x000f924d
 * size:  50 bytes
 * name:  FUN_000f921c
 * ================================================================ */

void FUN_000f921c(int param_1,int param_2)

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



/* ================================================================
 * entry: 0x000f9258
 * end:   0x000f93ef
 * size:  408 bytes
 * name:  FUN_000f9258
 * ================================================================ */

uint FUN_000f9258(void)

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
      uVar5 = FUN_000f9018(0x12);
      uVar6 = FUN_000f9018(0x13);
      if (uVar6 < uVar5) {
        uVar7 = 0x12;
      }
      else {
        uVar7 = 0x13;
      }
      iVar8 = FUN_000f9018(uVar7);
      iVar8 = iVar8 + -1;
      FUN_000f852c();
      iVar9 = FUN_000f8fa4(0x12,iVar8,auStack_5c,&local_54);
      iVar10 = FUN_000f8fa4(0x13,iVar8,auStack_58,&uStack_50);
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
        iVar9 = FUN_000f8fa4(0x12,iVar8,auStack_5c,&local_54);
        iVar10 = FUN_000f8fa4(0x13,iVar8,auStack_58,&uStack_50);
        iVar10 = iVar10 + iVar9 * 2;
        if (iVar10 == 0) {
          FUN_000f8b48();
        }
        else {
          FUN_000f89d0();
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
          FUN_000f8640(uVar7,uVar11);
        }
      }
      FUN_000f9124(0,0x18,0x19,0x10);
      uVar5 = (uVar12 & 0x1fff) >> 0xc;
    }
  }
  return uVar5;
}



/* ================================================================
 * entry: 0x000f943c
 * end:   0x000f9441
 * size:  6 bytes
 * name:  FUN_000f943c
 * ================================================================ */

void FUN_000f943c(undefined4 param_1)

{
  *DAT_000f9444 = param_1;
  return;
}



/* ================================================================
 * entry: 0x000f9448
 * end:   0x000f944d
 * size:  6 bytes
 * name:  FUN_000f9448
 * ================================================================ */

void FUN_000f9448(undefined4 param_1)

{
  *DAT_000f9450 = param_1;
  return;
}



/* ================================================================
 * entry: 0x000f9454
 * end:   0x000f947b
 * size:  40 bytes
 * name:  FUN_000f9454
 * ================================================================ */

uint FUN_000f9454(uint param_1)

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



/* ================================================================
 * entry: 0x000f9488
 * end:   0x000f948b
 * size:  4 bytes
 * name:  thunk_FUN_000f841a
 * ================================================================ */

void thunk_FUN_000f841a(undefined4 *param_1,undefined4 *param_2,uint param_3)

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



/* ================================================================
 * entry: 0x000f948c
 * end:   0x000f948f
 * size:  4 bytes
 * name:  thunk_FUN_000f846e
 * ================================================================ */

undefined4 thunk_FUN_000f846e(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  FUN_000f845c(param_1,param_3,param_2);
  return param_1;
}



/* ================================================================
 * entry: 0x000f9490
 * end:   0x000f9497
 * size:  8 bytes
 * name:  FUN_000f9490
 * ================================================================ */

void FUN_000f9490(undefined4 param_1,undefined4 param_2)

{
  FUN_000f846e(param_1,0,param_2);
  return;
}



/* ================================================================
 * entry: 0x000f95fc
 * end:   0x000f9639
 * size:  62 bytes
 * name:  FUN_000f95fc
 * ================================================================ */

undefined4 FUN_000f95fc(undefined4 *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;

  uVar1 = DAT_000f9640;
  if ((param_1 != (undefined4 *)0x0) &&
     (thunk_FUN_000f846e(param_1 + 1,0,0xa0,param_4,param_4), uVar1 = DAT_000f9644, param_2 != 0)) {
    FUN_000f8510(param_1 + 0x19,param_2,8);
    FUN_000f8510(param_1 + 0x21,param_2 + 0x20,8);
    *param_1 = DAT_000f963c;
    uVar1 = 0;
  }
  return uVar1;
}



/* ================================================================
 * entry: 0x000f9648
 * end:   0x000f966f
 * size:  348 bytes
 * name:  FUN_000f9648
 * ================================================================ */

int FUN_000f9648(int param_1,undefined4 param_2,int param_3,undefined4 param_4,int param_5)

{
  undefined4 *puVar1;
  int iVar2;
  int iVar3;
  undefined8 uVar4;
  int local_24;
  undefined4 uStack_20;
  int local_18;

  local_18 = param_5;
  iVar3 = FUN_000f95fc();
  if (iVar3 != 0) {
    return iVar3;
  }
  local_24 = param_3;
  uStack_20 = param_4;
  uVar4 = FUN_000f9958(param_1,param_4,param_4,local_18,param_1);
  iVar2 = (int)((ulonglong)uVar4 >> 0x20);
  iVar3 = (int)uVar4;
  if (((((int)uVar4 == 0) && (iVar3 = DAT_000f95f0, param_3 != 0)) &&
      (iVar3 = DAT_000f95f4, iVar2 != 0)) && (iVar3 = DAT_000f95f8, local_18 == 0x20)) {
    FUN_000f8510(param_1 + 0x44,iVar2,8);
    FUN_000f8510(param_1 + 4,param_3,8);
    FUN_000f8510(param_1 + 0x24,param_3 + 0x20,8);
    local_24 = local_18;
    iVar2 = FUN_000f90a8(0x100,&local_24);
    puVar1 = DAT_000f95cc;
    iVar3 = DAT_000f95ec;
    if (iVar2 == 0) {
      *DAT_000f95cc = 0x100;
      puVar1[2] = 0x100;
      FUN_000f8914(0,1,DAT_000f95d0,8);
      FUN_000f8914(1,1,DAT_000f95d4,5);
      FUN_000f8914(0x1c,1,param_1 + 4,8);
      FUN_000f8914(3,1,param_1 + 0x24,8);
      FUN_000f8914(2,1,param_1 + 0x44,8);
      FUN_000f8914(0x1a,1,DAT_000f95d8,8);
      FUN_000f8914(0x1b,1,DAT_000f95dc,5);
      FUN_000f8914(0x14,1,DAT_000f95e0,8);
      FUN_000f8914(0x15,1,DAT_000f95e4,8);
      FUN_000f8914(0x16,1,param_1 + 100,8);
      FUN_000f8914(0x17,1,param_1 + 0x84,8);
      FUN_000f8914(0xb,1,DAT_000f95e8,8);
      iVar2 = FUN_000f8cf4();
      FUN_000f8f80(local_24);
      iVar3 = 0;
      if (iVar2 != 0) {
        iVar3 = DAT_000f95ec;
      }
    }
    FUN_000f9490(param_1,0xa4);
  }
  return iVar3;
}



/* ================================================================
 * entry: 0x000f9670
 * end:   0x000f96c5
 * size:  86 bytes
 * name:  FUN_000f9670
 * ================================================================ */

int FUN_000f9670(int param_1,int param_2)

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
  iVar1 = FUN_000f9978(param_1);
  iVar6 = iVar1;
  if ((iVar1 == 0) && (iVar6 = DAT_000f96cc, param_2 != 0)) {
    if (*(int *)(param_1 + 0x24) == 0) {
      *(undefined4 *)(param_1 + 0x24) = 1;
      local_24 = (uint *)(param_1 + 4);
      FUN_000f97a8(&local_28,param_1 + 0x30,*(undefined4 *)(param_1 + 0x70));
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



/* ================================================================
 * entry: 0x000f96d0
 * end:   0x000f96f7
 * size:  40 bytes
 * name:  FUN_000f96d0
 * ================================================================ */

undefined4
FUN_000f96d0(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;

  uVar1 = DAT_000f9700;
  if (param_1 != (undefined4 *)0x0) {
    FUN_000f9490(param_1 + 1,0x70,param_3,param_4,param_1);
    thunk_FUN_000f841a(param_1 + 1,DAT_000f96f8,0x20);
    *param_1 = DAT_000f96fc;
    uVar1 = 0;
  }
  return uVar1;
}



/* ================================================================
 * entry: 0x000f9704
 * end:   0x000f979f
 * size:  156 bytes
 * name:  FUN_000f9704
 * ================================================================ */

int FUN_000f9704(int param_1,int param_2,uint param_3)

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
    iVar1 = FUN_000f9978(param_1);
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
      thunk_FUN_000f841a(iVar1 + param_1 + 0x30,param_2,uVar2);
      iVar1 = *(int *)(param_1 + 0x70) + uVar2;
      param_2 = param_2 + uVar2;
      *(int *)(param_1 + 0x70) = iVar1;
      param_3 = param_3 - uVar2;
      if (iVar1 == 0x40) {
        FUN_000f97a8(&local_30,param_1 + 0x30);
        *(undefined4 *)(param_1 + 0x70) = 0;
      }
    }
    uVar2 = param_3 & 0x3f;
    param_3 = param_3 & 0xffffffc0;
    if (param_3 != 0) {
      FUN_000f97a8(&local_30,param_2,param_3);
      param_2 = param_2 + param_3;
    }
    if (uVar2 != 0) {
      thunk_FUN_000f841a(param_1 + 0x30,param_2,uVar2);
      *(uint *)(param_1 + 0x70) = uVar2;
      return 0;
    }
  }
  return 0;
}



/* ================================================================
 * entry: 0x000f97a8
 * end:   0x000f9871
 * size:  202 bytes
 * name:  FUN_000f97a8
 * ================================================================ */

void FUN_000f97a8(undefined4 *param_1,undefined4 param_2,int param_3)

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
  FUN_000f943c(0xffffffff);
  FUN_000f9448(0x80);
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
    FUN_000f9454(0x40);
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



/* ================================================================
 * entry: 0x000f9898
 * end:   0x000f98bb
 * size:  36 bytes
 * name:  FUN_000f9898
 * ================================================================ */

undefined4 FUN_000f9898(void)

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



/* ================================================================
 * entry: 0x000f9958
 * end:   0x000f996b
 * size:  20 bytes
 * name:  FUN_000f9958
 * ================================================================ */

undefined4 FUN_000f9958(int *param_1)

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



/* ================================================================
 * entry: 0x000f9978
 * end:   0x000f998b
 * size:  20 bytes
 * name:  FUN_000f9978
 * ================================================================ */

undefined4 FUN_000f9978(int *param_1)

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



/* ================================================================
 * entry: 0x000f9998
 * end:   0x000f9a01
 * size:  106 bytes
 * name:  FUN_000f9998
 * ================================================================ */

void FUN_000f9998(void)

{
  ushort uVar1;
  int iVar2;
  undefined4 *puVar3;
  uint uVar4;

  iVar2 = DAT_000f9a04;
  if (*(int *)(DAT_000f9a04 + 0x104) != 0) {
    *(int *)(DAT_000f9a08 + 0xc) = *(int *)(DAT_000f9a08 + 0xc) + 1;
    FUN_000fc114(iVar2,0x104);
  }
  uVar4 = 0;
  do {
    uVar1 = (short)(uVar4 << 2) + 0x140;
    if (*(int *)(iVar2 + (uint)uVar1) != 0) {
      FUN_000fc114(iVar2,uVar1);
      puVar3 = (undefined4 *)(DAT_000f9a08 + 0x10 + uVar4 * 0x10);
      FUN_000fd6bc(puVar3);
      if (puVar3[1] == 0) {
        if (puVar3[2] != 0) {
          FUN_000fd5cc(puVar3);
        }
        if ((code *)*puVar3 != (code *)0x0) {
          (*(code *)*puVar3)();
        }
      }
      else {
        FUN_000fd5cc(puVar3);
      }
    }
    uVar4 = uVar4 + 1;
  } while (uVar4 < 2);
  return;
}



/* ================================================================
 * entry: 0x000f9a0c
 * end:   0x000f9a0f
 * size:  4 bytes
 * name:  thunk_FUN_000fc30c
 * ================================================================ */

void thunk_FUN_000fc30c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 *param_4
                       )

{
  undefined4 uStack_10;
  undefined4 uStack_c;
  undefined4 *puStack_8;

  uStack_10 = param_2;
  uStack_c = param_3;
  puStack_8 = param_4;
  FUN_000fc394(&uStack_10,DAT_000fc32c);
  while (puStack_8 != (undefined4 *)0x0) {
    (*(code *)*puStack_8)(puStack_8[1]);
    FUN_000fc3c2(&uStack_10);
  }
  return;
}



/* ================================================================
 * entry: 0x000f9a10
 * end:   0x000f9bef
 * size:  480 bytes
 * name:  bootloader_entry
 * ================================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void bootloader_entry(void)

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
  FUN_000fc450(0,puVar3,0x10000000,1);
  do {
  } while (*DAT_000f9c18 == 0);
  if ((_DAT_10001200 < 0) && (_DAT_10001204 < 0)) {
    *DAT_000f9c2c = DAT_000f9c28;
    return;
  }
  FUN_000fc450(2);
  do {
  } while (*extraout_r2 == 0);
  *DAT_000f9c1c = extraout_r3;
  do {
  } while (*extraout_r2 == 0);
  FUN_000fc450(0);
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
  FUN_000fc450(0);
  do {
  } while (*extraout_r2_01 == 0);
  DataSynchronizationBarrier(0xf);
  DAT_000f9c14[-0x1f] = DAT_000f9c14[-0x1f] & 0x700 | DAT_000f9c24;
  DataSynchronizationBarrier(0xf);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* ================================================================
 * entry: 0x000f9c30
 * end:   0x000f9c3d
 * size:  14 bytes
 * name:  FUN_000f9c30
 * ================================================================ */

void FUN_000f9c30(void)

{
  *DAT_000f9c40 = 0;
  return;
}



/* ================================================================
 * entry: 0x000f9c44
 * end:   0x000f9c45
 * size:  2 bytes
 * name:  thunk_FUN_000f9c4c
 * ================================================================ */

void thunk_FUN_000f9c4c(undefined4 *param_1,undefined4 *param_2,int param_3)

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



/* ================================================================
 * entry: 0x000f9c4c
 * end:   0x000f9c51
 * size:  12 bytes
 * name:  FUN_000f9c4c
 * ================================================================ */

void FUN_000f9c4c(undefined4 *param_1,undefined4 *param_2,int param_3)

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



/* ================================================================
 * entry: 0x000f9c64
 * end:   0x000f9c83
 * size:  32 bytes
 * name:  FUN_000f9c64
 * ================================================================ */

undefined4 FUN_000f9c64(uint param_1)

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



/* ================================================================
 * entry: 0x000f9c88
 * end:   0x000f9c93
 * size:  12 bytes
 * name:  FUN_000f9c88
 * ================================================================ */

undefined4 FUN_000f9c88(uint param_1)

{
  if ((param_1 & 3) != 0) {
    return 0;
  }
  return 1;
}



/* ================================================================
 * entry: 0x000f9c94
 * end:   0x000f9cab
 * size:  24 bytes
 * name:  FUN_000f9c94
 * ================================================================ */

undefined4 FUN_000f9c94(int param_1,uint param_2,int param_3)

{
  if ((*(uint *)(param_1 + 0xc) <= param_2) &&
     ((param_2 + param_3) - 1 <= *(uint *)(param_1 + 0x10))) {
    return 1;
  }
  return 0;
}



/* ================================================================
 * entry: 0x000f9cac
 * end:   0x000f9d37
 * size:  140 bytes
 * name:  dfu_advertising_name_get
 * ================================================================ */

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
    FUN_000f9dc4();
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



/* ================================================================
 * entry: 0x000f9d44
 * end:   0x000f9d6f
 * size:  44 bytes
 * name:  FUN_000f9d44
 * ================================================================ */

uint FUN_000f9d44(void)

{
  uint uVar1;
  undefined1 auStack_20 [24];

  FUN_000f841a(auStack_20,DAT_000f9d70,0x18);
  uVar1 = dfu_advertising_name_get(6,auStack_20);
  if (uVar1 == 0) {
    software_interrupt(0x74);
    uVar1 = (uint)*DAT_000f9d74;
    software_interrupt(0x73);
  }
  return uVar1;
}



/* ================================================================
 * entry: 0x000f9d78
 * end:   0x000f9db9
 * size:  66 bytes
 * name:  nrf_bootloader_app_activate
 * ================================================================ */

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
  iVar2 = FUN_000fb4d0();
  iVar4 = *(int *)(iVar1 + 0x30);
  iVar5 = iVar6 - iVar4;
  iVar7 = iVar4 + iVar7;
  if (iVar7 == iVar2 + iVar4) {
    iVar5 = 0;
  }
  iVar2 = FUN_000fac3c(iVar2 + iVar4,iVar7,iVar5,8);
  if (iVar2 == 0) {
    uVar3 = FUN_000fb4d0();
    iVar4 = FUN_000fa65c(uVar3,iVar6,0);
    if (*(int *)(iVar1 + 0x28) == iVar4) {
      *(int *)(iVar1 + 0x18) = iVar6;
      *(int *)(iVar1 + 0x1c) = iVar4;
      *(undefined4 *)(iVar1 + 0x20) = 1;
    }
  }
  return iVar2;
}



/* ================================================================
 * entry: 0x000f9dc4
 * end:   0x000f9dc7
 * size:  4 bytes
 * name:  FUN_000f9dc4
 * ================================================================ */

undefined4 FUN_000f9dc4(void)

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

  uVar7 = FUN_000fc654();
  pcVar1 = DAT_000f9e64;
  uVar5 = (uint)((ulonglong)uVar7 >> 0x20);
  if (*(ushort *)(DAT_000f9e64 + 2) < uVar5) {
    uVar4 = 9;
  }
  else {
    uStack_28 = extraout_r3 & 0xffffff00;
    FUN_000f9ed4(&uStack_28);
    if ((ushort)(byte)pcVar1[1] < *(ushort *)(pcVar1 + 4)) {
      cVar2 = pcVar1[1] + 1;
    }
    else {
      cVar2 = '\0';
    }
    if (cVar2 == *pcVar1) {
      FUN_000f9f1c(uStack_28 & 0xff);
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
      FUN_000f9f1c(uStack_28 & 0xff);
      if (uVar6 != 0xffff) {
        iVar3 = *(int *)(pcVar1 + 8);
        *(undefined4 *)(iVar3 + uVar6 * 8) = extraout_r2;
        if (((int)uVar7 == 0) || (uVar5 == 0)) {
          *(undefined2 *)(iVar3 + uVar6 * 8 + 4) = 0;
        }
        else {
          FUN_000f841a(uVar6 * *(ushort *)(pcVar1 + 2) + *(int *)(pcVar1 + 0xc),(int)uVar7,uVar5);
          *(short *)(*(int *)(pcVar1 + 8) + uVar6 * 8 + 4) = (short)((ulonglong)uVar7 >> 0x20);
        }
        return 0;
      }
    }
    uVar4 = 4;
  }
  return uVar4;
}



/* ================================================================
 * entry: 0x000f9dc8
 * end:   0x000f9e61
 * size:  154 bytes
 * name:  FUN_000f9dc8
 * ================================================================ */

undefined4 FUN_000f9dc8(int param_1,uint param_2,undefined4 param_3,uint param_4)

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
    FUN_000f9ed4(&local_28);
    if ((ushort)(byte)pcVar1[1] < *(ushort *)(pcVar1 + 4)) {
      cVar2 = pcVar1[1] + 1;
    }
    else {
      cVar2 = '\0';
    }
    if (cVar2 == *pcVar1) {
      FUN_000f9f1c(local_28 & 0xff);
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
      FUN_000f9f1c(local_28 & 0xff);
      if (uVar5 != 0xffff) {
        iVar3 = *(int *)(pcVar1 + 8);
        *(undefined4 *)(iVar3 + uVar5 * 8) = param_3;
        if ((param_1 == 0) || (param_2 == 0)) {
          *(undefined2 *)(iVar3 + uVar5 * 8 + 4) = 0;
        }
        else {
          FUN_000f841a(uVar5 * *(ushort *)(pcVar1 + 2) + *(int *)(pcVar1 + 0xc),param_1,param_2);
          *(short *)(*(int *)(pcVar1 + 8) + uVar5 * 8 + 4) = (short)param_2;
        }
        return 0;
      }
    }
    uVar4 = 4;
  }
  return uVar4;
}



/* ================================================================
 * entry: 0x000f9e68
 * end:   0x000f9ea1
 * size:  58 bytes
 * name:  FUN_000f9e68
 * ================================================================ */

void FUN_000f9e68(void)

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



/* ================================================================
 * entry: 0x000f9ea8
 * end:   0x000f9ecf
 * size:  40 bytes
 * name:  FUN_000f9ea8
 * ================================================================ */

undefined4 FUN_000f9ea8(undefined2 param_1,short param_2,uint param_3)

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



/* ================================================================
 * entry: 0x000f9ed4
 * end:   0x000f9f13
 * size:  64 bytes
 * name:  FUN_000f9ed4
 * ================================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000f9ed4(undefined1 *param_1)

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



/* ================================================================
 * entry: 0x000f9f1c
 * end:   0x000f9f49
 * size:  46 bytes
 * name:  FUN_000f9f1c
 * ================================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000f9f1c(int param_1)

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



/* ================================================================
 * entry: 0x000f9f50
 * end:   0x000f9f91
 * size:  66 bytes
 * name:  nrf_bootloader_bl_activate
 * ================================================================ */

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
    iVar2 = FUN_000fb4f8();
  }
  iVar1 = FUN_000f848e(DAT_000f9f98,iVar2,iVar3);
  if (iVar1 == 0) {
    return;
  }
  FUN_000fb198();
  nrf_dfu_mbr_copy_bl(iVar2,iVar3);
  return;
}



/* ================================================================
 * entry: 0x000f9f9c
 * end:   0x000fa051
 * size:  182 bytes
 * name:  FUN_000f9f9c
 * ================================================================ */

/* WARNING: Removing unreachable block (ram,0x000f9fc4) */
/* WARNING: Removing unreachable block (ram,0x000f9fd6) */
/* WARNING: Removing unreachable block (ram,0x000fa014) */

undefined8 FUN_000f9f9c(void)

{
  undefined1 local_50 [68];

  *(undefined2 *)(DAT_000fa054 + 2) = 0xffff;
  software_interrupt(0xa8);
  return CONCAT44(local_50,1);
}



/* ================================================================
 * entry: 0x000fa060
 * end:   0x000fa113
 * size:  170 bytes
 * name:  FUN_000fa060
 * ================================================================ */

void FUN_000fa060(char *param_1)

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

  FUN_000f846a(&local_28,0x14);
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
      iVar4 = FUN_000fd242(&local_28,*(undefined4 *)(param_1 + 4),*(undefined4 *)(param_1 + 8));
      break;
    case '\x06':
      uVar8 = *(undefined4 *)(param_1 + 8);
      uVar7 = *(undefined4 *)(param_1 + 4);
      iVar2 = FUN_000fd6d0(*(undefined4 *)(param_1 + 0xc),local_25);
      iVar3 = FUN_000fd6d0(uVar7,local_25 + iVar2);
      iVar4 = FUN_000fd6d0(uVar8,local_25 + iVar2 + iVar3);
      iVar4 = iVar4 + iVar2 + iVar3;
    }
    uVar6 = iVar4 + 3U & 0xff;
  }
  else if (param_1[1] == '\v') {
    local_25[0] = FUN_000faac8(0xb,3);
    FUN_000faad8(0);
    uVar6 = 4;
  }
switchD_000fa0c4_caseD_0:
  FUN_000fd264(&local_28,uVar6);
  return;
}



/* ================================================================
 * entry: 0x000fa118
 * end:   0x000fa169
 * size:  82 bytes
 * name:  FUN_000fa118
 * ================================================================ */

uint FUN_000fa118(int param_1)

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
    uVar2 = FUN_000fc244(uVar2);
    return uVar2;
  }
  return 0;
}



/* ================================================================
 * entry: 0x000fa178
 * end:   0x000fa1fd
 * size:  134 bytes
 * name:  FUN_000fa178
 * ================================================================ */

int FUN_000fa178(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 local_10;

  iVar1 = DAT_000fa200;
  if ((*(byte *)(DAT_000fa200 + 8) & 1) == 0) {
    *(undefined4 *)(DAT_000fa200 + 0xc) = param_1;
    local_10 = param_4;
    FUN_000faf26(DAT_000fa204);
    local_10 = 0;
    iVar2 = FUN_000fb758();
    if (iVar2 == 0) {
      software_interrupt(0x13);
      iVar2 = DAT_000fa208;
      if ((((DAT_000fa208 == 0) && (iVar2 = FUN_000fc298(), iVar2 == 0)) &&
          (iVar2 = FUN_000fc120(&local_10), iVar2 == 0)) &&
         (iVar2 = FUN_000fc134(1,&local_10), iVar2 == 0)) {
        iVar2 = FUN_000fc1d0(&local_10);
      }
    }
    if (iVar2 == 0) {
      iVar2 = bootloader_adv_name_record_valid();
      if (iVar2 != 0) {
        FUN_000fb918(DAT_000fa20c);
        *(uint *)(iVar1 + 8) = *(uint *)(iVar1 + 8) | 2;
      }
      iVar2 = gap_params_init();
      if (((iVar2 == 0) && (iVar2 = FUN_000f9f9c(DAT_000fa20c + 0x1c), iVar2 == 0)) &&
         (iVar2 = FUN_000f9d44(), iVar2 == 0)) {
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



/* ================================================================
 * entry: 0x000fa210
 * end:   0x000fa3d7
 * size:  456 bytes
 * name:  FUN_000fa210
 * ================================================================ */

uint FUN_000fa210(ushort *param_1,undefined4 param_2,undefined4 param_3,ushort *param_4)

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
      uVar2 = FUN_000f9dc4(uVar1,puVar6,0);
    }
  }
  else {
    if (uVar2 < 0x22) {
      if (uVar2 == 0x13) {
        local_28 = *(undefined4 *)(DAT_000fa3e4 + -0x68);
        local_24 = auStack_20;
        software_interrupt(0xad);
        if (*(short *)(DAT_000fa3d8 + 2) != 0) {
          FUN_000f9dc4(*(short *)(DAT_000fa3d8 + 2),0x2a05,&local_28);
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
            iVar3 = FUN_000f9d44();
            uVar2 = 0;
            if (iVar3 != 0) {
              uVar2 = FUN_000f9dc4();
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
        iVar4 = FUN_000fc690(DAT_000fa3dc,param_1);
        if (iVar4 == 0) {
          return 0;
        }
        uVar2 = FUN_000fc468(DAT_000fa3dc,param_1 + 4);
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
          iVar4 = FUN_000faeb2(DAT_000fa3e0);
          if (iVar4 == 0) {
            return 0;
          }
          FUN_000f841a(iVar4,param_1 + 9,param_1[8]);
          FUN_000f841a(&local_28,DAT_000fa3e4,0x18);
          local_24 = (undefined1 *)iVar3;
          local_14 = param_1[8];
          local_18 = iVar4;
          iVar3 = FUN_000fb7c0(&local_28);
          if (iVar3 == 0) {
            return 0;
          }
          uVar2 = FUN_000faef6(DAT_000fa3e0,iVar4);
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
      uVar2 = FUN_000f9dc4(uVar1,param_1,puVar7,param_4);
      return uVar2;
    }
  }
  return uVar2;
}



/* ================================================================
 * entry: 0x000fa3e8
 * end:   0x000fa3ef
 * size:  8 bytes
 * name:  FUN_000fa3e8
 * ================================================================ */

byte FUN_000fa3e8(byte *param_1)

{
  return *param_1 & 1;
}



/* ================================================================
 * entry: 0x000fa3f0
 * end:   0x000fa3ff
 * size:  16 bytes
 * name:  FUN_000fa3f0
 * ================================================================ */

undefined4 FUN_000fa3f0(char *param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  undefined4 uVar1;

  if ((param_4 == 0) && (*param_1 == '\x01')) {
    return 1;
  }
  uVar1 = nrf_dfu_validation_boot_validate();
  return uVar1;
}



/* ================================================================
 * entry: 0x000fa400
 * end:   0x000fa40b
 * size:  12 bytes
 * name:  FUN_000fa400
 * ================================================================ */

void FUN_000fa400(int param_1)

{
  FUN_000fa65c(param_1 + 0x260,0xc3,0);
  return;
}



/* ================================================================
 * entry: 0x000fa40c
 * end:   0x000fa49d
 * size:  146 bytes
 * name:  FUN_000fa40c
 * ================================================================ */

undefined4
FUN_000fa40c(undefined1 *param_1,int param_2,uint param_3,undefined4 param_4,undefined4 param_5,
            uint param_6)

{
  undefined4 uVar1;
  int iVar2;
  undefined1 auStack_a0 [124];
  undefined4 local_24 [2];

  local_24[0] = 0x20;
  FUN_000f846a(auStack_a0,0x7c);
  FUN_000f846a(param_1,0x41);
  iVar2 = param_2 + param_3 * 0x44;
  if (param_3 < *(ushort *)(param_2 + 0x94)) {
    param_6 = (uint)*(byte *)(iVar2 + 0x96);
  }
  *param_1 = (char)param_6;
  if (param_6 != 0) {
    if (param_6 == 1) {
      uVar1 = FUN_000fa65c(param_4,param_5,0);
      *(undefined4 *)(param_1 + 1) = uVar1;
    }
    else if (param_6 == 2) {
      iVar2 = FUN_000fb320(auStack_a0,DAT_000fa4a0,param_4,param_5,param_1 + 1,local_24);
      if (iVar2 != 0) {
        return 0;
      }
    }
    else {
      if (param_6 != 3) {
        return 0;
      }
      FUN_000f841a(param_1 + 1,iVar2 + 0x9a,*(undefined2 *)(iVar2 + 0x98));
    }
  }
  uVar1 = nrf_dfu_validation_boot_validate(param_1,param_4,param_5);
  return uVar1;
}



/* ================================================================
 * entry: 0x000fa4a4
 * end:   0x000fa4e3
 * size:  64 bytes
 * name:  FUN_000fa4a4
 * ================================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000fa4a4(int param_1)

{
  undefined1 *puVar1;
  int extraout_r2;
  int iVar2;
  undefined1 *puVar3;
  undefined1 *puVar4;
  bool bVar5;

  if (param_1 != 0) {
    *puRam000fa4c0 = 0;
    FUN_000fb988(uRam000fa4c4);
    return;
  }
  FUN_000fa978();
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



/* ================================================================
 * entry: 0x000fa4e4
 * end:   0x000fa4fb
 * size:  24 bytes
 * name:  FUN_000fa4e4
 * ================================================================ */

undefined4 FUN_000fa4e4(void)

{
  int iVar1;

  iVar1 = FUN_000faea8(DAT_000fa4fc,1);
  DataMemoryBarrier(0x1f);
  if (iVar1 != 0) {
    return 0;
  }
  return 1;
}



/* ================================================================
 * entry: 0x000fa500
 * end:   0x000fa50b
 * size:  12 bytes
 * name:  FUN_000fa500
 * ================================================================ */

void FUN_000fa500(void)

{
  DataMemoryBarrier(0x1f);
  *DAT_000fa50c = 0;
  return;
}



/* ================================================================
 * entry: 0x000fa510
 * end:   0x000fa529
 * size:  26 bytes
 * name:  FUN_000fa510
 * ================================================================ */

void FUN_000fa510(void)

{
  *DAT_000fa52c = 0;
  *(undefined4 *)(DAT_000fa530 + 0x180) = 0x400;
  DataSynchronizationBarrier(0xf);
  InstructionSynchronizationBarrier(0xf);
  return;
}



/* ================================================================
 * entry: 0x000fa534
 * end:   0x000fa543
 * size:  16 bytes
 * name:  FUN_000fa534
 * ================================================================ */

void FUN_000fa534(void)

{
  *DAT_000fa544 = 1;
  *(undefined4 *)(DAT_000fa548 + 0x100) = 0x400;
  return;
}



/* ================================================================
 * entry: 0x000fa5a4
 * end:   0x000fa603
 * size:  96 bytes
 * name:  FUN_000fa5a4
 * ================================================================ */

undefined4 FUN_000fa5a4(int param_1,int param_2,uint param_3)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;

  iVar1 = FUN_000fa4e4();
  if (iVar1 != 0) {
    FUN_000fa534();
    do {
      uVar3 = 0x1000;
      if (param_3 < 0x1001) {
        uVar3 = param_3;
      }
      FUN_000f841a(DAT_000fa604,param_2,uVar3);
      iVar1 = FUN_000f9704(param_1 + 8,DAT_000fa604,uVar3);
      param_3 = param_3 - uVar3;
      param_2 = param_2 + uVar3;
    } while ((iVar1 == 0) && (param_3 != 0));
    FUN_000fa510();
    FUN_000fa500();
    uVar2 = FUN_000fabf4(iVar1);
    return uVar2;
  }
  return 0x8504;
}



/* ================================================================
 * entry: 0x000fa608
 * end:   0x000fa635
 * size:  46 bytes
 * name:  FUN_000fa608
 * ================================================================ */

undefined4 FUN_000fa608(void)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;

  *DAT_000fa638 = 0;
  puVar1 = DAT_000fa63c;
  DataMemoryBarrier(0x1f);
  *DAT_000fa63c = 1;
  iVar2 = FUN_000f9898();
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



/* ================================================================
 * entry: 0x000fa64c
 * end:   0x000fa657
 * size:  12 bytes
 * name:  FUN_000fa64c
 * ================================================================ */

void FUN_000fa64c(int param_1)

{
  int iVar1;

  iVar1 = DAT_000fa658;
  *(undefined4 *)(param_1 + 4) = *(undefined4 *)(DAT_000fa658 + 0x3c);
  *(undefined4 *)(param_1 + 8) = *(undefined4 *)(iVar1 + 0x40);
  return;
}



/* ================================================================
 * entry: 0x000fa65c
 * end:   0x000fa691
 * size:  54 bytes
 * name:  FUN_000fa65c
 * ================================================================ */

uint FUN_000fa65c(int param_1,uint param_2,uint *param_3)

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



/* ================================================================
 * entry: 0x000fa698
 * end:   0x000fa6b5
 * size:  30 bytes
 * name:  FUN_000fa698
 * ================================================================ */

undefined4 FUN_000fa698(int *param_1)

{
  int iVar1;

  if ((*param_1 != -1) && (iVar1 = FUN_000fd410(param_1), *param_1 == iVar1)) {
    return 1;
  }
  return 0;
}



/* ================================================================
 * entry: 0x000fa6b8
 * end:   0x000fa6e5
 * size:  46 bytes
 * name:  FUN_000fa6b8
 * ================================================================ */

void FUN_000fa6b8(void)

{
  int iVar1;
  undefined1 auStack_48 [64];

  iVar1 = DAT_000fa6e8;
  if (*(char *)(DAT_000fa6e8 + 1) == '\0') {
    FUN_000fb3e8();
    FUN_000fb428(auStack_48,DAT_000fa6ec,0x20);
    FUN_000fb298(DAT_000fa6f4,DAT_000fa6f0,auStack_48,0x40);
    *(undefined1 *)(iVar1 + 1) = 1;
  }
  return;
}



/* ================================================================
 * entry: 0x000fa776
 * end:   0x000fa86b
 * size:  372 bytes
 * name:  FUN_000fa776
 * ================================================================ */

undefined4 FUN_000fa776(int param_1,int param_2,int param_3)

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
      uVar4 = FUN_000fcec4(param_1);
      return uVar4;
    }
    if (param_2 == 2) {
      iVar3 = FUN_000fcdf0(param_1,&local_48);
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
      iVar3 = FUN_000fd1e0(param_1,param_2,&local_24,&local_48);
      uVar4 = 0;
      if (iVar3 != 0) {
        FUN_000fcddc(&local_44,&local_24,local_48);
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
          iVar3 = FUN_000fcdf0(param_1,&iStack_28);
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
        FUN_000f846a(*(undefined4 *)(param_3 + 0x10),*(undefined2 *)(*(int *)(param_3 + 4) + 8));
        FUN_000fce26(*(undefined4 *)(*(int *)(param_3 + 4) + 0xc),*(undefined4 *)(param_3 + 0x10));
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



/* ================================================================
 * entry: 0x000fa870
 * end:   0x000fa8e3
 * size:  116 bytes
 * name:  nrf_bootloader_app_is_valid
 * ================================================================ */

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
       (iVar2 = FUN_000fa3f0(DAT_000fa8ec + 0x260,0x1000,*(undefined4 *)(DAT_000fa8ec + 0x34),uVar6)
       , iVar2 != 0)) {
      uVar3 = FUN_000fb4d0();
      iVar4 = FUN_000fa3f0(DAT_000fa8f4,uVar3,*(undefined4 *)(iVar4 + 0x18),uVar6);
      if ((iVar4 != 0) && ((DAT_000fa8e8[-1] & 0xf9) != 0xb1)) {
        return 0;
      }
    }
  }
  return 1;
}



/* ================================================================
 * entry: 0x000fa908
 * end:   0x000fa945
 * size:  56 bytes
 * name:  FUN_000fa908
 * ================================================================ */

void FUN_000fa908(undefined4 param_1)

{
  switch(param_1) {
  case 2:
    nrf_dfu_settings_init();
    break;
  case 3:
  case 4:
    FUN_000fafdc(0x3c0000,DAT_000fa948);
    break;
  case 6:
  case 7:
    FUN_000fa4a4(1);
  }
  if (*(code **)(DAT_000fa94c + 4) != (code *)0x0) {
                    /* WARNING: Could not recover jumptable at 0x000fa942. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (**(code **)(DAT_000fa94c + 4))(param_1);
    return;
  }
  return;
}



/* ================================================================
 * entry: 0x000fa950
 * end:   0x000fa973
 * size:  36 bytes
 * name:  FUN_000fa950
 * ================================================================ */

void FUN_000fa950(int param_1)

{
  if ((param_1 == 6) || (param_1 == 7)) {
    FUN_000fbb08(0);
  }
  if ((code *)*DAT_000fa974 != (code *)0x0) {
                    /* WARNING: Could not recover jumptable at 0x000fa970. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*(code *)*DAT_000fa974)(param_1);
    return;
  }
  return;
}



/* ================================================================
 * entry: 0x000fa978
 * end:   0x000fa991
 * size:  26 bytes
 * name:  FUN_000fa978
 * ================================================================ */

void FUN_000fa978(void)

{
  DataSynchronizationBarrier(0xf);
  *DAT_000fa994 = *DAT_000fa994 & 0x700 | DAT_000fa998;
  DataSynchronizationBarrier(0xf);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* ================================================================
 * entry: 0x000fa9e4
 * end:   0x000faa2b
 * size:  72 bytes
 * name:  FUN_000fa9e4
 * ================================================================ */

undefined4 FUN_000fa9e4(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  undefined4 uStack_20;

  puVar1 = DAT_000faa2c;
  uStack_20 = param_4;
  puVar2 = (undefined4 *)FUN_000fae2e(*DAT_000faa2c,&uStack_20);
  if (puVar2 == (undefined4 *)0x0) {
    uVar3 = 4;
  }
  else {
    FUN_000f846a(puVar2,0x1c);
    *(undefined1 *)(puVar2 + 1) = 1;
    puVar2[5] = param_3;
    *puVar2 = param_1;
    puVar2[2] = param_4;
    puVar2[3] = param_2 >> 0xc;
    FUN_000fae70(*puVar1,&uStack_20);
    FUN_000fd1a0();
    uVar3 = 0;
  }
  return uVar3;
}



/* ================================================================
 * entry: 0x000faa30
 * end:   0x000faa65
 * size:  54 bytes
 * name:  FUN_000faa30
 * ================================================================ */

void FUN_000faa30(int param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4,
                 undefined4 param_5,undefined4 param_6)

{
  undefined1 local_38 [8];
  undefined4 local_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;

  if (*(int *)(param_1 + 8) != 0) {
    FUN_000f846a(local_38,0x18);
    uStack_28 = param_5;
    uStack_24 = param_6;
    local_38[0] = param_2;
    local_30 = param_4;
    uStack_2c = param_3;
    (**(code **)(param_1 + 8))(local_38);
  }
  return;
}



/* ================================================================
 * entry: 0x000faa66
 * end:   0x000faab9
 * size:  84 bytes
 * name:  FUN_000faa66
 * ================================================================ */

void FUN_000faa66(int *param_1,undefined4 param_2)

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
  FUN_000f846a(local_28,0x18);
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



/* ================================================================
 * entry: 0x000faaba
 * end:   0x000faac7
 * size:  14 bytes
 * name:  FUN_000faaba
 * ================================================================ */

void FUN_000faaba(uint param_1)

{
  if (10 < param_1) {
    FUN_000faad8(param_1 - 0xb & 0xff);
    return;
  }
  return;
}



/* ================================================================
 * entry: 0x000faac8
 * end:   0x000faad1
 * size:  10 bytes
 * name:  FUN_000faac8
 * ================================================================ */

undefined1 FUN_000faac8(void)

{
  undefined1 uVar1;

  uVar1 = *DAT_000faad4;
  *DAT_000faad4 = 0;
  return uVar1;
}



/* ================================================================
 * entry: 0x000faad8
 * end:   0x000faadf
 * size:  8 bytes
 * name:  FUN_000faad8
 * ================================================================ */

undefined4 FUN_000faad8(undefined1 param_1)

{
  *DAT_000faae0 = param_1;
  return 0xb;
}



/* ================================================================
 * entry: 0x000faafc
 * end:   0x000fab03
 * size:  8 bytes
 * name:  FUN_000faafc
 * ================================================================ */

undefined4 FUN_000faafc(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_b8 [124];
  undefined1 auStack_3c [32];
  undefined4 uStack_1c;

  uStack_1c = 0x20;
  uVar2 = 1;
  FUN_000f846a(auStack_b8,0x7c);
  FUN_000fa6b8();
  FUN_000fb4a0(auStack_3c,param_1 + 0x72,0x20);
  iVar1 = FUN_000fb320(auStack_b8,DAT_000fbc24,param_2,param_3,DAT_000fbc20,&uStack_1c);
  if ((iVar1 != 0) || (iVar1 = FUN_000f848e(DAT_000fbc20,auStack_3c,0x20), iVar1 != 0)) {
    uVar2 = 0;
  }
  return uVar2;
}



/* ================================================================
 * entry: 0x000fab04
 * end:   0x000fabd9
 * size:  214 bytes
 * name:  gap_params_init
 * ================================================================ */

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
        FUN_000f9dc4();
      }
      FUN_000f846a(iVar6,0x14);
      iVar2 = FUN_000f8480(s_B210_DFU_000fabe4);
      FUN_000f841a(iVar4 + 4,s_B210_DFU_000fabe4,iVar2);
      iVar3 = FUN_000f84a8(iVar4 + 4,s_B210_DFU_000fabe4,8);
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



/* ================================================================
 * entry: 0x000fabf4
 * end:   0x000fac33
 * size:  64 bytes
 * name:  FUN_000fabf4
 * ================================================================ */

undefined4 FUN_000fabf4(int param_1)

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



/* ================================================================
 * entry: 0x000fac3c
 * end:   0x000facc7
 * size:  140 bytes
 * name:  FUN_000fac3c
 * ================================================================ */

int FUN_000fac3c(int param_1,int param_2,int param_3,uint param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;

  if (param_2 != param_1) {
    uVar3 = (uint)(param_2 - param_1) >> 0xc;
    uVar4 = param_3 + 0xfffU >> 0xc;
    FUN_000fb1c0();
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
      iVar1 = FUN_000fb6cc(param_1,uVar5,0);
      if (iVar1 != 0) {
        return iVar1;
      }
      iVar1 = FUN_000fb6f8(param_1,param_2,(iVar2 - (iVar2 - 1U & 3)) + 3,0);
      if (iVar1 != 0) {
        return iVar1;
      }
      uVar4 = uVar4 - uVar5;
      param_3 = param_3 - iVar2;
      param_1 = param_1 + iVar2;
      *(int *)(DAT_000facc8 + 0x30) = *(int *)(DAT_000facc8 + 0x30) + iVar2;
      param_2 = param_2 + iVar2;
      iVar2 = FUN_000fbae0(0);
      if (iVar2 != 0) {
        return iVar2;
      }
    }
  }
  return 0;
}



/* ================================================================
 * entry: 0x000face0
 * end:   0x000fad0d
 * size:  46 bytes
 * name:  FUN_000face0
 * ================================================================ */

undefined4 FUN_000face0(int param_1)

{
  undefined1 uVar1;
  int iVar2;

  *(int *)(param_1 + 4) = DAT_000fad10;
  iVar2 = FUN_000fae8c(DAT_000fad14);
  if (iVar2 == 0) {
    uVar1 = FUN_000fc330();
    iVar2 = DAT_000fad14;
    *(undefined1 *)(DAT_000fad14 + 0x10) = uVar1;
    FUN_000fae08(*(undefined4 *)(DAT_000fad10 + -4),iVar2 + -0x1dc,0x1dc,0x1c);
  }
  return 0;
}



/* ================================================================
 * entry: 0x000fad38
 * end:   0x000fad8f
 * size:  88 bytes
 * name:  FUN_000fad38
 * ================================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_000fad38(int param_1)

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



/* ================================================================
 * entry: 0x000fad98
 * end:   0x000fadc5
 * size:  46 bytes
 * name:  FUN_000fad98
 * ================================================================ */

void FUN_000fad98(int param_1,int *param_2)

{
  int iVar1;

  iVar1 = *(int *)(*param_2 + 8);
  FUN_000fcc68(param_1,iVar1,param_2[1]);
  *(int *)(param_1 + 0x10) = param_2[1];
  *(int **)(param_1 + 0x14) = param_2 + 3;
  if (*(byte *)(iVar1 + 2) >> 6 == 2) {
    *(int **)(param_1 + 0x10) = param_2 + 1;
  }
  return;
}



/* ================================================================
 * entry: 0x000fadc8
 * end:   0x000fadf7
 * size:  48 bytes
 * name:  FUN_000fadc8
 * ================================================================ */

undefined4 FUN_000fadc8(void)

{
  int iVar1;
  undefined2 *puVar2;

  FUN_000fb168();
  iVar1 = nrf_bootloader_acl_add(0,0x1000);
  if ((iVar1 == 0) &&
     (iVar1 = nrf_bootloader_acl_add(iRam000fadf0,0xfe000 - iRam000fadf0), iVar1 == 0)) {
    nrf_bootloader_main(uRam000fadf4);
  }
  puVar2 = (undefined2 *)FUN_000fc654();
  *puVar2 = (short)puVar2;
  iVar1 = FUN_000f82ae(puVar2,&stack0x00000014);
  if (iVar1 != 0) {
    return 0;
  }
  return 0x11;
}



/* ================================================================
 * entry: 0x000fadf8
 * end:   0x000fae07
 * size:  16 bytes
 * name:  FUN_000fadf8
 * ================================================================ */

undefined4 FUN_000fadf8(void)

{
  int iVar1;

  iVar1 = FUN_000f82ae();
  if (iVar1 != 0) {
    return 0;
  }
  return 0x11;
}



/* ================================================================
 * entry: 0x000fae08
 * end:   0x000fae2d
 * size:  38 bytes
 * name:  FUN_000fae08
 * ================================================================ */

undefined4 FUN_000fae08(int *param_1,int param_2,uint param_3,uint param_4)

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



/* ================================================================
 * entry: 0x000fae2e
 * end:   0x000fae43
 * size:  22 bytes
 * name:  FUN_000fae2e
 * ================================================================ */

int FUN_000fae2e(int *param_1,ushort *param_2)

{
  int iVar1;
  int iVar2;

  iVar1 = FUN_000f8218();
  iVar2 = 0;
  if (iVar1 != 0) {
    iVar2 = *param_1 + (uint)*param_2;
  }
  return iVar2;
}



/* ================================================================
 * entry: 0x000fae44
 * end:   0x000fae59
 * size:  22 bytes
 * name:  FUN_000fae44
 * ================================================================ */

undefined4 FUN_000fae44(undefined4 param_1,short *param_2)

{
  if (*param_2 == param_2[1]) {
    FUN_000f829c();
    return 1;
  }
  return 0;
}



/* ================================================================
 * entry: 0x000fae5a
 * end:   0x000fae6f
 * size:  22 bytes
 * name:  FUN_000fae5a
 * ================================================================ */

int FUN_000fae5a(int *param_1,int param_2)

{
  int iVar1;
  int iVar2;

  iVar1 = FUN_000f8262();
  iVar2 = 0;
  if (iVar1 != 0) {
    iVar2 = *param_1 + (uint)*(ushort *)(param_2 + 2);
  }
  return iVar2;
}



/* ================================================================
 * entry: 0x000fae70
 * end:   0x000fae85
 * size:  22 bytes
 * name:  FUN_000fae70
 * ================================================================ */

undefined4 FUN_000fae70(undefined4 param_1,short *param_2)

{
  if (*param_2 == param_2[1]) {
    FUN_000f8250();
    return 1;
  }
  return 0;
}



/* ================================================================
 * entry: 0x000fae86
 * end:   0x000fae9d
 * size:  18 bytes
 * name:  FUN_000fae86
 * ================================================================ */

undefined4 FUN_000fae86(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 local_8;

  local_8 = param_4;
  FUN_000f8312(param_1,0,&local_8);
  return local_8;
}



/* ================================================================
 * entry: 0x000fae8c
 * end:   0x000faea7
 * size:  16 bytes
 * name:  FUN_000fae8c
 * ================================================================ */

void FUN_000fae8c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uStack_8;

  uStack_8 = param_4;
  FUN_000f82f8(param_1,1,&uStack_8);
  return;
}



/* ================================================================
 * entry: 0x000faea8
 * end:   0x000faeb1
 * size:  10 bytes
 * name:  FUN_000faea8
 * ================================================================ */

void FUN_000faea8(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uStack_8;

  uStack_8 = param_4;
  FUN_000f82e0(param_1,param_2,&uStack_8);
  return;
}



/* ================================================================
 * entry: 0x000faeb2
 * end:   0x000faef5
 * size:  68 bytes
 * name:  FUN_000faeb2
 * ================================================================ */

int FUN_000faeb2(int *param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  uint uVar1;
  byte *pbVar2;
  int iVar3;
  uint local_10;

  iVar3 = 0;
  local_10 = param_4 & 0xffffff00;
  FUN_000f9ed4(&local_10);
  uVar1 = *(uint *)*param_1;
  if ((uint)param_1[1] < uVar1) {
    pbVar2 = (byte *)(uVar1 - 1);
    *(uint *)*param_1 = (uint)pbVar2;
    iVar3 = (uint)*pbVar2 * (uint)*(ushort *)(param_1 + 4) + param_1[3];
    if ((uint)*(byte *)(*param_1 + 4) < ((uint)*(byte *)(param_1 + 2) - (int)pbVar2 & 0xff)) {
      *(char *)(*param_1 + 4) = (char)((uint)*(byte *)(param_1 + 2) - (int)pbVar2);
    }
  }
  FUN_000f9f1c(local_10 & 0xff);
  return iVar3;
}



/* ================================================================
 * entry: 0x000faef6
 * end:   0x000faf25
 * size:  48 bytes
 * name:  FUN_000faef6
 * ================================================================ */

void FUN_000faef6(undefined4 *param_1,int param_2,undefined4 param_3,uint param_4)

{
  ushort uVar1;
  int iVar2;
  undefined1 *puVar3;
  uint local_10;

  local_10 = param_4 & 0xffffff00;
  FUN_000f9ed4(&local_10);
  iVar2 = param_1[3];
  uVar1 = *(ushort *)(param_1 + 4);
  puVar3 = *(undefined1 **)*param_1;
  *(undefined1 **)*param_1 = puVar3 + 1;
  *puVar3 = (char)((uint)(param_2 - iVar2) / (uint)uVar1);
  FUN_000f9f1c(local_10 & 0xff);
  return;
}



/* ================================================================
 * entry: 0x000faf26
 * end:   0x000faf55
 * size:  48 bytes
 * name:  FUN_000faf26
 * ================================================================ */

undefined4 FUN_000faf26(int *param_1)

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



/* ================================================================
 * entry: 0x000faf56
 * end:   0x000fafd3
 * size:  124 bytes
 * name:  nrf_bootloader_app_start
 * ================================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void nrf_bootloader_app_start(void)

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
  FUN_000fb770();
  iVar3 = nrf_bootloader_acl_add(DAT_000fafd4,0xff000 - DAT_000fafd4);
  if (iVar3 != 0) {
    FUN_000f9dc4();
  }
  iVar3 = FUN_000fb4d0();
  uVar4 = *(int *)(DAT_000fafd8 + 0x18) - 1U & 0xfff;
  iVar3 = nrf_bootloader_acl_add
                    (0,iVar3 + (*(int *)(DAT_000fafd8 + 0x18) - uVar4) + 0xfff,uVar4,extraout_r3,
                     unaff_r4,unaff_lr);
  if (iVar3 != 0) {
    FUN_000f9dc4();
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



/* ================================================================
 * entry: 0x000fafdc
 * end:   0x000faffd
 * size:  34 bytes
 * name:  FUN_000fafdc
 * ================================================================ */

void FUN_000fafdc(int param_1,undefined4 param_2)

{
  int iVar1;

  iVar1 = DAT_000fb000;
  FUN_000fd6bc(*(undefined4 *)(DAT_000fb000 + 4));
  if (param_1 != 0) {
    FUN_000fd6a0(*(undefined4 *)(iVar1 + 4),param_1,param_2);
    return;
  }
  return;
}



/* ================================================================
 * entry: 0x000fb004
 * end:   0x000fb03b
 * size:  56 bytes
 * name:  nrf_bootloader_acl_add
 * ================================================================ */

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



/* ================================================================
 * entry: 0x000fb044
 * end:   0x000fb0a9
 * size:  102 bytes
 * name:  nrf_bootloader_fw_activate
 * ================================================================ */

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
  FUN_000fb518(iVar4);
  *DAT_000fb0b0 = 0;
  iVar2 = FUN_000fbae0(DAT_000fb0b4);
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



/* ================================================================
 * entry: 0x000fb0b8
 * end:   0x000fb14d
 * size:  150 bytes
 * name:  nrf_bootloader_main
 * ================================================================ */

undefined4 nrf_bootloader_main(undefined4 param_1)

{
  undefined1 *puVar1;
  int iVar2;

  puVar1 = DAT_000fb150;
  *(undefined4 *)(DAT_000fb150 + 4) = param_1;
  iVar2 = FUN_000fb994(0);
  if (iVar2 != 0) {
    return 3;
  }
  iVar2 = nrf_bootloader_fw_activate();
  if (iVar2 == 0) {
    iVar2 = nrf_bootloader_app_is_valid();
    if (iVar2 == 0) {
      iVar2 = FUN_000fb8e4();
      if (iVar2 != 0) {
        return 3;
      }
      *puVar1 = 0;
      FUN_000fb988(DAT_000fb164);
      nrf_bootloader_app_start();
      return 3;
    }
  }
  else {
    if (iVar2 == 1) {
      FUN_000fa4a4(1);
      return 3;
    }
    if (iVar2 != 2) {
      return 3;
    }
  }
  FUN_000fb1c0();
  iVar2 = FUN_000f9ea8(0x18,0x20,DAT_000fb154);
  if (iVar2 != 0) {
    FUN_000f9dc4();
  }
  if ((*DAT_000fb158 & 0xf9) == 0xb1) {
    *DAT_000fb158 = *DAT_000fb158 & 0x4e;
  }
  iVar2 = FUN_000fb73c();
  if (iVar2 == 0) {
    FUN_000fafdc(0x3c0000,DAT_000fb15c);
    iVar2 = FUN_000fb710(DAT_000fb160);
    if (iVar2 == 0) {
      do {
        FUN_000fb198();
        FUN_000f9e68();
        software_interrupt(0x41);
      } while( true );
    }
  }
  return 3;
}



/* ================================================================
 * entry: 0x000fb168
 * end:   0x000fb191
 * size:  42 bytes
 * name:  FUN_000fb168
 * ================================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000fb168(void)

{
  if (_DAT_00000ff8 == -1) {
    FUN_000fc0a0(0xff8,DAT_000fb194);
  }
  if (_DAT_00000ffc == -1) {
    FUN_000fc0a0(0xffc,0xfe000);
    return;
  }
  return;
}



/* ================================================================
 * entry: 0x000fb198
 * end:   0x000fb1ab
 * size:  20 bytes
 * name:  FUN_000fb198
 * ================================================================ */

void FUN_000fb198(void)

{
  int iVar1;

  iVar1 = FUN_000fc440();
  if (iVar1 != 0) {
    FUN_000fd78c();
    return;
  }
  return;
}



/* ================================================================
 * entry: 0x000fb1ac
 * end:   0x000fb1bb
 * size:  16 bytes
 * name:  FUN_000fb1ac
 * ================================================================ */

void FUN_000fb1ac(undefined4 param_1,undefined4 param_2)

{
  int iVar1;

  iVar1 = *(int *)(DAT_000fb1bc + 8);
  *(undefined4 *)(iVar1 + 8) = param_1;
  FUN_000fd6a0(iVar1,param_1,param_2);
  return;
}



/* ================================================================
 * entry: 0x000fb1c0
 * end:   0x000fb1fb
 * size:  60 bytes
 * name:  FUN_000fb1c0
 * ================================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000fb1c0(void)

{
  char *pcVar1;
  int iVar2;

  pcVar1 = DAT_000fb1fc;
  if (*DAT_000fb1fc == '\0') {
    iVar2 = FUN_000fc440();
    if (iVar2 != 0) {
      iVar2 = *DAT_000fb200 + -0xc80;
      if (iVar2 < 0x96) {
        iVar2 = 0x96;
      }
      FUN_000fd78c();
      FUN_000fb1ac(iVar2,DAT_000fb204);
      _DAT_e000e100 = 0x10000;
    }
    *pcVar1 = '\x01';
  }
  return;
}



/* ================================================================
 * entry: 0x000fb208
 * end:   0x000fb227
 * size:  32 bytes
 * name:  FUN_000fb208
 * ================================================================ */

undefined4 FUN_000fb208(int param_1,int param_2)

{
  FUN_000f841a(param_1 + 8,param_2,0x20);
  FUN_000f841a(param_1 + 0x28,param_2 + 0x20,0x20);
  return 0;
}



/* ================================================================
 * entry: 0x000fb228
 * end:   0x000fb28b
 * size:  100 bytes
 * name:  FUN_000fb228
 * ================================================================ */

undefined4
FUN_000fb228(undefined4 *param_1,int param_2,undefined4 param_3,undefined4 param_4,
            undefined4 param_5)

{
  int iVar1;
  undefined4 uVar2;

  *param_1 = DAT_000fb28c;
  iVar1 = FUN_000faea8(DAT_000fb290,1,param_3,param_4,param_4);
  DataMemoryBarrier(0x1f);
  if (iVar1 == 0) {
    FUN_000fa534();
    iVar1 = FUN_000f9648(param_1,param_2 + 8,param_5,param_3,param_4);
    FUN_000fa510();
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



/* ================================================================
 * entry: 0x000fb298
 * end:   0x000fb2c7
 * size:  48 bytes
 * name:  FUN_000fb298
 * ================================================================ */

void FUN_000fb298(int param_1,undefined4 *param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 extraout_r3;

  iVar1 = FUN_000fb470();
  if (((iVar1 == 0) &&
      (iVar1 = FUN_000fb48a(param_3,extraout_r3,*(undefined1 *)(param_1 + 6)), iVar1 == 0)) &&
     (iVar1 = FUN_000fb208(param_2,param_3), iVar1 == 0)) {
    *param_2 = DAT_000fb2c8;
  }
  return;
}



/* ================================================================
 * entry: 0x000fb2cc
 * end:   0x000fb31b
 * size:  80 bytes
 * name:  FUN_000fb2cc
 * ================================================================ */

int FUN_000fb2cc(int param_1,int param_2,int param_3,undefined4 param_4,undefined4 param_5,
                undefined4 param_6)

{
  int iVar1;

  iVar1 = FUN_000fb458(param_2,DAT_000fb31c,param_3,param_4,param_4);
  if ((iVar1 == 0) &&
     (iVar1 = FUN_000fb48a(param_5,param_6,(uint)*(byte *)(*(int *)(param_2 + 4) + 5) << 1),
     iVar1 == 0)) {
    if (param_3 == 0) {
      iVar1 = 0x8510;
    }
    else if (param_1 == 0) {
      iVar1 = 0x8515;
    }
    else {
      iVar1 = FUN_000fb228(param_1,param_2,param_3,param_4,param_5);
    }
  }
  return iVar1;
}



/* ================================================================
 * entry: 0x000fb320
 * end:   0x000fb38b
 * size:  108 bytes
 * name:  FUN_000fb320
 * ================================================================ */

int FUN_000fb320(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,int param_5,
                uint *param_6)

{
  int iVar1;

  iVar1 = FUN_000fb38c();
  if ((iVar1 != 0) || (iVar1 = FUN_000fb3b8(param_1,param_3,param_4), iVar1 != 0)) {
    return iVar1;
  }
  iVar1 = FUN_000fd76c();
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



/* ================================================================
 * entry: 0x000fb38c
 * end:   0x000fb3b1
 * size:  38 bytes
 * name:  FUN_000fb38c
 * ================================================================ */

int FUN_000fb38c(undefined4 *param_1,undefined4 *param_2)

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



/* ================================================================
 * entry: 0x000fb3b8
 * end:   0x000fb3e5
 * size:  46 bytes
 * name:  FUN_000fb3b8
 * ================================================================ */

int FUN_000fb3b8(int param_1,int param_2,int param_3)

{
  int iVar1;

  iVar1 = FUN_000fd76c();
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



/* ================================================================
 * entry: 0x000fb3e8
 * end:   0x000fb419
 * size:  48 bytes
 * name:  FUN_000fb3e8
 * ================================================================ */

int FUN_000fb3e8(void)

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



/* ================================================================
 * entry: 0x000fb428
 * end:   0x000fb441
 * size:  26 bytes
 * name:  FUN_000fb428
 * ================================================================ */

void FUN_000fb428(int param_1,int param_2,int param_3)

{
  FUN_000fb4a0();
  FUN_000fb4a0(param_1 + param_3,param_2 + param_3,param_3);
  return;
}



/* ================================================================
 * entry: 0x000fb442
 * end:   0x000fb457
 * size:  22 bytes
 * name:  FUN_000fb442
 * ================================================================ */

void FUN_000fb442(int param_1,int param_2)

{
  FUN_000fb4b6();
  FUN_000fb4b6(param_1 + param_2,param_2);
  return;
}



/* ================================================================
 * entry: 0x000fb458
 * end:   0x000fb46f
 * size:  24 bytes
 * name:  FUN_000fb458
 * ================================================================ */

undefined4 FUN_000fb458(int *param_1,int param_2)

{
  if (param_1 == (int *)0x0) {
    return 0x8510;
  }
  if (*param_1 != param_2) {
    return 0x8540;
  }
  return 0;
}



/* ================================================================
 * entry: 0x000fb470
 * end:   0x000fb489
 * size:  26 bytes
 * name:  FUN_000fb470
 * ================================================================ */

undefined4 FUN_000fb470(int param_1,undefined4 *param_2)

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



/* ================================================================
 * entry: 0x000fb48a
 * end:   0x000fb49f
 * size:  22 bytes
 * name:  FUN_000fb48a
 * ================================================================ */

undefined4 FUN_000fb48a(int param_1,int param_2,int param_3)

{
  if (param_1 == 0) {
    return 0x8510;
  }
  if (param_2 != param_3) {
    return 0x8511;
  }
  return 0;
}



/* ================================================================
 * entry: 0x000fb4a0
 * end:   0x000fb4b5
 * size:  20 bytes
 * name:  FUN_000fb4a0
 * ================================================================ */

void FUN_000fb4a0(undefined1 *param_1,undefined1 *param_2,int param_3)

{
  undefined1 *puVar1;

  puVar1 = param_1 + param_3;
  while (puVar1 = puVar1 + -1, param_1 <= puVar1) {
    *puVar1 = *param_2;
    param_2 = param_2 + 1;
  }
  return;
}



/* ================================================================
 * entry: 0x000fb4b6
 * end:   0x000fb4cd
 * size:  24 bytes
 * name:  FUN_000fb4b6
 * ================================================================ */

void FUN_000fb4b6(undefined1 *param_1,int param_2)

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



/* ================================================================
 * entry: 0x000fb4d0
 * end:   0x000fb4f1
 * size:  34 bytes
 * name:  FUN_000fb4d0
 * ================================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int FUN_000fb4d0(void)

{
  if (_DAT_00003004 == DAT_000fb4f4) {
    return (_DAT_00003008 - (_DAT_00003008 - 1U & 0xfff)) + 0xfff;
  }
  return 0x1000;
}



/* ================================================================
 * entry: 0x000fb4f8
 * end:   0x000fb513
 * size:  28 bytes
 * name:  FUN_000fb4f8
 * ================================================================ */

int FUN_000fb4f8(void)

{
  int iVar1;

  iVar1 = FUN_000fb4d0();
  return ((*(int *)(DAT_000fb514 + 0x18) + iVar1) -
         (iVar1 + -1 + *(int *)(DAT_000fb514 + 0x18) & 0xfffU)) + 0xfff;
}



/* ================================================================
 * entry: 0x000fb518
 * end:   0x000fb525
 * size:  14 bytes
 * name:  FUN_000fb518
 * ================================================================ */

void FUN_000fb518(undefined4 *param_1)

{
  *param_1 = 0;
  param_1[1] = 0;
  param_1[2] = 0;
  *(undefined4 *)(DAT_000fb528 + 0x30) = 0;
  return;
}



/* ================================================================
 * entry: 0x000fb52c
 * end:   0x000fb5b7
 * size:  140 bytes
 * name:  FUN_000fb52c
 * ================================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_000fb52c(uint param_1,uint param_2,int param_3,int param_4)

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
      iVar2 = FUN_000fb4f8();
      uVar6 = extraout_r3;
      if ((param_3 == 0) || (uVar4 = 1, *(int *)(DAT_000fb5bc + 0x20) != 1)) {
LAB_000fb582:
        uVar4 = 0;
      }
    }
    else if (uVar6 == 1) {
      iVar2 = FUN_000fb4d0();
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
          FUN_000fb518(DAT_000fb5bc + 0x18);
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



/* ================================================================
 * entry: 0x000fb5c4
 * end:   0x000fb651
 * size:  132 bytes
 * name:  FUN_000fb5c4
 * ================================================================ */

void FUN_000fb5c4(undefined1 *param_1,int param_2)

{
  undefined1 uVar1;
  int iVar2;

  switch(*param_1) {
  case 1:
    (**(code **)(DAT_000fb654 + 0xc))(3);
    FUN_000fbc94(*(undefined4 *)(param_1 + 0x14));
    uVar1 = FUN_000faaba();
    *(undefined1 *)(param_2 + 1) = uVar1;
    break;
  case 3:
    goto LAB_000fb64a;
  case 4:
    FUN_000fbcc8(DAT_000fb654 + 4);
    iVar2 = FUN_000faaba();
    *(char *)(param_2 + 1) = (char)iVar2;
    if ((iVar2 == 1) && (iVar2 = FUN_000fbae0(0), iVar2 != 0)) {
      *(undefined1 *)(param_2 + 1) = 10;
      return;
    }
    break;
  case 6:
    *(undefined4 *)(param_2 + 0xc) = 0x200;
LAB_000fb64a:
    FUN_000fa64c(param_2);
    return;
  case 8:
    FUN_000fbc4c(*(undefined4 *)(param_1 + 0x10),*(undefined2 *)(param_1 + 0x14));
    uVar1 = FUN_000faaba();
    *(undefined1 *)(param_2 + 1) = uVar1;
    FUN_000fa64c(param_2);
    if (*(code **)(param_1 + 0xc) != (code *)0x0) {
                    /* WARNING: Could not recover jumptable at 0x000fb61a. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      (**(code **)(param_1 + 0xc))(*(undefined4 *)(param_1 + 0x10));
      return;
    }
  }
  return;
}



/* ================================================================
 * entry: 0x000fb658
 * end:   0x000fb6c3
 * size:  98 bytes
 * name:  FUN_000fb658
 * ================================================================ */

undefined4 FUN_000fb658(undefined1 *param_1,int param_2)

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
      FUN_000fc550(param_1,0);
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



/* ================================================================
 * entry: 0x000fb6cc
 * end:   0x000fb6d7
 * size:  12 bytes
 * name:  FUN_000fb6cc
 * ================================================================ */

void FUN_000fb6cc(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  FUN_000fbed4(DAT_000fb6d8,param_1,param_2,param_3);
  return;
}



/* ================================================================
 * entry: 0x000fb6dc
 * end:   0x000fb6eb
 * size:  16 bytes
 * name:  FUN_000fb6dc
 * ================================================================ */

void FUN_000fb6dc(int param_1)

{
  undefined4 uVar1;

  uVar1 = DAT_000fb6f0;
  if (param_1 != 0) {
    uVar1 = DAT_000fb6ec;
  }
  FUN_000fbf00(DAT_000fb6f4,uVar1,0);
  return;
}



/* ================================================================
 * entry: 0x000fb6f8
 * end:   0x000fb709
 * size:  18 bytes
 * name:  FUN_000fb6f8
 * ================================================================ */

void FUN_000fb6f8(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  FUN_000fc030(DAT_000fb70c,param_1,param_2,param_3,param_4);
  return;
}



/* ================================================================
 * entry: 0x000fb710
 * end:   0x000fb7b9
 * size:  96 bytes
 * name:  FUN_000fb710
 * ================================================================ */

int FUN_000fb710(undefined4 param_1)

{
  int iVar1;
  int iVar2;

  *DAT_000fb734 = param_1;
  FUN_000fa950(0);
  iVar2 = FUN_000fbb3c(DAT_000fb738);
  iVar1 = DAT_000fb738;
  if (iVar2 != 0) {
    return iVar2;
  }
  if (DAT_000fb738 != 0) {
    iVar2 = FUN_000fb6dc(1);
    if (iVar2 == 0) {
      FUN_000fbc28();
      iVar2 = FUN_000fbd5c();
      if ((iVar2 == 0) || (iVar2 = FUN_000fbcc8(DAT_000fb7bc + -4), iVar2 == 1)) {
        *(int *)(DAT_000fb7bc + 4) = iVar1;
        FUN_000faad8(0);
        return 0;
      }
      iVar2 = 3;
    }
    return iVar2;
  }
  return 7;
}



/* ================================================================
 * entry: 0x000fb73c
 * end:   0x000fb73f
 * size:  4 bytes
 * name:  FUN_000fb73c
 * ================================================================ */

undefined4 FUN_000fb73c(void)

{
  return 0;
}



/* ================================================================
 * entry: 0x000fb740
 * end:   0x000fb755
 * size:  22 bytes
 * name:  nrf_dfu_mbr_copy_bl
 * ================================================================ */

undefined1 * nrf_dfu_mbr_copy_bl(void)

{
  undefined1 local_18 [16];

  software_interrupt(0x18);
  return local_18;
}



/* ================================================================
 * entry: 0x000fb758
 * end:   0x000fb769
 * size:  18 bytes
 * name:  FUN_000fb758
 * ================================================================ */

undefined1 * FUN_000fb758(void)

{
  undefined1 local_18 [16];

  software_interrupt(0x18);
  return local_18;
}



/* ================================================================
 * entry: 0x000fb770
 * end:   0x000fb77b
 * size:  12 bytes
 * name:  FUN_000fb770
 * ================================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_000fb770(void)

{
  _DAT_20000000 = 0x1000;
  return 0;
}



/* ================================================================
 * entry: 0x000fb7c0
 * end:   0x000fb7cf
 * size:  16 bytes
 * name:  FUN_000fb7c0
 * ================================================================ */

undefined4 FUN_000fb7c0(int param_1)

{
  undefined4 uVar1;

  if (*(int *)(param_1 + 8) != 0) {
    uVar1 = FUN_000f9dc8(param_1,0x18,DAT_000fb7d0);
    return uVar1;
  }
  return 7;
}



/* ================================================================
 * entry: 0x000fb7d8
 * end:   0x000fb85f
 * size:  122 bytes
 * name:  FUN_000fb7d8
 * ================================================================ */

void FUN_000fb7d8(byte *param_1)

{
  byte bVar1;
  byte *pbVar2;
  int iVar3;
  byte local_28;
  char local_27;

  FUN_000f841a(&local_28,DAT_000fb860,0x18);
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
      FUN_000fb5c4(param_1,&local_28);
    }
    else if (*pbVar2 == 2) {
      iVar3 = FUN_000fb658();
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



/* ================================================================
 * entry: 0x000fb868
 * end:   0x000fb87d
 * size:  22 bytes
 * name:  FUN_000fb868
 * ================================================================ */

undefined4 FUN_000fb868(undefined4 *param_1)

{
  if (param_1 != (undefined4 *)0x0) {
    *param_1 = DAT_000fb880;
    param_1[1] = DAT_000fb884;
    *(undefined1 *)(param_1 + 2) = 1;
    return 0;
  }
  return 0xe;
}



/* ================================================================
 * entry: 0x000fb8e4
 * end:   0x000fb911
 * size:  46 bytes
 * name:  FUN_000fb8e4
 * ================================================================ */

undefined4 FUN_000fb8e4(void)

{
  if ((*(int *)(DAT_000fb914 + 0x324) != -1) || (*(int *)(DAT_000fb914 + 0x364) != -1)) {
    FUN_000fc070(0xff000);
    FUN_000fc0d0(0xff000,DAT_000fb914,0xc9);
  }
  return 0;
}



/* ================================================================
 * entry: 0x000fb918
 * end:   0x000fb92b
 * size:  20 bytes
 * name:  FUN_000fb918
 * ================================================================ */

undefined4 FUN_000fb918(int param_1)

{
  if (param_1 != 0) {
    FUN_000f841a(param_1,DAT_000fb92c,0x1c);
    return 0;
  }
  return 0xe;
}



/* ================================================================
 * entry: 0x000fb930
 * end:   0x000fb94b
 * size:  28 bytes
 * name:  bootloader_adv_name_record_valid
 * ================================================================ */

undefined4 bootloader_adv_name_record_valid(void)

{
  int *piVar1;
  int iVar2;

  piVar1 = DAT_000fb94c;
  iVar2 = FUN_000fa65c(DAT_000fb94c + 1,0x18,0);
  if (*piVar1 == iVar2) {
    return 1;
  }
  return 0;
}



/* ================================================================
 * entry: 0x000fb950
 * end:   0x000fb981
 * size:  50 bytes
 * name:  bootloader_adv_name_record_write
 * ================================================================ */

undefined8 bootloader_adv_name_record_write(undefined4 *param_1,undefined4 param_2)

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
  uVar1 = FUN_000fa65c(param_1 + 1,0x18,0);
  *param_1 = uVar1;
  software_interrupt(0x29);
  return CONCAT44(param_1,iVar2);
}



/* ================================================================
 * entry: 0x000fb988
 * end:   0x000fb98d
 * size:  6 bytes
 * name:  FUN_000fb988
 * ================================================================ */

void FUN_000fb988(undefined4 param_1)

{
  FUN_000fd3fc(param_1,DAT_000fb990);
  return;
}



/* ================================================================
 * entry: 0x000fb994
 * end:   0x000fb9ad
 * size:  26 bytes
 * name:  FUN_000fb994
 * ================================================================ */

undefined4 FUN_000fb994(void)

{
  int iVar1;

  iVar1 = FUN_000fb6dc();
  if (iVar1 == 0) {
    nrf_dfu_settings_init();
    iVar1 = FUN_000fbae0(0);
    if (iVar1 == 0) {
      return 0;
    }
  }
  return 3;
}



/* ================================================================
 * entry: 0x000fb9b0
 * end:   0x000fb9d1
 * size:  34 bytes
 * name:  FUN_000fb9b0
 * ================================================================ */

void FUN_000fb9b0(void)

{
  FUN_000f845c(DAT_000fb9d4,0x200,0xff);
  FUN_000f846a(DAT_000fb9d4 + -0x24,0x20);
  *(undefined4 *)(DAT_000fb9d4 + -0x2c) = 0;
  return;
}



/* ================================================================
 * entry: 0x000fb9d8
 * end:   0x000fba95
 * size:  190 bytes
 * name:  nrf_dfu_settings_init
 * ================================================================ */

void nrf_dfu_settings_init(void)

{
  bool bVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;

  iVar3 = FUN_000fa698(DAT_000fba98);
  piVar2 = DAT_000fba9c;
  iVar6 = *DAT_000fba9c;
  iVar4 = FUN_000fa698(iVar6);
  if ((iVar4 == 0) ||
     ((*(int *)(iVar6 + 4) != 1 && (iVar4 = FUN_000fa400(iVar6), iVar4 != *(int *)(iVar6 + 0x25c))))
     ) {
    bVar1 = false;
  }
  else {
    bVar1 = true;
  }
  iVar4 = DAT_000fbaa0;
  if (iVar3 == 0) {
    if (!bVar1) {
      FUN_000f846a(DAT_000fbaa0);
      goto LAB_000fba86;
    }
    uVar5 = 0x380;
    iVar6 = *piVar2;
    iVar3 = DAT_000fbaa0;
LAB_000fba4e:
    FUN_000f841a(iVar3,iVar6,uVar5);
  }
  else {
    FUN_000f841a(DAT_000fbaa0,DAT_000fba98,0x380);
    if (bVar1) {
      iVar6 = *piVar2;
      FUN_000f841a(iVar4 + 4,iVar6 + 4,0x54);
      uVar5 = 0x2c8;
      iVar6 = iVar6 + 0x5c;
      iVar3 = iVar4 + 0x5c;
      goto LAB_000fba4e;
    }
  }
  if (*(int *)(iVar4 + 4) != 1) {
    return;
  }
  FUN_000f841a(DAT_000fbaa4 + 0x1c8,DAT_000fbaa4,0x40);
  FUN_000f841a(DAT_000fbaa4 + 0x208,DAT_000fbaa4 + 0x40,0x1c);
  *(undefined1 *)(iVar4 + 0x260) = 0;
  *(undefined1 *)(iVar4 + 0x2a1) = 1;
  iVar3 = DAT_000fbaa8;
  *(undefined1 *)(iVar4 + 0x2e2) = 0;
  *(undefined4 *)(iVar3 + 0x22) = *(undefined4 *)(iVar4 + 0x1c);
LAB_000fba86:
  *(undefined4 *)(iVar4 + 4) = 2;
  return;
}



/* ================================================================
 * entry: 0x000fbaac
 * end:   0x000fbad5
 * size:  42 bytes
 * name:  FUN_000fbaac
 * ================================================================ */

void FUN_000fbaac(undefined4 param_1)

{
  undefined4 *puVar1;
  undefined4 uVar2;

  uVar2 = FUN_000fd410(DAT_000fbad8);
  puVar1 = DAT_000fbad8;
  *DAT_000fbad8 = uVar2;
  uVar2 = FUN_000fa400(puVar1);
  puVar1[0x97] = uVar2;
  FUN_000fd41a(DAT_000fbadc,puVar1,param_1,puVar1 + -0x1c0);
  return;
}



/* ================================================================
 * entry: 0x000fbae0
 * end:   0x000fbaf9
 * size:  26 bytes
 * name:  FUN_000fbae0
 * ================================================================ */

int FUN_000fbae0(undefined4 param_1)

{
  int iVar1;

  iVar1 = FUN_000fbaac(0);
  if (iVar1 == 0) {
    FUN_000fd3fc(param_1,DAT_000fbafc);
  }
  return iVar1;
}



/* ================================================================
 * entry: 0x000fbb00
 * end:   0x000fbb05
 * size:  6 bytes
 * name:  FUN_000fbb00
 * ================================================================ */

undefined4 FUN_000fbb00(void)

{
  return 0x1000;
}



/* ================================================================
 * entry: 0x000fbb08
 * end:   0x000fbb33
 * size:  44 bytes
 * name:  FUN_000fbb08
 * ================================================================ */

void FUN_000fbb08(undefined4 param_1)

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



/* ================================================================
 * entry: 0x000fbb3c
 * end:   0x000fbb65
 * size:  42 bytes
 * name:  FUN_000fbb3c
 * ================================================================ */

void FUN_000fbb3c(undefined4 param_1)

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



/* ================================================================
 * entry: 0x000fbb70
 * end:   0x000fbb75
 * size:  6 bytes
 * name:  FUN_000fbb70
 * ================================================================ */

void FUN_000fbb70(undefined4 param_1,undefined4 param_2)

{
  nrf_dfu_validation_postvalidate_impl(param_1,param_2,1);
  return;
}



/* ================================================================
 * entry: 0x000fbb76
 * end:   0x000fbc1d
 * size:  168 bytes
 * name:  nrf_dfu_validation_boot_validate
 * ================================================================ */

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
      FUN_000fa65c(param_2,param_3,0);
    }
    else {
      if (cVar1 == '\x02') {
        local_1c[0] = 0x20;
        uVar3 = 1;
        FUN_000f846a(auStack_b8,0x7c);
        FUN_000fa6b8();
        iVar2 = FUN_000fb320(auStack_b8,DAT_000fbc24,param_2,param_3,DAT_000fbc20,local_1c);
        if ((iVar2 != 0) || (iVar2 = FUN_000f848e(DAT_000fbc20,param_1 + 1,0x20), iVar2 != 0)) {
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



/* ================================================================
 * entry: 0x000fbc28
 * end:   0x000fbc41
 * size:  26 bytes
 * name:  FUN_000fbc28
 * ================================================================ */

void FUN_000fbc28(void)

{
  undefined1 *puVar1;
  undefined1 uVar2;
  int iVar3;

  puVar1 = DAT_000fbc48;
  if ((*(int *)(DAT_000fbc44 + 0x38) == 0) || (iVar3 = FUN_000fd504(), iVar3 == 0)) {
    uVar2 = 0;
  }
  else {
    uVar2 = 1;
  }
  *puVar1 = uVar2;
  return;
}



/* ================================================================
 * entry: 0x000fbc4c
 * end:   0x000fbc8d
 * size:  66 bytes
 * name:  FUN_000fbc4c
 * ================================================================ */

undefined4 FUN_000fbc4c(undefined4 param_1,int param_2)

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
    FUN_000f841a(*(int *)(DAT_000fbc90 + 0x3c) + DAT_000fbc90 + 0x5c,param_1,param_2);
    iVar2 = DAT_000fbc90;
    *(int *)(iVar1 + 0x3c) = *(int *)(iVar1 + 0x3c) + param_2;
    uVar3 = FUN_000fa65c(param_1,param_2,iVar2 + 0x40);
    *(undefined4 *)(iVar1 + 0x40) = uVar3;
  }
  return uVar4;
}



/* ================================================================
 * entry: 0x000fbc94
 * end:   0x000fbcbd
 * size:  42 bytes
 * name:  FUN_000fbc94
 * ================================================================ */

undefined4 FUN_000fbc94(uint param_1)

{
  undefined4 uVar1;

  uVar1 = 1;
  if (param_1 == 0) {
    uVar1 = 3;
  }
  else if (param_1 < 0x201) {
    *DAT_000fbcc0 = 0;
    FUN_000fb9b0();
    *(uint *)(DAT_000fbcc4 + 0x38) = param_1;
  }
  else {
    uVar1 = 4;
  }
  return uVar1;
}



/* ================================================================
 * entry: 0x000fbcc8
 * end:   0x000fbd51
 * size:  138 bytes
 * name:  FUN_000fbcc8
 * ================================================================ */

int FUN_000fbcc8(undefined4 *param_1,undefined4 *param_2)

{
  char *pcVar1;
  undefined4 uVar2;
  int iVar3;

  pcVar1 = DAT_000fbd58;
  if (*(int *)(DAT_000fbd54 + 0x3c) == *(int *)(DAT_000fbd54 + 0x38)) {
    if (*DAT_000fbd58 == '\0') {
      iVar3 = FUN_000fd504();
      if (iVar3 == 0) {
        iVar3 = 5;
      }
      else {
        iVar3 = nrf_dfu_validation_prevalidate();
        *param_1 = 0;
        *param_2 = 0;
        if ((iVar3 == 1) &&
           (iVar3 = FUN_000fd714(*(undefined4 *)(pcVar1 + 0xc),param_2), iVar3 == 1)) {
          uVar2 = 0;
          if ((*(char *)(*(int *)(pcVar1 + 0xc) + 0x55) == '\0') ||
             (*(char *)(*(int *)(pcVar1 + 0xc) + 0x55) == '\x01')) {
            uVar2 = 1;
          }
          iVar3 = FUN_000fb52c(*param_2,uVar2,0,1);
          if (iVar3 == 0) {
            uVar2 = FUN_000fb4f8();
            *param_1 = uVar2;
            *pcVar1 = '\x01';
            return 1;
          }
          iVar3 = 4;
        }
        FUN_000fb9b0();
      }
    }
    else {
      uVar2 = FUN_000fb4f8();
      *param_1 = uVar2;
      iVar3 = FUN_000fd714(*(undefined4 *)(pcVar1 + 0xc),param_2);
    }
  }
  else {
    iVar3 = 8;
  }
  return iVar3;
}



/* ================================================================
 * entry: 0x000fbd5c
 * end:   0x000fbd61
 * size:  6 bytes
 * name:  FUN_000fbd5c
 * ================================================================ */

undefined1 FUN_000fbd5c(void)

{
  return *DAT_000fbd64;
}



/* ================================================================
 * entry: 0x000fbd68
 * end:   0x000fbda5
 * size:  62 bytes
 * name:  nrf_dfu_validation_prevalidate
 * ================================================================ */

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



/* ================================================================
 * entry: 0x000fbdb0
 * end:   0x000fbe3f
 * size:  144 bytes
 * name:  nrf_dfu_validation_signature_check
 * ================================================================ */

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
  FUN_000f846a(auStack_9c,0x7c);
  FUN_000f846a(auStack_140,0xa4);
  FUN_000fa6b8();
  if (param_2 == 0) {
    uVar1 = 0x13;
  }
  else if (param_1 == 0) {
    iVar2 = FUN_000fb320(auStack_9c,DAT_000fbe44,param_4,param_5,DAT_000fbe40,local_20);
    if ((iVar2 == 0) && (param_3 == 0x40)) {
      FUN_000f841a(DAT_000fbe40 + -0x40,param_2,0x40);
      FUN_000fb442(DAT_000fbe40 + -0x40,0x20);
      iVar2 = FUN_000fb2cc(auStack_140,DAT_000fbe40 + -0x88,DAT_000fbe40,local_20[0],
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



/* ================================================================
 * entry: 0x000fbe48
 * end:   0x000fbecd
 * size:  134 bytes
 * name:  nrf_dfu_ver_validation_check
 * ================================================================ */

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
      iVar2 = FUN_000fd338(param_1);
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



/* ================================================================
 * entry: 0x000fbed4
 * end:   0x000fbeff
 * size:  44 bytes
 * name:  FUN_000fbed4
 * ================================================================ */

void FUN_000fbed4(int *param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  FUN_000f9c94(param_1,param_2,param_3 * *(int *)param_1[1]);
                    /* WARNING: Could not recover jumptable at 0x000fbefe. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (**(code **)(*param_1 + 0x10))(param_1,param_2,param_3,param_4);
  return;
}



/* ================================================================
 * entry: 0x000fbf00
 * end:   0x000fbf07
 * size:  8 bytes
 * name:  FUN_000fbf00
 * ================================================================ */

void FUN_000fbf00(undefined4 *param_1,undefined4 *param_2,undefined4 param_3)

{
  *param_1 = param_2;
                    /* WARNING: Could not recover jumptable at 0x000fbf06. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)*param_2)(param_1,param_3);
  return;
}



/* ================================================================
 * entry: 0x000fbf08
 * end:   0x000fbf4d
 * size:  68 bytes
 * name:  FUN_000fbf08
 * ================================================================ */

undefined4 FUN_000fbf08(int *param_1)

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



/* ================================================================
 * entry: 0x000fbf90
 * end:   0x000fc025
 * size:  150 bytes
 * name:  FUN_000fbf90
 * ================================================================ */

void FUN_000fbf90(int param_1)

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
  FUN_000faa66(iVar3,uVar5);
  FUN_000fd0f0();
LAB_000fc00c:
  if (*(char *)(iVar2 + 0x11) == '\0') {
    FUN_000fd104();
    return;
  }
  FUN_000fc33c();
  return;
}



/* ================================================================
 * entry: 0x000fc030
 * end:   0x000fc06d
 * size:  62 bytes
 * name:  FUN_000fc030
 * ================================================================ */

void FUN_000fc030(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                 undefined4 param_5)

{
  FUN_000f9c88(param_2);
  FUN_000f9c88(param_3);
  FUN_000f9c94(param_1,param_2,param_4);
  (**(code **)(*param_1 + 0xc))(param_1,param_2,param_3,param_4,param_5);
  return;
}



/* ================================================================
 * entry: 0x000fc070
 * end:   0x000fc097
 * size:  40 bytes
 * name:  FUN_000fc070
 * ================================================================ */

void FUN_000fc070(undefined4 param_1)

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



/* ================================================================
 * entry: 0x000fc0a0
 * end:   0x000fc0c5
 * size:  38 bytes
 * name:  FUN_000fc0a0
 * ================================================================ */

void FUN_000fc0a0(undefined4 *param_1,undefined4 param_2)

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



/* ================================================================
 * entry: 0x000fc0d0
 * end:   0x000fc109
 * size:  56 bytes
 * name:  FUN_000fc0d0
 * ================================================================ */

void FUN_000fc0d0(int param_1,int param_2,uint param_3)

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



/* ================================================================
 * entry: 0x000fc114
 * end:   0x000fc11f
 * size:  12 bytes
 * name:  FUN_000fc114
 * ================================================================ */

void FUN_000fc114(int param_1,int param_2)

{
  *(undefined4 *)(param_1 + param_2) = 0;
  return;
}



/* ================================================================
 * entry: 0x000fc120
 * end:   0x000fc12f
 * size:  16 bytes
 * name:  FUN_000fc120
 * ================================================================ */

undefined4 FUN_000fc120(undefined4 *param_1)

{
  if (param_1 != (undefined4 *)0x0) {
    *param_1 = *DAT_000fc130;
    return 0;
  }
  return 0xe;
}



/* ================================================================
 * entry: 0x000fc134
 * end:   0x000fc1cf
 * size:  156 bytes
 * name:  FUN_000fc134
 * ================================================================ */

undefined8 FUN_000fc134(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 local_20;

  iVar1 = FUN_000fc120(param_2);
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



/* ================================================================
 * entry: 0x000fc1d0
 * end:   0x000fc1dd
 * size:  14 bytes
 * name:  FUN_000fc1d0
 * ================================================================ */

void FUN_000fc1d0(int param_1)

{
  software_interrupt(0x60);
  if (param_1 == 0) {
    *DAT_000fc1e0 = 1;
  }
  return;
}



/* ================================================================
 * entry: 0x000fc1e4
 * end:   0x000fc23b
 * size:  88 bytes
 * name:  FUN_000fc1e4
 * ================================================================ */

void FUN_000fc1e4(void)

{
  undefined1 auStack_210 [508];
  undefined4 *local_14;
  undefined2 local_10 [2];

  if (*DAT_000fc23c != '\0') {
    while( true ) {
      local_10[0] = 500;
      software_interrupt(0x61);
      if (&stack0x00000000 != (undefined1 *)0x210) break;
      FUN_000fc394(500,DAT_000fc240);
      while (local_14 != (undefined4 *)0x0) {
        (*(code *)*local_14)(0,local_14[1]);
        FUN_000fc3c2(500);
      }
    }
    if (&stack0x00000000 != (undefined1 *)0x215) {
      FUN_000f9dc4(auStack_210,local_10);
      return;
    }
  }
  return;
}



/* ================================================================
 * entry: 0x000fc244
 * end:   0x000fc293
 * size:  80 bytes
 * name:  FUN_000fc244
 * ================================================================ */

int FUN_000fc244(void)

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
  iVar2 = FUN_000fd3a0();
  if (iVar2 != 0x11) {
    FUN_000fd3d0(2);
    local_18 = local_18 & 0xffffff00;
    iVar2 = FUN_000f9ed4(&local_18);
    software_interrupt(0x11);
    *pcVar1 = '\0';
    FUN_000f9f1c(local_18 & 0xff);
    if (iVar2 != 0) {
      return iVar2;
    }
    pcVar1[2] = '\0';
    FUN_000fd46c();
    FUN_000fd3d0(3);
  }
  return 0;
}



/* ================================================================
 * entry: 0x000fc298
 * end:   0x000fc2fd
 * size:  102 bytes
 * name:  FUN_000fc298
 * ================================================================ */

undefined4 * FUN_000fc298(undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  char *pcVar1;
  undefined4 uVar2;
  int iVar3;
  uint local_18;
  undefined4 local_14;

  pcVar1 = DAT_000fc300;
  if (*DAT_000fc300 != '\0') {
    return (undefined4 *)&NMI;
  }
  DAT_000fc300[2] = '\x01';
  local_18 = param_3;
  local_14 = param_4;
  iVar3 = FUN_000fd3a0(0);
  if (iVar3 != 0x11) {
    FUN_000fd3d0(0);
    local_14 = *DAT_000fc304;
    local_18 = local_18 & 0xffffff00;
    FUN_000f9ed4(&local_18);
    uVar2 = DAT_000fc308;
    software_interrupt(0x10);
    *pcVar1 = &local_14 == (undefined4 *)0x0;
    FUN_000f9f1c(local_18 & 0xff,uVar2);
    if (&local_14 != (undefined4 *)0x0) {
      return &local_14;
    }
    pcVar1[2] = '\0';
    pcVar1[1] = '\0';
    FUN_000fd4ac();
    FUN_000fd3d0(1);
  }
  return (undefined4 *)0x0;
}



/* ================================================================
 * entry: 0x000fc30c
 * end:   0x000fc32b
 * size:  32 bytes
 * name:  FUN_000fc30c
 * ================================================================ */

void FUN_000fc30c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 *param_4)

{
  undefined4 uStack_10;
  undefined4 uStack_c;
  undefined4 *local_8;

  uStack_10 = param_2;
  uStack_c = param_3;
  local_8 = param_4;
  FUN_000fc394(&uStack_10,DAT_000fc32c);
  while (local_8 != (undefined4 *)0x0) {
    (*(code *)*local_8)(local_8[1]);
    FUN_000fc3c2(&uStack_10);
  }
  return;
}



/* ================================================================
 * entry: 0x000fc330
 * end:   0x000fc335
 * size:  6 bytes
 * name:  FUN_000fc330
 * ================================================================ */

undefined1 FUN_000fc330(void)

{
  return *DAT_000fc338;
}



/* ================================================================
 * entry: 0x000fc33c
 * end:   0x000fc351
 * size:  22 bytes
 * name:  FUN_000fc33c
 * ================================================================ */

undefined4 FUN_000fc33c(void)

{
  undefined4 uVar1;

  if (DAT_000fc354[2] == '\0') {
    return 8;
  }
  if (*DAT_000fc354 != '\0') {
    uVar1 = FUN_000fc244();
    return uVar1;
  }
  uVar1 = FUN_000fc298();
  return uVar1;
}



/* ================================================================
 * entry: 0x000fc394
 * end:   0x000fc3c1
 * size:  46 bytes
 * name:  FUN_000fc394
 * ================================================================ */

void FUN_000fc394(int *param_1,int *param_2)

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



/* ================================================================
 * entry: 0x000fc3c2
 * end:   0x000fc3e1
 * size:  32 bytes
 * name:  FUN_000fc3c2
 * ================================================================ */

void FUN_000fc3c2(int *param_1)

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



/* ================================================================
 * entry: 0x000fc3e4
 * end:   0x000fc437
 * size:  84 bytes
 * name:  hardfault_c_handler
 * ================================================================ */

void hardfault_c_handler(undefined4 *param_1)

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



/* ================================================================
 * entry: 0x000fc440
 * end:   0x000fc44b
 * size:  12 bytes
 * name:  FUN_000fc440
 * ================================================================ */

bool FUN_000fc440(void)

{
  return *DAT_000fc44c != 0;
}



/* ================================================================
 * entry: 0x000fc450
 * end:   0x000fc45d
 * size:  14 bytes
 * name:  FUN_000fc450
 * ================================================================ */

void FUN_000fc450(undefined4 param_1)

{
  *DAT_000fc460 = param_1;
  do {
  } while (*DAT_000fc464 == 0);
  return;
}



/* ================================================================
 * entry: 0x000fc468
 * end:   0x000fc4cd
 * size:  102 bytes
 * name:  FUN_000fc468
 * ================================================================ */

void FUN_000fc468(undefined4 param_1,int param_2)

{
  undefined2 uVar1;
  int iVar2;
  char local_28 [4];
  undefined4 local_24;
  uint local_18;
  undefined4 local_14;

  FUN_000f841a(local_28,DAT_000fc4d0,0x18);
  iVar2 = DAT_000fc4d4;
  local_28[0] = *(char *)(param_2 + 0xc);
  local_24 = param_1;
  if (local_28[0] == '\x01') {
    *(undefined2 *)(DAT_000fc4d4 + 6) = *(undefined2 *)(DAT_000fc4d4 + 4);
    local_18 = (uint)*(byte *)(param_2 + 0xd);
    local_14 = *(undefined4 *)(param_2 + 0xe);
    if (local_18 == 1) {
      FUN_000fbb08(DAT_000fc4d8);
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
  FUN_000fb7c0(local_28);
  return;
}



/* ================================================================
 * entry: 0x000fc4dc
 * end:   0x000fc547
 * size:  108 bytes
 * name:  nrf_dfu_data_object_create
 * ================================================================ */

void nrf_dfu_data_object_create(int param_1,int param_2)

{
  int iVar1;
  undefined1 uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;

  iVar3 = FUN_000fbd5c();
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
        iVar4 = FUN_000fb6cc(iVar3 + *(int *)(iVar1 + 4),*(int *)(param_1 + 0x14) + 0xfffU >> 0xc,0)
        ;
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



/* ================================================================
 * entry: 0x000fc550
 * end:   0x000fc5b3
 * size:  100 bytes
 * name:  FUN_000fc550
 * ================================================================ */

void FUN_000fc550(int param_1)

{
  int iVar1;
  undefined1 uStack_20;
  undefined1 local_1f;

  iVar1 = FUN_000fbf08(0);
  if (iVar1 == 0) {
    FUN_000f841a(&uStack_20,DAT_000fc5b8,0x18);
    if (*(int *)(DAT_000fc5bc + 0x50) == *(int *)(DAT_000fc5c0 + 8)) {
      local_1f = FUN_000fbb70(*(undefined4 *)(DAT_000fc5c0 + 4));
      local_1f = FUN_000faaba();
      (**(code **)(param_1 + 8))(&uStack_20,*(undefined4 *)(param_1 + 4));
      FUN_000fbae0(DAT_000fc5c4);
    }
    else {
      local_1f = 1;
      (**(code **)(param_1 + 8))(&uStack_20,*(undefined4 *)(param_1 + 4));
    }
  }
  else {
    FUN_000f9dc8(param_1,0x18,DAT_000fc5b4);
  }
  return;
}



/* ================================================================
 * entry: 0x000fc5c8
 * end:   0x000fc63d
 * size:  118 bytes
 * name:  nrf_dfu_data_object_write
 * ================================================================ */

void nrf_dfu_data_object_write(int param_1,int param_2)

{
  ushort uVar1;
  int iVar2;
  undefined1 uVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;

  iVar4 = FUN_000fbd5c();
  iVar2 = DAT_000fc640;
  if (iVar4 == 0) {
    uVar3 = 8;
  }
  else {
    if ((*(int *)(DAT_000fc640 + 0x50) - *(int *)(DAT_000fc640 + 0x54)) +
        (uint)*(ushort *)(param_1 + 0x14) <= *(uint *)(DAT_000fc640 + 0x44)) {
      iVar4 = *(int *)(DAT_000fc640 + 0x30);
      iVar6 = *(int *)(DAT_000fc644 + 4);
      uVar5 = FUN_000fa65c(*(undefined4 *)(param_1 + 0x10),(uint)*(ushort *)(param_1 + 0x14),
                           DAT_000fc640 + 0x48);
      iVar4 = FUN_000fb6f8(iVar4 + iVar6,*(undefined4 *)(param_1 + 0x10),
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



/* ================================================================
 * entry: 0x000fc654
 * end:   0x000fc679
 * size:  38 bytes
 * name:  FUN_000fc654
 * ================================================================ */

void FUN_000fc654(void)

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



/* ================================================================
 * entry: 0x000fc690
 * end:   0x000fc70f
 * size:  128 bytes
 * name:  FUN_000fc690
 * ================================================================ */

undefined8 FUN_000fc690(int param_1,int param_2)

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
       (iVar2 = FUN_000fa3e8(auStack_28,*(undefined2 *)(param_1 + 0x10),&local_14), iVar2 == 0)) {
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



/* ================================================================
 * entry: 0x000fc7a4
 * end:   0x000fc7e3
 * size:  64 bytes
 * name:  FUN_000fc7a4
 * ================================================================ */

void FUN_000fc7a4(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

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
  iVar1 = FUN_000fcdf0(param_1,&iStack_28);
  if ((iVar1 != 0) && (*(int *)(param_2 + 0xc) != 0)) {
    if ((*(byte *)(param_2 + 2) & 0x3f) >> 4 == 2) {
      FUN_000fc8ec(&iStack_28,uVar2,param_3);
    }
    else {
      FUN_000fc990();
    }
    *(int *)(param_1 + 4) = local_24;
  }
  return;
}



/* ================================================================
 * entry: 0x000fc7e4
 * end:   0x000fc83b
 * size:  88 bytes
 * name:  FUN_000fc7e4
 * ================================================================ */

undefined4 FUN_000fc7e4(undefined4 param_1,int param_2,short *param_3,int param_4)

{
  short sVar1;
  int iVar2;
  short *psVar3;
  short *local_18;
  int iStack_14;

  local_18 = param_3;
  iStack_14 = param_4;
  iVar2 = FUN_000fcb1a(param_1,&local_18);
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



/* ================================================================
 * entry: 0x000fc83c
 * end:   0x000fc893
 * size:  88 bytes
 * name:  FUN_000fc83c
 * ================================================================ */

undefined4 FUN_000fc83c(undefined4 param_1,int param_2,undefined4 *param_3,int param_4)

{
  short sVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 *local_18;
  int iStack_14;

  local_18 = param_3;
  iStack_14 = param_4;
  iVar2 = FUN_000fcb96(param_1,&local_18);
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



/* ================================================================
 * entry: 0x000fc894
 * end:   0x000fc8eb
 * size:  88 bytes
 * name:  FUN_000fc894
 * ================================================================ */

undefined4 FUN_000fc894(undefined4 param_1,int param_2,short *param_3,int param_4)

{
  short sVar1;
  int iVar2;
  short *psVar3;
  short *local_18;
  int iStack_14;

  local_18 = param_3;
  iStack_14 = param_4;
  iVar2 = FUN_000fcb96(param_1,&local_18);
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



/* ================================================================
 * entry: 0x000fc8ec
 * end:   0x000fc909
 * size:  30 bytes
 * name:  FUN_000fc8ec
 * ================================================================ */

void FUN_000fc8ec(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  FUN_000fce26(param_2,param_3);
  FUN_000fc990(param_1,param_2,param_3);
  return;
}



/* ================================================================
 * entry: 0x000fc90a
 * end:   0x000fc933
 * size:  42 bytes
 * name:  FUN_000fc90a
 * ================================================================ */

bool FUN_000fc90a(undefined4 param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;

  local_10 = param_4;
  iVar1 = FUN_000fce4c(param_1,&local_10,4);
  if (iVar1 != 0) {
    *param_2 = local_10;
  }
  return iVar1 != 0;
}



/* ================================================================
 * entry: 0x000fc934
 * end:   0x000fc98f
 * size:  92 bytes
 * name:  FUN_000fc934
 * ================================================================ */

bool FUN_000fc934(undefined4 param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 local_c;

  local_10 = param_3;
  local_c = param_4;
  iVar1 = FUN_000fce4c(param_1,&local_10,8);
  if (iVar1 != 0) {
    *param_2 = local_10;
    param_2[1] = local_c;
  }
  return iVar1 != 0;
}



/* ================================================================
 * entry: 0x000fc990
 * end:   0x000fcb19
 * size:  392 bytes
 * name:  FUN_000fc990
 * ================================================================ */

undefined4 FUN_000fc990(int param_1)

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
  FUN_000fcc68(auStack_94);
LAB_000fcabc:
  do {
    if (*(int *)(param_1 + 8) == 0) {
LAB_000fcac4:
      do {
        uVar7 = local_8c;
        uVar1 = local_90[1];
        iVar4 = FUN_000fccb8(auStack_94);
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
    iVar4 = FUN_000fcb54(param_1,local_6c,&local_98,local_50);
    if (iVar4 == 0) {
      if (local_50[0] == '\0') {
        return 0;
      }
      goto LAB_000fcac4;
    }
    iVar4 = FUN_000fcc8a(auStack_94,local_98);
    puVar2 = local_90;
    if (iVar4 == 0) {
      if (uVar7 <= local_98) {
        do {
          if ((local_90[1] & 0xf) == 8) {
            uVar7 = (uint)*local_90;
            goto LAB_000fca0a;
          }
          FUN_000fccb8(auStack_94);
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
                FUN_000fad98(auStack_3c,piVar6);
                *(undefined1 *)(piVar6 + 3) = 1;
                iVar3 = FUN_000fa776(local_5c[2],uVar5,auStack_3c);
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
      iVar4 = FUN_000fcec4(param_1,local_6c[0]);
    }
    else {
      if (((local_90[1] & 0x30) == 0) && (local_8c < 0x40)) {
        local_5c[local_8c >> 5] = local_5c[local_8c >> 5] | 1 << (local_8c & 0x1f);
      }
      if (*(code **)(param_1 + 0xc) != (code *)0x0) {
        (**(code **)(param_1 + 0xc))(param_1,local_98,local_6c[0],auStack_94);
      }
      iVar4 = FUN_000fa776(param_1,local_6c[0],auStack_94);
    }
    if (iVar4 == 0) {
      return 0;
    }
  } while( true );
}



/* ================================================================
 * entry: 0x000fcb1a
 * end:   0x000fcb53
 * size:  58 bytes
 * name:  FUN_000fcb1a
 * ================================================================ */

undefined4 FUN_000fcb1a(undefined4 param_1,uint *param_2,uint param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint local_10;
  uint uStack_c;

  local_10 = param_3;
  uStack_c = param_4;
  iVar1 = FUN_000fcb96(param_1,&local_10);
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



/* ================================================================
 * entry: 0x000fcb54
 * end:   0x000fcb95
 * size:  66 bytes
 * name:  FUN_000fcb54
 * ================================================================ */

undefined4 FUN_000fcb54(int param_1,byte *param_2,uint *param_3,undefined1 *param_4)

{
  int iVar1;
  undefined1 *local_18;

  *param_4 = 0;
  *param_2 = 0;
  *param_3 = 0;
  local_18 = param_4;
  iVar1 = FUN_000fcbe0(param_1,&local_18);
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



/* ================================================================
 * entry: 0x000fcb96
 * end:   0x000fcbdf
 * size:  74 bytes
 * name:  FUN_000fcb96
 * ================================================================ */

undefined4 FUN_000fcb96(undefined4 param_1,uint *param_2,undefined4 param_3,uint param_4)

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
    iVar2 = FUN_000fcea4(param_1,&local_20);
    uVar1 = local_20;
    if (iVar2 == 0) {
      return 0;
    }
    uVar6 = FUN_000f83fc(local_20 & 0x7f,0,uVar5);
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



/* ================================================================
 * entry: 0x000fcbe0
 * end:   0x000fcc2b
 * size:  76 bytes
 * name:  FUN_000fcbe0
 * ================================================================ */

undefined4 FUN_000fcbe0(undefined4 param_1,uint *param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint local_18;

  local_18 = param_4;
  iVar1 = FUN_000fcea4(param_1,&local_18);
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
      iVar1 = FUN_000fcea4(param_1,&local_18);
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



/* ================================================================
 * entry: 0x000fcc2c
 * end:   0x000fcc5f
 * size:  52 bytes
 * name:  nrf_dfu_init_command_decode_callback
 * ================================================================ */

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



/* ================================================================
 * entry: 0x000fcc68
 * end:   0x000fcc89
 * size:  34 bytes
 * name:  FUN_000fcc68
 * ================================================================ */

bool FUN_000fcc68(undefined4 *param_1,short *param_2,int param_3)

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



/* ================================================================
 * entry: 0x000fcc8a
 * end:   0x000fccb7
 * size:  46 bytes
 * name:  FUN_000fcc8a
 * ================================================================ */

undefined4 FUN_000fcc8a(int param_1,uint param_2)

{
  int iVar1;

  iVar1 = *(int *)(param_1 + 4);
  while( true ) {
    if ((**(ushort **)(param_1 + 4) == param_2) && (((*(ushort **)(param_1 + 4))[1] & 0xf) != 8))
    break;
    FUN_000fccb8(param_1);
    if (*(int *)(param_1 + 4) == iVar1) {
      return 0;
    }
  }
  return 1;
}



/* ================================================================
 * entry: 0x000fccb8
 * end:   0x000fcd35
 * size:  126 bytes
 * name:  FUN_000fccb8
 * ================================================================ */

undefined4 FUN_000fccb8(undefined4 *param_1)

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
    FUN_000fcc68(param_1,*param_1,param_1[3]);
  }
  return 0;
}



/* ================================================================
 * entry: 0x000fcd36
 * end:   0x000fcdd9
 * size:  164 bytes
 * name:  FUN_000fcd36
 * ================================================================ */

void FUN_000fcd36(int param_1)

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
      FUN_000fad98(auStack_28,iVar3);
      FUN_000fcd36(auStack_28);
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
    FUN_000fce26(*(undefined4 *)(iVar3 + 0xc),*(undefined4 *)(param_1 + 0x10));
    return;
  }
  if (*(int *)(iVar3 + 0xc) != 0) {
    FUN_000f841a(*(undefined4 *)(param_1 + 0x10),*(int *)(iVar3 + 0xc),*(undefined2 *)(iVar3 + 8));
    return;
  }
  FUN_000f846a(*(undefined4 *)(param_1 + 0x10),*(undefined2 *)(iVar3 + 8));
  return;
}



/* ================================================================
 * entry: 0x000fcddc
 * end:   0x000fcde9
 * size:  14 bytes
 * name:  FUN_000fcddc
 * ================================================================ */

void FUN_000fcddc(undefined4 *param_1,undefined4 param_2,undefined4 param_3)

{
  *param_1 = DAT_000fcdec;
  param_1[1] = param_2;
  param_1[2] = param_3;
  param_1[3] = 0;
  return;
}



/* ================================================================
 * entry: 0x000fcdf0
 * end:   0x000fce25
 * size:  54 bytes
 * name:  FUN_000fcdf0
 * ================================================================ */

undefined4 FUN_000fcdf0(undefined4 *param_1,undefined4 *param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  uint local_10;

  local_10 = param_4;
  iVar1 = FUN_000fcbe0(param_1,&local_10);
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



/* ================================================================
 * entry: 0x000fce26
 * end:   0x000fce4b
 * size:  38 bytes
 * name:  FUN_000fce26
 * ================================================================ */

void FUN_000fce26(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined1 auStack_20 [28];

  iVar1 = FUN_000fcc68(auStack_20,param_1,param_2);
  while (iVar1 != 0) {
    FUN_000fcd36(auStack_20);
    iVar1 = FUN_000fccb8(auStack_20);
  }
  return;
}



/* ================================================================
 * entry: 0x000fce4c
 * end:   0x000fce9f
 * size:  84 bytes
 * name:  FUN_000fce4c
 * ================================================================ */

undefined4 FUN_000fce4c(int *param_1,int param_2,uint param_3,undefined4 param_4)

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
      iVar2 = FUN_000fce4c(param_1,&piStack_20,0x10);
      if (iVar2 == 0) {
        return 0;
      }
    }
    uVar1 = FUN_000fce4c(param_1,&piStack_20,param_3);
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



/* ================================================================
 * entry: 0x000fcea4
 * end:   0x000fcec3
 * size:  32 bytes
 * name:  FUN_000fcea4
 * ================================================================ */

undefined4 FUN_000fcea4(undefined4 *param_1,undefined4 param_2)

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



/* ================================================================
 * entry: 0x000fcec4
 * end:   0x000fcf1d
 * size:  90 bytes
 * name:  FUN_000fcec4
 * ================================================================ */

undefined4 FUN_000fcec4(undefined4 param_1,int param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  undefined4 uVar2;
  int local_10;

  local_10 = param_4;
  if (param_2 == 0) {
    do {
      iVar1 = FUN_000fce4c(param_1,&local_10,1);
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
      iVar1 = FUN_000fcbe0(param_1,&local_10);
      if (iVar1 == 0) {
        return 0;
      }
      uVar2 = FUN_000fce4c(param_1,0,local_10);
      return uVar2;
    }
    if (param_2 != 5) {
      return 0;
    }
    uVar2 = 4;
  }
  uVar2 = FUN_000fce4c(param_1,0,uVar2,param_4);
  return uVar2;
}



/* ================================================================
 * entry: 0x000fcf20
 * end:   0x000fcfe3
 * size:  196 bytes
 * name:  nrf_dfu_validation_postvalidate_impl
 * ================================================================ */

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
  iVar2 = FUN_000faafc(iVar5,param_1,param_2);
  iVar1 = DAT_000fcfe8;
  if (iVar2 == 0) {
    iVar6 = 0x17;
LAB_000fcfa6:
    if (param_3 == 0) {
      if (iVar6 != 1) {
        FUN_000fb9b0();
        return iVar6;
      }
LAB_000fcfce:
      *(undefined4 *)(iVar1 + 0x14) = 1;
      return 1;
    }
    if (iVar6 != 1) {
      FUN_000fb518(DAT_000fcfe8 + 0x24);
      goto LAB_000fcfb4;
    }
  }
  else {
    uVar3 = (uint)*(byte *)(iVar5 + 0x55);
    if (uVar3 != 0) {
      iVar2 = FUN_000fcff0(iVar5,uVar3 & 1,(uVar3 & 3) >> 1,param_1,param_2,param_3);
      if (iVar2 == 0) goto LAB_000fcfa4;
      goto LAB_000fcfa6;
    }
    iVar2 = FUN_000fa40c(auStack_68,iVar5,0,param_1,param_2,1);
    if (iVar2 == 0) {
LAB_000fcfa4:
      iVar6 = 5;
      goto LAB_000fcfa6;
    }
    if (param_3 == 0) goto LAB_000fcfce;
    FUN_000f841a(DAT_000fcfec,auStack_68,0x41);
    *(undefined4 *)(iVar1 + 0x20) = 0;
    *(undefined4 *)(iVar1 + 0x2c) = 1;
    if ((*(char *)(iVar5 + 0x92) == '\0') || (*(char *)(iVar5 + 0x93) == '\0')) {
      *(undefined4 *)(iVar1 + 8) = *(undefined4 *)(iVar5 + 4);
    }
  }
  uVar4 = FUN_000fa65c(param_1,param_2,0);
  *(undefined4 *)(iVar1 + 0x24) = param_2;
  *(undefined4 *)(iVar1 + 0x28) = uVar4;
LAB_000fcfb4:
  FUN_000fb9b0();
  *(undefined4 *)(iVar1 + 0x48) = param_1;
  return iVar6;
}



/* ================================================================
 * entry: 0x000fcff0
 * end:   0x000fd0e3
 * size:  244 bytes
 * name:  FUN_000fcff0
 * ================================================================ */

undefined4 FUN_000fcff0(int param_1,int param_2,int param_3,int param_4,int param_5,int param_6)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_a8 [68];
  undefined1 auStack_64 [68];

  FUN_000f846a(auStack_a8,0x44);
  FUN_000f846a(auStack_64,0x44);
  iVar1 = param_4;
  if (param_2 != 0) {
    if (((*(int *)(param_4 + 0x2004) != DAT_000fd0e4) ||
        (*(uint *)(param_4 + 0x2008) <
         (*(int *)(param_1 + 0x58) - (*(int *)(param_1 + 0x58) - 1U & 0xfff)) + 0x1fff)) ||
       ((iVar1 = FUN_000fad38(param_4), iVar1 != 0 && (param_3 == 0)))) {
      return 0;
    }
    iVar1 = FUN_000fa40c(auStack_a8,param_1,0,param_4,*(undefined4 *)(param_1 + 0x58),1);
    if (iVar1 == 0) {
      return 0;
    }
    iVar1 = param_4 + *(int *)(param_1 + 0x58);
    param_5 = param_5 - *(int *)(param_1 + 0x58);
  }
  if ((param_3 != 0) &&
     (iVar1 = FUN_000fa40c(auStack_64,param_1,param_2,iVar1,param_5,0), iVar1 == 0)) {
    return 0;
  }
  iVar1 = DAT_000fd0e8;
  if (param_6 != 0) {
    if (param_2 == 0) {
      *(undefined4 *)(DAT_000fd0e8 + 0x2c) = 0xaa;
    }
    else {
      iVar2 = FUN_000fad38(param_4);
      if (iVar2 != 0) {
        FUN_000fb518(iVar1 + 0x18);
      }
      FUN_000f841a(DAT_000fd0ec,auStack_a8,0x41);
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
       ((FUN_000f841a(DAT_000fd0ec + 0x82,auStack_64,0x41), *(char *)(param_1 + 0x92) == '\0' ||
        (*(char *)(param_1 + 0x93) == '\0')))) {
      *(undefined4 *)(iVar1 + 0xc) = *(undefined4 *)(param_1 + 4);
    }
  }
  return 1;
}



/* ================================================================
 * entry: 0x000fd0f0
 * end:   0x000fd0f9
 * size:  10 bytes
 * name:  FUN_000fd0f0
 * ================================================================ */

void FUN_000fd0f0(void)

{
  FUN_000fae44(*DAT_000fd100,DAT_000fd0fc);
  return;
}



/* ================================================================
 * entry: 0x000fd104
 * end:   0x000fd193
 * size:  144 bytes
 * name:  FUN_000fd104
 * ================================================================ */

void FUN_000fd104(void)

{
  int iVar1;
  int *piVar2;
  int iVar3;

  piVar2 = DAT_000fd198;
  iVar1 = DAT_000fd194;
  if (*(char *)(DAT_000fd194 + 8) == '\0') {
    iVar3 = FUN_000fae5a(*DAT_000fd19c,DAT_000fd198 + 1);
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
      FUN_000fbf90(2,0);
      return;
    }
  }
  else {
    if (iVar3 != 0x11) {
LAB_000fd16a:
      FUN_000faa66(*piVar2,3);
      *(undefined1 *)(iVar1 + 8) = 0;
      *(undefined4 *)(iVar1 + 4) = 0;
      FUN_000fd0f0();
      return;
    }
    *(undefined1 *)(iVar1 + 8) = 1;
  }
  return;
}



/* ================================================================
 * entry: 0x000fd1a0
 * end:   0x000fd1bd
 * size:  30 bytes
 * name:  FUN_000fd1a0
 * ================================================================ */

void FUN_000fd1a0(void)

{
  int iVar1;
  int iVar2;

  iVar1 = DAT_000fd1c0;
  iVar2 = FUN_000fae8c(DAT_000fd1c0 + 4);
  if ((iVar2 == 0) && (*(char *)(iVar1 + 0x11) == '\0')) {
    FUN_000fd104();
    return;
  }
  return;
}



/* ================================================================
 * entry: 0x000fd1c4
 * end:   0x000fd1d1
 * size:  14 bytes
 * name:  FUN_000fd1c4
 * ================================================================ */

undefined4 FUN_000fd1c4(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  FUN_000f841a(param_3,param_2,param_4);
  return 0;
}



/* ================================================================
 * entry: 0x000fd1d2
 * end:   0x000fd1df
 * size:  14 bytes
 * name:  FUN_000fd1d2
 * ================================================================ */

undefined4 FUN_000fd1d2(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  FUN_000f841a(param_3,param_2,param_4);
  return 0;
}



/* ================================================================
 * entry: 0x000fd1e0
 * end:   0x000fd241
 * size:  98 bytes
 * name:  FUN_000fd1e0
 * ================================================================ */

undefined4 FUN_000fd1e0(undefined4 param_1,int param_2,byte *param_3,uint *param_4)

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
      iVar2 = FUN_000fce4c(param_1,param_3,1);
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
  uVar3 = FUN_000fce4c(param_1,param_3,uVar3);
  return uVar3;
}



/* ================================================================
 * entry: 0x000fd242
 * end:   0x000fd261
 * size:  32 bytes
 * name:  FUN_000fd242
 * ================================================================ */

int FUN_000fd242(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;

  iVar1 = FUN_000fd6d0(param_2,param_1 + 3);
  iVar2 = FUN_000fd6d0(param_3,param_1 + iVar1 + 3);
  return iVar2 + iVar1;
}



/* ================================================================
 * entry: 0x000fd264
 * end:   0x000fd28b
 * size:  40 bytes
 * name:  FUN_000fd264
 * ================================================================ */

undefined8 FUN_000fd264(void)

{
  undefined1 local_20 [28];

  software_interrupt(0xae);
  return CONCAT44(local_20,(uint)*(ushort *)(DAT_000fd294 + 2));
}



/* ================================================================
 * entry: 0x000fd2a0
 * end:   0x000fd2e9
 * size:  74 bytes
 * name:  nrf_bootloader_sd_activate
 * ================================================================ */

int nrf_bootloader_sd_activate(void)

{
  int iVar1;
  int iVar2;
  int iVar3;

  iVar1 = FUN_000fbb00();
  iVar3 = *(int *)(DAT_000fd2ec + 0x30);
  iVar2 = *(int *)(DAT_000fd2ec + 0x34) - iVar3;
  if (*(int *)(*(int *)(DAT_000fd2ec + 0x48) + 0x2004) != DAT_000fd2f0) {
    return 3;
  }
  if (iVar3 == *(int *)(DAT_000fd2ec + 0x34)) {
    iVar1 = 0;
  }
  else {
    iVar1 = FUN_000fac3c(iVar1 + iVar3,*(int *)(DAT_000fd2ec + 0x48) + iVar3,
                         (iVar2 - (iVar2 - 1U & 0xfff)) + 0xfff,8);
    if (iVar1 == 0) {
      iVar1 = FUN_000fbae0();
      return iVar1;
    }
  }
  return iVar1;
}



/* ================================================================
 * entry: 0x000fd2f4
 * end:   0x000fd333
 * size:  64 bytes
 * name:  FUN_000fd2f4
 * ================================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_000fd2f4(int param_1,uint param_2,int param_3)

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



/* ================================================================
 * entry: 0x000fd338
 * end:   0x000fd39b
 * size:  100 bytes
 * name:  FUN_000fd338
 * ================================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_000fd338(char *param_1)

{
  ushort uVar1;
  char cVar2;
  undefined4 uVar3;

  uVar1 = *(ushort *)(param_1 + 0x10);
  if (_DAT_00003004 == DAT_000fd39c) {
    if (uVar1 != 0) {
      cVar2 = param_1[0x55];
      if (*(int *)(param_1 + 0x14) != 0) {
        uVar3 = FUN_000fd2f4(param_1 + 0x14,uVar1 & 0xff,cVar2 == '\x04');
        return uVar3;
      }
      if (cVar2 == '\0') {
        if (uVar1 < 2) {
          return 1;
        }
        FUN_000fd2f4(param_1 + 0x14,uVar1 & 0xff,0);
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



/* ================================================================
 * entry: 0x000fd3a0
 * end:   0x000fd3cb
 * size:  42 bytes
 * name:  FUN_000fd3a0
 * ================================================================ */

longlong FUN_000fd3a0(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 *param_4)

{
  int iVar1;
  uint uStack_18;
  undefined4 uStack_14;
  undefined4 *local_10;

  uStack_18 = param_2;
  uStack_14 = param_3;
  local_10 = param_4;
  FUN_000fc394(&uStack_18,DAT_000fd3cc);
  while( true ) {
    if (local_10 == (undefined4 *)0x0) {
      return (ulonglong)uStack_18 << 0x20;
    }
    iVar1 = (*(code *)*local_10)(param_1,local_10[1]);
    if (iVar1 == 0) break;
    FUN_000fc3c2(&uStack_18);
  }
  return CONCAT44(uStack_18,0x11);
}



/* ================================================================
 * entry: 0x000fd3d0
 * end:   0x000fd3f5
 * size:  36 bytes
 * name:  FUN_000fd3d0
 * ================================================================ */

void FUN_000fd3d0(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 *param_4)

{
  undefined4 uStack_18;
  undefined4 uStack_14;
  undefined4 *local_10;

  uStack_18 = param_2;
  uStack_14 = param_3;
  local_10 = param_4;
  FUN_000fc394(&uStack_18,DAT_000fd3f8);
  while (local_10 != (undefined4 *)0x0) {
    (*(code *)*local_10)(param_1,local_10[1]);
    FUN_000fc3c2(&uStack_18);
  }
  return;
}



/* ================================================================
 * entry: 0x000fd3fc
 * end:   0x000fd407
 * size:  12 bytes
 * name:  FUN_000fd3fc
 * ================================================================ */

void FUN_000fd3fc(undefined4 param_1,undefined4 param_2)

{
  FUN_000fd41a(*DAT_000fd40c,param_2,param_1,DAT_000fd408);
  return;
}



/* ================================================================
 * entry: 0x000fd410
 * end:   0x000fd419
 * size:  10 bytes
 * name:  FUN_000fd410
 * ================================================================ */

void FUN_000fd410(int param_1)

{
  FUN_000fa65c(param_1 + 4,0x58,0);
  return;
}



/* ================================================================
 * entry: 0x000fd41a
 * end:   0x000fd469
 * size:  80 bytes
 * name:  FUN_000fd41a
 * ================================================================ */

undefined4 FUN_000fd41a(undefined4 param_1,undefined4 param_2,code *param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;

  iVar1 = FUN_000f848e(param_1,param_2,0x380);
  if (iVar1 == 0) {
    if (param_3 != (code *)0x0) {
      (*param_3)(0);
    }
    uVar2 = 0;
  }
  else {
    iVar1 = FUN_000fb6cc(param_1,1,0);
    if (iVar1 == 0) {
      FUN_000f841a(param_4,param_2,0x380);
      iVar1 = FUN_000fb6f8(param_1,param_4,0x380,param_3);
      if (iVar1 == 0) {
        return 0;
      }
    }
    uVar2 = 3;
  }
  return uVar2;
}



/* ================================================================
 * entry: 0x000fd46c
 * end:   0x000fd4a7
 * size:  60 bytes
 * name:  FUN_000fd46c
 * ================================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000fd46c(void)

{
  int iVar1;

  iVar1 = FUN_000f9c64(0x16);
  if (iVar1 == 0) {
    FUN_000f9dc4(0x2001);
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



/* ================================================================
 * entry: 0x000fd4ac
 * end:   0x000fd4fb
 * size:  80 bytes
 * name:  FUN_000fd4ac
 * ================================================================ */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000fd4ac(void)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;

  iVar1 = FUN_000f9c64(0x16);
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
  FUN_000f9dc4(uVar3);
  return;
}



/* ================================================================
 * entry: 0x000fd504
 * end:   0x000fd5af
 * size:  172 bytes
 * name:  FUN_000fd504
 * ================================================================ */

undefined4 FUN_000fd504(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

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
  FUN_000fcddc(&local_20,DAT_000fd5b0 + 0x5c,*(undefined4 *)(DAT_000fd5b0 + 0x38));
  iVar1 = DAT_000fd5bc;
  iVar3 = DAT_000fd5b4;
  *(undefined4 *)(DAT_000fd5b4 + 0x1c) = local_20;
  *(undefined4 *)(iVar3 + 0x20) = uStack_1c;
  *(undefined4 *)(iVar3 + 0x24) = uStack_18;
  *(undefined4 *)(iVar3 + 0x28) = DAT_000fd5b8;
  *(undefined1 *)(iVar1 + 2) = 0;
  *(undefined4 *)(iVar1 + 4) = 0;
  *(undefined4 *)(iVar1 + 8) = 0;
  FUN_000f846a(iVar3 + -0x300,0x31c);
  iVar2 = FUN_000fc8ec(iVar3 + 0x1c,DAT_000fd5c0);
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
      FUN_000fcddc(&local_20,*(undefined4 *)(iVar1 + 4),*(undefined4 *)(iVar1 + 8));
      *(undefined4 *)(iVar3 + 0x1c) = local_20;
      *(undefined4 *)(iVar3 + 0x20) = uStack_1c;
      *(undefined4 *)(iVar3 + 0x24) = uStack_18;
      *(undefined4 *)(iVar3 + 0x28) = uStack_14;
      FUN_000f846a(iVar2,0x164);
      iVar3 = FUN_000fc8ec((undefined4 *)(iVar3 + 0x1c),DAT_000fd5c4,iVar2);
      if (iVar3 == 0) {
        return 0;
      }
    }
    uVar4 = 1;
    *(int *)(iVar1 + 0xc) = iVar2;
  }
  return uVar4;
}



/* ================================================================
 * entry: 0x000fd5cc
 * end:   0x000fd621
 * size:  86 bytes
 * name:  FUN_000fd5cc
 * ================================================================ */

void FUN_000fd5cc(int param_1,uint param_2)

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
  FUN_000fc114(iVar1,uVar4 * 4 + 0x140);
  *(int *)(iVar1 + 0x304) = 0x10000 << uVar4;
  return;
}



/* ================================================================
 * entry: 0x000fd62c
 * end:   0x000fd68b
 * size:  96 bytes
 * name:  FUN_000fd62c
 * ================================================================ */

void FUN_000fd62c(void)

{
  char *pcVar1;
  undefined4 *puVar2;

  pcVar1 = DAT_000fd68c;
  if (*DAT_000fd68c == '\0') {
    if (-1 < *DAT_000fd690 << 0xf) {
      *DAT_000fd694 = 1;
    }
    puVar2 = DAT_000fd698;
    FUN_000fc114(DAT_000fd698,0x100);
    FUN_000fc114(puVar2,0x140);
    FUN_000fc114(puVar2,0x144);
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



/* ================================================================
 * entry: 0x000fd6a0
 * end:   0x000fd6b9
 * size:  26 bytes
 * name:  FUN_000fd6a0
 * ================================================================ */

void FUN_000fd6a0(undefined4 *param_1,undefined4 param_2,undefined4 param_3)

{
  FUN_000fd62c();
  *param_1 = param_3;
  FUN_000fd5cc(param_1,param_2);
  return;
}



/* ================================================================
 * entry: 0x000fd6bc
 * end:   0x000fd6cb
 * size:  16 bytes
 * name:  FUN_000fd6bc
 * ================================================================ */

void FUN_000fd6bc(int param_1)

{
  *(int *)(DAT_000fd6cc + 0x308) = 0x10000 << *(sbyte *)(param_1 + 0xc);
  return;
}



/* ================================================================
 * entry: 0x000fd6d0
 * end:   0x000fd6e1
 * size:  18 bytes
 * name:  FUN_000fd6d0
 * ================================================================ */

undefined4 FUN_000fd6d0(undefined4 param_1,undefined1 *param_2)

{
  *param_2 = (char)param_1;
  param_2[1] = (char)((uint)param_1 >> 8);
  param_2[2] = (char)((uint)param_1 >> 0x10);
  param_2[3] = (char)((uint)param_1 >> 0x18);
  return 4;
}



/* ================================================================
 * entry: 0x000fd714
 * end:   0x000fd767
 * size:  84 bytes
 * name:  FUN_000fd714
 * ================================================================ */

undefined4 FUN_000fd714(int param_1,int *param_2)

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



/* ================================================================
 * entry: 0x000fd76c
 * end:   0x000fd785
 * size:  26 bytes
 * name:  FUN_000fd76c
 * ================================================================ */

undefined4 FUN_000fd76c(int *param_1)

{
  if (param_1 == (int *)0x0) {
    return 0x8501;
  }
  if (*param_1 != DAT_000fd788) {
    return 0x8502;
  }
  return 0;
}



/* ================================================================
 * entry: 0x000fd78c
 * end:   0x000fd7bb
 * size:  48 bytes
 * name:  FUN_000fd78c
 * ================================================================ */

void FUN_000fd78c(void)

{
  uint *puVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;

  iVar4 = FUN_000fc440();
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



/* ================================================================
 * entry: 0x000fd7d4
 * end:   0x000fd813
 * size:  64 bytes
 * name:  FUN_000fd7d4
 * ================================================================ */

undefined4
FUN_000fd7d4(undefined4 param_1,undefined4 param_2,undefined4 param_3,uint param_4,
            undefined4 param_5)

{
  int iVar1;
  undefined4 uVar2;

  iVar1 = FUN_000fae8c(DAT_000fd814);
  if (iVar1 == 0) {
    FUN_000fc0d0(param_2,param_3,param_4 >> 2);
    FUN_000fae86(DAT_000fd814);
    FUN_000faa30(param_1,1,param_3,param_2,param_4,param_5);
    uVar2 = 0;
  }
  else {
    uVar2 = 0x11;
  }
  return uVar2;
}



/* ================================================================
 * entry: 0x000fd818
 * end:   0x000fd861
 * size:  74 bytes
 * name:  FUN_000fd818
 * ================================================================ */

undefined4
FUN_000fd818(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
            undefined4 param_5)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  undefined4 uStack_28;

  puVar1 = DAT_000fd864;
  uStack_28 = param_4;
  puVar2 = (undefined4 *)FUN_000fae2e(*DAT_000fd864,&uStack_28);
  if (puVar2 == (undefined4 *)0x0) {
    uVar3 = 4;
  }
  else {
    FUN_000f846a(puVar2,0x1c);
    *(undefined1 *)(puVar2 + 1) = 0;
    *puVar2 = param_1;
    puVar2[4] = param_2;
    puVar2[5] = param_4;
    puVar2[2] = param_5;
    puVar2[3] = param_3;
    FUN_000fae70(*puVar1,&uStack_28);
    FUN_000fd1a0();
    uVar3 = 0;
  }
  return uVar3;
}



/* ================================================================
 * entry: 0x000fd8b0
 * end:   0x000fd8b5
 * size:  6 bytes
 * name:  FUN_000fd8b0
 * ================================================================ */

void FUN_000fd8b0(uint param_1)

{
  bool bVar1;

  do {
    bVar1 = 2 < param_1;
    param_1 = param_1 - 3;
  } while (bVar1 && param_1 != 0);
  return;
}



/* ================================================================
 * entry: 0x000fdaa0
 * end:   0x000fdaa5
 * size:  6 bytes
 * name:  FUN_000fdaa0
 * ================================================================ */

void FUN_000fdaa0(uint param_1)

{
  bool bVar1;

  do {
    bVar1 = 2 < param_1;
    param_1 = param_1 - 3;
  } while (bVar1 && param_1 != 0);
  return;
}


