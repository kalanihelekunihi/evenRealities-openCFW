/* FUN 0x080000c0 thunk_FUN_0800a598 */

void thunk_FUN_0800a598(void)

{
  (*DAT_080000c4)();
  return;
}



/* FUN 0x080000cc FUN_080000cc */

void FUN_080000cc(void)

{
  bool bVar1;
  char cVar2;
  undefined4 in_stack_00000000;
  undefined4 in_stack_00000004;
  code *UNRECOVERED_JUMPTABLE;
  undefined4 in_stack_0000001c;
  
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setProcessStackPointer(*(int *)*DAT_080000f0 + 0x20);
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
  InstructionSynchronizationBarrier(0xf);
  enableIRQinterrupts();
                    /* WARNING: Could not recover jumptable at 0x080000ec. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)(in_stack_00000000,in_stack_00000004,in_stack_0000001c);
  return;
}



/* FUN 0x080000f4 FUN_080000f4 */

undefined4 FUN_080000f4(void)

{
  bool bVar1;
  undefined4 uVar2;
  
  uVar2 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar2 = isIRQinterruptsEnabled();
  }
  disableIRQinterrupts();
  return uVar2;
}



/* FUN 0x080000fc FUN_080000fc */

void FUN_080000fc(uint param_1)

{
  bool bVar1;
  
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((param_1 & 1) == 1);
  }
  return;
}



/* FUN 0x08000102 FUN_08000102 */

int FUN_08000102(void)

{
  bool bVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 unaff_r4;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  undefined4 unaff_r7;
  undefined4 unaff_r8;
  undefined4 unaff_r9;
  undefined4 unaff_r10;
  undefined4 unaff_r11;
  
  puVar2 = DAT_08000140;
  iVar3 = getProcessStackPointer();
  *(undefined4 **)*DAT_08000140 = (undefined4 *)(iVar3 + -0x20);
  *(undefined4 *)(iVar3 + -0x20) = unaff_r4;
  *(undefined4 *)(iVar3 + -0x1c) = unaff_r5;
  *(undefined4 *)(iVar3 + -0x18) = unaff_r6;
  *(undefined4 *)(iVar3 + -0x14) = unaff_r7;
  *(undefined4 *)(iVar3 + -0x10) = unaff_r8;
  *(undefined4 *)(iVar3 + -0xc) = unaff_r9;
  *(undefined4 *)(iVar3 + -8) = unaff_r10;
  *(undefined4 *)(iVar3 + -4) = unaff_r11;
  disableIRQinterrupts();
  FUN_0800c390(iVar3);
  enableIRQinterrupts();
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setProcessStackPointer(*(int *)*puVar2 + 0x20);
  }
  return *(int *)*puVar2 + 0x10;
}



/* FUN 0x08000144 FUN_08000144 */

void FUN_08000144(void)

{
  (*DAT_08000158)();
                    /* WARNING: Could not recover jumptable at 0x0800014a. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*DAT_0800015c)();
  return;
}



/* FUN 0x08000156 FUN_08000156 */

void FUN_08000156(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* FUN 0x08000160 FUN_08000160 */

int FUN_08000160(uint param_1,uint param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  iVar1 = 0;
  uVar2 = 0x20;
  while (uVar3 = uVar2 - 1, 0 < (int)uVar2) {
    uVar2 = uVar3;
    if (param_2 <= param_1 >> (uVar3 & 0xff)) {
      param_1 = param_1 - (param_2 << (uVar3 & 0xff));
      iVar1 = iVar1 + (1 << (uVar3 & 0xff));
    }
  }
  return iVar1;
}



/* FUN 0x0800018c FUN_0800018c */

int FUN_0800018c(int param_1,int param_2)

{
  int iVar1;
  bool bVar2;
  bool bVar3;
  
  bVar2 = param_1 < 0;
  if (bVar2) {
    param_1 = -param_1;
  }
  bVar3 = param_2 < 0;
  if (bVar3) {
    param_2 = -param_2;
  }
  iVar1 = FUN_08000160(param_1,param_2);
  if (bVar2 != bVar3) {
    iVar1 = -iVar1;
  }
  return iVar1;
}



/* FUN 0x080001b4 FUN_080001b4 */

void FUN_080001b4(undefined4 *param_1,undefined4 *param_2,uint param_3)

{
  undefined4 uVar1;
  bool bVar2;
  
  if ((((uint)param_1 | (uint)param_2) & 3) == 0) {
    for (; 3 < param_3; param_3 = param_3 - 4) {
      uVar1 = *param_2;
      param_2 = param_2 + 1;
      *param_1 = uVar1;
      param_1 = param_1 + 1;
    }
  }
  while (bVar2 = param_3 != 0, param_3 = param_3 - 1, bVar2) {
    *(undefined1 *)param_1 = *(undefined1 *)param_2;
    param_1 = (undefined4 *)((int)param_1 + 1);
    param_2 = (undefined4 *)((int)param_2 + 1);
  }
  return;
}



/* FUN 0x080001d8 FUN_080001d8 */

void FUN_080001d8(undefined1 *param_1,int param_2,undefined1 param_3)

{
  bool bVar1;
  
  while (bVar1 = param_2 != 0, param_2 = param_2 + -1, bVar1) {
    *param_1 = param_3;
    param_1 = param_1 + 1;
  }
  return;
}



/* FUN 0x080001e6 FUN_080001e6 */

void FUN_080001e6(undefined4 param_1,undefined4 param_2)

{
  FUN_080001d8(param_1,param_2,0);
  return;
}



/* FUN 0x080001ea FUN_080001ea */

undefined4 FUN_080001ea(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  FUN_080001d8(param_1,param_3,param_2);
  return param_1;
}



/* FUN 0x080001fc FUN_080001fc */

uint FUN_080001fc(int param_1,undefined4 param_2,uint param_3)

{
  byte *pbVar1;
  int iVar2;
  
  iVar2 = 3;
  pbVar1 = (byte *)(param_1 + 4);
  do {
    pbVar1 = pbVar1 + -1;
    param_3 = param_3 << 8 | (uint)*pbVar1;
    iVar2 = iVar2 + -1;
  } while (-1 < iVar2);
  return param_3;
}



/* FUN 0x08000210 FUN_08000210 */

longlong FUN_08000210(uint param_1,int param_2,uint param_3,uint param_4)

{
  longlong lVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  bool bVar5;
  undefined8 uVar6;
  longlong lVar7;
  int local_2c;
  
  lVar1 = 0;
  iVar3 = 0x40;
  local_2c = param_2;
  while (iVar4 = iVar3 + -1, 0 < iVar3) {
    uVar6 = FUN_080002b4(param_1,local_2c,iVar4);
    uVar2 = (uint)((ulonglong)uVar6 >> 0x20);
    iVar3 = iVar4;
    if (param_4 < uVar2 || uVar2 - param_4 < (uint)(param_3 <= (uint)uVar6)) {
      uVar6 = FUN_08000294(param_3,param_4,iVar4);
      bVar5 = param_1 < (uint)uVar6;
      param_1 = param_1 - (uint)uVar6;
      local_2c = (local_2c - (int)((ulonglong)uVar6 >> 0x20)) - (uint)bVar5;
      lVar7 = FUN_08000294(1,0,iVar4);
      lVar1 = lVar7 + lVar1;
    }
  }
  return lVar1;
}



/* FUN 0x08000270 FUN_08000270 */

/* WARNING: Removing unreachable block (ram,0x08000292) */
/* WARNING: Removing unreachable block (ram,0x0800029a) */
/* WARNING: Removing unreachable block (ram,0x080002a4) */
/* WARNING: Removing unreachable block (ram,0x08000350) */
/* WARNING: Removing unreachable block (ram,0x08000372) */
/* WARNING: Removing unreachable block (ram,0x0800039a) */
/* WARNING: Removing unreachable block (ram,0x08000384) */
/* WARNING: Removing unreachable block (ram,0x080003a4) */
/* WARNING: Removing unreachable block (ram,0x080003d8) */
/* WARNING: Removing unreachable block (ram,0x080003c0) */
/* WARNING: Removing unreachable block (ram,0x080003e2) */
/* WARNING: Removing unreachable block (ram,0x08000402) */
/* WARNING: Removing unreachable block (ram,0x080003e8) */
/* WARNING: Removing unreachable block (ram,0x0800040e) */
/* WARNING: Removing unreachable block (ram,0x080003f4) */
/* WARNING: Removing unreachable block (ram,0x080003f8) */
/* WARNING: Removing unreachable block (ram,0x08000400) */
/* WARNING: Removing unreachable block (ram,0x08000406) */
/* WARNING: Removing unreachable block (ram,0x080003ce) */
/* WARNING: Removing unreachable block (ram,0x08000390) */
/* WARNING: Removing unreachable block (ram,0x0800035e) */

undefined8 FUN_08000270(void)

{
  byte bVar1;
  byte *pbVar2;
  byte *pbVar3;
  byte *pbVar4;
  uint uVar5;
  uint uVar6;
  byte *pbVar7;
  bool bVar8;
  bool bVar9;
  undefined8 uVar10;
  
  pbVar3 = pbRam08000290;
  pbVar7 = pbRam0800028c;
  while( true ) {
    bVar9 = pbVar3 <= pbVar7;
    bVar8 = pbVar7 == pbVar3;
    if (bVar9) break;
    (**(code **)(pbVar7 + 0xc))
              (*(undefined4 *)pbVar7,*(undefined4 *)(pbVar7 + 4),*(undefined4 *)(pbVar7 + 8));
    pbVar7 = pbVar7 + 0x10;
  }
  uVar10 = thunk_FUN_0800a598();
  if (!bVar9 || bVar8) {
    while( true ) {
      pbVar4 = (byte *)((ulonglong)uVar10 >> 0x20);
      pbVar3 = (byte *)uVar10;
      if (pbVar7 <= pbVar4) break;
      bVar1 = *pbVar3;
      pbVar2 = pbVar3 + 1;
      uVar6 = bVar1 & 0xf;
      if ((bVar1 & 0xf) == 0) {
        uVar6 = (uint)*pbVar2;
        pbVar2 = pbVar3 + 2;
      }
      uVar5 = (uint)(bVar1 >> 4);
      if (uVar5 == 0) {
        uVar5 = (uint)*pbVar2;
        pbVar2 = pbVar2 + 1;
      }
      while (uVar6 = uVar6 - 1, uVar6 != 0) {
        *pbVar4 = *pbVar2;
        pbVar2 = pbVar2 + 1;
        pbVar4 = pbVar4 + 1;
      }
      while( true ) {
        uVar10 = CONCAT44(pbVar4,pbVar2);
        uVar5 = uVar5 - 1;
        if (uVar5 == 0) break;
        *pbVar4 = 0;
        pbVar4 = pbVar4 + 1;
      }
    }
    return 0;
  }
  FUN_0800a24a();
  pbVar7[8] = 0x20;
  pbVar7[9] = 0;
  pbVar7[10] = 0;
  pbVar7[0xb] = 0;
  return 0;
}



/* FUN 0x08000294 FUN_08000294 */

longlong FUN_08000294(uint param_1,int param_2,uint param_3)

{
  if (0x1f < (int)param_3) {
    return (ulonglong)(param_1 << (param_3 - 0x20 & 0xff)) << 0x20;
  }
  return CONCAT44(param_2 << (param_3 & 0xff) | param_1 >> (0x20 - param_3 & 0xff),
                  param_1 << (param_3 & 0xff));
}



/* FUN 0x080002b4 FUN_080002b4 */

ulonglong FUN_080002b4(uint param_1,uint param_2,uint param_3)

{
  if (0x1f < (int)param_3) {
    return (ulonglong)(param_2 >> (param_3 - 0x20 & 0xff));
  }
  return CONCAT44(param_2 >> (param_3 & 0xff),
                  param_1 >> (param_3 & 0xff) | param_2 << (0x20 - param_3 & 0xff));
}



/* FUN 0x080002d6 FUN_080002d6 */

undefined4 FUN_080002d6(byte *param_1,byte *param_2,int param_3)

{
  byte bVar1;
  byte *pbVar2;
  uint uVar3;
  uint uVar4;
  byte *pbVar5;
  
  pbVar5 = param_2 + param_3;
  do {
    bVar1 = *param_1;
    uVar4 = bVar1 & 0xf;
    pbVar2 = param_1 + 1;
    if ((bVar1 & 0xf) == 0) {
      uVar4 = (uint)param_1[1];
      pbVar2 = param_1 + 2;
    }
    param_1 = pbVar2;
    uVar3 = (uint)(bVar1 >> 4);
    if (uVar3 == 0) {
      uVar3 = (uint)*param_1;
      param_1 = param_1 + 1;
    }
    while (uVar4 = uVar4 - 1, uVar4 != 0) {
      *param_2 = *param_1;
      param_1 = param_1 + 1;
      param_2 = param_2 + 1;
    }
    while (uVar3 = uVar3 - 1, uVar3 != 0) {
      *param_2 = 0;
      param_2 = param_2 + 1;
    }
  } while (param_2 < pbVar5);
  return 0;
}



/* FUN 0x08000310 FUN_08000310 */

undefined4 FUN_08000310(int param_1,undefined4 param_2,int param_3,int param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int local_30;
  undefined4 local_2c;
  int iStack_24;
  undefined4 local_20;
  int iStack_1c;
  int local_18;
  
  iVar1 = DAT_0800041c;
  local_2c = 1;
  *(undefined4 *)(DAT_0800041c + 8) = 0;
  if (param_1 << 0x19 < 0) {
    *(undefined4 *)(iVar1 + 8) = 0x1f;
  }
  else {
    iStack_24 = param_1;
    local_20 = param_2;
    iStack_1c = param_3;
    local_18 = param_4;
    FUN_0800a310();
    FUN_0800a24a();
    FUN_0800a2c4(param_1,1);
    FUN_0800a19a(0);
    iVar2 = FUN_0800c43c(&local_30);
    if (iVar2 == 0) {
      FUN_0800a24a();
      uVar3 = 0x20;
    }
    else {
      iVar2 = FUN_0800c412(param_1 * 2 & 0xff);
      if (iVar2 == local_30) {
        FUN_0800a2c4(local_20,0);
        iVar2 = FUN_0800c43c(&local_30);
        if (iVar2 == 0) {
          FUN_0800a24a();
          uVar3 = 0x22;
        }
        else {
          iVar2 = FUN_0800c412(local_20);
          if (iVar2 == local_30) {
            FUN_0800a24a();
            FUN_0800a2c4(param_1,1);
            FUN_0800a19a(1);
            iVar2 = FUN_0800c43c(&local_30);
            if (iVar2 == 0) {
              FUN_0800a24a();
              uVar3 = 0x24;
            }
            else {
              iVar2 = FUN_0800c412(param_1 * 2 + 1U & 0xff);
              if (iVar2 == local_30) {
                iVar2 = 0;
                while( true ) {
                  if (param_3 <= iVar2) {
                    FUN_0800a24a();
                    return local_2c;
                  }
                  iVar4 = FUN_0800b5d6(local_18 + iVar2);
                  if (iVar4 == 0) break;
                  if (iVar2 != param_3 + -1) {
                    FUN_0800a176(*(undefined1 *)(local_18 + iVar2));
                  }
                  iVar2 = iVar2 + 1;
                }
                FUN_0800a24a();
                uVar3 = 0x26;
              }
              else {
                FUN_0800a24a();
                uVar3 = 0x25;
              }
            }
          }
          else {
            FUN_0800a24a();
            uVar3 = 0x23;
          }
        }
      }
      else {
        FUN_0800a24a();
        uVar3 = 0x21;
      }
    }
    *(undefined4 *)(iVar1 + 8) = uVar3;
  }
  return 0;
}



/* FUN 0x08000420 FUN_08000420 */

undefined4 FUN_08000420(uint param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int local_30;
  undefined4 local_2c;
  uint uStack_24;
  int iStack_20;
  int iStack_1c;
  int local_18;
  
  iVar1 = DAT_080004bc;
  local_2c = 1;
  *(undefined4 *)(DAT_080004bc + 4) = 0;
  if ((int)(param_1 << 0x19) < 0) {
    uStack_24 = param_1;
    iStack_20 = param_2;
    iStack_1c = param_3;
    local_18 = param_4;
    FUN_0800a224();
    uVar5 = (param_1 & 0xfffffff0) + param_2 & 0xff;
    FUN_0800a2a2(uVar5,1);
    FUN_0800a188(1);
    iVar3 = FUN_0800c42c(&local_30);
    if (iVar3 == 0) {
      FUN_0800a224();
      uVar2 = 0x2a;
    }
    else {
      iVar3 = FUN_0800c3f8(uVar5 * 2 + 1 & 0xff);
      if (iVar3 == local_30) {
        iVar3 = 0;
        while( true ) {
          if (param_3 <= iVar3) {
            FUN_0800a224();
            return local_2c;
          }
          iVar4 = FUN_0800b5ac(local_18 + iVar3);
          if (iVar4 == 0) break;
          if (iVar3 != param_3 + -1) {
            FUN_0800a164(*(undefined1 *)(local_18 + iVar3));
          }
          iVar3 = iVar3 + 1;
        }
        FUN_0800a224();
        uVar2 = 0x2c;
      }
      else {
        FUN_0800a224();
        uVar2 = 0x2b;
      }
    }
  }
  else {
    uVar2 = 0x29;
  }
  *(undefined4 *)(iVar1 + 4) = uVar2;
  return 0;
}



/* FUN 0x080004c0 FUN_080004c0 */

undefined4 FUN_080004c0(uint param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  int local_30;
  undefined4 local_2c;
  uint uStack_24;
  int iStack_20;
  int iStack_1c;
  int local_18;
  
  iVar1 = DAT_08000568;
  local_2c = 1;
  *(undefined4 *)(DAT_08000568 + 8) = 0;
  if ((int)(param_1 << 0x19) < 0) {
    uStack_24 = param_1;
    iStack_20 = param_2;
    iStack_1c = param_3;
    local_18 = param_4;
    FUN_0800a310();
    FUN_0800a24a();
    uVar5 = (param_1 & 0xfffffff0) + param_2 & 0xff;
    FUN_0800a2c4(uVar5,1);
    FUN_0800a19a(1);
    iVar2 = FUN_0800c43c(&local_30);
    if (iVar2 == 0) {
      FUN_0800a24a();
      uVar3 = 0x2a;
    }
    else {
      iVar2 = FUN_0800c412(uVar5 * 2 + 1 & 0xff);
      if (iVar2 == local_30) {
        iVar2 = 0;
        while( true ) {
          if (param_3 <= iVar2) {
            FUN_0800a24a();
            return local_2c;
          }
          iVar4 = FUN_0800b5d6(local_18 + iVar2);
          if (iVar4 == 0) break;
          if (iVar2 != param_3 + -1) {
            FUN_0800a176(*(undefined1 *)(local_18 + iVar2));
          }
          iVar2 = iVar2 + 1;
        }
        FUN_0800a24a();
        uVar3 = 0x2c;
      }
      else {
        FUN_0800a24a();
        uVar3 = 0x2b;
      }
    }
    *(undefined4 *)(iVar1 + 8) = uVar3;
  }
  else {
    *(undefined4 *)(iVar1 + 8) = 0x29;
  }
  return 0;
}



/* FUN 0x0800056c FUN_0800056c */

undefined8 FUN_0800056c(uint param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  int local_1c;
  int iStack_18;
  
  iVar1 = DAT_0800060c;
  *(undefined4 *)(DAT_0800060c + 4) = 0;
  if ((int)(param_1 << 0x19) < 0) {
    uVar3 = (param_1 & 0xfffffff0) + param_2;
    local_1c = param_3;
    iStack_18 = param_4;
    FUN_0800a224();
    FUN_0800a2a2(uVar3 & 0xff,1);
    FUN_0800a188(0);
    iVar4 = FUN_0800c42c(&local_1c);
    if (iVar4 == 0) {
      FUN_0800a224();
      uVar2 = 0x16;
    }
    else {
      iVar4 = FUN_0800c3f8((uVar3 & 0x7f) << 1);
      if (iVar4 == local_1c) {
        iVar4 = 0;
        while( true ) {
          if (param_3 <= iVar4) {
            FUN_0800a224();
            return 0x100000001;
          }
          FUN_0800a2a2(*(undefined1 *)(param_4 + iVar4),0);
          iVar5 = FUN_0800c42c(&local_1c);
          if (iVar5 == 0) break;
          iVar5 = FUN_0800c3f8(*(undefined1 *)(param_4 + iVar4));
          if (iVar5 != local_1c) {
            FUN_0800a224();
            uVar2 = 0x19;
            goto LAB_080005ee;
          }
          iVar4 = iVar4 + 1;
        }
        FUN_0800a224();
        uVar2 = 0x18;
      }
      else {
        FUN_0800a224();
        uVar2 = 0x17;
      }
    }
  }
  else {
    uVar2 = 0x15;
  }
LAB_080005ee:
  *(undefined4 *)(iVar1 + 4) = uVar2;
  return 0x100000000;
}



/* FUN 0x08000610 FUN_08000610 */

undefined8 FUN_08000610(uint param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  int local_1c;
  int iStack_18;
  
  iVar1 = DAT_080006c0;
  *(undefined4 *)(DAT_080006c0 + 8) = 0;
  if (-1 < (int)(param_1 << 0x19)) {
    *(undefined4 *)(iVar1 + 8) = 0x15;
    return 0x100000000;
  }
  uVar2 = (param_1 & 0xfffffff0) + param_2;
  local_1c = param_3;
  iStack_18 = param_4;
  FUN_0800a310();
  FUN_0800a24a();
  FUN_0800a2c4(uVar2 & 0xff,1);
  FUN_0800a19a(0);
  iVar3 = FUN_0800c43c(&local_1c);
  if (iVar3 == 0) {
    FUN_0800a24a();
    uVar4 = 0x16;
  }
  else {
    iVar3 = FUN_0800c412((uVar2 & 0x7f) << 1);
    if (iVar3 == local_1c) {
      iVar3 = 0;
      while( true ) {
        if (param_3 <= iVar3) {
          FUN_0800a24a();
          return 0x100000001;
        }
        FUN_0800a2c4(*(undefined1 *)(param_4 + iVar3),0);
        iVar5 = FUN_0800c43c(&local_1c);
        if (iVar5 == 0) break;
        iVar5 = FUN_0800c412(*(undefined1 *)(param_4 + iVar3));
        if (iVar5 != local_1c) {
          FUN_0800a24a();
          uVar4 = 0x19;
          goto LAB_080006a0;
        }
        iVar3 = iVar3 + 1;
      }
      FUN_0800a24a();
      uVar4 = 0x18;
    }
    else {
      FUN_0800a24a();
      uVar4 = 0x17;
    }
  }
LAB_080006a0:
  *(undefined4 *)(iVar1 + 8) = uVar4;
  return 0x100000000;
}



/* FUN 0x080006c4 FUN_080006c4 */

void FUN_080006c4(void)

{
  FUN_08004330(DAT_080006d0);
  return;
}



/* FUN 0x080006d4 FUN_080006d4 */

undefined4 FUN_080006d4(int *param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_0800678a(*param_1);
  if (iVar1 != 0) {
    iVar1 = *param_1;
    if (-1 < *(int *)(iVar1 + 8) << 0x1e) {
      *(uint *)(iVar1 + 8) = (*(uint *)(iVar1 + 8) & DAT_08000730) + 0x10;
    }
    iVar1 = FUN_08004eac();
    while (*(int *)(*param_1 + 8) << 0x1d < 0) {
      iVar2 = FUN_08004eac();
      if ((2 < (uint)(iVar2 - iVar1)) && (*(int *)(*param_1 + 8) << 0x1d < 0)) {
        param_1[0x16] = param_1[0x16] | 0x10;
        param_1[0x17] = param_1[0x17] | 1;
        return 1;
      }
    }
  }
  return 0;
}



/* FUN 0x08000734 FUN_08000734 */

undefined4 FUN_08000734(int *param_1)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = *(uint *)(*param_1 + 8);
  iVar1 = FUN_0800677a();
  if ((iVar1 != 0) && ((uVar3 & 3) >> 1 == 0)) {
    iVar1 = *param_1;
    if ((*(uint *)(iVar1 + 8) & 5) == 1) {
      *(uint *)(iVar1 + 8) = (*(uint *)(iVar1 + 8) & DAT_080007a4) + 2;
      *(undefined4 *)*param_1 = 3;
      iVar1 = FUN_08004eac();
      do {
        if ((*(uint *)(*param_1 + 8) & 1) == 0) {
          return 0;
        }
        iVar2 = FUN_08004eac();
      } while (((uint)(iVar2 - iVar1) < 3) || ((*(uint *)(*param_1 + 8) & 1) == 0));
    }
    param_1[0x16] = param_1[0x16] | 0x10;
    param_1[0x17] = param_1[0x17] | 1;
    return 1;
  }
  return 0;
}



/* FUN 0x080007a8 FUN_080007a8 */

undefined4 FUN_080007a8(int *param_1)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  iVar1 = FUN_0800677a(*param_1);
  if (iVar1 != 0) {
    return 0;
  }
  iVar1 = *param_1;
  if ((*(uint *)(iVar1 + 8) & DAT_0800084c) == 0) {
    uVar3 = ~DAT_0800084c;
    *(uint *)(iVar1 + 8) = (*(uint *)(iVar1 + 8) & uVar3) + 1;
    if ((int)((*DAT_08000850 & 0x1c00000) << 8) < 0) {
      iVar1 = FUN_08000160(*DAT_08000858,DAT_08000854);
      for (iVar1 = iVar1 + 1; iVar1 != 0; iVar1 = iVar1 + -1) {
      }
    }
    if (*(char *)((int)param_1 + 0x19) == '\x01') {
      return 0;
    }
    iVar1 = FUN_08004eac();
    do {
      if ((~*(uint *)*param_1 & 1) == 0) {
        return 0;
      }
      iVar2 = FUN_0800677a();
      if (iVar2 == 0) {
        *(uint *)(*param_1 + 8) = (*(uint *)(*param_1 + 8) & uVar3) + 1;
      }
      iVar2 = FUN_08004eac();
    } while (((uint)(iVar2 - iVar1) < 3) || ((~*(uint *)*param_1 & 1) == 0));
  }
  param_1[0x16] = param_1[0x16] | 0x10;
  param_1[0x17] = param_1[0x17] | 1;
  return 1;
}



/* FUN 0x0800085c FUN_0800085c */

void FUN_0800085c(void)

{
  ushort uVar1;
  ushort *puVar2;
  char cVar3;
  byte bVar4;
  int iVar5;
  char *pcVar6;
  uint uVar7;
  undefined4 uVar8;
  undefined4 in_r3;
  uint uVar9;
  
  puVar2 = DAT_0800091c;
  uVar1 = *DAT_0800091c;
  if (uVar1 < 2) {
    return;
  }
  if (*(byte *)(DAT_08000920 + 0x17) < 0x1e) {
    *(undefined1 *)(DAT_08000920 + 0x17) = 0;
  }
  pcVar6 = DAT_08000924;
  if (*DAT_08000924 != -0x22) {
    iVar5 = FUN_08009b94(*DAT_08000924);
    if ((iVar5 != 0xd) || (iVar5 = FUN_08009b94(pcVar6[1]), iVar5 != 0xe)) {
      uVar7 = (uint)*puVar2;
      if (uVar7 < 5) {
        return;
      }
      if (*pcVar6 != 'Z') {
        return;
      }
      if (pcVar6[1] != -0x5b) {
        return;
      }
      if (pcVar6[2] == '\x7f') {
        uVar9 = (uint)(byte)pcVar6[3];
        if (uVar9 != uVar7 - 5) {
          return;
        }
        uVar7 = uVar7 - 4;
        uVar8 = 0;
        pcVar6 = pcVar6 + 4;
      }
      else {
        if (pcVar6[2] != -0x31) {
          return;
        }
        if ((uint)(byte)pcVar6[3] != (uVar7 - 6 & 0xff)) {
          return;
        }
        uVar9 = (uint)(byte)pcVar6[4];
        if (uVar9 != (int)(uVar7 - 6) >> 8) {
          return;
        }
        uVar7 = uVar7 - 5;
        uVar8 = 1;
        pcVar6 = pcVar6 + 5;
      }
      FUN_08000e1c(pcVar6,uVar7 & 0xffff,uVar8,uVar9,in_r3);
      return;
    }
    for (uVar7 = 1; uVar7 < *puVar2 >> 1; uVar7 = uVar7 + 1 & 0xffff) {
      iVar5 = uVar7 * 2;
      cVar3 = FUN_08009b94(pcVar6[iVar5]);
      bVar4 = FUN_08009b94(pcVar6[iVar5 + 1]);
      pcVar6[uVar7] = cVar3 << 4 | bVar4;
    }
    uVar1 = *puVar2 >> 1;
  }
  FUN_08000928(pcVar6 + 1,uVar1 - 1);
  return;
}



/* FUN 0x08000928 FUN_08000928 */

/* WARNING: Function: __ARM_common_switch8 replaced with injection: switch8_r3 */
/* WARNING (jumptable): Removing unreachable block (ram,0x08000940) */
/* WARNING: Removing unreachable block (ram,0x08000940) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08000928(byte *param_1,uint param_2)

{
  char cVar1;
  byte bVar2;
  byte *pbVar3;
  char *pcVar4;
  char *pcVar5;
  uint uVar6;
  undefined1 auStack_30 [32];
  
  pcVar5 = DAT_08000c68;
  uVar6 = (uint)*param_1;
  cVar1 = *DAT_08000c68;
  if (uVar6 == 0xaf) {
    if (param_2 < 2) {
      return;
    }
    pcVar5 = (char *)(uint)param_1[1];
    *DAT_08000c68 = pcVar5 != (char *)0x0;
    if (pcVar5 == (char *)0x0) {
      return;
    }
    pcVar4 = &DAT_08000c88;
  }
  else {
    if (uVar6 < 0xb0) {
                    /* WARNING: Could not recover jumptable at 0x08000940. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      if (uVar6 - 0xa0 < (uint)DAT_08000944) {
        pbVar3 = (byte *)(uVar6 + 0x80008a5);
      }
      else {
        pbVar3 = (byte *)(DAT_08000944 + 0x8000945);
      }
      (*(code *)((uint)*pbVar3 * 2 + 0x8000945))();
      return;
    }
    if (uVar6 == 0xd4) {
      if (cVar1 == '\0') {
        FUN_08009170(s_Set_PMIC_chip_id_to_0x08_08000df0);
        FUN_08009170(&DAT_08000cac);
      }
      FUN_080039e4(0x14,8);
      return;
    }
    if (uVar6 < 0xd5) {
      if (uVar6 == 0xd1) {
        if (param_2 < 4) {
          return;
        }
        *(bool *)DAT_08000d74 = param_1[1] != 0;
        *(bool *)DAT_08000d78 = param_1[2] != 0;
        *(bool *)_DAT_08000d7c = param_1[3] != 0;
        if (cVar1 != '\0') {
          return;
        }
        FUN_08009170(s_simu_full_bat__d__simu_empty_bat_08000d7f + 1);
        goto LAB_080009f4;
      }
      if (uVar6 < 0xd2) {
        if (uVar6 == 0xb0) {
          FUN_0800a888(*DAT_08000d00,0x100);
          return;
        }
        if (uVar6 != 0xd0) {
          return;
        }
        if (param_2 < 2) {
          return;
        }
        FUN_08002c8e(param_1[1] != 0);
        if (*pcVar5 != '\0') {
          return;
        }
        if (param_1[1] == 0) {
          pcVar5 = s_Disable_08000c93;
        }
        else {
          pcVar5 = s_Enable_08000c6f;
        }
        pcVar5 = pcVar5 + 1;
        pcVar4 = s__s_watchdog_4005_08000d60;
      }
      else if (uVar6 == 0xd2) {
        if (param_2 < 2) {
          return;
        }
        bVar2 = param_1[1];
        *_DAT_08000c78 = bVar2 != 0;
        if (cVar1 != '\0') {
          return;
        }
        if (bVar2 != 0) {
          pcVar5 = s_Disable_08000c93;
        }
        else {
          pcVar5 = s_Enable_08000c6f;
        }
        pcVar5 = pcVar5 + 1;
        pcVar4 = s__s_one_side_charging_08000db8;
      }
      else {
        if (uVar6 != 0xd3) {
          return;
        }
        if (cVar1 != '\0') {
          return;
        }
        if (*_DAT_08000c78 == '\0') {
          pcVar5 = s_enabled_08000dd0;
        }
        else {
          pcVar5 = s_disabled_08000c7b + 1;
        }
        pcVar4 = s_One_side_charging___s_08000dd8;
      }
    }
    else {
      if (uVar6 == 0xdd) {
        *(bool *)_DAT_08000d04 = param_1[1] != 0;
        return;
      }
      if (uVar6 != 0xdf) {
        if (uVar6 != 0xee) {
          if (uVar6 != 0xff) {
            return;
          }
          if (cVar1 == '\0') {
            FUN_08009170(s__Reset__reason__cmd__08000d4b + 1);
            FUN_08009170(&DAT_08000cac);
          }
          FUN_0800502c();
          return;
        }
        if (*(char *)(_DAT_08000c6c + 3) == '\0') {
          if (cVar1 == '\0') {
            FUN_08009170(s_Standby__reason__cmd__08000d28);
            FUN_08009170(&DAT_08000cac);
          }
          FUN_080035d4(0x10,auStack_30,1);
          FUN_080035d4(0x11,auStack_30,1);
          FUN_08002c8e(0);
          FUN_08002c30(0);
          FUN_08005094(0x2b);
          FUN_080050a8(DAT_08000d40);
          *(undefined4 *)(_DAT_08000d48 + 0x18) = DAT_08000d44;
          FUN_080050c4();
          return;
        }
        if (cVar1 != '\0') {
          return;
        }
        FUN_08009170(s_usb_in__cannot_enter_shipmode__08000d07 + 1);
        goto LAB_080009f4;
      }
      if (param_2 < 2) {
        return;
      }
      bVar2 = param_1[1];
      *(bool *)_DAT_08000e0c = bVar2 != 0;
      if (cVar1 != '\0') {
        return;
      }
      if (bVar2 != 0) {
        pcVar5 = s_Enable_08000c6f;
      }
      else {
        pcVar5 = s_Disable_08000c93;
      }
      pcVar5 = pcVar5 + 1;
      pcVar4 = s__s_dog_feed_08000e0f + 1;
    }
  }
  FUN_08009170(pcVar4,pcVar5);
LAB_080009f4:
  FUN_08009170(&DAT_08000cac);
  return;
}



/* FUN 0x08000e1c FUN_08000e1c */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08000e1c(byte *param_1,uint param_2,int param_3)

{
  byte bVar1;
  byte bVar2;
  char cVar3;
  uint uVar4;
  byte *pbVar5;
  undefined4 *puVar6;
  undefined1 uVar7;
  char *pcVar8;
  int iVar9;
  int *piVar10;
  undefined4 uVar11;
  int local_40;
  undefined4 local_3c;
  undefined4 local_38;
  undefined1 local_34;
  byte local_33;
  undefined1 local_32;
  undefined1 local_31;
  undefined1 local_30;
  undefined1 local_2f;
  undefined1 local_2e;
  undefined1 uStack_2d;
  undefined4 local_2c;
  undefined1 local_28 [8];
  byte *pbStack_20;
  uint uStack_1c;
  int local_18;
  
  iVar9 = _DAT_0800118c;
  puVar6 = DAT_08001184;
  pbVar5 = DAT_08001180;
  piVar10 = &local_40;
  local_28[0] = 0;
  bVar1 = DAT_08001180[1];
  uVar11 = *DAT_08001184;
  pbStack_20 = param_1;
  uStack_1c = param_2;
  local_18 = param_3;
  if (param_1[2] != 2) {
    if (((*param_1 == 0x3d) && (bVar1 != 0)) && (FUN_0800a888(uVar11,0x80), *DAT_08001188 == '\0'))
    {
      FUN_08009170(s__AGING_NOT___exit_aging_status_0_080012b8);
      FUN_08009170(&DAT_080011b0);
    }
    if (local_18 == 0) {
      if (param_2 < 5) {
        return;
      }
      if (param_1[1] != 0) {
        return;
      }
      if (1 < param_1[2]) {
        return;
      }
      if (param_1[3] + 5 != param_2) {
        return;
      }
      uVar11 = 0x20;
    }
    else {
      if (param_2 < 5) {
        return;
      }
      if (param_1[1] != 0) {
        return;
      }
      if (1 < param_1[2]) {
        return;
      }
      if ((uint)param_1[3] + (uint)param_1[4] * 0x100 + 6 != param_2) {
        return;
      }
      uVar11 = 0x400;
    }
    FUN_0800a888(*puVar6,uVar11);
    FUN_080001b4(DAT_080012e0,param_1,param_2);
    return;
  }
  bVar2 = *param_1;
  cVar3 = *DAT_08001188;
  if (bVar2 == 0x51) {
    local_40 = DAT_080011c8;
    local_3c = DAT_080011cc;
    local_38 = DAT_080011d0;
    FUN_08002f60(&local_3c,DAT_080011cc,DAT_080011d0,&local_34);
    uVar11 = 0xc;
    goto LAB_08000f1c;
  }
  if (bVar2 < 0x52) {
    if (bVar2 == 0x3f) {
      if (param_2 < 5) {
        return;
      }
      *(bool *)(_DAT_0800118c + 0x15) = param_1[4] != 0;
      if (cVar3 == '\0') {
        if (param_1[4] == 0) {
          pcVar8 = s_disable_08001204;
        }
        else {
          pcVar8 = s_enable_080011fc;
        }
        FUN_08009170(s__s_output__reason__cmd_0800120c,pcVar8);
        FUN_08009170(&DAT_080011b0);
      }
      if (*(char *)(iVar9 + 0x15) != '\0') {
        FUN_0800d154();
        *(undefined1 *)(iVar9 + 0x10) = 0;
        *(undefined1 *)(iVar9 + 0x11) = 0;
      }
      uVar11 = 0x3f;
      goto LAB_08001102;
    }
    if (bVar2 < 0x40) {
      if (bVar2 == 6) {
        FUN_080068d0(6);
        local_28[0] = 0xee;
LAB_08000eb0:
        FUN_08000928(local_28,1);
        return;
      }
      if (bVar2 == 0x14) {
        local_3c = 0;
        FUN_08009ff0(&local_3c);
        local_3c = FUN_0800018c(local_3c,10);
        local_40 = 0;
        FUN_08009f18(&local_40);
        local_2c = 0;
        FUN_0800a01e(&local_2c);
        local_38 = DAT_080011b4;
        uVar4 = (uint)local_40 >> 0x1f;
        if (local_40 < 0) {
          local_40 = -local_40;
        }
        _local_34 = CONCAT13((char)((uint)local_40 >> 8),
                             CONCAT12((char)local_40,
                                      CONCAT11((byte)uVar4,*(undefined1 *)(iVar9 + 1))));
        iVar9 = local_3c;
        if (local_3c < 0) {
          iVar9 = ~-local_3c + 1;
        }
        uStack_2d = (undefined1)((uint)DAT_080011bc >> 0x18);
        _local_30 = CONCAT12((char)((uint)local_2c >> 8),CONCAT11((char)local_2c,(char)iVar9));
        uVar11 = 0xb;
        piVar10 = &local_38;
        goto LAB_08000f1c;
      }
      if (bVar2 == 0x3e) {
        if (param_2 < 5) {
          return;
        }
        bVar2 = param_1[4];
        if (*DAT_08001180 != bVar2) {
          *DAT_08001180 = bVar2 != 0;
          pbVar5[8] = 0;
          pbVar5[9] = 0;
          pbVar5[10] = 0;
          pbVar5[0xb] = 0;
          if (((bVar2 == 0) && (bVar1 != 0)) && (FUN_0800a888(uVar11,0x80), *DAT_08001188 == '\0'))
          {
            FUN_08009170(s__AGING_NOT___exit_aging_status_0_080011d4);
            FUN_08009170(&DAT_080011b0);
          }
        }
        uVar11 = 0x3e;
        goto LAB_08001102;
      }
    }
    else {
      if (bVar2 == 0x41) {
        FUN_080068d0(0x41);
        local_28[0] = 0xff;
        goto LAB_08000eb0;
      }
      if (bVar2 == 0x50) {
        local_40 = DAT_080011c0;
        local_3c = CONCAT13((char)((uint)DAT_080011c4 >> 0x18),0x390201);
        uVar11 = 7;
        piVar10 = &local_40;
        goto LAB_08000f1c;
      }
    }
  }
  else {
    if (bVar2 == 0x5e) {
      if (0x13 < param_2) {
        iVar9 = FUN_0800373c(param_1 + 4);
        if (iVar9 == 0) {
          local_3c = DAT_08001288;
          local_40 = DAT_08001284;
          FUN_0800680c(&local_40,5);
          if (*DAT_08001188 != '\0') goto LAB_080010be;
          pcVar8 = s_Set_SN_Even_fail__0800128c;
        }
        else {
          FUN_080068d0(0x5e);
          if (*DAT_08001188 != '\0') goto LAB_080010be;
          pcVar8 = s_Set_SN_Even_done__08001270;
        }
        FUN_08009170(pcVar8);
LAB_080010be:
        FUN_080067c8(param_1 + 4,0x10);
        return;
      }
      if (cVar3 != '\0') {
        return;
      }
      pcVar8 = s_SN_Even_length_wrong__080012a0;
      goto LAB_08000e96;
    }
    if (bVar2 < 0x5f) {
      if (bVar2 == 0x56) {
        if (param_2 < 6) {
          return;
        }
        if (param_1[4] == 0) {
          if (param_1[5] == 0) {
            if (cVar3 == '\0') {
              FUN_08009170(s_Enter_GLS_OTA_Status__L_08001224);
              FUN_08009170(&DAT_080011b0);
            }
            uVar7 = 1;
          }
          else {
            if (cVar3 == '\0') {
              FUN_08009170(s_Enter_GLS_OTA_Status__R_0800123c);
              FUN_08009170(&DAT_080011b0);
            }
            uVar7 = 2;
          }
          *(undefined1 *)(iVar9 + 0x19) = uVar7;
          *(undefined1 *)(iVar9 + 0x1a) = 0;
          return;
        }
        if (cVar3 == '\0') {
          FUN_08009170(s_Exit_GLS_OTA_Status_08001254);
          FUN_08009170(&DAT_080011b0);
        }
        *(undefined1 *)(iVar9 + 0x19) = 0;
        FUN_080012e4();
        uVar11 = 0x56;
LAB_08001102:
        FUN_080068d0(uVar11);
        return;
      }
      if (bVar2 == 0x5c) {
        local_40 = DAT_08001268;
        local_3c = CONCAT31((int3)((uint)DAT_0800126c >> 8),*(char *)(_DAT_0800118c + 4) == '\0');
        uVar11 = 5;
        piVar10 = &local_40;
        goto LAB_08000f1c;
      }
      if (bVar2 == 0x5d) {
        if (param_2 < 6) {
          return;
        }
        if (param_1[4] == 0) {
          FUN_08006b98(param_1[5] == 0);
        }
        else {
          FUN_08006b80(param_1[5] == 0);
        }
        uVar11 = 0x5d;
        goto LAB_08001102;
      }
    }
    else {
      if (bVar2 == 0x5f) {
        local_40 = 0x1003015f;
        FUN_08002f88(&local_3c);
        uVar11 = 0x14;
        piVar10 = &local_40;
LAB_08000f1c:
        FUN_0800680c(piVar10,uVar11);
        return;
      }
      if (bVar2 == 0x68) {
        if (param_2 < 5) {
          return;
        }
        *DAT_08001188 = param_1[4] != 0;
        uVar11 = 0x68;
        goto LAB_08001102;
      }
    }
  }
  if (cVar3 != '\0') {
    return;
  }
  FUN_08009170(s_dst_box__cannot_parse_cmd___02x_0800118f + 1,bVar2);
  pcVar8 = &DAT_080011b0;
LAB_08000e96:
  FUN_08009170(pcVar8);
  return;
}



/* FUN 0x080012e4 FUN_080012e4 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_080012e4(void)

{
  int iVar1;
  
  iVar1 = DAT_08001314;
  FUN_0800ab26(*(undefined4 *)(DAT_08001314 + 0x18));
  FUN_08006b80(0);
  FUN_08006b98(0);
  *(undefined1 *)(_DAT_08001318 + 2) = 0;
  if (*(char *)(iVar1 + 7) == '\0') {
    FUN_08009170(s_clear_led_status__0800131b + 1);
    FUN_08009170(&DAT_08001330);
  }
  return;
}



/* FUN 0x08001334 FUN_08001334 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08001334(void)

{
  int iVar1;
  
  iVar1 = _DAT_08001378;
  *(undefined1 *)(_DAT_08001378 + 1) = 1;
  *(undefined1 *)(iVar1 + 6) = 1;
  *(undefined1 *)(iVar1 + 2) = 0;
  *(undefined1 *)(iVar1 + 3) = 0;
  *(undefined1 *)(iVar1 + 4) = 0;
  *(undefined4 *)(iVar1 + 0xc) = 0;
  *(undefined1 *)(iVar1 + 5) = 0;
  *(undefined1 *)(iVar1 + 7) = 4;
  if (*(char *)(iVar1 + -0x35) == '\0') {
    FUN_08009170(s__AGING_RUNNING___Start_aging__go_0800137b + 1);
    FUN_08009170(&DAT_080013b0);
  }
  FUN_0800aaf0(*(undefined4 *)(iVar1 + -0x20),DAT_080013b4);
  FUN_0800aaf0(*(undefined4 *)(iVar1 + -0x1c),2000);
  return;
}



/* FUN 0x080013b8 FUN_080013b8 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_080013b8(void)

{
  int iVar1;
  
  iVar1 = _DAT_080013f0;
  *(undefined1 *)(DAT_080013ec + 0x17) = 0;
  FUN_0800aa00(*(undefined4 *)(iVar1 + 0x2c));
  FUN_0800aa00(*(undefined4 *)(iVar1 + 0x30));
  FUN_0800aa00(*(undefined4 *)(iVar1 + 0x28));
  *(undefined1 *)(iVar1 + 3) = 0;
  if (*(char *)(iVar1 + 7) == '\0') {
    FUN_08009170(s_Exit_idle_mode_080013f3 + 1);
    FUN_08009170(&DAT_08001404);
  }
  return;
}



/* FUN 0x08001408 FUN_08001408 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

bool FUN_08001408(void)

{
  char *pcVar1;
  int iVar2;
  int iVar3;
  undefined1 uVar4;
  bool bVar5;
  undefined4 local_24;
  undefined4 local_20;
  undefined1 local_1c [3];
  undefined1 uStack_19;
  byte local_18;
  undefined1 uStack_17;
  undefined2 uStack_16;
  
  pcVar1 = _DAT_08001514;
  iVar3 = DAT_0800150c;
  if ((*(char *)(DAT_0800150c + 0x10) == '\0') || (*(char *)(DAT_0800150c + 0x11) == '\0')) {
    if (*DAT_08001510 == '\0') {
      FUN_08009170(s_GetAgingStatus_fail__not_inbox_08001517 + 1);
      FUN_08009170(&DAT_08001538);
    }
    bVar5 = false;
  }
  else if (*_DAT_08001514 == '\0') {
    *_DAT_08001514 = '\x01';
    local_20 = DAT_08001568;
    local_24 = DAT_08001564;
    FUN_08009b70(&local_24,5);
    FUN_0800258c(1,&local_24,5);
    iVar2 = FUN_08001e94(1);
    if (*(char *)(iVar3 + 4) == '\0') {
      uVar4 = 2;
    }
    else {
      uVar4 = 1;
    }
    uStack_16 = (undefined2)((uint)DAT_08001570 >> 0x10);
    _local_18 = CONCAT11(uVar4,*(char *)(iVar3 + 3) << 7 | *(byte *)(iVar3 + 1));
    uStack_19 = (undefined1)((uint)DAT_0800156c >> 0x18);
    local_1c._0_2_ = (undefined2)DAT_0800156c;
    local_1c = (undefined1  [3])CONCAT12(0,local_1c._0_2_);
    FUN_08009b70(local_1c,7);
    FUN_0800258c(1,local_1c,7);
    FUN_08001e94(1);
    local_1c = (undefined1  [3])CONCAT12(1,local_1c._0_2_);
    FUN_08009b70(local_1c,7);
    FUN_0800258c(0,local_1c,7,1);
    FUN_08001e94(0);
    local_24._0_3_ = CONCAT12(1,(undefined2)local_24);
    FUN_08009b70(&local_24,5);
    FUN_0800258c(0,&local_24,5,1);
    iVar3 = FUN_08001e94(0);
    bVar5 = iVar3 == 0x46 && iVar2 == 0x46;
    *pcVar1 = '\0';
  }
  else {
    if (*DAT_08001510 == '\0') {
      FUN_08009170(s_Skip_GetAgingStatus_since_2510_b_0800153c);
      FUN_08009170(&DAT_08001538);
    }
    bVar5 = true;
  }
  return bVar5;
}



/* FUN 0x08001574 FUN_08001574 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_08001574(void)

{
  char *pcVar1;
  int iVar2;
  char *pcVar3;
  uint uVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  char cVar8;
  char cVar9;
  uint uVar10;
  undefined4 local_44;
  undefined4 local_40;
  undefined1 local_3c;
  undefined3 uStack_3b;
  int local_28;
  uint local_24;
  undefined4 local_20;
  undefined4 local_1c;
  
  pcVar3 = DAT_08001770;
  uVar7 = 0;
  while (pcVar1 = _DAT_08001774, *pcVar3 != '\0') {
    FUN_0800a7b0(100);
  }
  *pcVar3 = '\x01';
  if (*pcVar1 == '\0') {
    FUN_08009170(s__OTA_BOX___Check_gls_ready_08001777 + 1);
    FUN_08009170(&DAT_08001794);
  }
  local_1c = DAT_0800179c;
  local_20 = DAT_08001798;
  FUN_08009b70(&local_20,5);
  FUN_08002744(1,&local_20,5);
  *pcVar3 = '\0';
  iVar2 = FUN_08001e94(1);
  if (iVar2 == 0x59) {
    FUN_0800a7b0(100);
    if (*pcVar1 == '\0') {
      FUN_08009170(s__OTA_BOX___Get_running_bank_080017bc);
      FUN_08009170(&DAT_08001794);
    }
    iVar2 = FUN_08002f46();
    *(char *)(_DAT_080017d8 + 0x18) = (char)iVar2;
    if (iVar2 == 0) {
      if (*pcVar1 != '\0') {
        return 0;
      }
      pcVar3 = s__OTA_BOX___Get_running_bank_fail_080017db + 1;
    }
    else {
      if (*pcVar1 == '\0') {
        FUN_08009170(s__OTA_BOX___Running_bank___d_08001800);
        FUN_08009170(&DAT_08001794);
      }
      iVar2 = FUN_08002d48();
      if (iVar2 == 0) {
        if (*pcVar1 != '\0') {
          return 0;
        }
        pcVar3 = s__OTA_BOX___Erase_bank_fail__0800181c;
      }
      else {
        if (*pcVar1 == '\0') {
          FUN_08009170(s__OTA_BOX___Copy_SN__08001838);
          FUN_08009170(&DAT_08001794);
        }
        iVar2 = FUN_08002b4c();
        if (iVar2 != 0) {
          if (*_DAT_08001774 == '\0') {
            FUN_08009170(s__OTA_BOX___Copy_SN_done__0800184c);
            FUN_08009170(&DAT_08001794);
            if (*_DAT_08001774 == '\0') {
              FUN_08009170(s__OTA_BOX___get_bin_file_08001884);
              FUN_08009170(&DAT_08001794);
            }
          }
          *pcVar3 = '\x01';
          uVar10 = 0xf0;
          local_28 = _DAT_080017d8 + 0x20;
          local_24 = 0;
          cVar9 = '\0';
          do {
            uVar6 = *(uint *)(_DAT_080017d8 + 0x20);
            if (uVar6 <= uVar7) {
              if (*_DAT_08001774 == '\0') {
                FUN_08009170(s__OTA_BOX___get_bin_file_done__to_080018b0,local_24);
                FUN_08009170(&DAT_08001794);
              }
              *pcVar3 = '\0';
              uVar5 = FUN_08002cc0();
              return uVar5;
            }
            if (uVar6 < uVar7 + uVar10) {
              uVar10 = uVar6 - uVar7 & 0xff;
            }
            *(undefined4 *)(_DAT_080017d8 + 0x28) = 0;
            *(undefined1 *)(local_28 + 0xc) = 0;
            local_44 = DAT_0800189c;
            local_40 = DAT_080018a0;
            _local_3c = CONCAT31((int3)((uint)DAT_080018a4 >> 8),(char)uVar10);
            uVar6 = 0;
            do {
              uVar4 = uVar6 + 1 & 0xff;
              *(char *)((int)&local_40 + uVar6) = (char)(uVar7 >> ((uVar6 & 0x1f) << 3));
              uVar6 = uVar4;
            } while (uVar4 < 4);
            FUN_08009b70(&local_44,10);
            FUN_08002744(1,&local_44,10);
            FUN_08001e94(1);
            if ((*(int *)(_DAT_080017d8 + 0x28) == 0) || (*(char *)(local_28 + 0xc) == '\0')) {
              if (*_DAT_08001774 == '\0') {
                FUN_08009170(&DAT_080018ac);
              }
              local_24 = local_24 + 1 & 0xffff;
LAB_08001718:
              cVar8 = cVar9 + '\x01';
              if (cVar9 == '\n') {
                *pcVar3 = '\0';
                return 0;
              }
            }
            else {
              iVar2 = FUN_08002e04(uVar7);
              if (iVar2 == 0) {
                if (*_DAT_08001774 == '\0') {
                  FUN_08009170(&DAT_080018a8);
                }
                goto LAB_08001718;
              }
              uVar7 = *(byte *)(local_28 + 0xc) + uVar7;
              cVar8 = '\0';
            }
            FUN_0800a7b0(0x14);
            cVar9 = cVar8;
          } while( true );
        }
        if (*pcVar1 != '\0') {
          return 0;
        }
        pcVar3 = s__OTA_BOX___Copy_SN_fail__08001868;
      }
    }
  }
  else {
    if (*pcVar1 != '\0') {
      return 0;
    }
    pcVar3 = s__OTA_BOX___GLS_not_ready__080017a0;
  }
  FUN_08009170(pcVar3);
  FUN_08009170(&DAT_08001794);
  return 0;
}



/* FUN 0x080018e4 FUN_080018e4 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_080018e4(void)

{
  char cVar1;
  char cVar2;
  short sVar3;
  bool bVar4;
  bool bVar5;
  int iVar6;
  char *pcVar7;
  undefined1 uVar8;
  char *pcVar9;
  int iVar10;
  int extraout_r1;
  int extraout_r1_00;
  int extraout_r1_01;
  int extraout_r1_02;
  int extraout_r1_03;
  undefined1 local_20 [4];
  byte local_1c;
  undefined1 uStack_1b;
  undefined2 uStack_1a;
  
  pcVar7 = _DAT_08001ad8;
  iVar6 = DAT_08001ad0;
  cVar1 = *(char *)(DAT_08001ad0 + 0x10);
  cVar2 = *(char *)(DAT_08001ad0 + 0x11);
  if ((cVar1 == '\0') && (cVar2 == '\0')) {
    return;
  }
  bVar4 = true;
  bVar5 = true;
  if (*DAT_08001ad4 == '\0') {
LAB_0800193e:
    if (*(char *)(iVar6 + 0x10) != '\0') goto LAB_08001944;
  }
  else {
    if ((cVar1 == '\0') || (cVar2 == '\0')) {
      bVar4 = false;
      bVar5 = false;
      if (((*(uint *)(DAT_08001ad0 + 0xc) < 5) ||
          (FUN_08000160(*(uint *)(DAT_08001ad0 + 0xc),0x14), extraout_r1 == 0)) && (*pcVar7 == '\0')
         ) {
        FUN_08009170(s_only_one_side__dont_send_0x13__L_08001adb + 1,cVar1,cVar2);
        FUN_08009170(&DAT_08001b08);
      }
      goto LAB_0800193e;
    }
LAB_08001944:
    iVar10 = DAT_08001ad0;
    if ((*(char *)(DAT_08001ad0 + 0x31) != '\0') && (sVar3 = *(short *)(iVar6 + 0x38), sVar3 != 0))
    {
      bVar4 = false;
      FUN_08000160(sVar3,0x1e);
      if (extraout_r1_00 == 0) {
        if (*(char *)(iVar10 + 0x33) == '\0') {
          if (*pcVar7 == '\0') {
            pcVar9 = s_L_charging_done__dont_send_0x13__08001b38;
            goto LAB_08001980;
          }
        }
        else if (*pcVar7 == '\0') {
          pcVar9 = s_L_water_detected__disable_5V__ti_08001b0c;
LAB_08001980:
          FUN_08009170(pcVar9,sVar3);
          FUN_08009170(&DAT_08001b08);
        }
      }
    }
  }
  iVar6 = DAT_08001ad0;
  if (((*(char *)(DAT_08001ad0 + 0x11) != '\0') && (*(char *)(DAT_08001ad0 + 0x4d) != '\0')) &&
     (sVar3 = *(short *)(DAT_08001ad0 + 0x54), sVar3 != 0)) {
    bVar5 = false;
    FUN_08000160(sVar3,0x1e);
    if (extraout_r1_01 == 0) {
      if (*(char *)(iVar6 + 0x4f) == '\0') {
        if (*pcVar7 != '\0') goto LAB_080019d4;
        pcVar9 = s_R_charging_done__dont_send_0x13__08001b98;
      }
      else {
        if (*pcVar7 != '\0') goto LAB_080019d4;
        pcVar9 = s_R_water_detected__disable_5V__ti_08001b6c;
      }
      FUN_08009170(pcVar9,sVar3);
      FUN_08009170(&DAT_08001b08);
    }
  }
LAB_080019d4:
  iVar6 = DAT_08001ad0;
  local_20 = (undefined1  [4])DAT_08001bcc;
  if (*(char *)(DAT_08001ad0 + 4) == '\0') {
    uVar8 = 2;
  }
  else {
    uVar8 = 1;
  }
  uStack_1a = (undefined2)((uint)DAT_08001bd0 >> 0x10);
  _local_1c = CONCAT11(uVar8,*(char *)(DAT_08001ad0 + 3) << 7 | *(byte *)(DAT_08001ad0 + 1));
  if (((*(char *)(DAT_08001ad0 + 0x10) != '\0') && (bVar4)) &&
     (FUN_08000160(*(undefined4 *)(DAT_08001ad0 + 0x44),0xf), extraout_r1_02 == 0)) {
    local_20[2] = 0;
    FUN_08009b70(local_20,7);
    FUN_0800258c(1,local_20,7);
    *(int *)(iVar6 + 0x48) = *(int *)(iVar6 + 0x48) + 1;
    iVar10 = FUN_08001e94(1);
    if (iVar10 == 0x13) {
      *(undefined4 *)(iVar6 + 0x40) = 0;
      *(undefined4 *)(iVar6 + 0x44) = 0;
      *(int *)(iVar6 + 0x3c) = *(int *)(iVar6 + 0x3c) + 1;
    }
    else {
      *(undefined4 *)(iVar6 + 0x3c) = 0;
      *(int *)(iVar6 + 0x40) = *(int *)(iVar6 + 0x40) + 1;
      if (*pcVar7 == '\0') {
        FUN_08009170(s_Fail_to_get_GLS_L_status__cnt__d_08001bd4);
        FUN_08009170(&DAT_08001b08);
      }
    }
  }
  if (((*(char *)(iVar6 + 0x11) != '\0') && (bVar5)) &&
     (FUN_08000160(*(undefined4 *)(iVar6 + 0x60),0xf), extraout_r1_03 == 0)) {
    local_20[2] = 1;
    FUN_08009b70(local_20,7);
    FUN_0800258c(0,local_20,7,1);
    *(int *)(iVar6 + 100) = *(int *)(iVar6 + 100) + 1;
    iVar10 = FUN_08001e94(0);
    if (iVar10 == 0x13) {
      *(undefined4 *)(iVar6 + 0x5c) = 0;
      *(undefined4 *)(iVar6 + 0x60) = 0;
      *(int *)(iVar6 + 0x58) = *(int *)(iVar6 + 0x58) + 1;
    }
    else {
      *(int *)(iVar6 + 0x5c) = *(int *)(iVar6 + 0x5c) + 1;
      *(undefined4 *)(iVar6 + 0x58) = 0;
      if (*pcVar7 == '\0') {
        FUN_08009170(s_Fail_to_get_GLS_R_status__cnt__d_08001bf8);
        FUN_08009170(&DAT_08001b08);
      }
    }
  }
  return;
}



/* FUN 0x08001c1c FUN_08001c1c */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08001c1c(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  char *pcVar2;
  int iVar3;
  undefined1 uVar4;
  undefined1 local_20 [3];
  undefined1 uStack_1d;
  byte local_1c;
  undefined1 uStack_1b;
  undefined2 uStack_1a;
  undefined4 uStack_18;
  
  pcVar2 = _DAT_08001d10;
  iVar1 = DAT_08001d0c;
  if (param_1 != 0 || param_2 != 0) {
    _local_20 = DAT_08001d04;
    if (*(char *)(DAT_08001d0c + 4) == '\0') {
      uVar4 = 2;
    }
    else {
      uVar4 = 1;
    }
    uStack_1a = (undefined2)((uint)DAT_08001d08 >> 0x10);
    _local_1c = CONCAT11(uVar4,*(char *)(DAT_08001d0c + 3) << 7 | *(byte *)(DAT_08001d0c + 1));
    uStack_18 = param_4;
    if ((param_1 != 0) && (*(char *)(DAT_08001d0c + 0x10) != '\0')) {
      uStack_1d = (undefined1)((uint)DAT_08001d04 >> 0x18);
      local_20._0_2_ = (undefined2)DAT_08001d04;
      local_20 = (undefined1  [3])CONCAT12(0,local_20._0_2_);
      FUN_08009b70(local_20,7);
      FUN_0800258c(1,local_20,7);
      *(int *)(iVar1 + 0x48) = *(int *)(iVar1 + 0x48) + 1;
      iVar3 = FUN_08001e94(1);
      if (iVar3 == 0x13) {
        *(undefined4 *)(iVar1 + 0x40) = 0;
        *(undefined4 *)(iVar1 + 0x44) = 0;
        *(int *)(iVar1 + 0x3c) = *(int *)(iVar1 + 0x3c) + 1;
      }
      else {
        *(undefined4 *)(iVar1 + 0x3c) = 0;
        *(int *)(iVar1 + 0x40) = *(int *)(iVar1 + 0x40) + 1;
        if (*pcVar2 == '\0') {
          FUN_08009170(s_Fail_to_get_GLS_L_status_FORCE___08001d13 + 1);
          FUN_08009170(&DAT_08001d3c);
        }
      }
    }
    if ((param_2 != 0) && (*(char *)(iVar1 + 0x11) != '\0')) {
      local_20 = (undefined1  [3])CONCAT12(1,local_20._0_2_);
      FUN_08009b70(local_20,7);
      FUN_0800258c(0,local_20,7,1);
      *(int *)(iVar1 + 100) = *(int *)(iVar1 + 100) + 1;
      iVar3 = FUN_08001e94(0);
      if (iVar3 == 0x13) {
        *(undefined4 *)(iVar1 + 0x5c) = 0;
        *(undefined4 *)(iVar1 + 0x60) = 0;
        *(int *)(iVar1 + 0x58) = *(int *)(iVar1 + 0x58) + 1;
        return;
      }
      *(undefined4 *)(iVar1 + 0x58) = 0;
      *(int *)(iVar1 + 0x5c) = *(int *)(iVar1 + 0x5c) + 1;
      if (*pcVar2 == '\0') {
        FUN_08009170(s_Fail_to_get_GLS_R_status_FORCE___08001d40);
        FUN_08009170(&DAT_08001d3c);
      }
    }
  }
  return;
}



/* FUN 0x08001d68 FUN_08001d68 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08001d68(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  char *pcVar2;
  undefined1 uVar3;
  uint uVar4;
  byte bVar5;
  undefined4 local_20;
  undefined4 local_1c;
  uint local_18;
  
  pcVar2 = DAT_08001e18;
  local_20 = param_2;
  local_1c = param_3;
  local_18 = param_4;
  while (*pcVar2 != '\0') {
    FUN_0800a7b0(100);
  }
  if (*_DAT_08001e1c == '\0') {
    FUN_08009170(s__OTA_BOX___Inform_GLS_ota_result_08001e1f + 1,param_1);
    FUN_08009170(&DAT_08001e48);
  }
  local_20 = DAT_08001e4c;
  if (param_1 == 0) {
    local_1c._0_3_ = 0x20100;
    uVar3 = 0x39;
    uVar4 = DAT_08001e54;
  }
  else {
    local_1c._0_3_ = CONCAT12(*(byte *)(_DAT_08001e58 + 0x1c),0x101);
    uVar3 = *(undefined1 *)(_DAT_08001e58 + 0x1d);
    uVar4 = (uint)*(byte *)(_DAT_08001e58 + 0x1c);
  }
  local_1c = CONCAT13(uVar3,(undefined3)local_1c);
  local_18 = DAT_08001e54 & 0xffffff00;
  FUN_08009b70(&local_20,10,uVar4,&stack0xffffffec);
  bVar5 = 0;
  do {
    if (*pcVar2 == '\0') {
      *pcVar2 = '\x01';
      FUN_08002744(1,&local_20,10);
      *pcVar2 = '\0';
      iVar1 = FUN_08001e94(1);
      if (iVar1 == 0x5b) {
        if (*_DAT_08001e1c != '\0') {
          return;
        }
        pcVar2 = s__OTA_BOX___Inform_GLS_done__08001e78;
        goto LAB_08001e00;
      }
    }
    FUN_0800a7b0(200);
    bVar5 = bVar5 + 1;
  } while (bVar5 < 3);
  if (*_DAT_08001e1c == '\0') {
    pcVar2 = s__OTA_BOX___Inform_GLS_fail__08001e5b + 1;
LAB_08001e00:
    FUN_08009170(pcVar2);
    FUN_08009170(&DAT_08001e48);
  }
  return;
}



/* FUN 0x08001e94 FUN_08001e94 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_08001e94(int param_1)

{
  char cVar1;
  uint *puVar2;
  uint *puVar3;
  byte *pbVar4;
  undefined1 uVar5;
  ushort uVar6;
  uint uVar7;
  char *pcVar8;
  bool bVar9;
  byte bVar10;
  int iVar11;
  byte *pbVar12;
  uint uVar13;
  undefined4 uVar14;
  undefined1 uVar15;
  uint uVar16;
  
  pbVar4 = _DAT_080022bc;
  puVar2 = DAT_080022b8;
  uVar14 = 0xff;
  uVar13 = 0;
  pbVar12 = (byte *)0x0;
  uVar7 = 0;
  uVar16 = 0;
  do {
    if (((*(char *)(DAT_08002254 + uVar7) == 'Z') &&
        (iVar11 = DAT_08002254 + uVar7, *(char *)(iVar11 + 1) == -0x5b)) &&
       (*(char *)(iVar11 + 2) == -1)) {
      pbVar12 = (byte *)(iVar11 + 4);
      uVar16 = (uint)*(byte *)(iVar11 + 3);
      uVar13 = uVar16 - 2 & 0xff;
    }
    uVar7 = uVar7 + 1 & 0xff;
  } while (uVar7 < 4);
  if (pbVar12 == (byte *)0x0) {
    return 0xff;
  }
  for (uVar7 = 0; uVar7 < uVar16; uVar7 = uVar7 + 1 & 0xff) {
    uVar13 = pbVar12[uVar7] + uVar13 & 0xff;
  }
  cVar1 = *_DAT_08002258;
  bVar10 = *pbVar12;
  if (pbVar12[uVar16] != uVar13) {
    if (bVar10 == 0x5a) {
      return 0xff;
    }
    if (cVar1 == '\0') {
      FUN_08009170(s_GLS_RX_error__CRC_wrong__0800225b + 1);
      FUN_08009170(&DAT_08002278);
      if (*_DAT_08002258 == '\0') {
        FUN_08009170(s_CRC_Cal___02x__CRC_Rx___02x__hea_0800227c,uVar13,pbVar12[uVar16],uVar16);
      }
    }
    FUN_080067c8(pbVar12,uVar16);
    return 0xff;
  }
  if (bVar10 == 0x46) {
    if (param_1 == 0) {
      _DAT_080022e8[3] = pbVar12[4] != 0;
    }
    else {
      _DAT_080022e8[2] = pbVar12[4] != 0;
    }
    uVar14 = 0x46;
    goto LAB_08001f5e;
  }
  if (0x46 < bVar10) {
    if (bVar10 == 0x58) {
      if (pbVar12[3] == 0x20) {
        if ((pbVar12[9] == 2) && (0x39 < pbVar12[10])) {
          *(undefined1 *)(DAT_080022b8 + -1) = 2;
          *(byte *)((int)puVar2 + -3) = pbVar12[10];
          uVar7 = FUN_080001fc(pbVar12 + 0xc);
          uVar7 = uVar7 << 0x18 | (uVar7 >> 8 & 0xff) << 0x10 | (uVar7 >> 0x10 & 0xff) << 8 |
                  (uint)pbVar12[0xf];
          *puVar2 = uVar7;
          uVar16 = FUN_080001fc(pbVar12 + 0x10);
          uVar16 = uVar16 << 0x18 | (uVar16 >> 8 & 0xff) << 0x10 | (uVar16 >> 0x10 & 0xff) << 8 |
                   (uint)pbVar12[0x13];
          puVar2[1] = uVar16;
          *(undefined1 *)((int)puVar2 + -7) = 3;
          *(undefined1 *)((int)puVar2 + -6) = 0;
          if (cVar1 != '\0') goto LAB_08001f5e;
          FUN_08009170(DAT_080023b8,2,0x39,pbVar12[9],pbVar12[10],uVar7,uVar16);
        }
        else {
          if (cVar1 != '\0') goto LAB_08001f5e;
          FUN_08009170(s__OTA_BOX___nothing_new__cur_1__d_080023bc,2,0x39,pbVar12[9],pbVar12[10]);
        }
      }
      else {
        if (cVar1 != '\0') goto LAB_08001f5e;
        FUN_08009170(s_ota_check__0x58___len__d_0800239c);
      }
      FUN_08009170(&DAT_08002278);
      goto LAB_08001f5e;
    }
    if (bVar10 == 0x59) {
      if ((pbVar12[3] == 1) && (pbVar12[4] == 0)) {
        uVar14 = 0x59;
      }
      goto LAB_08001f5e;
    }
    if (bVar10 == 0x5a) {
      if ((pbVar12[3] & 7) == 1) {
        bVar10 = 0;
        for (uVar7 = 0; (int)uVar7 < (int)(pbVar12[3] - 1); uVar7 = uVar7 + 1 & 0xff) {
          bVar10 = pbVar12[uVar7 + 4] + bVar10;
        }
        if (pbVar12[uVar7 + 4] == bVar10) {
          FUN_080001b4(DAT_080023f0,pbVar12 + 4);
          DAT_080022b8[2] = DAT_080023f0;
          *(byte *)(puVar2 + 3) = pbVar12[3] - 1;
        }
      }
      goto LAB_08001f5e;
    }
    if (bVar10 == 0x5b) {
      if ((pbVar12[3] == 1) && (pbVar12[4] == 0)) {
        uVar14 = 0x5b;
      }
      goto LAB_08001f5e;
    }
    goto LAB_08001f56;
  }
  if (bVar10 == 8) {
    uVar14 = 8;
    goto LAB_08001f5e;
  }
  if (bVar10 < 9) {
    if (bVar10 == 0) goto LAB_08001f5e;
    if (bVar10 == 7) {
      uVar14 = 7;
      goto LAB_08001f5e;
    }
  }
  else {
    if (bVar10 == 0x13) {
      if (pbVar12[3] == 6) {
        uVar6 = *(ushort *)(pbVar12 + 5) << 8 | *(ushort *)(pbVar12 + 5) >> 8;
        uVar16 = pbVar12[4] & 1;
        uVar7 = (uint)pbVar12[9];
        if (pbVar12[8] != 0) {
          uVar7 = -uVar7;
        }
        if (((pbVar12[4] & 1) == 0) && (0 < (int)uVar7)) {
          bVar9 = false;
        }
        else {
          bVar9 = true;
        }
        uVar5 = (undefined1)uVar16;
        if (param_1 == 0) {
          bVar10 = _DAT_080022bc[1];
          _DAT_080022bc[1] = bVar10 * '\x02';
          if ((bVar9) || (DAT_080022b8[0x11] < 10)) {
            pbVar4[1] = bVar10 * '\x02' + 1;
          }
          puVar2 = DAT_080022b8;
          *(undefined1 *)(DAT_080022b8 + 0xc) = 1;
          uVar15 = (pbVar4[1] & 7) != 0;
          *(undefined1 *)(puVar2 + 0xb) = uVar15;
          if ((*(char *)((int)puVar2 + 0x2d) != '\0') ||
             (*(char *)((int)DAT_080022b8 + -0xd) != '\0')) {
            if (pbVar12[7] < 0x62) {
              uVar5 = 0;
            }
            else {
              uVar5 = 1;
            }
          }
          *(undefined1 *)((int)puVar2 + 0x2d) = uVar5;
          if ((*_DAT_080022e8 != '\0') && (_DAT_080022e8[1] == '\0')) {
            *(undefined1 *)((int)puVar2 + 0x2d) = 0;
          }
          *(undefined1 *)((int)DAT_080022b8 + -0xd) = 0;
          *(byte *)((int)puVar2 + 0x2e) = pbVar12[7];
          *(ushort *)((int)puVar2 + 0x32) = uVar6;
          if (cVar1 != '\0') goto LAB_08002120;
          bVar10 = pbVar12[7];
          pcVar8 = s_R_charging__d__done__d__vol__dmv_08002320;
        }
        else {
          bVar10 = *_DAT_080022bc;
          *_DAT_080022bc = bVar10 * '\x02';
          if ((bVar9) || (DAT_080022b8[10] < 10)) {
            *pbVar4 = bVar10 * '\x02' + 1;
          }
          *(undefined1 *)(puVar2 + 5) = 1;
          *(bool *)(puVar2 + 4) = (*pbVar4 & 7) != 0;
          if (*(char *)((int)puVar2 + 0x11) == '\0') {
            if (*(char *)((int)DAT_080022b8 + -0xe) == '\0') goto LAB_08001ff6;
            *(bool *)((int)puVar2 + 0x11) = 0x61 < pbVar12[7];
            if ((0x61 < pbVar12[7]) && (cVar1 == '\0')) {
              FUN_08009170(s_Disable_charging_since_bat__d__>_080022bf + 1);
              FUN_08009170(&DAT_08002278);
            }
          }
          else {
            if (pbVar12[7] < 0x62) {
              uVar5 = 0;
            }
            else {
              uVar5 = 1;
            }
LAB_08001ff6:
            *(undefined1 *)((int)puVar2 + 0x11) = uVar5;
          }
          if ((*_DAT_080022e8 != '\0') && (_DAT_080022e8[1] == '\0')) {
            *(undefined1 *)((int)puVar2 + 0x11) = 0;
          }
          puVar3 = DAT_080022b8;
          *(undefined1 *)((int)DAT_080022b8 + -0xe) = 0;
          *(byte *)((int)puVar2 + 0x12) = pbVar12[7];
          *(ushort *)((int)puVar3 + 0x16) = uVar6;
          if (*_DAT_08002258 != '\0') goto LAB_08002120;
          bVar10 = pbVar12[7];
          uVar15 = (undefined1)puVar2[4];
          pcVar8 = s_L_charging__d__done__d__vol__dmv_080022eb + 1;
        }
        FUN_08009170(pcVar8,uVar15,uVar16,uVar6,bVar10,uVar7);
LAB_0800211a:
        FUN_08009170(&DAT_08002278);
      }
      else {
        if ((pbVar12[3] != 1) || (pbVar12[4] != 1)) goto LAB_08001f5e;
        if (param_1 == 0) {
          if (cVar1 == '\0') {
            pcVar8 = s_R_charging_1__confirmed_by_GLS_R_08002378;
            goto LAB_08002116;
          }
        }
        else if (cVar1 == '\0') {
          pcVar8 = s_L_charging_1__confirmed_by_GLS_L_08002354;
LAB_08002116:
          FUN_08009170(pcVar8);
          goto LAB_0800211a;
        }
      }
LAB_08002120:
      uVar14 = 0x13;
      goto LAB_08001f5e;
    }
    if (bVar10 == 0x3e) {
      if ((pbVar12[4] == 0) || (pbVar12[4] == 4)) {
        uVar14 = 0x3e;
      }
      goto LAB_08001f5e;
    }
  }
LAB_08001f56:
  FUN_0800680c(pbVar12,uVar16);
LAB_08001f5e:
  FUN_080001e6(DAT_08002254,0x118);
  return uVar14;
}



/* FUN 0x080023f4 FUN_080023f4 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_080023f4(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  undefined4 local_18;
  undefined4 local_14;
  
  pcVar1 = _DAT_08002464;
  if (*(char *)(DAT_0800245c + 0x10) == '\0') {
    if (*DAT_08002460 != '\0') {
      return;
    }
    pcVar1 = s_SetAgingStatusL_fail__not_inbox_08002494;
  }
  else {
    if (*_DAT_08002464 == '\0') {
      *_DAT_08002464 = '\x01';
      local_18 = DAT_080024b4;
      local_14 = CONCAT31((int3)((uint)DAT_080024b8 >> 8),param_1);
      FUN_08009b70(&local_18,6);
      FUN_0800258c(1,&local_18,6);
      iVar2 = FUN_08001e94(1);
      if (iVar2 == 0x3e) {
        *(undefined1 *)(DAT_080024bc + 2) = param_1;
      }
      *pcVar1 = '\0';
      return;
    }
    if (*DAT_08002460 != '\0') {
      return;
    }
    pcVar1 = s_Skip_SetAgingStatusL_since_2510_b_08002467 + 1;
  }
  local_18 = param_3;
  local_14 = param_4;
  FUN_08009170(pcVar1);
  FUN_08009170(&DAT_08002490);
  return;
}



/* FUN 0x080024c0 FUN_080024c0 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_080024c0(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  undefined4 local_18;
  undefined4 local_14;
  
  pcVar1 = _DAT_08002530;
  if (*(char *)(DAT_08002528 + 0x11) == '\0') {
    if (*DAT_0800252c != '\0') {
      return;
    }
    pcVar1 = s_SetAgingStatusR_fail__not_inbox_08002560;
  }
  else {
    if (*_DAT_08002530 == '\0') {
      *_DAT_08002530 = '\x01';
      local_18 = DAT_08002580;
      local_14 = CONCAT31((int3)((uint)DAT_08002584 >> 8),param_1);
      FUN_08009b70(&local_18,6);
      FUN_0800258c(0,&local_18,6,1);
      iVar2 = FUN_08001e94(0);
      if (iVar2 == 0x3e) {
        *(undefined1 *)(DAT_08002588 + 3) = param_1;
      }
      *pcVar1 = '\0';
      return;
    }
    if (*DAT_0800252c != '\0') {
      return;
    }
    pcVar1 = s_Skip_SetAgingStatusR_since_2510_b_08002533 + 1;
  }
  local_18 = param_3;
  local_14 = param_4;
  FUN_08009170(pcVar1);
  FUN_08009170(&DAT_0800255c);
  return;
}



/* FUN 0x0800258c FUN_0800258c */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0800258c(int param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  short sVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  char *pcVar5;
  uint uVar6;
  uint uVar7;
  
  FUN_0800d250();
  iVar2 = FUN_08005f44(DAT_080026bc);
  if (-1 < iVar2 << 0x1a) {
    FUN_08006cf8();
  }
  FUN_08004e9e(0x50000000,8,1);
  if (param_1 == 0) {
    FUN_0800bede();
  }
  else {
    FUN_0800be90();
  }
  FUN_0800a7b0(1);
  FUN_08003bb0(param_2,param_3);
  FUN_08006c80();
  if (param_4 == 0) goto LAB_080026ae;
  iVar3 = FUN_080063ec(DAT_080026bc,DAT_080026c0,5,0x50);
  pcVar5 = _DAT_080026c4;
  iVar2 = DAT_080026c0;
  if (iVar3 == 3) {
    if (*_DAT_080026c4 != '\0') goto LAB_080026ae;
    FUN_08009170(s_receive_header_timeout_080026c7 + 1);
  }
  else {
    uVar4 = 0;
    do {
      if (*(char *)(DAT_080026c0 + uVar4) == 'Z') break;
      uVar4 = uVar4 + 1 & 0xff;
    } while (uVar4 < 5);
    if (4 < uVar4) {
      if (*_DAT_080026c4 == '\0') {
        pcVar5 = s_no_header_in_first_5_char__RX__080026e0;
LAB_08002694:
        FUN_08009170(pcVar5);
      }
LAB_0800261e:
      FUN_080067c8(DAT_080026c0,5);
      goto LAB_080026ae;
    }
    uVar7 = 5 - uVar4 & 0xff;
    if (uVar4 != 0) {
      for (uVar6 = 0; uVar6 < uVar7; uVar6 = uVar6 + 1 & 0xff) {
        *(undefined1 *)(iVar2 + uVar6) = *(undefined1 *)(iVar2 + uVar6 + uVar4);
      }
      if (1 < uVar4) {
        iVar3 = FUN_080063ec(DAT_080026bc,iVar2 + uVar4 + 1,uVar4 - 1 & 0xffff,0x32);
        if (iVar3 == 3) {
          if (*pcVar5 == '\0') {
            FUN_08009170(s_receive_len_timeout__RX__08002700);
            pcVar5 = &DAT_0800271c;
            goto LAB_08002694;
          }
          goto LAB_0800261e;
        }
        uVar7 = 4;
      }
    }
    uVar4 = 0x113;
    if (*(byte *)(iVar2 + 3) < 0x113) {
      uVar4 = (uint)*(byte *)(iVar2 + 3);
    }
    sVar1 = FUN_08000160(uVar4,0x1e);
    iVar2 = FUN_080063ec(DAT_080026bc,iVar2 + uVar7,uVar4,sVar1 * 5 + 5);
    if ((iVar2 != 3) || (*pcVar5 != '\0')) goto LAB_080026ae;
    FUN_08009170(s_receive_data_timeout__RX__len__d_08002720,uVar4);
  }
  FUN_08009170(&DAT_0800271c);
LAB_080026ae:
  FUN_08005f00(DAT_080026bc);
  FUN_08009a14();
  return 1;
}



/* FUN 0x08002744 FUN_08002744 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_08002744(undefined4 param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  short sVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  char *pcVar5;
  uint uVar6;
  uint uVar7;
  
  iVar2 = FUN_08005f44(DAT_0800282c);
  if (-1 < iVar2 << 0x1a) {
    FUN_08006cf8();
  }
  FUN_08004e9e(0x50000000,8,1);
  FUN_08003bb0(param_2,param_3);
  FUN_08006c80();
  if ((param_4 == 0) ||
     (iVar3 = FUN_080063ec(DAT_0800282c,DAT_08002830,5,100), pcVar5 = _DAT_08002834,
     iVar2 = DAT_08002830, iVar3 == 3)) goto LAB_0800280e;
  uVar4 = 0;
  do {
    if (*(char *)(DAT_08002830 + uVar4) == 'Z') break;
    uVar4 = uVar4 + 1 & 0xff;
  } while (uVar4 < 5);
  if (uVar4 < 5) {
    uVar7 = 5 - uVar4 & 0xff;
    if (uVar4 != 0) {
      for (uVar6 = 0; uVar6 < uVar7; uVar6 = uVar6 + 1 & 0xff) {
        *(undefined1 *)(iVar2 + uVar6) = *(undefined1 *)(iVar2 + uVar6 + uVar4);
      }
      if (1 < uVar4) {
        iVar3 = FUN_080063ec(DAT_0800282c,iVar2 + uVar4 + 1,uVar4 - 1 & 0xffff,0x32);
        if (iVar3 == 3) {
          if (*pcVar5 == '\0') {
            FUN_08009170(s__noctrl_receive_len_timeout__RX__08002860);
            pcVar5 = &DAT_08002884;
            goto LAB_08002826;
          }
          goto LAB_080027ac;
        }
        uVar7 = 4;
      }
    }
    uVar4 = 0x113;
    if (*(byte *)(iVar2 + 3) < 0x113) {
      uVar4 = (uint)*(byte *)(iVar2 + 3);
    }
    sVar1 = FUN_08000160(uVar4,0x1e);
    FUN_080063ec(DAT_0800282c,iVar2 + uVar7,uVar4,sVar1 * 5 + 5);
  }
  else {
    if (*_DAT_08002834 == '\0') {
      pcVar5 = s__noctrl_no_header_in_first_5_cha_08002837 + 1;
LAB_08002826:
      FUN_08009170(pcVar5);
    }
LAB_080027ac:
    FUN_080067c8(DAT_08002830,5);
  }
LAB_0800280e:
  FUN_08005f00(DAT_0800282c);
  return 1;
}



/* FUN 0x08002888 FUN_08002888 */

void FUN_08002888(void)

{
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  
  FUN_080001e6(&local_18,0x14);
  local_18 = 0x18;
  local_14 = 0x11;
  local_10 = 0;
  FUN_08004d30(DAT_080028b0,&local_18);
  FUN_0800a4dc();
  return;
}



/* FUN 0x080028b4 FUN_080028b4 */

undefined4 FUN_080028b4(undefined4 param_1,int param_2,uint param_3)

{
  undefined1 uVar1;
  int iVar2;
  uint uVar3;
  
  *DAT_08002928 = 0;
  FUN_0800a4b4();
  FUN_0800a46c(200);
  iVar2 = FUN_0800a4fa();
  if (iVar2 == 0) {
    FUN_0800a46c(param_1);
    iVar2 = FUN_0800a4fa();
    if (iVar2 == 0) {
      FUN_0800a4b4();
      FUN_0800a46c(0xc9);
      iVar2 = FUN_0800a4fa();
      if (iVar2 == 0) {
        for (uVar3 = 0; uVar3 < param_3; uVar3 = uVar3 + 1 & 0xffff) {
          uVar1 = FUN_0800a436();
          *(undefined1 *)(param_2 + uVar3) = uVar1;
          if (uVar3 == param_3 - 1) {
            FUN_0800a414();
          }
          else {
            FUN_0800a3d2();
          }
        }
        FUN_0800a4dc();
        return 1;
      }
    }
  }
  FUN_0800a4dc();
  return 0;
}



/* FUN 0x0800292c FUN_0800292c */

undefined4 FUN_0800292c(undefined4 param_1,int param_2,uint param_3)

{
  undefined1 uVar1;
  int iVar2;
  uint uVar3;
  
  *DAT_080029a0 = 0;
  FUN_0800a4b4();
  FUN_0800a46c(0x70);
  iVar2 = FUN_0800a4fa();
  if (iVar2 == 0) {
    FUN_0800a46c(param_1);
    iVar2 = FUN_0800a4fa();
    if (iVar2 == 0) {
      FUN_0800a4b4();
      FUN_0800a46c(0x71);
      iVar2 = FUN_0800a4fa();
      if (iVar2 == 0) {
        for (uVar3 = 0; uVar3 < param_3; uVar3 = uVar3 + 1 & 0xffff) {
          uVar1 = FUN_0800a436();
          *(undefined1 *)(param_2 + uVar3) = uVar1;
          if (uVar3 == param_3 - 1) {
            FUN_0800a414();
          }
          else {
            FUN_0800a3d2();
          }
        }
        FUN_0800a4dc();
        return 1;
      }
    }
  }
  FUN_0800a4dc();
  return 0;
}



/* FUN 0x080029a4 FUN_080029a4 */

undefined4 FUN_080029a4(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  byte bVar2;
  
  bVar2 = 0;
  *DAT_080029fc = 0;
  do {
    FUN_0800a4b4();
    FUN_0800a46c(200);
    iVar1 = FUN_0800a4fa();
    if (iVar1 == 0) break;
    bVar2 = bVar2 + 1;
  } while (bVar2 < 200);
  if (bVar2 != 200) {
    FUN_0800a46c(param_1);
    iVar1 = FUN_0800a4fa();
    if (iVar1 == 0) {
      FUN_0800a46c(param_2);
      iVar1 = FUN_0800a4fa();
      if (iVar1 == 0) {
        FUN_0800a4dc();
        return 1;
      }
    }
  }
  FUN_0800a4dc();
  return 0;
}



/* FUN 0x08002a00 FUN_08002a00 */

undefined4 FUN_08002a00(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  byte bVar2;
  
  bVar2 = 0;
  *DAT_08002a58 = 0;
  do {
    FUN_0800a4b4();
    FUN_0800a46c(0x70);
    iVar1 = FUN_0800a4fa();
    if (iVar1 == 0) break;
    bVar2 = bVar2 + 1;
  } while (bVar2 < 200);
  if (bVar2 != 200) {
    FUN_0800a46c(param_1);
    iVar1 = FUN_0800a4fa();
    if (iVar1 == 0) {
      FUN_0800a46c(param_2);
      iVar1 = FUN_0800a4fa();
      if (iVar1 == 0) {
        FUN_0800a4dc();
        return 1;
      }
    }
  }
  FUN_0800a4dc();
  return 0;
}



/* FUN 0x08002a5c FUN_08002a5c */

undefined1 FUN_08002a5c(void)

{
  return *(undefined1 *)(DAT_08002a64 + 3);
}



/* FUN 0x08002a68 FUN_08002a68 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08002a68(void)

{
  byte bVar1;
  byte *pbVar2;
  char *pcVar3;
  int iVar4;
  uint in_r3;
  bool bVar5;
  uint local_18;
  
  local_18 = in_r3;
  iVar4 = FUN_08004e94(DAT_08002af4,0x20);
  bVar5 = iVar4 == 0;
  local_18._0_1_ = 0xff;
  FUN_080035d4(0x15,&local_18,1);
  pbVar2 = DAT_08002afc;
  iVar4 = DAT_08002af8;
  bVar1 = (byte)local_18 & 1;
  local_18 = CONCAT31(local_18._1_3_,(byte)local_18) & 0xffffff01;
  if (bVar1 == 0) {
    if ((bVar5) && (*(char *)(DAT_08002af8 + 3) != '\0')) goto LAB_08002aec;
  }
  else if ((!bVar5) && (*(char *)(DAT_08002af8 + 3) == '\0')) {
LAB_08002aec:
    *DAT_08002afc = 0;
    return;
  }
  bVar1 = *DAT_08002afc;
  *DAT_08002afc = bVar1 + 1;
  if (2 < (byte)(bVar1 + 1)) {
    *(bool *)(iVar4 + 3) = bVar5;
    FUN_08002c30(!bVar5);
    pcVar3 = _DAT_08002b00;
    *pbVar2 = 0;
    if (*pcVar3 == '\0') {
      FUN_08009170(s_Check_pmic_boost_status_fail__tr_08002b03 + 1);
      FUN_08009170(&DAT_08002b3c);
    }
  }
  return;
}



/* FUN 0x08002b40 FUN_08002b40 */

void FUN_08002b40(void)

{
  FUN_080039c8(0xa2,0);
  return;
}



/* FUN 0x08002b4c FUN_08002b4c */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_08002b4c(void)

{
  char *pcVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  byte local_28 [8];
  byte local_20 [8];
  byte local_18 [8];
  
  FUN_08002f60(local_18);
  FUN_08002f88(local_28);
  FUN_08004bf4();
  iVar4 = DAT_08002c08;
  uVar5 = 0;
  uVar6 = 0;
  uVar2 = 0;
  do {
    uVar6 = uVar6 << 8 | uVar5 >> 0x18;
    uVar5 = uVar5 << 8 | (uint)local_18[uVar2];
    uVar2 = uVar2 + 1 & 0xff;
  } while (uVar2 < 8);
  iVar3 = FUN_08004b94(1,DAT_08002c04,uVar5,uVar6);
  pcVar1 = _DAT_08002c0c;
  if (iVar3 == 0) {
    uVar5 = 0;
    uVar6 = 0;
    uVar2 = 0;
    do {
      uVar6 = uVar6 << 8 | uVar5 >> 0x18;
      uVar5 = uVar5 << 8 | (uint)local_28[uVar2];
      uVar2 = uVar2 + 1 & 0xff;
    } while (uVar2 < 8);
    iVar3 = FUN_08004b94(1,iVar4,uVar5,uVar6);
    if (iVar3 == 0) {
      uVar5 = 0;
      uVar6 = 0;
      uVar2 = 0;
      do {
        uVar6 = uVar6 << 8 | uVar5 >> 0x18;
        uVar5 = uVar5 << 8 | (uint)local_20[uVar2];
        uVar2 = uVar2 + 1 & 0xff;
      } while (uVar2 < 8);
      iVar4 = FUN_08004b94(1,iVar4 + 8,uVar5,uVar6);
      if (iVar4 == 0) {
        FUN_08004b20();
        return 1;
      }
    }
  }
  if (*pcVar1 == '\0') {
    FUN_08009170(s__OTA_BOX___Fail_to_program__08002c0f + 1);
    FUN_08009170(&DAT_08002c2c);
  }
  FUN_08004b20();
  return 0;
}



/* FUN 0x08002c30 FUN_08002c30 */

void FUN_08002c30(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  char local_10;
  undefined3 uStack_f;
  
  uStack_f = (undefined3)((uint)param_4 >> 8);
  if (param_1 == 0) {
    _local_10 = CONCAT31(uStack_f,9);
    bVar1 = 0;
    while( true ) {
      FUN_080039e4(0x15,8);
      FUN_080035d4(0x15,&local_10,1);
      bVar1 = bVar1 + 1;
      if (local_10 == '\b') break;
      if (2 < bVar1) {
        return;
      }
    }
  }
  else {
    _local_10 = CONCAT31(uStack_f,8);
    bVar1 = 0;
    do {
      FUN_080039e4(0x15,9);
      FUN_080035d4(0x15,&local_10,1);
      bVar1 = bVar1 + 1;
      if (local_10 == '\t') {
        return;
      }
    } while (bVar1 < 3);
  }
  return;
}



/* FUN 0x08002c8e FUN_08002c8e */

void FUN_08002c8e(int param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  uint local_8;
  
  local_8 = param_4 & 0xffffff00;
  if (param_1 != 0) {
    local_8._0_1_ = 0x3b;
    local_8._1_3_ = (int3)(param_4 >> 8);
    FUN_08009004(5,1);
    local_8 = CONCAT31(local_8._1_3_,7);
  }
  FUN_08009004(4,1,&local_8);
  return;
}



/* FUN 0x08002cb8 FUN_08002cb8 */

void FUN_08002cb8(void)

{
  FUN_0800a270();
  return;
}



/* FUN 0x08002cc0 FUN_08002cc0 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_08002cc0(void)

{
  int iVar1;
  byte *pbVar2;
  int iVar3;
  
  iVar1 = DAT_08002d14;
  iVar3 = 0;
  for (pbVar2 = DAT_08002d10; pbVar2 < DAT_08002d10 + *(int *)(DAT_08002d14 + 0x20);
      pbVar2 = pbVar2 + 4) {
    iVar3 = iVar3 + ((uint)pbVar2[3] | (uint)*pbVar2 << 0x18 |
                    (uint)pbVar2[1] << 0x10 | (uint)pbVar2[2] << 8);
  }
  if (*_DAT_08002d18 == '\0') {
    FUN_08009170(s__OTA_BOX___crc_cal__0x_x__crc_rx_08002d1b + 1,iVar3,
                 *(undefined4 *)(DAT_08002d14 + 0x24));
    FUN_08009170(&DAT_08002d44);
  }
  if (*(int *)(iVar1 + 0x24) == iVar3) {
    return 1;
  }
  return 0;
}



/* FUN 0x08002d48 FUN_08002d48 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_08002d48(void)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 in_r3;
  char cVar4;
  undefined4 local_10;
  
  local_10 = in_r3;
  FUN_08004bf4();
  puVar1 = DAT_08002dbc;
  local_10 = 0;
  *DAT_08002dbc = 2;
  if (*(char *)(DAT_08002dc0 + 0x18) == '\x01') {
    uVar3 = 0x8000;
  }
  else {
    uVar3 = 4;
  }
  puVar1[1] = uVar3;
  puVar1[2] = 0;
  puVar1[3] = 0x80;
  cVar4 = '\0';
  while( true ) {
    iVar2 = FUN_0800497c(DAT_08002dbc,&local_10);
    if (iVar2 == 0) {
      FUN_08004b20();
      return 1;
    }
    if (cVar4 == '\x03') break;
    FUN_0800a7b0(200);
    cVar4 = cVar4 + '\x01';
  }
  if (*_DAT_08002dc4 == '\0') {
    FUN_08009170(s__OTA_BOX__fail_to_erase__d_pages_08002dc7 + 1,0x80,local_10,4);
    FUN_08009170(&DAT_08002e00);
  }
  FUN_08004b20();
  return 0;
}



/* FUN 0x08002e04 FUN_08002e04 */

undefined4 FUN_08002e04(int param_1,int param_2,uint param_3)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  if (*DAT_08002eb0 == '\0') {
    FUN_08009170(&DAT_08002eb4);
  }
  if (param_3 != 0) {
    FUN_08004bf4();
    iVar1 = DAT_08002eb8;
    uVar8 = param_3 >> 3;
    if ((param_3 & 7) != 0) {
      uVar8 = uVar8 + 1;
    }
    for (uVar7 = 0; uVar7 < uVar8; uVar7 = uVar7 + 1 & 0xffff) {
      uVar5 = 0;
      uVar2 = 8;
      uVar6 = 0;
      do {
        iVar3 = uVar7 * 8 + uVar2;
        if (iVar3 + -1 < (int)param_3) {
          uVar6 = uVar6 << 8 | uVar5 >> 0x18;
          uVar4 = (uint)*(byte *)(iVar3 + param_2 + -1);
        }
        else {
          uVar6 = uVar6 << 8 | uVar5 >> 0x18;
          uVar4 = 0xff;
        }
        uVar5 = uVar5 << 8 | uVar4;
        uVar2 = uVar2 - 1 & 0xff;
      } while (uVar2 != 0);
      iVar3 = FUN_08004b94(1,iVar1 + param_1 + uVar7 * 8,uVar5,uVar6);
      if (iVar3 != 0) {
        if (*DAT_08002eb0 == '\0') {
          FUN_08009170(s__OTA_BOX__fail_to_program__08002ebc);
          FUN_08009170(&DAT_08002ed8);
        }
        FUN_08004b20();
        return 0;
      }
    }
    FUN_08004b20();
  }
  return 1;
}



/* FUN 0x08002edc FUN_08002edc */

undefined2 FUN_08002edc(void)

{
  undefined2 uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  byte bVar5;
  int iVar6;
  
  FUN_080047d4(DAT_08002f24);
  FUN_08004710(DAT_08002f24,10);
  iVar6 = 0;
  uVar4 = 0xffffffff;
  uVar3 = 0;
  bVar5 = 0;
  do {
    uVar2 = FUN_08004328(DAT_08002f24);
    if (uVar3 < uVar2) {
      uVar3 = uVar2;
    }
    if (uVar2 < uVar4) {
      uVar4 = uVar2;
    }
    bVar5 = bVar5 + 1;
    iVar6 = iVar6 + uVar2;
  } while (bVar5 < 8);
  FUN_0800483c(DAT_08002f24);
  uVar1 = FUN_08000160((iVar6 - uVar3) - uVar4,6);
  return uVar1;
}



/* FUN 0x08002f28 FUN_08002f28 */

bool FUN_08002f28(void)

{
  uint in_r3;
  uint local_8;
  
  local_8 = in_r3 & 0xffffff00;
  FUN_080035b8(0xa2,&local_8,1);
  return (local_8 & 0xff) == 1;
}



/* FUN 0x08002f46 FUN_08002f46 */

undefined4 FUN_08002f46(void)

{
  undefined4 uVar1;
  undefined1 auStack_20 [24];
  int local_8;
  
  FUN_08004a00(auStack_20);
  if (local_8 << 0xb < 0) {
    uVar1 = 1;
  }
  else {
    uVar1 = 2;
  }
  return uVar1;
}



/* FUN 0x08002f60 FUN_08002f60 */

void FUN_08002f60(int param_1)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = *DAT_08002f84;
  uVar3 = DAT_08002f84[1];
  uVar2 = 8;
  do {
    *(char *)(param_1 + uVar2 + -1) = (char)uVar1;
    uVar1 = uVar1 >> 8 | uVar3 << 0x18;
    uVar3 = uVar3 >> 8;
    uVar2 = uVar2 - 1 & 0xff;
  } while (uVar2 != 0);
  return;
}



/* FUN 0x08002f88 FUN_08002f88 */

void FUN_08002f88(int param_1)

{
  uint *puVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  puVar1 = DAT_08002fc4;
  uVar2 = *DAT_08002fc4;
  uVar4 = DAT_08002fc4[1];
  uVar3 = 8;
  do {
    *(char *)(param_1 + uVar3 + -1) = (char)uVar2;
    uVar2 = uVar2 >> 8 | uVar4 << 0x18;
    uVar4 = uVar4 >> 8;
    uVar3 = uVar3 - 1 & 0xff;
  } while (uVar3 != 0);
  uVar2 = puVar1[2];
  uVar4 = puVar1[3];
  uVar3 = 8;
  do {
    *(char *)(param_1 + uVar3 + 7) = (char)uVar2;
    uVar2 = uVar2 >> 8 | uVar4 << 0x18;
    uVar4 = uVar4 >> 8;
    uVar3 = uVar3 - 1 & 0xff;
  } while (uVar3 != 0);
  return;
}



/* FUN 0x08002fc8 FUN_08002fc8 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08002fc8(void)

{
  bool bVar1;
  char *pcVar2;
  char *pcVar3;
  byte *pbVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  int iVar8;
  char *pcVar9;
  byte bVar10;
  uint uVar11;
  char cVar12;
  byte local_2c [4];
  undefined1 auStack_28 [4];
  char local_24 [4];
  undefined1 auStack_20 [12];
  
  pcVar3 = DAT_08003344;
  if (*DAT_08003344 == '\0') {
    uVar5 = FUN_08004ed0();
    uVar6 = FUN_08004ec4();
    uVar7 = FUN_08004eb8();
    FUN_08009170(s________B200__s__08x_08x_08x______08003350,s_1_2_57_08003348,uVar7,uVar6,uVar5);
    FUN_08009170(&DAT_08003374);
  }
  pcVar9 = DAT_08003378;
  pcVar2 = DAT_08003378;
  pcVar2[8] = '\0';
  pcVar2[9] = '\0';
  pcVar2[10] = '\0';
  pcVar2[0xb] = '\0';
  pcVar2[0xc] = '\0';
  pcVar2[0xd] = '\0';
  pcVar2[0xe] = '\0';
  pcVar2[0xf] = '\0';
  pcVar9[1] = '\0';
  pcVar9[2] = '\0';
  iVar8 = FUN_08004e94(_DAT_0800337c,0x20);
  pcVar9[3] = iVar8 == 0;
  iVar8 = FUN_08004e94(0x50000000,4);
  pcVar9[4] = iVar8 == 1;
  pcVar9[0x12] = *pcVar9 == '\x03';
  pcVar2 = DAT_08003378;
  DAT_08003378[0x13] = *pcVar9 == '\x03';
  pcVar2[0x10] = '\0';
  pcVar2[0x11] = '\0';
  pcVar2[0x14] = '\0';
  pcVar2[0x15] = '\x01';
  pcVar2[0x17] = '\0';
  pcVar2[0x1c] = '\0';
  pcVar2[0x1d] = '\0';
  pcVar2[0x18] = '\0';
  pcVar2[0x19] = '\0';
  pcVar2[0x1a] = '\0';
  pcVar2[0x1b] = '\0';
  pcVar2[0x24] = '\0';
  pcVar2[0x25] = '\0';
  pcVar2[0x26] = '\0';
  pcVar2[0x27] = '\0';
  pcVar2[0x20] = '\0';
  pcVar2[0x21] = '\0';
  pcVar2[0x22] = '\0';
  pcVar2[0x23] = '\0';
  pcVar2[0x28] = '\0';
  pcVar2[0x29] = '\0';
  pcVar2[0x2a] = '\0';
  pcVar2[0x2b] = '\0';
  pcVar2[0x2c] = '\0';
  pcVar2[0x16] = '\x01';
  FUN_08003a30();
  bVar1 = true;
  cVar12 = '\0';
  local_2c[0] = 0;
  do {
    FUN_080035b8(0,local_2c,1);
    if (local_2c[0] == 0xa0) {
      if (cVar12 != '\x03') {
        if (*pcVar3 != '\0') goto LAB_080030c6;
        FUN_08009170(s_2217_self_check_done__080033b4);
        goto LAB_080030c0;
      }
      break;
    }
    FUN_08004958(100);
    cVar12 = cVar12 + '\x01';
  } while (cVar12 != '\x03');
  bVar1 = false;
  if (*pcVar3 == '\0') {
    FUN_08009170(s_Pself_check_fail__reason__2217_w_0800337f + 1,local_2c[0]);
LAB_080030c0:
    FUN_08009170(&DAT_08003374);
  }
LAB_080030c6:
  FUN_08009df4();
  cVar12 = '\0';
  local_2c[0] = 0;
LAB_080030d0:
  while (FUN_080035d4(0x14,local_2c,1), local_2c[0] != 0x14) {
    if (*pcVar3 == '\0') {
      FUN_08009170(s_using__0x70__chipid__0x_x_080033cc);
      FUN_08009170(&DAT_08003374);
    }
    if (local_2c[0] != 0) {
      if (*pcVar3 == '\0') {
        FUN_08009170(s_reset_pmic_register____080033e8);
        FUN_08009170(&DAT_08003374);
      }
      FUN_080039e4(0x14);
    }
    FUN_08004958(100);
    cVar12 = cVar12 + '\x01';
    iVar8 = FUN_08004e94(_DAT_0800337c,0x20);
    if (iVar8 != 0) goto code_r0x0800312c;
    cVar12 = '\0';
    FUN_08004958(200);
  }
  if (cVar12 != '\x03') {
    if (*pcVar3 == '\0') {
      FUN_08009170(s__pmic_self_check_done__08003437 + 1);
      FUN_08009170(&DAT_08003374);
    }
    uVar11 = 0;
    do {
      FUN_080035d4(uVar11 + 0x10 & 0xff,auStack_20 + uVar11,1);
      uVar11 = uVar11 + 1 & 0xff;
    } while (uVar11 < 8);
    if (*pcVar3 == '\0') {
      FUN_08009170(s_PMIC_reg_0x10_0x17__08003450);
    }
    FUN_080067c8(auStack_20,8);
    goto LAB_080031b2;
  }
  goto LAB_08003148;
code_r0x0800312c:
  if (cVar12 == '\x03') goto LAB_08003148;
  goto LAB_080030d0;
LAB_08003148:
  if (*pcVar3 == '\0') {
    FUN_08009170(s_self_check_fail__reason__pmic_in_08003400);
    FUN_08009170(&DAT_08003374);
  }
  FUN_08002c8e(0);
  FUN_08005094(0x2b);
  FUN_080050a8(DAT_0800342c);
  *(undefined4 *)(_DAT_08003434 + 0x18) = DAT_08003430;
  FUN_080050c4();
LAB_080031b2:
  iVar8 = FUN_08004e94(_DAT_0800337c,0x20);
  pcVar2 = DAT_08003378;
  DAT_08003378[3] = iVar8 == 0;
  FUN_08002c30(iVar8 != 0);
  if (*pcVar3 == '\0') {
    FUN_08009170(s_PMIC_enable_boost___d_08003464,pcVar2[3] == '\0');
    FUN_08009170(&DAT_08003374);
  }
  FUN_08004958(10);
  local_2c[0] = 0;
  FUN_08009040(0,1,local_2c);
  if (local_2c[0] == 0x81) {
    FUN_080090ac(0xa4,1,_DAT_0800347c);
    pbVar4 = _DAT_0800347c;
    bVar10 = *_DAT_0800347c;
    if ((int)((uint)bVar10 << 0x1c) < 0) {
      bVar10 = (bVar10 & 7) * '\x02' + 0x50;
    }
    else {
      bVar10 = (bVar10 & 7) * '\x02' + 0x60;
    }
    *_DAT_0800347c = bVar10;
    if (*pcVar3 == '\0') {
      bVar10 = *pbVar4;
      pcVar9 = s_2510_self_check_done__adjVal__d_0800347f + 1;
      goto LAB_0800324c;
    }
  }
  else {
    bVar1 = false;
    if (*pcVar3 == '\0') {
      pcVar9 = s_self_check_fail__reason__2510_wr_080034a0;
      bVar10 = local_2c[0];
LAB_0800324c:
      FUN_08009170(pcVar9,bVar10);
      FUN_08009170(&DAT_08003374);
    }
  }
  local_2c[0] = 0;
  FUN_08008fa8(0,1,local_2c);
  if (local_2c[0] >> 4 == 9) {
    FUN_08002c8e(1);
    if (*pcVar3 == '\0') {
      FUN_08009170(s_4005_self_check_done__080034d4);
      FUN_08009170(&DAT_08003374);
    }
    if (bVar1) goto LAB_080032cc;
  }
  else if (*pcVar3 == '\0') {
    FUN_08009170(s_self_check_fail__reason__4005_wr_080034ec);
    FUN_08009170(&DAT_08003374);
  }
  uVar11 = 0;
  do {
    if (*pcVar3 == '\0') {
      FUN_08009170(s_wait_for__ds_to_reset______08003520,5 - uVar11);
      FUN_08009170(&DAT_08003374);
    }
    FUN_08004958(1000);
    uVar11 = uVar11 + 1 & 0xff;
  } while (uVar11 < 5);
  FUN_0800502c();
LAB_080032cc:
  iVar8 = FUN_08002f28();
  if (iVar8 != 0) {
    if (*pcVar3 == '\0') {
      FUN_08009170(s_Show_led_for_usb_reset__0800353c);
      FUN_08009170(&DAT_08003374);
    }
    FUN_080038a0();
    FUN_08002b40();
  }
  FUN_080035f0();
  FUN_080035d4(0x10,auStack_28,1);
  FUN_080035d4(0x11,auStack_28,1);
  FUN_080039c8(10,0x40);
  FUN_080039c8(0xb,0xff);
  FUN_08009ebc(local_24);
  pcVar2[1] = local_24[0];
  FUN_0800d178();
  iVar8 = DAT_08003554;
  uVar11 = 0;
  do {
    FUN_08009040(uVar11,1,iVar8 + uVar11);
    uVar11 = uVar11 + 1 & 0xff;
  } while (uVar11 < 8);
  FUN_0800d218();
  return;
}



/* FUN 0x080035b8 FUN_080035b8 */

void FUN_080035b8(void)

{
  int iVar1;
  
  iVar1 = DAT_080035d0;
  if (*(char *)(DAT_080035d0 + 1) == '\0') {
    *(undefined1 *)(DAT_080035d0 + 1) = 1;
    FUN_080028b4();
    *(undefined1 *)(iVar1 + 1) = 0;
  }
  return;
}



/* FUN 0x080035d4 FUN_080035d4 */

void FUN_080035d4(void)

{
  int iVar1;
  
  iVar1 = DAT_080035ec;
  if (*(char *)(DAT_080035ec + 1) == '\0') {
    *(undefined1 *)(DAT_080035ec + 1) = 1;
    FUN_0800292c();
    *(undefined1 *)(iVar1 + 1) = 0;
  }
  return;
}



/* FUN 0x080035f0 FUN_080035f0 */

void FUN_080035f0(void)

{
  FUN_080039e4(0x13,0x90);
  FUN_08004958(2);
  FUN_080039e4(0x16,0);
  FUN_08004958(2);
  FUN_080039e4(0x19,2);
  FUN_08004958(2);
  FUN_080039e4(0x17,0x28);
  FUN_08004958(2);
  FUN_080039e4(0x18,1);
  FUN_08004958(2);
  FUN_080039e4(0x1a,0);
  FUN_08004958(2);
  FUN_080039e4(0x1b,1);
  FUN_08004958(2);
  return;
}



/* FUN 0x08003656 FUN_08003656 */

void FUN_08003656(void)

{
  FUN_080039c8(0xa2,1);
  return;
}



/* FUN 0x08003664 FUN_08003664 */

void FUN_08003664(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  char *pcVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  byte bVar8;
  undefined4 local_18;
  
  puVar1 = DAT_08003700;
  *DAT_08003700 = 2;
  local_18 = param_4;
  iVar3 = FUN_08002f46();
  if (iVar3 == 1) {
    uVar4 = 4;
  }
  else {
    uVar4 = 0x8000;
  }
  puVar1[1] = uVar4;
  puVar1[2] = 0x7f;
  puVar1[3] = 1;
  FUN_08004bf4();
  bVar8 = 0;
  do {
    iVar3 = FUN_0800497c(DAT_08003700,&local_18);
    if (iVar3 == 0) break;
    FUN_08004958(10);
    bVar8 = bVar8 + 1;
  } while (bVar8 < 3);
  pcVar2 = DAT_08003704;
  if (bVar8 == 3) {
    if (*DAT_08003704 != '\0') goto LAB_080036f8;
    FUN_08009170(s_fail_to_erase__err_0x_x_0800370c,local_18);
  }
  else {
    uVar6 = 0;
    uVar7 = 0;
    uVar5 = 0;
    do {
      uVar7 = uVar7 << 8 | uVar6 >> 0x18;
      uVar6 = uVar6 << 8 | (uint)*(byte *)(param_1 + uVar5);
      uVar5 = uVar5 + 1 & 0xff;
    } while (uVar5 < 8);
    iVar3 = FUN_08004b94(1,DAT_08003708,uVar6,uVar7);
    if ((iVar3 == 0) || (*pcVar2 != '\0')) goto LAB_080036f8;
    FUN_08009170(s_fail_to_program__08003724);
  }
  FUN_08009170(&LAB_08003738);
LAB_080036f8:
  FUN_08004b20();
  return;
}



/* FUN 0x0800373c FUN_0800373c */

undefined4 FUN_0800373c(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  char *pcVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  byte bVar8;
  undefined4 local_18;
  
  puVar1 = DAT_0800380c;
  *DAT_0800380c = 2;
  local_18 = param_4;
  iVar3 = FUN_08002f46();
  if (iVar3 == 1) {
    uVar4 = 4;
  }
  else {
    uVar4 = 0x8000;
  }
  puVar1[1] = uVar4;
  puVar1[2] = 0x7e;
  puVar1[3] = 1;
  FUN_08004bf4();
  bVar8 = 0;
  do {
    iVar3 = FUN_0800497c(DAT_0800380c,&local_18);
    if (iVar3 == 0) break;
    FUN_08004958(10);
    bVar8 = bVar8 + 1;
  } while (bVar8 < 3);
  pcVar2 = DAT_08003810;
  if (bVar8 == 3) {
    if (*DAT_08003810 != '\0') goto LAB_080037c8;
    FUN_08009170(s_fail_to_erase__err_0x_x_08003818,local_18);
  }
  else {
    uVar6 = 0;
    uVar7 = 0;
    uVar5 = 0;
    do {
      uVar7 = uVar7 << 8 | uVar6 >> 0x18;
      uVar6 = uVar6 << 8 | (uint)*(byte *)(param_1 + uVar5);
      uVar5 = uVar5 + 1 & 0xff;
    } while (uVar5 < 8);
    iVar3 = FUN_08004b94(1,DAT_08003814,uVar6,uVar7);
    if (iVar3 == 0) {
      uVar6 = 0;
      uVar7 = 0;
      uVar5 = 0;
      do {
        uVar7 = uVar7 << 8 | uVar6 >> 0x18;
        uVar6 = uVar6 << 8 | (uint)*(byte *)(param_1 + uVar5 + 8);
        uVar5 = uVar5 + 1 & 0xff;
      } while (uVar5 < 8);
      iVar3 = FUN_08004b94(1,DAT_08003814 + 8,uVar6,uVar7);
      if (iVar3 == 0) {
        FUN_08004b20();
        return 1;
      }
    }
    if (*pcVar2 != '\0') goto LAB_080037c8;
    FUN_08009170(s_fail_to_program__08003834);
  }
  FUN_08009170(&DAT_08003830);
LAB_080037c8:
  FUN_08004b20();
  return 0;
}



/* FUN 0x08003848 FUN_08003848 */

void FUN_08003848(int param_1)

{
  byte bVar1;
  
  if (((*(char *)(DAT_0800389c + 0x11) == '\0') || (*(char *)(DAT_0800389c + 0x10) == '\0')) &&
     (param_1 == 0)) {
    if (*(char *)(DAT_0800389c + 0x11) != '\0') {
      return;
    }
    if (*(char *)(DAT_0800389c + 0x10) != '\0') {
      return;
    }
    bVar1 = *(byte *)(DAT_0800389c + 1);
  }
  else {
    bVar1 = *(byte *)(DAT_0800389c + 0x32);
    if (*(byte *)(DAT_0800389c + 0x4e) <= *(byte *)(DAT_0800389c + 0x32)) {
      bVar1 = *(byte *)(DAT_0800389c + 0x4e);
    }
  }
  if (bVar1 < 0x5a) {
    FUN_08006b80(1);
    FUN_08006b98(0);
    return;
  }
  FUN_08006b98(1);
  FUN_08006b80(0);
  return;
}



/* FUN 0x080038a0 FUN_080038a0 */

void FUN_080038a0(void)

{
  byte bVar1;
  
  bVar1 = 0;
  do {
    FUN_08006b80(1);
    FUN_08006b98(0);
    FUN_08004958(200);
    FUN_08006b80(0);
    FUN_08006b98(1);
    FUN_08004958(200);
    bVar1 = bVar1 + 1;
  } while (bVar1 < 3);
  FUN_08006b80(0);
  FUN_08006b98(0);
  return;
}



/* FUN 0x080038e0 FUN_080038e0 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_080038e0(void)

{
  uint uVar1;
  char *pcVar2;
  undefined4 uVar3;
  undefined1 auStack_30 [24];
  uint local_18;
  
  FUN_08004a00(auStack_30);
  pcVar2 = _DAT_08003960;
  uVar1 = DAT_0800395c;
  if ((int)(local_18 << 0xb) < 0) {
    if (*_DAT_08003960 == '\0') {
      FUN_08009170(s_Swap_bank_1_>2____RESET__cur_ob_v_08003990,local_18);
      FUN_08009170(&DAT_0800398c);
    }
    local_18 = local_18 & ~uVar1;
  }
  else {
    if (*_DAT_08003960 == '\0') {
      FUN_08009170(s_Swap_bank_2_>1____RESET__cur_ob_v_08003963 + 1,local_18);
      FUN_08009170(&DAT_0800398c);
    }
    local_18 = local_18 & ~uVar1 | uVar1;
  }
  FUN_08004bf4();
  FUN_08004b6c();
  if (*pcVar2 == '\0') {
    uVar3 = FUN_08004a6c(auStack_30);
    FUN_08009170(s_ob_program___d_080039b8,uVar3);
    FUN_08009170(&DAT_0800398c);
  }
  FUN_0800a7b0(100);
  FUN_08004b3c();
  FUN_08004b50();
  FUN_08004b20();
  return;
}



/* FUN 0x080039c8 FUN_080039c8 */

void FUN_080039c8(void)

{
  int iVar1;
  
  iVar1 = DAT_080039e0;
  if (*(char *)(DAT_080039e0 + 1) == '\0') {
    *(undefined1 *)(DAT_080039e0 + 1) = 1;
    FUN_080029a4();
    *(undefined1 *)(iVar1 + 1) = 0;
  }
  return;
}



/* FUN 0x080039e4 FUN_080039e4 */

void FUN_080039e4(void)

{
  int iVar1;
  
  iVar1 = DAT_080039fc;
  if (*(char *)(DAT_080039fc + 1) == '\0') {
    *(undefined1 *)(DAT_080039fc + 1) = 1;
    FUN_08002a00();
    *(undefined1 *)(iVar1 + 1) = 0;
  }
  return;
}



/* FUN 0x08003a00 FUN_08003a00 */

void FUN_08003a00(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_08003a2c;
  if (param_1 != 0) {
    *(undefined1 *)(DAT_08003a2c + 0x34) = 0;
    *(undefined4 *)(iVar1 + 0x3c) = 0;
    *(undefined4 *)(iVar1 + 0x48) = 0;
    *(undefined2 *)(iVar1 + 0x38) = 0;
    *(undefined1 *)(iVar1 + 0x31) = 0;
    *(undefined1 *)(iVar1 + 0x12) = 1;
    return;
  }
  *(undefined1 *)(DAT_08003a2c + 0x50) = 0;
  *(undefined4 *)(iVar1 + 0x58) = 0;
  *(undefined4 *)(iVar1 + 100) = 0;
  *(undefined2 *)(iVar1 + 0x54) = 0;
  *(undefined1 *)(iVar1 + 0x4d) = 0;
  *(undefined1 *)(iVar1 + 0x13) = 1;
  return;
}



/* FUN 0x08003a30 FUN_08003a30 */

void FUN_08003a30(void)

{
  FUN_08003a3c();
  FUN_08003a60();
  return;
}



/* FUN 0x08003a3c FUN_08003a3c */

void FUN_08003a3c(void)

{
  int iVar1;
  
  iVar1 = DAT_08003a5c;
  *(undefined1 *)(DAT_08003a5c + 0x10) = 0;
  *(undefined1 *)(iVar1 + 0x11) = 0;
  *(undefined2 *)(iVar1 + 0x18) = 0;
  *(undefined1 *)(iVar1 + 0x12) = 0;
  *(undefined1 *)(iVar1 + 0x13) = 0;
  *(undefined2 *)(iVar1 + 0x16) = 0;
  *(undefined1 *)(iVar1 + 0x14) = 0;
  *(undefined4 *)(iVar1 + 0x20) = 0;
  *(undefined4 *)(iVar1 + 0x1c) = 0;
  *(undefined4 *)(iVar1 + 0x24) = 0;
  *(undefined4 *)(iVar1 + 0x28) = 0;
  return;
}



/* FUN 0x08003a60 FUN_08003a60 */

void FUN_08003a60(void)

{
  int iVar1;
  
  iVar1 = DAT_08003a80;
  *(undefined1 *)(DAT_08003a80 + 0xc) = 0;
  *(undefined1 *)(iVar1 + 0xd) = 0;
  *(undefined2 *)(iVar1 + 0x14) = 0;
  *(undefined1 *)(iVar1 + 0xe) = 0;
  *(undefined1 *)(iVar1 + 0xf) = 0;
  *(undefined2 *)(iVar1 + 0x12) = 0;
  *(undefined1 *)(iVar1 + 0x10) = 0;
  *(undefined4 *)(iVar1 + 0x1c) = 0;
  *(undefined4 *)(iVar1 + 0x18) = 0;
  *(undefined4 *)(iVar1 + 0x20) = 0;
  *(undefined4 *)(iVar1 + 0x24) = 0;
  return;
}



/* FUN 0x08003a84 FUN_08003a84 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08003a84(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int in_r3;
  int local_10;
  
  local_10 = in_r3;
  iVar3 = FUN_08009ebc(&local_10);
  iVar2 = _DAT_08003b34;
  iVar1 = DAT_08003b30;
  if (iVar3 == 0) {
    if (*(char *)(DAT_08003b30 + 3) != '\0') {
      if (local_10 <= (int)(uint)*(byte *)(DAT_08003b30 + 1)) {
        if (*(char *)(_DAT_08003b34 + 7) == '\0') {
          FUN_08009170(s_Bat_change_not_used____d__>__d_08003b70);
          FUN_08009170(&DAT_08003b50);
        }
        goto LAB_08003b24;
      }
    }
    if (*(char *)(_DAT_08003b34 + 7) == '\0') {
      FUN_08009170(s_Bat_change___d__>__d_08003b37 + 1,*(undefined1 *)(DAT_08003b30 + 1),local_10);
      FUN_08009170(&DAT_08003b50);
    }
    *(char *)(iVar1 + 1) = (char)local_10;
    if (*(char *)(iVar2 + 7) == '\0') {
      FUN_08009170(s_Bat_change__send_0x13_soon__08003b54);
      FUN_08009170(&DAT_08003b50);
    }
    if (((*(char *)(DAT_08003b30 + 0x31) == '\0') || (*(short *)(iVar1 + 0x38) == 0)) ||
       (*(char *)(DAT_08003b30 + 0x33) != '\0')) {
      *(undefined4 *)(iVar1 + 0x3c) = 0;
    }
    else {
      FUN_08003a00(1);
    }
    if (((*(char *)(DAT_08003b30 + 0x4d) == '\0') || (*(short *)(DAT_08003b30 + 0x54) == 0)) ||
       (*(char *)(DAT_08003b30 + 0x4f) != '\0')) {
      *(undefined4 *)(iVar1 + 0x58) = 0;
    }
    else {
      FUN_08003a00(0);
    }
  }
LAB_08003b24:
  FUN_080039c8(10,0x40);
  return;
}



/* FUN 0x08003b90 FUN_08003b90 */

undefined4 FUN_08003b90(void)

{
  int iVar1;
  
  iVar1 = FUN_080064ec(DAT_08003bac,DAT_08003ba8,1);
  if (iVar1 != 0) {
    return 0;
  }
  return 1;
}



/* FUN 0x08003bb0 FUN_08003bb0 */

void FUN_08003bb0(undefined4 param_1,undefined4 param_2)

{
  FUN_080066ac(DAT_08003bc4,param_1,param_2,DAT_08003bc0);
  return;
}



/* FUN 0x08003bc8 FUN_08003bc8 */

void FUN_08003bc8(void)

{
  undefined4 in_r3;
  undefined4 uStack_8;
  
  uStack_8 = in_r3;
  if (((*(uint *)(DAT_08003c14 + 0xc) & 1) == 0) && ((*(uint *)(DAT_08003c14 + 0x10) & 1) == 0)) {
    if (*DAT_08003c18 == '\0') {
      FUN_08009170(s_2217_int_08003c1c);
      FUN_08009170(&DAT_08003c28);
    }
    FUN_08003a84();
  }
  else {
    FUN_080035d4(0x10,&uStack_8,1);
    FUN_080035d4(0x11,&uStack_8,1);
  }
  FUN_08004d04(1);
  FUN_08004d04(2);
  return;
}



/* FUN 0x08003c2c FUN_08003c2c */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08003c2c(void)

{
  int iVar1;
  undefined1 *puVar2;
  char *pcVar3;
  undefined4 *puVar4;
  int iVar5;
  
  puVar2 = DAT_08003ce4;
  iVar1 = DAT_08003ce0;
  *(char *)(DAT_08003ce0 + 4) = (char)((*(uint *)(DAT_08003cdc + 0xc) & 7) >> 2);
  pcVar3 = _DAT_08003ce8;
  *puVar2 = 1;
  if (*pcVar3 == '\0') {
    FUN_08009170(s_hall_int__isOpen__d_08003ceb + 1);
    FUN_08009170(&DAT_08003d00);
  }
  puVar4 = _DAT_08003d04;
  if (*(char *)(iVar1 + 2) == '\0') {
    FUN_08003848();
    *(undefined1 *)(iVar1 + 2) = 1;
    FUN_0800a888(*puVar4,2);
  }
  iVar5 = FUN_08002a5c();
  if (iVar5 == 0) {
    *(undefined1 *)(iVar1 + 0x17) = 0;
  }
  else {
    FUN_0800a888(*puVar4,0x1000);
  }
  FUN_08004d04(4);
  if (*pcVar3 == '\0') {
    FUN_08009170(s_Hall_int__send_0x13_soon__08003d07 + 1);
    FUN_08009170(&DAT_08003d00);
  }
  if (((*(char *)(DAT_08003ce0 + 0x31) == '\0') || (*(short *)(iVar1 + 0x38) == 0)) ||
     (*(char *)(DAT_08003ce0 + 0x33) != '\0')) {
    *(undefined4 *)(iVar1 + 0x3c) = 0;
  }
  else {
    FUN_08003a00(1);
  }
  if (((*(char *)(DAT_08003ce0 + 0x4d) != '\0') && (*(short *)(DAT_08003ce0 + 0x54) != 0)) &&
     (*(char *)(DAT_08003ce0 + 0x4f) == '\0')) {
    FUN_08003a00(0);
    return;
  }
  *(undefined4 *)(iVar1 + 0x58) = 0;
  return;
}



/* FUN 0x08003d24 FUN_08003d24 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08003d24(void)

{
  int iVar1;
  char *pcVar2;
  undefined4 *puVar3;
  int *piVar4;
  int iVar5;
  
  pcVar2 = _DAT_08003e30;
  iVar1 = DAT_08003e2c;
  *(char *)(DAT_08003e2c + 3) = (char)((*(uint *)(DAT_08003e28 + 0x10) & 0x3f) >> 5);
  if (*pcVar2 == '\0') {
    FUN_08009170(s_USB_int__hasUsb__d_08003e33 + 1);
    FUN_08009170(&DAT_08003e48);
  }
  puVar3 = DAT_08003e4c;
  if (*(char *)(iVar1 + 2) == '\0') {
    FUN_08003848();
    *(undefined1 *)(iVar1 + 2) = 1;
    FUN_0800a888(*puVar3,2);
  }
  iVar5 = FUN_08002a5c();
  if (iVar5 == 0) {
    *(undefined1 *)(iVar1 + 0x17) = 0;
  }
  else {
    FUN_0800a888(*puVar3,0x1000);
  }
  piVar4 = _DAT_08003e50;
  if (*(char *)(iVar1 + 3) == '\0') {
    iVar5 = *(int *)(iVar1 + 8);
    if ((((uint)(iVar5 - *_DAT_08003e50) < 7) && (*_DAT_08003e50 != 0)) && (_DAT_08003e50[1] != 0))
    {
      if (*pcVar2 == '\0') {
        FUN_08009170(s_Reset_GLS_and_BOX__reason__USB__08003e53 + 1);
        FUN_08009170(&DAT_08003e48);
      }
      FUN_08003656();
      FUN_0800a888(*puVar3,0x200);
    }
    else {
      *_DAT_08003e50 = _DAT_08003e50[1];
      piVar4[1] = iVar5;
    }
  }
  FUN_08002c30(*(char *)(iVar1 + 3) == '\0');
  FUN_08004d04(0x20);
  if (*pcVar2 == '\0') {
    FUN_08009170(s_USB_int__send_0x13_soon__08003e74);
    FUN_08009170(&DAT_08003e48);
  }
  if (((*(char *)(DAT_08003e2c + 0x31) == '\0') || (*(short *)(iVar1 + 0x38) == 0)) ||
     (*(char *)(DAT_08003e2c + 0x33) != '\0')) {
    *(undefined4 *)(iVar1 + 0x3c) = 0;
  }
  else {
    FUN_08003a00(1);
  }
  if (((*(char *)(DAT_08003e2c + 0x4d) != '\0') && (*(short *)(DAT_08003e2c + 0x54) != 0)) &&
     (*(char *)(DAT_08003e2c + 0x4f) == '\0')) {
    FUN_08003a00(0);
    return;
  }
  *(undefined4 *)(iVar1 + 0x58) = 0;
  return;
}



/* FUN 0x08003e90 FUN_08003e90 */

void FUN_08003e90(void)

{
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* FUN 0x08003e94 FUN_08003e94 */

void FUN_08003e94(uint param_1)

{
  *(uint *)(DAT_08003ea4 + 0x14) = *(uint *)(DAT_08003ea4 + 0x14) | param_1 | 0x10000;
  return;
}



/* FUN 0x08003ea8 FUN_08003ea8 */

uint FUN_08003ea8(void)

{
  uint uVar1;
  
  uVar1 = *(uint *)(DAT_08003ebc + 0x20) & 0xff;
  if ((uVar1 != 0xaa) && (uVar1 != 0xcc)) {
    uVar1 = 0xbb;
  }
  return uVar1;
}



/* FUN 0x08003ec0 FUN_08003ec0 */

uint FUN_08003ec0(void)

{
  return *(uint *)(DAT_08003ecc + 0x20) & DAT_08003ed0;
}



/* FUN 0x08003ed4 FUN_08003ed4 */

void FUN_08003ed4(uint param_1,uint param_2,uint param_3)

{
  *(uint *)(DAT_08003ee8 + 0x20) =
       *(uint *)(DAT_08003ee8 + 0x20) & ~(param_1 | 0xff) | param_2 | param_3;
  return;
}



/* FUN 0x08003eec FUN_08003eec */

void FUN_08003eec(int param_1,int param_2)

{
  uint uVar1;
  
  uVar1 = *(uint *)(DAT_08003f10 + 0x14) & DAT_08003f14;
  if (param_1 == 4) {
    uVar1 = uVar1 & 0xffffdfff;
  }
  else {
    uVar1 = uVar1 | 0x2000;
  }
  *(uint *)(DAT_08003f10 + 0x14) = param_2 << 3 | uVar1 | DAT_08003f18;
  return;
}



/* FUN 0x08003f1c FUN_08003f1c */

void FUN_08003f1c(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  *(uint *)(DAT_08003f34 + 0x14) = *(uint *)(DAT_08003f34 + 0x14) | 1;
  *param_1 = param_3;
  InstructionSynchronizationBarrier(0xf);
  param_1[1] = param_4;
  return;
}



/* FUN 0x08003f38 FUN_08003f38 */

void FUN_08003f38(undefined4 *param_1,undefined4 *param_2)

{
  bool bVar1;
  int iVar2;
  uint uVar3;
  byte bVar4;
  undefined4 uVar5;
  
  iVar2 = DAT_08003f68;
  bVar4 = 0;
  *(uint *)(DAT_08003f68 + 0x14) = *(uint *)(DAT_08003f68 + 0x14) | 0x40000;
  uVar3 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar3 = isIRQinterruptsEnabled();
  }
  disableIRQinterrupts();
  do {
    uVar5 = *param_2;
    param_2 = param_2 + 1;
    bVar4 = bVar4 + 1;
    *param_1 = uVar5;
    param_1 = param_1 + 1;
  } while (bVar4 < 0x40);
  do {
  } while ((*(uint *)(iVar2 + 0x10) & 0x3ffff) >> 0x10 != 0);
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar3 & 1) == 1);
  }
  return;
}



/* FUN 0x08003f6c FUN_08003f6c */

undefined4 FUN_08003f6c(int param_1)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  iVar2 = FUN_08004eac();
  iVar1 = DAT_08003fc0;
  while ((*(uint *)(iVar1 + 0x10) & 0x30000) != 0) {
    uVar3 = FUN_08004eac();
    if ((uint)(iVar2 + param_1) <= uVar3) {
      return 3;
    }
  }
  uVar3 = *(uint *)(iVar1 + 0x10) & DAT_08003fc4;
  *(undefined4 *)(iVar1 + 0x10) = DAT_08003fc8;
  if (uVar3 == 0) {
    iVar2 = FUN_08004eac();
    do {
      if (-1 < *(int *)(iVar1 + 0x10) << 0xd) {
        return 0;
      }
      uVar3 = FUN_08004eac();
    } while (uVar3 < (uint)(iVar2 + param_1));
    return 3;
  }
  *(uint *)(DAT_08003fcc + 4) = uVar3;
  return 1;
}



/* FUN 0x08003fd0 FUN_08003fd0 */

undefined8 FUN_08003fd0(int *param_1)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  uint local_20;
  
  local_20 = 0;
  iVar6 = 0;
  if ((char)param_1[0x15] == '\x01') {
    return 2;
  }
  *(undefined1 *)(param_1 + 0x15) = 1;
  uVar1 = FUN_08000734(param_1);
  iVar2 = FUN_08006782(*param_1);
  if (iVar2 == 0) {
    param_1[0x16] = param_1[0x16] & 0xfffffeffU | 2;
    iVar2 = *param_1;
    uVar3 = *(uint *)(iVar2 + 0xc) & DAT_080040ec;
    *(uint *)(iVar2 + 0xc) = *(uint *)(iVar2 + 0xc) & ~DAT_080040ec;
    uVar5 = 0;
    do {
      *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & 0xffffffe8 | 0x80000000;
      while (*(int *)(*param_1 + 8) < 0) {
        local_20 = local_20 + 1;
        if (DAT_080040f0 <= local_20) {
          param_1[0x16] = param_1[0x16] & 0xfffffffdU | 0x10;
          *(undefined1 *)(param_1 + 0x15) = 0;
          goto LAB_080040c2;
        }
      }
      uVar5 = uVar5 + 1;
      iVar6 = (*(uint *)(*param_1 + 0xb4) & 0x7f) + iVar6;
    } while (uVar5 < 8);
    uVar4 = FUN_08000160(iVar6);
    uVar5 = DAT_080040f4;
    *(uint *)(*param_1 + 8) = (*(uint *)(*param_1 + 8) & DAT_080040f4) + 1;
    *(uint *)(*param_1 + 0xb4) = *(uint *)(*param_1 + 0xb4) & 0xffffff80 | uVar4;
    *(uint *)(*param_1 + 8) = (*(uint *)(*param_1 + 8) & uVar5) + 2;
    iVar6 = FUN_08004eac();
    while (iVar2 = FUN_08006782(*param_1), iVar2 != 0) {
      iVar2 = FUN_08004eac();
      if ((2 < (uint)(iVar2 - iVar6)) && (iVar2 = FUN_08006782(*param_1), iVar2 != 0)) {
        param_1[0x16] = param_1[0x16] | 0x10;
        param_1[0x17] = param_1[0x17] | 1;
LAB_080040c2:
        return CONCAT44(local_20,1);
      }
    }
    *(uint *)(*param_1 + 0xc) = *(uint *)(*param_1 + 0xc) | uVar3;
    uVar3 = (param_1[0x16] & 0xfffffffcU) + 1;
  }
  else {
    uVar3 = param_1[0x16] | 0x10;
  }
  param_1[0x16] = uVar3;
  *(undefined1 *)(param_1 + 0x15) = 0;
  return CONCAT44(local_20,uVar1);
}



/* FUN 0x080040f8 FUN_080040f8 */

void FUN_080040f8(void)

{
  return;
}



/* FUN 0x080040fa FUN_080040fa */

void FUN_080040fa(void)

{
  return;
}



/* FUN 0x080040fc FUN_080040fc */

void FUN_080040fc(void)

{
  return;
}



/* FUN 0x080040fe FUN_080040fe */

void FUN_080040fe(void)

{
  return;
}



/* FUN 0x08004100 FUN_08004100 */

undefined4 FUN_08004100(int *param_1,uint *param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  
  uVar5 = 0;
  uVar6 = 0;
  if ((char)param_1[0x15] == '\x01') {
    return 2;
  }
  *(undefined1 *)(param_1 + 0x15) = 1;
  iVar1 = FUN_0800678a(*param_1);
  if (iVar1 != 0) {
    param_1[0x16] = param_1[0x16] | 0x20;
    uVar5 = 1;
    goto LAB_0800412c;
  }
  if (param_2[1] == 2) {
    if ((param_1[4] == -0x80000000) || (param_1[4] == -0x7ffffffc)) {
      *(uint *)(*param_1 + 0x28) = *(uint *)(*param_1 + 0x28) & ~(*param_2 & 0x7ffff);
    }
    uVar3 = *param_2;
    if (-1 < (int)uVar3) goto LAB_0800412c;
    if (uVar3 == DAT_08004310) {
      uVar3 = uVar3 << 0xb;
      uVar4 = DAT_08004310;
    }
    else if (uVar3 == DAT_0800431c) {
      uVar3 = uVar3 << 10;
      uVar4 = DAT_0800431c;
    }
    else {
      if (uVar3 != DAT_08004320) goto LAB_0800412c;
      uVar3 = uVar3 << 9;
      uVar4 = DAT_08004320;
    }
    uVar3 = *DAT_0800430c & 0x1c00000 & ~uVar3;
  }
  else {
    if ((param_1[4] == -0x80000000) || (param_1[4] == -0x7ffffffc)) {
      iVar1 = *param_1;
      uVar3 = *(uint *)(iVar1 + 0x28) | *param_2 & 0x7ffff;
LAB_0800423a:
      *(uint *)(iVar1 + 0x28) = uVar3;
    }
    else {
      uVar4 = param_2[1] & 0x1f;
      uVar3 = *param_2;
      if ((uVar3 & 0x7ffff) == 0) {
        uVar3 = (uVar3 & 0x7fffffff) >> 0x1a;
      }
      else if ((uVar3 & 1) == 0) {
        if ((int)(uVar3 << 0x1e) < 0) {
          uVar3 = 1;
        }
        else if ((int)(uVar3 << 0x1d) < 0) {
          uVar3 = 2;
        }
        else if ((int)(uVar3 << 0x1c) < 0) {
          uVar3 = 3;
        }
        else if ((int)(uVar3 << 0x1b) < 0) {
          uVar3 = 4;
        }
        else if ((int)(uVar3 << 0x1a) < 0) {
          uVar3 = 5;
        }
        else if ((int)(uVar3 << 0x19) < 0) {
          uVar3 = 6;
        }
        else if ((int)(uVar3 << 0x18) < 0) {
          uVar3 = 7;
        }
        else if ((int)(uVar3 << 0x17) < 0) {
          uVar3 = 8;
        }
        else if ((int)(uVar3 << 0x16) < 0) {
          uVar3 = 9;
        }
        else if ((int)(uVar3 << 0x15) < 0) {
          uVar3 = 10;
        }
        else if ((int)(uVar3 << 0x14) < 0) {
          uVar3 = 0xb;
        }
        else if ((int)(uVar3 << 0x13) < 0) {
          uVar3 = 0xc;
        }
        else if ((int)(uVar3 << 0x12) < 0) {
          uVar3 = 0xd;
        }
        else if ((int)(uVar3 << 0x11) < 0) {
          uVar3 = 0xe;
        }
        else if ((int)(uVar3 << 0x10) < 0) {
          uVar3 = 0xf;
        }
        else if ((int)(uVar3 << 0xf) < 0) {
          uVar3 = 0x10;
        }
        else if ((int)(uVar3 << 0xe) < 0) {
          uVar3 = 0x11;
        }
        else {
          if (-1 < (int)(uVar3 << 0xd)) goto LAB_0800420a;
          uVar3 = 0x12;
        }
      }
      else {
LAB_0800420a:
        uVar3 = 0;
      }
      param_1[0x18] = param_1[0x18] & ~(0xf << uVar4) | uVar3 << uVar4;
      if ((param_2[1] >> 2) + 1 <= (uint)param_1[7]) {
        iVar1 = *param_1;
        uVar3 = param_2[1] & 0x1f;
        uVar3 = *(uint *)(iVar1 + 0x28) & ~(0xf << uVar3) |
                ((*param_2 & 0x3fffffff) >> 0x1a) << uVar3;
        goto LAB_0800423a;
      }
    }
    *(uint *)(*param_1 + 0x14) =
         *(uint *)(*param_1 + 0x14) & ~(*param_2 << 8) | *param_2 << 8 & param_2[2] & 0x7ffffff;
    uVar2 = *param_2;
    if (-1 < (int)uVar2) goto LAB_0800412c;
    uVar3 = *DAT_0800430c & 0x1c00000;
    if ((uVar2 == DAT_08004310) && (-1 < (int)(uVar3 << 8))) {
      FUN_080067a2(DAT_0800430c,uVar3 | uVar2 << 0xb,DAT_0800430c,uVar3 << 8,uVar6);
      iVar1 = FUN_08000160(*DAT_08004318,DAT_08004314);
      for (iVar1 = (iVar1 + 1) * 0xc; iVar1 != 0; iVar1 = iVar1 + -1) {
      }
      goto LAB_0800412c;
    }
    if ((uVar2 == DAT_0800431c) && (-1 < (int)(uVar3 << 7))) {
      uVar2 = uVar2 << 10;
      uVar4 = uVar3 << 7;
    }
    else {
      if ((uVar2 != DAT_08004320) || ((int)(uVar3 << 9) < 0)) goto LAB_0800412c;
      uVar2 = DAT_08004320 << 9;
      uVar4 = DAT_08004320;
    }
    uVar3 = uVar3 | uVar2;
  }
  FUN_080067a2(DAT_0800430c,uVar3,DAT_0800430c,uVar4,uVar6);
LAB_0800412c:
  *(undefined1 *)(param_1 + 0x15) = 0;
  return uVar5;
}



/* FUN 0x08004324 FUN_08004324 */

void FUN_08004324(void)

{
  return;
}



/* FUN 0x08004326 FUN_08004326 */

void FUN_08004326(void)

{
  return;
}



/* FUN 0x08004328 FUN_08004328 */

undefined4 FUN_08004328(int *param_1)

{
  return *(undefined4 *)(*param_1 + 0x40);
}



/* FUN 0x08004330 FUN_08004330 */

void FUN_08004330(int *param_1)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = *(int *)*param_1;
  iVar3 = ((int *)*param_1)[1];
  if ((iVar4 << 0x1e < 0) && (iVar3 << 0x1e < 0)) {
    if (-1 < param_1[0x16] << 0x1b) {
      param_1[0x16] = param_1[0x16] | 0x800;
    }
    FUN_080040fa(param_1);
    *(undefined4 *)*param_1 = 2;
  }
  uVar1 = DAT_0800447c;
  if (((iVar4 << 0x1d < 0) && (iVar3 << 0x1d < 0)) || ((iVar4 << 0x1c < 0 && (iVar3 << 0x1c < 0))))
  {
    if (-1 < param_1[0x16] << 0x1b) {
      param_1[0x16] = param_1[0x16] | 0x200;
    }
    iVar2 = FUN_08006792(*param_1);
    if ((iVar2 != 0) && (*(char *)((int)param_1 + 0x1a) == '\0')) {
      if (*(int *)*param_1 << 0x1c < 0) {
        iVar2 = FUN_0800678a();
        if (iVar2 == 0) {
          *(uint *)(*param_1 + 4) = *(uint *)(*param_1 + 4) & 0xfffffff3;
          param_1[0x16] = param_1[0x16] & ~uVar1 | 1;
        }
        else {
          param_1[0x16] = param_1[0x16] | 0x20;
          param_1[0x17] = param_1[0x17] | 1;
        }
      }
    }
    FUN_08004324(param_1);
    *(undefined4 *)*param_1 = 0xc;
  }
  if ((iVar4 << 0x18 < 0) && (iVar3 << 0x18 < 0)) {
    param_1[0x16] = param_1[0x16] | 0x10000;
    FUN_080046a0(param_1);
    *(undefined4 *)*param_1 = 0x80;
  }
  if ((iVar4 << 0x17 < 0) && (iVar3 << 0x17 < 0)) {
    param_1[0x16] = param_1[0x16] | 0x20000;
    FUN_080040fc(param_1);
    *(uint *)*param_1 = uVar1;
  }
  if ((iVar4 << 0x16 < 0) && (iVar3 << 0x16 < 0)) {
    param_1[0x16] = param_1[0x16] | 0x40000;
    FUN_080040fe(param_1);
    *(undefined4 *)*param_1 = 0x200;
  }
  if ((iVar4 << 0x1b < 0) && (iVar3 << 0x1b < 0)) {
    if ((param_1[0xc] == 0) || ((*(uint *)(*param_1 + 0xc) & 3) != 0)) {
      param_1[0x16] = param_1[0x16] | 0x400;
      param_1[0x17] = param_1[0x17] | 2;
      FUN_08004326(param_1);
    }
    *(undefined4 *)*param_1 = 0x10;
  }
  if ((iVar4 << 0x12 < 0) && (iVar3 << 0x12 < 0)) {
    FUN_080040f8(param_1);
    *(undefined4 *)*param_1 = 0x2000;
  }
  return;
}



/* FUN 0x08004480 FUN_08004480 */

undefined8 FUN_08004480(int *param_1)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  bool bVar5;
  int local_20;
  
  local_20 = 0;
  if (param_1 == (int *)0x0) {
    return 1;
  }
  if (param_1[0x16] == 0) {
    FUN_080046a4(param_1);
    param_1[0x17] = 0;
    *(undefined1 *)(param_1 + 0x15) = 0;
  }
  iVar1 = *param_1;
  if (-1 < *(int *)(iVar1 + 8) << 3) {
    *(uint *)(iVar1 + 8) = *(uint *)(iVar1 + 8) & DAT_08004684 | 0x10000000;
    iVar1 = FUN_08000160(*DAT_0800468c,DAT_08004688);
    for (local_20 = iVar1 * 2 + 2; local_20 != 0; local_20 = local_20 + -1) {
    }
  }
  bVar5 = -1 < *(int *)(*param_1 + 8) << 3;
  if (bVar5) {
    param_1[0x16] = param_1[0x16] | 0x10;
    param_1[0x17] = param_1[0x17] | 1;
  }
  uVar4 = (uint)bVar5;
  iVar1 = FUN_0800678a();
  if ((param_1[0x16] << 0x1b < 0) || (iVar1 != 0)) {
    param_1[0x16] = param_1[0x16] | 0x10;
  }
  else {
    param_1[0x16] = param_1[0x16] & 0xfffffeffU | 2;
    iVar1 = FUN_0800677a(*param_1);
    if (iVar1 == 0) {
      uVar2 = 0;
      if (param_1[0xc] != 0) {
        uVar2 = 0x1000;
      }
      if (param_1[4] < 0) {
        uVar3 = param_1[4] & 0x7fffffff;
      }
      else {
        uVar3 = 0x200000;
      }
      uVar2 = param_1[2] | (uint)*(byte *)(param_1 + 6) << 0xe |
              (uint)*(byte *)((int)param_1 + 0x19) << 0xf |
              (uint)*(byte *)((int)param_1 + 0x1a) << 0xd | uVar2 | param_1[3] | uVar3 |
              (uint)*(byte *)(param_1 + 0xb) << 1;
      if ((char)param_1[8] == '\x01') {
        if (*(byte *)((int)param_1 + 0x1a) == 0) {
          uVar2 = uVar2 | 0x10000;
        }
        else {
          param_1[0x16] = param_1[0x16] | 0x20;
          param_1[0x17] = param_1[0x17] | 1;
        }
      }
      if (param_1[9] != 0) {
        uVar2 = param_1[10] | param_1[9] & 0x1c0U | uVar2;
      }
      *(uint *)(*param_1 + 0xc) = *(uint *)(*param_1 + 0xc) & DAT_08004690 | uVar2;
      uVar2 = DAT_08004694;
      uVar3 = param_1[0x13] | param_1[1] & 0xc0000000U;
      if ((char)param_1[0xf] == '\x01') {
        uVar3 = uVar3 | param_1[0x10] | param_1[0x11] |
                        param_1[0x12] | (param_1[1] & 0xc0000000U) + 1;
      }
      *(uint *)(*param_1 + 0x10) = *(uint *)(*param_1 + 0x10) & DAT_08004694 | uVar3;
      uVar3 = param_1[1];
      if (((uVar3 != 0xc0000000) && (uVar3 != uVar2 * 0x20000000)) && (uVar3 != uVar2 * 0x40000000))
      {
        *(uint *)(DAT_08004698 + 8) = *(uint *)(DAT_08004698 + 8) & 0xffc3ffff | uVar3 & 0x3c0000;
      }
    }
    FUN_080067b0(*param_1,0,param_1[0xd]);
    FUN_080067b0(*param_1,DAT_0800469c,param_1[0xe]);
    if (param_1[4] == 0) {
      *(uint *)(*param_1 + 0x28) = *(uint *)(*param_1 + 0x28) | 0xfffffff0;
    }
    else if (param_1[4] == 0x200000) {
      *(int *)(*param_1 + 0x28) = -0x10 << ((char)param_1[7] * '\x04' - 4U & 0x1f) | param_1[0x18];
    }
    if ((*(uint *)(*param_1 + 0x14) & 7) == param_1[0xd]) {
      param_1[0x17] = 0;
      param_1[0x16] = (param_1[0x16] & 0xfffffffcU) + 1;
      goto LAB_0800467e;
    }
    param_1[0x16] = param_1[0x16] & 0xfffffffdU | 0x10;
    param_1[0x17] = param_1[0x17] | 1;
  }
  uVar4 = 1;
LAB_0800467e:
  return CONCAT44(local_20,uVar4);
}



/* FUN 0x080046a0 FUN_080046a0 */

void FUN_080046a0(void)

{
  return;
}



/* FUN 0x080046a4 FUN_080046a4 */

void FUN_080046a4(int *param_1)

{
  uint *puVar1;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  uint local_c;
  
  FUN_080001e6(&local_20,0x14);
  if (*param_1 == DAT_08004708) {
    *DAT_0800470c = *DAT_0800470c | 0x100000;
    puVar1 = DAT_0800470c;
    DAT_0800470c[-3] = DAT_0800470c[-3] | 1;
    local_c = puVar1[-3] & 1;
    local_20 = 0x10;
    local_1c = 3;
    local_18 = 0;
    FUN_08004d30(0x50000000,&local_20);
    FUN_08005024(0xc,3,0);
    FUN_0800500c(0xc);
  }
  return;
}



/* FUN 0x08004710 FUN_08004710 */

undefined4 FUN_08004710(int *param_1,uint param_2)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  if (param_1[5] == 8) {
    uVar3 = 8;
  }
  else {
    if ((*(uint *)(*param_1 + 0xc) & 1) != 0) {
      param_1[0x16] = param_1[0x16] | 0x20;
      return 1;
    }
    uVar3 = 4;
  }
  iVar1 = FUN_08004eac();
  do {
    if ((*(uint *)*param_1 & uVar3) != 0) {
      param_1[0x16] = param_1[0x16] | 0x200;
      iVar1 = FUN_08006792(*param_1);
      if (((iVar1 != 0) && (*(char *)((int)param_1 + 0x1a) == '\0')) &&
         (*(int *)*param_1 << 0x1c < 0)) {
        iVar1 = FUN_0800678a();
        if (iVar1 == 0) {
          *(uint *)(*param_1 + 4) = *(uint *)(*param_1 + 4) & 0xfffffff3;
          param_1[0x16] = param_1[0x16] & 0xfffffeffU | 1;
        }
        else {
          param_1[0x16] = param_1[0x16] | 0x20;
          param_1[0x17] = param_1[0x17] | 1;
        }
      }
      if ((char)param_1[6] == '\0') {
        *(undefined4 *)*param_1 = 0xc;
      }
      return 0;
    }
  } while (((param_2 == 0xffffffff) ||
           ((iVar2 = FUN_08004eac(), (uint)(iVar2 - iVar1) <= param_2 && (param_2 != 0)))) ||
          ((*(uint *)*param_1 & uVar3) != 0));
  param_1[0x16] = param_1[0x16] | 4;
  *(undefined1 *)(param_1 + 0x15) = 0;
  return 3;
}



/* FUN 0x080047d4 FUN_080047d4 */

int FUN_080047d4(int *param_1)

{
  int iVar1;
  
  iVar1 = FUN_0800678a(*param_1);
  if (iVar1 == 0) {
    if ((char)param_1[0x15] == '\x01') {
      return 2;
    }
    *(undefined1 *)(param_1 + 0x15) = 1;
    iVar1 = FUN_080007a8(param_1);
    if (iVar1 == 0) {
      param_1[0x16] = param_1[0x16] & DAT_08004834 | 0x100;
      param_1[0x17] = 0;
      *(undefined4 *)*param_1 = 0x1c;
      *(undefined1 *)(param_1 + 0x15) = 0;
      *(uint *)(*param_1 + 8) = (*(uint *)(*param_1 + 8) & DAT_08004838) + 4;
    }
    else {
      *(undefined1 *)(param_1 + 0x15) = 0;
    }
  }
  else {
    iVar1 = 2;
  }
  return iVar1;
}



/* FUN 0x0800483c FUN_0800483c */

int FUN_0800483c(int param_1)

{
  int iVar1;
  
  if (*(char *)(param_1 + 0x54) == '\x01') {
    return 2;
  }
  *(undefined1 *)(param_1 + 0x54) = 1;
  iVar1 = FUN_080006d4(param_1);
  if ((iVar1 == 0) && (iVar1 = FUN_08000734(param_1), iVar1 == 0)) {
    *(uint *)(param_1 + 0x58) = *(uint *)(param_1 + 0x58) & 0xfffffeff | 1;
  }
  *(undefined1 *)(param_1 + 0x54) = 0;
  return iVar1;
}



/* FUN 0x0800487a FUN_0800487a */

undefined4 FUN_0800487a(undefined4 *param_1)

{
  uint *puVar1;
  
  if (param_1 != (undefined4 *)0x0) {
    if (*(char *)((int)param_1 + 0x25) == '\x02') {
      *(uint *)*param_1 = *(uint *)*param_1 & 0xfffffff1;
      *(uint *)param_1[0x12] = *(uint *)param_1[0x12] & 0xfffffeff;
      *(uint *)*param_1 = *(uint *)*param_1 & 0xfffffffe;
      *(int *)(param_1[0x10] + 4) = 1 << (param_1[0x11] & 0x1c);
      *(undefined4 *)(param_1[0x13] + 4) = param_1[0x14];
      puVar1 = (uint *)param_1[0x15];
      if (puVar1 != (uint *)0x0) {
        *puVar1 = *puVar1 & 0xfffffeff;
        *(undefined4 *)(param_1[0x16] + 4) = param_1[0x17];
      }
      *(undefined1 *)((int)param_1 + 0x25) = 1;
      *(undefined1 *)(param_1 + 9) = 0;
      return 0;
    }
    param_1[0xf] = 4;
    *(undefined1 *)(param_1 + 9) = 0;
  }
  return 1;
}



/* FUN 0x080048e6 FUN_080048e6 */

undefined4 FUN_080048e6(undefined4 *param_1)

{
  uint *puVar1;
  undefined4 uVar2;
  
  uVar2 = 0;
  if (*(char *)((int)param_1 + 0x25) == '\x02') {
    *(uint *)*param_1 = *(uint *)*param_1 & 0xfffffff1;
    *(uint *)*param_1 = *(uint *)*param_1 & 0xfffffffe;
    *(uint *)param_1[0x12] = *(uint *)param_1[0x12] & 0xfffffeff;
    *(int *)(param_1[0x10] + 4) = 1 << (param_1[0x11] & 0x1c);
    *(undefined4 *)(param_1[0x13] + 4) = param_1[0x14];
    puVar1 = (uint *)param_1[0x15];
    if (puVar1 != (uint *)0x0) {
      *puVar1 = *puVar1 & 0xfffffeff;
      *(undefined4 *)(param_1[0x16] + 4) = param_1[0x17];
    }
    *(undefined1 *)((int)param_1 + 0x25) = 1;
    *(undefined1 *)(param_1 + 9) = 0;
    if ((code *)param_1[0xe] != (code *)0x0) {
      (*(code *)param_1[0xe])();
    }
  }
  else {
    param_1[0xf] = 4;
    uVar2 = 1;
  }
  return uVar2;
}



/* FUN 0x08004958 FUN_08004958 */

void FUN_08004958(uint param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_08004eac();
  if (param_1 != 0xffffffff) {
    param_1 = param_1 + *DAT_08004978;
  }
  do {
    iVar2 = FUN_08004eac();
  } while ((uint)(iVar2 - iVar1) < param_1);
  return;
}



/* FUN 0x0800497c FUN_0800497c */

int FUN_0800497c(int *param_1,uint *param_2)

{
  char *pcVar1;
  int iVar2;
  uint uVar3;
  
  pcVar1 = DAT_080049f8;
  if (*DAT_080049f8 == '\x01') {
    return 2;
  }
  *DAT_080049f8 = '\x01';
  pcVar1[4] = '\0';
  pcVar1[5] = '\0';
  pcVar1[6] = '\0';
  pcVar1[7] = '\0';
  iVar2 = FUN_08003f6c(1000);
  if (iVar2 == 0) {
    if (*param_1 == 4) {
      FUN_08003e94(param_1[1]);
      iVar2 = FUN_08003f6c(1000);
    }
    else {
      *param_2 = 0xffffffff;
      for (uVar3 = param_1[2]; uVar3 < (uint)(param_1[2] + param_1[3]); uVar3 = uVar3 + 1) {
        FUN_08003eec(param_1[1],uVar3);
        iVar2 = FUN_08003f6c(1000);
        if (iVar2 != 0) {
          *param_2 = uVar3;
          break;
        }
      }
      *(uint *)(DAT_080049fc + 0x14) = *(uint *)(DAT_080049fc + 0x14) & 0xfffffffd;
    }
  }
  *pcVar1 = '\0';
  return iVar2;
}



/* FUN 0x08004a00 FUN_08004a00 */

void FUN_08004a00(undefined4 *param_1)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  int iVar4;
  
  *param_1 = 7;
  iVar1 = DAT_08004a64;
  iVar4 = param_1[1];
  if (iVar4 == 1) {
    param_1[2] = *(uint *)(DAT_08004a64 + 0x2c) & 0x7f;
    uVar2 = *(uint *)(iVar1 + 0x2c);
  }
  else if (iVar4 == 4) {
    param_1[2] = *(uint *)(DAT_08004a64 + 0x4c) & 0x7f;
    uVar2 = *(uint *)(iVar1 + 0x4c);
  }
  else if (iVar4 == 8) {
    param_1[2] = *(uint *)(DAT_08004a64 + 0x50) & 0x7f;
    uVar2 = *(uint *)(iVar1 + 0x50);
  }
  else {
    param_1[2] = *(uint *)(DAT_08004a64 + 0x30) & 0x7f;
    uVar2 = *(uint *)(iVar1 + 0x30);
  }
  param_1[3] = (uVar2 & 0x7fffff) >> 0x10;
  uVar3 = FUN_08003ea8();
  param_1[4] = uVar3;
  uVar3 = FUN_08003ec0();
  param_1[6] = uVar3;
  param_1[5] = DAT_08004a68;
  return;
}



/* FUN 0x08004a6c FUN_08004a6c */

int FUN_08004a6c(uint *param_1)

{
  char *pcVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  
  pcVar1 = DAT_08004b18;
  if (*DAT_08004b18 == '\x01') {
    return 2;
  }
  *DAT_08004b18 = '\x01';
  pcVar1[4] = '\0';
  iVar2 = DAT_08004b1c;
  pcVar1[5] = '\0';
  pcVar1[6] = '\0';
  pcVar1[7] = '\0';
  if ((*param_1 & 1) != 0) {
    uVar6 = param_1[1];
    uVar5 = param_1[2];
    uVar3 = param_1[3];
    if (uVar6 == 1) {
      *(uint *)(DAT_08004b1c + 0x2c) = uVar3 << 0x10 | uVar5;
    }
    else if (uVar6 == 4) {
      *(uint *)(DAT_08004b1c + 0x4c) = uVar3 << 0x10 | uVar5;
    }
    else if (uVar6 == 8) {
      *(uint *)(DAT_08004b1c + 0x50) = uVar3 << 0x10 | uVar5;
    }
    else {
      *(uint *)(DAT_08004b1c + 0x30) = uVar3 << 0x10 | uVar5;
    }
  }
  uVar3 = *param_1;
  if ((uVar3 & 7) >> 1 == 3) {
    uVar3 = param_1[4];
LAB_08004ae6:
    uVar5 = param_1[6];
    uVar6 = param_1[5];
  }
  else {
    if (-1 < (int)(uVar3 << 0x1e)) {
      if (-1 < (int)(uVar3 << 0x1d)) goto LAB_08004aee;
      uVar3 = FUN_08003ea8();
      goto LAB_08004ae6;
    }
    uVar6 = FUN_08003ec0();
    uVar3 = param_1[4];
    uVar5 = uVar6;
  }
  FUN_08003ed4(uVar6,uVar5,uVar3);
LAB_08004aee:
  iVar4 = FUN_08003f6c(1000);
  if (iVar4 == 0) {
    *(uint *)(iVar2 + 0x14) = *(uint *)(iVar2 + 0x14) | 0x20000;
    iVar4 = FUN_08003f6c(1000);
    *(uint *)(iVar2 + 0x14) = *(uint *)(iVar2 + 0x14) & 0xfffdffff;
  }
  *pcVar1 = '\0';
  return iVar4;
}



/* FUN 0x08004b20 FUN_08004b20 */

bool FUN_08004b20(void)

{
  int iVar1;
  
  iVar1 = DAT_08004b38;
  *(uint *)(DAT_08004b38 + 0x14) = *(uint *)(DAT_08004b38 + 0x14) | 0x80000000;
  return -1 < *(int *)(iVar1 + 0x14);
}



/* FUN 0x08004b3c FUN_08004b3c */

undefined4 FUN_08004b3c(void)

{
  *(uint *)(DAT_08004b4c + 0x14) = *(uint *)(DAT_08004b4c + 0x14) | 0x8000000;
  return 1;
}



/* FUN 0x08004b50 FUN_08004b50 */

bool FUN_08004b50(void)

{
  int iVar1;
  
  iVar1 = DAT_08004b68;
  *(uint *)(DAT_08004b68 + 0x14) = *(uint *)(DAT_08004b68 + 0x14) | 0x40000000;
  return -1 < *(int *)(iVar1 + 0x14) << 1;
}



/* FUN 0x08004b6c FUN_08004b6c */

undefined4 FUN_08004b6c(void)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = DAT_08004b88;
  uVar2 = 1;
  if (*(int *)(DAT_08004b88 + 0x14) << 1 < 0) {
    *(undefined4 *)(DAT_08004b88 + 0xc) = DAT_08004b8c;
    *(undefined4 *)(iVar1 + 0xc) = DAT_08004b90;
    if (-1 < *(int *)(iVar1 + 0x14) << 1) {
      uVar2 = 0;
    }
  }
  return uVar2;
}



/* FUN 0x08004b94 FUN_08004b94 */

int FUN_08004b94(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  undefined8 uVar3;
  uint uVar4;
  undefined4 uVar5;
  
  pcVar1 = DAT_08004bec;
  if (*DAT_08004bec == '\x01') {
    iVar2 = 2;
  }
  else {
    *DAT_08004bec = '\x01';
    pcVar1[4] = '\0';
    pcVar1[5] = '\0';
    pcVar1[6] = '\0';
    pcVar1[7] = '\0';
    uVar4 = param_1;
    uVar5 = param_3;
    uVar3 = FUN_08003f6c(1000);
    iVar2 = (int)uVar3;
    if (iVar2 == 0) {
      if (param_1 == 1) {
        FUN_08003f1c(param_2,(int)((ulonglong)uVar3 >> 0x20),param_3,param_4,uVar4,param_2,uVar5);
      }
      else {
        FUN_08003f38(param_2,param_3);
      }
      iVar2 = FUN_08003f6c(1000);
      *(uint *)(DAT_08004bf0 + 0x14) = *(uint *)(DAT_08004bf0 + 0x14) & ~param_1;
    }
    *pcVar1 = '\0';
  }
  return iVar2;
}



/* FUN 0x08004bf4 FUN_08004bf4 */

undefined4 FUN_08004bf4(void)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = DAT_08004c10;
  uVar2 = 0;
  if (*(int *)(DAT_08004c10 + 0x14) < 0) {
    *(undefined4 *)(DAT_08004c10 + 8) = DAT_08004c14;
    *(undefined4 *)(iVar1 + 8) = DAT_08004c18;
    if (*(int *)(iVar1 + 0x14) < 0) {
      uVar2 = 1;
    }
  }
  return uVar2;
}



/* FUN 0x08004c1c FUN_08004c1c */

void FUN_08004c1c(uint *param_1,uint param_2)

{
  uint *puVar1;
  uint *puVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  
  for (uVar4 = 0; puVar2 = DAT_08004cec, param_2 >> (uVar4 & 0xff) != 0; uVar4 = uVar4 + 1) {
    uVar5 = 1 << (uVar4 & 0xff);
    uVar3 = uVar5 & param_2;
    if (uVar3 != 0) {
      uVar7 = uVar4 & 0xfffffffc;
      iVar8 = (uVar4 & 3) << 3;
      uVar6 = 0xf << iVar8;
      if (param_1 == (uint *)0x50000000) {
        iVar9 = 0;
      }
      else if (param_1 == DAT_08004cf0) {
        iVar9 = 1;
      }
      else if (param_1 == DAT_08004cf4) {
        iVar9 = 2;
      }
      else if (param_1 == DAT_08004cf8) {
        iVar9 = 3;
      }
      else if (param_1 == DAT_08004cfc) {
        iVar9 = 4;
      }
      else {
        iVar9 = 5;
      }
      if (iVar9 << iVar8 == (uVar6 & *(uint *)((int)DAT_08004cec + uVar7 + 0x60))) {
        DAT_08004cec[0x20] = DAT_08004cec[0x20] & ~uVar3;
        puVar2[0x21] = puVar2[0x21] & ~uVar3;
        puVar1 = DAT_08004cec;
        DAT_08004cec[1] = DAT_08004cec[1] & ~uVar3;
        *puVar1 = *puVar1 & ~uVar3;
        *(uint *)((int)puVar2 + uVar7 + 0x60) = *(uint *)((int)puVar2 + uVar7 + 0x60) & ~uVar6;
      }
      uVar3 = 3 << ((uVar4 & 0x7f) << 1);
      *param_1 = *param_1 | uVar3;
      param_1[(uVar4 >> 3) + 8] = param_1[(uVar4 >> 3) + 8] & ~(0xf << ((uVar4 & 7) << 2));
      param_1[2] = param_1[2] & ~uVar3;
      param_1[1] = param_1[1] & ~uVar5;
      param_1[3] = param_1[3] & ~uVar3;
    }
  }
  return;
}



/* FUN 0x08004d00 FUN_08004d00 */

void FUN_08004d00(void)

{
  return;
}



/* FUN 0x08004d04 FUN_08004d04 */

void FUN_08004d04(uint param_1)

{
  int iVar1;
  
  iVar1 = DAT_08004d28;
  if ((*(uint *)(DAT_08004d28 + 0xc) & param_1) != 0) {
    *(uint *)(DAT_08004d28 + 0xc) = param_1;
    FUN_08004d2c(param_1);
  }
  if ((*(uint *)(iVar1 + 0x10) & param_1) != 0) {
    *(uint *)(iVar1 + 0x10) = param_1;
    FUN_08004d00(param_1);
  }
  return;
}



/* FUN 0x08004d2c FUN_08004d2c */

void FUN_08004d2c(void)

{
  return;
}



/* FUN 0x08004d30 FUN_08004d30 */

void FUN_08004d30(uint *param_1,uint *param_2)

{
  uint *puVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  byte bVar5;
  int iVar6;
  uint *puVar7;
  int iVar8;
  
  for (uVar3 = 0; *param_2 >> (uVar3 & 0xff) != 0; uVar3 = uVar3 + 1) {
    uVar4 = 1 << (uVar3 & 0xff);
    uVar2 = *param_2 & uVar4;
    if (uVar2 != 0) {
      bVar5 = (byte)param_2[1] & 3;
      if ((bVar5 == 1) || (bVar5 == 2)) {
        param_1[2] = param_2[3] << (uVar3 << 1 & 0xff) | param_1[2] & ~(3 << (uVar3 << 1 & 0xff));
        param_1[1] = (((byte)param_2[1] & 0x1f) >> 4) << (uVar3 & 0xff) | param_1[1] & ~uVar4;
      }
      if ((~(byte)param_2[1] & 3) != 0) {
        param_1[3] = param_2[2] << (uVar3 << 1 & 0xff) | param_1[3] & ~(3 << (uVar3 << 1 & 0xff));
      }
      if ((param_2[1] & 3) == 2) {
        iVar6 = (uVar3 & 7) << 2;
        param_1[(uVar3 >> 3) + 8] =
             param_2[4] << iVar6 | param_1[(uVar3 >> 3) + 8] & ~(0xf << iVar6);
      }
      *param_1 = ((byte)param_2[1] & 3) << (uVar3 << 1 & 0xff) |
                 *param_1 & ~(3 << (uVar3 << 1 & 0xff));
      puVar7 = DAT_08004e80;
      if ((param_2[1] & 0x3ffff) >> 0x10 != 0) {
        iVar6 = (uVar3 & 3) << 3;
        if (param_1 == (uint *)0x50000000) {
          iVar8 = 0;
        }
        else if (param_1 == DAT_08004e84) {
          iVar8 = 1;
        }
        else if (param_1 == DAT_08004e88) {
          iVar8 = 2;
        }
        else if (param_1 == DAT_08004e8c) {
          iVar8 = 3;
        }
        else if (param_1 == DAT_08004e90) {
          iVar8 = 4;
        }
        else {
          iVar8 = 5;
        }
        *(uint *)((int)DAT_08004e80 + (uVar3 & 0xfffffffc) + 0x60) =
             iVar8 << iVar6 |
             *(uint *)((int)DAT_08004e80 + (uVar3 & 0xfffffffc) + 0x60) & ~(0xf << iVar6);
        puVar1 = DAT_08004e80;
        uVar4 = *puVar7 & ~uVar2;
        if ((int)(param_2[1] << 0xb) < 0) {
          uVar4 = uVar4 | uVar2;
        }
        *DAT_08004e80 = uVar4;
        uVar4 = puVar1[1] & ~uVar2;
        if ((int)(param_2[1] << 10) < 0) {
          uVar4 = uVar4 | uVar2;
        }
        puVar1[1] = uVar4;
        puVar7 = DAT_08004e80 + 0x20;
        uVar4 = DAT_08004e80[0x21] & ~uVar2;
        if ((int)(param_2[1] << 0xe) < 0) {
          uVar4 = uVar4 | uVar2;
        }
        DAT_08004e80[0x21] = uVar4;
        uVar4 = *puVar7 & ~uVar2;
        if ((int)(param_2[1] << 0xf) < 0) {
          uVar4 = uVar4 | uVar2;
        }
        *puVar7 = uVar4;
      }
    }
  }
  return;
}



/* FUN 0x08004e94 FUN_08004e94 */

bool FUN_08004e94(int param_1,uint param_2)

{
  return (*(uint *)(param_1 + 0x10) & param_2) != 0;
}



/* FUN 0x08004e9e FUN_08004e9e */

void FUN_08004e9e(int param_1,undefined4 param_2,int param_3)

{
  if (param_3 != 0) {
    *(undefined4 *)(param_1 + 0x18) = param_2;
    return;
  }
  *(undefined4 *)(param_1 + 0x28) = param_2;
  return;
}



/* FUN 0x08004eac FUN_08004eac */

undefined4 FUN_08004eac(void)

{
  return *(undefined4 *)(DAT_08004eb4 + 8);
}



/* FUN 0x08004eb8 FUN_08004eb8 */

undefined4 FUN_08004eb8(void)

{
  return *(undefined4 *)(DAT_08004ec0 + 0x10);
}



/* FUN 0x08004ec4 FUN_08004ec4 */

undefined4 FUN_08004ec4(void)

{
  return *(undefined4 *)(DAT_08004ecc + 0x14);
}



/* FUN 0x08004ed0 FUN_08004ed0 */

undefined4 FUN_08004ed0(void)

{
  return *(undefined4 *)(DAT_08004ed8 + 0x18);
}



/* FUN 0x08004edc FUN_08004edc */

void FUN_08004edc(void)

{
  *(uint *)(DAT_08004ee8 + 8) = *(int *)(DAT_08004ee8 + 8) + (uint)*DAT_08004ee8;
  return;
}



/* FUN 0x08004eec FUN_08004eec */

bool FUN_08004eec(void)

{
  int iVar1;
  
  *DAT_08004f10 = *DAT_08004f10 | (int)DAT_08004f10 >> 0x16;
  iVar1 = FUN_08004f14(3);
  if (iVar1 == 0) {
    FUN_08004fb0();
  }
  return iVar1 != 0;
}



/* FUN 0x08004f14 FUN_08004f14 */

int FUN_08004f14(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint *puVar1;
  undefined4 *puVar2;
  int iVar3;
  uint uVar4;
  undefined1 auStack_24 [12];
  int local_18;
  undefined1 auStack_14 [8];
  
  puVar1 = DAT_08004f98;
  uVar4 = *DAT_08004f98;
  *DAT_08004f98 = uVar4 | 0x40000;
  FUN_0800543c(auStack_24,auStack_14,uVar4 | 0x40000,param_4,*puVar1 & 0x40000);
  if (local_18 == 0) {
    iVar3 = FUN_08005474();
  }
  else {
    iVar3 = FUN_08005474();
    iVar3 = iVar3 << 1;
  }
  iVar3 = FUN_08000160(iVar3,DAT_08004f9c);
  puVar2 = DAT_08004fa4;
  *DAT_08004fa4 = DAT_08004fa0;
  puVar2[3] = DAT_08004fa8;
  puVar2[1] = iVar3 + -1;
  puVar2[4] = 0;
  puVar2[2] = 0;
  puVar2[6] = 0;
  iVar3 = FUN_08005bda();
  if ((iVar3 == 0) && (iVar3 = FUN_08005c28(DAT_08004fa4), iVar3 == 0)) {
    FUN_0800500c(0x16);
    if (param_1 < 4) {
      FUN_08005024(0x16,param_1,0);
      *DAT_08004fac = param_1;
    }
    else {
      iVar3 = 1;
    }
  }
  return iVar3;
}



/* FUN 0x08004fb0 FUN_08004fb0 */

void FUN_08004fb0(void)

{
  uint *puVar1;
  uint *puVar2;
  undefined4 in_r3;
  
  *DAT_08004fe8 = *DAT_08004fe8 | 1;
  puVar1 = DAT_08004fe8;
  puVar2 = DAT_08004fe8 + -0x10;
  DAT_08004fe8[-1] = DAT_08004fe8[-1] | (int)puVar2 * 0x10000;
  FUN_08005024(0xfffffffe,3,0,in_r3,puVar1[-1] & (int)puVar2 * 0x10000);
  FUN_08005bc0(0x600);
  return;
}



/* FUN 0x08004fec FUN_08004fec */

void FUN_08004fec(uint param_1)

{
  if (-1 < (int)param_1) {
    *DAT_08005008 = 1 << (param_1 & 0x1f);
    DataSynchronizationBarrier(0xf);
    InstructionSynchronizationBarrier(0xf);
  }
  return;
}



/* FUN 0x0800500c FUN_0800500c */

void FUN_0800500c(uint param_1)

{
  if (-1 < (int)param_1) {
    *DAT_08005020 = 1 << (param_1 & 0x1f);
  }
  return;
}



/* FUN 0x08005024 FUN_08005024 */

void FUN_08005024(void)

{
  FUN_080091ac();
  return;
}



/* FUN 0x0800502c FUN_0800502c */

void FUN_0800502c(void)

{
  DataSynchronizationBarrier(0xf);
  *(undefined4 *)(DAT_08005044 + 0xc) = DAT_08005040;
  DataSynchronizationBarrier(0xf);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* FUN 0x08005048 FUN_08005048 */

undefined4 FUN_08005048(uint param_1)

{
  uint *puVar1;
  int iVar2;
  
  puVar1 = DAT_08005088;
  *DAT_08005088 = *DAT_08005088 & 0xfffff9ff | param_1;
  if (param_1 == 0x200) {
    iVar2 = FUN_08000160(*DAT_0800508c * 6,DAT_08005090);
    iVar2 = iVar2 + 1;
    while ((int)(puVar1[5] << 0x15) < 0) {
      if (iVar2 == 0) {
        return 3;
      }
      iVar2 = iVar2 + -1;
    }
  }
  return 0;
}



/* FUN 0x08005094 FUN_08005094 */

void FUN_08005094(uint param_1)

{
  *(uint *)(DAT_080050a4 + 8) = *(uint *)(DAT_080050a4 + 8) & ~(param_1 & 0x3f);
  return;
}



/* FUN 0x080050a8 FUN_080050a8 */

void FUN_080050a8(uint param_1)

{
  int iVar1;
  
  iVar1 = DAT_080050c0;
  *(uint *)(DAT_080050c0 + 0xc) = *(uint *)(DAT_080050c0 + 0xc) & ~(param_1 & 0x3f) | param_1 >> 8;
  *(uint *)(iVar1 + 8) = *(uint *)(iVar1 + 8) | param_1 & 0x3f;
  return;
}



/* FUN 0x080050c4 FUN_080050c4 */

void FUN_080050c4(void)

{
  *DAT_080050e0 = (*DAT_080050e0 & 0xfffffff8) + 3;
  *(uint *)(DAT_080050e4 + 0x10) = *(uint *)(DAT_080050e4 + 0x10) | 4;
  WaitForInterrupt();
  return;
}



/* FUN 0x080050e8 FUN_080050e8 */

void FUN_080050e8(int param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  
  if (param_1 == 0) {
    uVar2 = *DAT_08005120 & 0xfffffff8;
  }
  else {
    uVar2 = (*DAT_08005120 & 0xfffffff8) + 1;
  }
  *DAT_08005120 = uVar2;
  iVar1 = DAT_08005124;
  *(uint *)(DAT_08005124 + 0x10) = *(uint *)(DAT_08005124 + 0x10) | 4;
  if (param_2 == 1) {
    WaitForInterrupt();
  }
  else {
    WaitForEvent();
    WaitForEvent();
  }
  *(uint *)(iVar1 + 0x10) = *(uint *)(iVar1 + 0x10) & 0xfffffffb;
  return;
}



/* FUN 0x08005128 FUN_08005128 */

undefined8 FUN_08005128(ushort *param_1,uint param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  bool bVar7;
  uint local_20;
  
  iVar2 = DAT_080052d4;
  iVar1 = DAT_080052d0;
  uVar6 = 0;
  local_20 = param_2;
  if (-1 < *(int *)param_1 << 0xe) goto LAB_080051e4;
  bVar7 = -1 < *(int *)(DAT_080052d4 + 0x3c) << 3;
  if (bVar7) {
    *(uint *)(DAT_080052d4 + 0x3c) = *(uint *)(DAT_080052d4 + 0x3c) | DAT_080052d0 << 0x16;
  }
  local_20 = (uint)bVar7;
  *DAT_080052d8 = *DAT_080052d8 | (int)DAT_080052d8 >> 0x16;
  iVar3 = FUN_08004eac();
  do {
    if ((int)(*DAT_080052d8 << 0x17) < 0) {
      uVar4 = *(uint *)(iVar1 + 0x1c) & 0x300;
      if ((uVar4 != 0) && (*(uint *)(param_1 + 0x12) != uVar4)) {
        uVar4 = *(uint *)(iVar1 + 0x1c) & 0xfffffcff;
        *(uint *)(iVar1 + 0x1c) = *(uint *)(iVar1 + 0x1c) | 0x10000;
        *(uint *)(iVar1 + 0x1c) = *(uint *)(iVar1 + 0x1c) & 0xfffeffff;
        *(uint *)(iVar1 + 0x1c) = uVar4;
      }
      if ((uVar4 & 1) == 0) goto LAB_080051c6;
      iVar3 = FUN_08004eac();
      goto LAB_080051c0;
    }
    iVar5 = FUN_08004eac();
  } while ((uint)(iVar5 - iVar3) < 3);
  goto LAB_080051bc;
LAB_080051c6:
  *(uint *)(iVar1 + 0x1c) = *(uint *)(iVar1 + 0x1c) & 0xfffffcff | *(uint *)(param_1 + 0x12);
  goto LAB_080051d4;
  while( true ) {
    iVar5 = FUN_08004eac();
    if (DAT_080052dc < (uint)(iVar5 - iVar3)) break;
LAB_080051c0:
    if (*(int *)(iVar1 + 0x1c) << 0x1e < 0) goto LAB_080051c6;
  }
LAB_080051bc:
  uVar6 = 3;
LAB_080051d4:
  if (local_20 != 0) {
    *(uint *)(iVar2 + 0x3c) = *(uint *)(iVar2 + 0x3c) & 0xefffffff;
  }
LAB_080051e4:
  if ((*param_1 & 1) != 0) {
    *(uint *)(iVar1 + 0x14) = *(uint *)(iVar1 + 0x14) & 0xfffffffc | *(uint *)(param_1 + 2);
  }
  if ((int)((uint)(byte)*param_1 * 0x40000000) < 0) {
    *(uint *)(iVar1 + 0x14) = *(uint *)(iVar1 + 0x14) & 0xfffffff3 | *(uint *)(param_1 + 4);
  }
  if ((int)((uint)(byte)*param_1 << 0x1d) < 0) {
    *(uint *)(iVar1 + 0x14) = *(uint *)(iVar1 + 0x14) & 0xffffffcf | *(uint *)(param_1 + 6);
  }
  uVar4 = DAT_080052e0;
  if ((int)((uint)(byte)*param_1 << 0x1a) < 0) {
    *(uint *)(iVar1 + 0x14) = *(uint *)(iVar1 + 0x14) & ~DAT_080052e0 | *(uint *)(param_1 + 8);
  }
  if ((int)((uint)(byte)*param_1 << 0x19) < 0) {
    *(uint *)(iVar1 + 0x14) = *(uint *)(iVar1 + 0x14) & 0xffff3fff | *(uint *)(param_1 + 10);
  }
  if (((int)((uint)*param_1 << 0x11) < 0) &&
     (*(uint *)(iVar1 + 0x14) = *(uint *)(iVar1 + 0x14) & 0x3fffffff | *(uint *)(param_1 + 0x10),
     *(int *)(param_1 + 0x10) == 0x40000000)) {
    *(uint *)(iVar2 + 0xc) = *(uint *)(iVar2 + 0xc) | 0x10000;
  }
  if (((int)((uint)*param_1 << 0x14) < 0) &&
     (*(uint *)(iVar1 + 0x18) = *(uint *)(iVar1 + 0x18) & 0xfffffffc | *(uint *)(param_1 + 0xc),
     *(int *)(param_1 + 0xc) == 1)) {
    *(uint *)(iVar2 + 0xc) = *(uint *)(iVar2 + 0xc) | 0x10000;
  }
  if (((int)((uint)*param_1 << 0x12) < 0) &&
     (*(uint *)(iVar1 + 0x18) = *(uint *)(iVar1 + 0x18) & 0xfffffff3 | *(uint *)(param_1 + 0xe),
     *(int *)(param_1 + 0xe) == 4)) {
    *(uint *)(iVar2 + 0xc) = *(uint *)(iVar2 + 0xc) | 0x10000;
  }
  if ((*(int *)param_1 << 7 < 0) &&
     (*(uint *)(iVar1 + 0x18) = *(uint *)(iVar1 + 0x18) & ~uVar4 | *(uint *)(param_1 + 0x14),
     *(int *)(param_1 + 0x14) == 0x2000)) {
    *(uint *)(iVar2 + 0xc) = *(uint *)(iVar2 + 0xc) | 0x1000000;
  }
  return CONCAT44(local_20,uVar6);
}



/* FUN 0x080052e4 FUN_080052e4 */

undefined4 FUN_080052e4(byte *param_1,uint param_2)

{
  uint *puVar1;
  int *piVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  
  puVar1 = DAT_08005424;
  if (param_1 == (byte *)0x0) {
    return 1;
  }
  if ((*DAT_08005424 & 7) < param_2) {
    *DAT_08005424 = *DAT_08005424 & 0xfffffff8 | param_2;
    iVar3 = FUN_08004eac();
    do {
      if ((*puVar1 & 7) == param_2) goto LAB_08005320;
      iVar5 = FUN_08004eac();
    } while ((uint)(iVar5 - iVar3) <= DAT_08005428);
  }
  else {
LAB_08005320:
    piVar2 = DAT_0800542c;
    if (*(int *)param_1 << 0x1e < 0) {
      if (*(int *)param_1 << 0x1d < 0) {
        DAT_0800542c[2] = DAT_0800542c[2] | 0x7000;
      }
      piVar2[2] = piVar2[2] & 0xfffff0ffU | *(uint *)(param_1 + 8);
    }
    if ((*param_1 & 1) == 0) {
LAB_080053b0:
      if ((*puVar1 & 7) <= param_2) {
LAB_080053ea:
        if ((int)((uint)*param_1 << 0x1d) < 0) {
          piVar2[2] = piVar2[2] & 0xffff8fffU | *(uint *)(param_1 + 0xc);
        }
        uVar4 = FUN_0800549c();
        *DAT_08005434 = uVar4 >> (*(byte *)(DAT_08005430 + ((uint)piVar2[2] >> 6 & 0x3c)) & 0x1f);
        uVar6 = FUN_08004f14(*DAT_08005438);
        return uVar6;
      }
      *DAT_08005424 = *DAT_08005424 & 0xfffffff8 | param_2;
      iVar3 = FUN_08004eac();
      do {
        if ((*DAT_08005424 & 7) == param_2) goto LAB_080053ea;
        iVar5 = FUN_08004eac();
      } while ((uint)(iVar5 - iVar3) <= DAT_08005428);
    }
    else {
      uVar4 = *(uint *)(param_1 + 4);
      if (uVar4 == 1) {
        iVar3 = *piVar2 << 0xe;
      }
      else if (uVar4 == 2) {
        iVar3 = *piVar2 << 6;
      }
      else if (uVar4 == 0) {
        iVar3 = *piVar2 << 0x15;
      }
      else {
        if (uVar4 == 3) {
          iVar3 = DAT_0800542c[0x18];
        }
        else {
          iVar3 = DAT_0800542c[0x17];
        }
        iVar3 = iVar3 << 0x1e;
      }
      if (-1 < iVar3) {
        return 1;
      }
      piVar2[2] = piVar2[2] & 0xfffffff8U | uVar4;
      iVar3 = FUN_08004eac();
      do {
        if ((piVar2[2] & 0x38U) == *(int *)(param_1 + 4) * 8) goto LAB_080053b0;
        iVar5 = FUN_08004eac();
      } while ((uint)(iVar5 - iVar3) <= DAT_08005428);
    }
  }
  return 3;
}



/* FUN 0x0800543c FUN_0800543c */

void FUN_0800543c(undefined4 *param_1,uint *param_2)

{
  int iVar1;
  
  *param_1 = 7;
  iVar1 = DAT_0800546c;
  param_1[1] = *(uint *)(DAT_0800546c + 8) & 7;
  param_1[2] = *(uint *)(iVar1 + 8) & 0xf00;
  param_1[3] = *(uint *)(iVar1 + 8) & 0x7000;
  *param_2 = *DAT_08005470 & 7;
  return;
}



/* FUN 0x08005474 FUN_08005474 */

uint FUN_08005474(void)

{
  return *DAT_08005490 >>
         (*(byte *)(DAT_08005498 + ((*(uint *)(DAT_08005494 + 8) & 0x7fff) >> 0xc) * 4) & 0x1f);
}



/* FUN 0x0800549c FUN_0800549c */

int FUN_0800549c(void)

{
  uint *puVar1;
  int iVar2;
  int iVar3;
  
  puVar1 = DAT_08005520;
  if ((DAT_08005520[2] & 0x3f) >> 3 == 0) {
    iVar3 = 1 << ((*DAT_08005520 & 0x3fff) >> 0xb);
    iVar2 = DAT_08005524;
LAB_0800550c:
    iVar2 = FUN_08000160(iVar2,iVar3);
    return iVar2;
  }
  iVar2 = DAT_08005524 >> 1;
  if ((DAT_08005520[2] & 0x3f) >> 3 != 1) {
    if ((DAT_08005520[2] & 0x3f) >> 3 == 2) {
      if ((DAT_08005520[3] & 3) != 3) {
        iVar2 = DAT_08005524;
      }
      iVar2 = FUN_08000160(iVar2,((DAT_08005520[3] & 0x7f) >> 4) + 1);
      iVar3 = (puVar1[3] >> 0x1d) + 1;
      iVar2 = ((puVar1[3] & 0x7fff) >> 8) * iVar2;
      goto LAB_0800550c;
    }
    if ((DAT_08005520[2] & 0x3f) >> 3 == 4) {
      return 0x8000;
    }
    if ((DAT_08005520[2] & 0x3f) >> 3 == 3) {
      return 32000;
    }
    iVar2 = 0;
  }
  return iVar2;
}



/* FUN 0x08005528 FUN_08005528 */

undefined4 FUN_08005528(byte *param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  uint *puVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  bool bVar8;
  bool bVar9;
  undefined8 uVar10;
  
  bVar8 = param_1 == (byte *)0x0;
LAB_0800552c:
  do {
    puVar1 = DAT_080058ec;
    if (bVar8) {
      return 1;
    }
    if ((*param_1 & 1) == 0) break;
    param_2 = DAT_080058ec[3] & 3;
    if ((DAT_080058ec[2] & 0x38) == 0x10) {
      if (param_2 != 3) goto LAB_08005552;
    }
    else if ((DAT_080058ec[2] & 0x38) != 8) {
LAB_08005552:
      if (*(int *)(param_1 + 4) == 0x10000) {
LAB_0800555c:
        *puVar1 = *puVar1 | 0x10000;
      }
      else {
        if (*(int *)(param_1 + 4) == 0x50000) {
          *DAT_080058ec = *DAT_080058ec | 0x40000;
          goto LAB_0800555c;
        }
        *DAT_080058ec = *DAT_080058ec & 0xfffeffff;
        *puVar1 = *puVar1 & 0xfffbffff;
      }
      if (*(int *)(param_1 + 4) != 0) {
        uVar10 = FUN_08004eac();
        goto LAB_080055a8;
      }
      uVar10 = FUN_08004eac();
      param_2 = (uint)((ulonglong)uVar10 >> 0x20);
      iVar3 = (int)uVar10;
      while ((int)(*puVar1 << 0xe) < 0) {
        uVar10 = FUN_08004eac();
        param_2 = (uint)((ulonglong)uVar10 >> 0x20);
        uVar2 = (int)uVar10 - iVar3;
        bVar9 = 99 < uVar2;
        bVar8 = uVar2 == 100;
        if (100 < uVar2) goto LAB_080055a6;
      }
      break;
    }
  } while (((int)(*DAT_080058ec << 0xe) < 0) && (bVar8 = true, *(int *)(param_1 + 4) == 0));
  while ((int)((uint)*param_1 << 0x1e) < 0) {
    uVar2 = puVar1[2] & 0x38;
    param_2 = 0x3800;
    if (uVar2 == 0x10) {
      if ((puVar1[3] & 3) == 2) goto LAB_0800560c;
    }
    else if (uVar2 == 0) {
LAB_0800560c:
      if (-1 < (int)(*puVar1 << 0x15)) goto LAB_08005618;
      bVar9 = *(int *)(param_1 + 0xc) == 0;
      goto LAB_08005616;
    }
    if (*(int *)(param_1 + 0xc) == 0) {
      *puVar1 = *puVar1 & 0xfffffeff;
      uVar10 = FUN_08004eac();
      param_2 = (uint)((ulonglong)uVar10 >> 0x20);
      iVar3 = (int)uVar10;
      do {
        if (-1 < (int)(*puVar1 << 0x15)) goto LAB_080056a2;
        uVar10 = FUN_08004eac();
        param_2 = (uint)((ulonglong)uVar10 >> 0x20);
        uVar2 = (int)uVar10 - iVar3;
        bVar9 = 1 < uVar2;
        bVar8 = uVar2 == 2;
      } while (uVar2 < 3);
    }
    else {
      *puVar1 = *puVar1 & 0xffffc7ff | *(uint *)(param_1 + 0x10);
      *puVar1 = *puVar1 | 0x100;
      iVar3 = FUN_08004eac();
      do {
        if ((int)(*puVar1 << 0x15) < 0) {
          param_2 = *(int *)(param_1 + 0x14) << 8;
          puVar1[1] = puVar1[1] & 0xffff80ff | param_2;
          goto LAB_080056a2;
        }
        uVar10 = FUN_08004eac();
        param_2 = (uint)((ulonglong)uVar10 >> 0x20);
        uVar2 = (int)uVar10 - iVar3;
        bVar9 = 1 < uVar2;
        bVar8 = uVar2 == 2;
      } while (uVar2 < 3);
    }
LAB_080055a6:
    while( true ) {
      uVar10 = CONCAT44(param_2,iVar3);
      if (bVar9 && !bVar8) {
        return 3;
      }
LAB_080055a8:
      param_2 = (uint)((ulonglong)uVar10 >> 0x20);
      iVar3 = (int)uVar10;
      if ((int)(*puVar1 << 0xe) < 0) break;
      uVar10 = FUN_08004eac();
      param_2 = (uint)((ulonglong)uVar10 >> 0x20);
      uVar2 = (int)uVar10 - iVar3;
      bVar9 = 99 < uVar2;
      bVar8 = uVar2 == 100;
    }
  }
LAB_080056a2:
  do {
    iVar3 = DAT_080058fc;
    if (-1 < (int)((uint)*param_1 << 0x1c)) goto LAB_08005708;
    if ((puVar1[2] & 0x3f) >> 3 != 3) {
      if (*(int *)(param_1 + 0x18) == 0) {
        *(uint *)(DAT_080058fc + 0x20) = *(uint *)(DAT_080058fc + 0x20) & 0xfffffffe;
        iVar5 = FUN_08004eac();
        while (*(int *)(iVar3 + 0x20) << 0x1e < 0) {
          iVar6 = FUN_08004eac();
          if (2 < (uint)(iVar6 - iVar5)) {
            return 3;
          }
        }
      }
      else {
        *(uint *)(DAT_080058fc + 0x20) = *(uint *)(DAT_080058fc + 0x20) | 1;
        iVar5 = FUN_08004eac();
        while (-1 < *(int *)(iVar3 + 0x20) << 0x1e) {
          iVar6 = FUN_08004eac();
          if (2 < (uint)(iVar6 - iVar5)) {
            return 3;
          }
        }
      }
LAB_08005708:
      if (-1 < (int)((uint)*param_1 << 0x1d)) goto LAB_080057e8;
      if ((puVar1[2] & 0x3f) >> 3 == 4) {
        if ((*(int *)(iVar3 + 0x1c) << 0x1e < 0) && (*(int *)(param_1 + 8) == 0)) {
          return 1;
        }
        goto LAB_080057e8;
      }
      bVar8 = -1 < (int)(puVar1[0xf] << 3);
      if (bVar8) {
        puVar1[0xf] = puVar1[0xf] | 0x10000000;
      }
      if (-1 < (int)(*DAT_08005900 << 0x17)) {
        *DAT_08005900 = *DAT_08005900 | (int)DAT_08005900 >> 0x16;
        iVar5 = FUN_08004eac();
        while (-1 < (int)(*DAT_08005900 << 0x17)) {
          iVar6 = FUN_08004eac();
          if (2 < (uint)(iVar6 - iVar5)) {
            return 3;
          }
        }
      }
      if (*(int *)(param_1 + 8) == 1) {
LAB_08005796:
        *(uint *)(iVar3 + 0x1c) = *(uint *)(iVar3 + 0x1c) | 1;
      }
      else {
        if (*(int *)(param_1 + 8) == 5) {
          *(uint *)(iVar3 + 0x1c) = *(uint *)(iVar3 + 0x1c) | 4;
          goto LAB_08005796;
        }
        *(uint *)(iVar3 + 0x1c) = *(uint *)(iVar3 + 0x1c) & 0xfffffffe;
        *(uint *)(iVar3 + 0x1c) = *(uint *)(iVar3 + 0x1c) & 0xfffffffb;
      }
      if (*(int *)(param_1 + 8) == 0) {
        iVar5 = FUN_08004eac();
        while (*(int *)(iVar3 + 0x1c) << 0x1e < 0) {
          iVar6 = FUN_08004eac();
          if (DAT_08005904 < (uint)(iVar6 - iVar5)) {
            return 3;
          }
        }
      }
      else {
        iVar5 = FUN_08004eac();
        while (-1 < *(int *)(iVar3 + 0x1c) << 0x1e) {
          iVar6 = FUN_08004eac();
          if (DAT_08005904 < (uint)(iVar6 - iVar5)) {
            return 3;
          }
        }
      }
      if (bVar8) {
        puVar1[0xf] = puVar1[0xf] & 0xefffffff;
      }
LAB_080057e8:
      iVar3 = *(int *)(param_1 + 0x1c);
      if (iVar3 == 0) {
        return 0;
      }
      if ((puVar1[2] & 0x3f) >> 3 != 2) {
        if (iVar3 == 2) {
          *puVar1 = *puVar1 & 0xfeffffff;
          iVar3 = FUN_08004eac();
          do {
            if (-1 < (int)(*puVar1 << 6)) {
              puVar1[3] = *(uint *)(param_1 + 0x20) | *(uint *)(param_1 + 0x24) |
                          *(uint *)(param_1 + 0x2c) | *(int *)(param_1 + 0x28) << 8 |
                          *(uint *)(param_1 + 0x30) | *(uint *)(param_1 + 0x34) |
                          puVar1[3] & DAT_08005908;
              *puVar1 = *puVar1 | 0x1000000;
              puVar1[3] = puVar1[3] | 0x10000000;
              iVar3 = FUN_08004eac();
              do {
                if ((int)(*puVar1 << 6) < 0) {
                  return 0;
                }
                iVar5 = FUN_08004eac();
              } while ((uint)(iVar5 - iVar3) < 3);
              return 3;
            }
            iVar5 = FUN_08004eac();
          } while ((uint)(iVar5 - iVar3) < 3);
        }
        else {
          *puVar1 = *puVar1 & 0xfeffffff;
          iVar3 = FUN_08004eac();
          do {
            if (-1 < (int)(*puVar1 << 6)) {
              puVar1[3] = puVar1[3] & DAT_0800590c;
              return 0;
            }
            iVar5 = FUN_08004eac();
          } while ((uint)(iVar5 - iVar3) < 3);
        }
        return 3;
      }
      if (iVar3 == 1) {
        return 1;
      }
      uVar2 = puVar1[3];
      if (((((uVar2 & 3) == *(uint *)(param_1 + 0x20)) &&
           ((uVar2 & 0x70) == *(uint *)(param_1 + 0x24))) &&
          ((uVar2 & 0x7f00) == *(int *)(param_1 + 0x28) * 0x100)) &&
         ((((uVar2 & 0x3e0000) == *(uint *)(param_1 + 0x2c) &&
           ((uVar2 & 0xe000000) == *(uint *)(param_1 + 0x30))) &&
          ((uVar2 & 0xe0000000) == *(uint *)(param_1 + 0x34))))) {
        return 0;
      }
      return 1;
    }
    if (-1 < *(int *)(DAT_080058fc + 0x20) << 0x1e) goto LAB_08005708;
    bVar9 = *(int *)(param_1 + 0x18) == 0;
    uVar2 = 0;
    if (!bVar9) goto LAB_08005708;
LAB_08005616:
    bVar8 = true;
    if (bVar9) goto LAB_0800552c;
LAB_08005618:
    iVar3 = *(int *)(param_1 + 0x14);
    uVar7 = puVar1[1] & 0xffff80ff | iVar3 << 8;
    puVar1[1] = uVar7;
    if (uVar2 == 0) {
      *puVar1 = *puVar1 & ~param_2 | *(uint *)(param_1 + 0x10);
      uVar4 = FUN_08000160(DAT_080058f0,1 << ((*puVar1 & 0x3fff) >> 0xb),uVar7,iVar3 << 8,param_4);
      *DAT_080058f4 = uVar4;
    }
    uVar10 = FUN_08004f14(*DAT_080058f8);
    param_2 = (uint)((ulonglong)uVar10 >> 0x20);
    if ((int)uVar10 != 0) {
      return 1;
    }
  } while( true );
}



/* FUN 0x08005910 FUN_08005910 */

undefined4 FUN_08005910(int *param_1)

{
  int iVar1;
  int iVar2;
  
  if ((char)param_1[10] == '\x01') {
    return 2;
  }
  *(undefined1 *)(param_1 + 10) = 1;
  *(undefined1 *)((int)param_1 + 0x29) = 2;
  *(undefined4 *)(*param_1 + 0x24) = 0xca;
  *(undefined4 *)(*param_1 + 0x24) = 0x53;
  *(uint *)(*param_1 + 0x18) = *(uint *)(*param_1 + 0x18) & 0xfffffbff;
  *(uint *)(*param_1 + 0x18) = *(uint *)(*param_1 + 0x18) & 0xffffbfff;
  iVar1 = FUN_08004eac();
  do {
    if (*(int *)(*param_1 + 0xc) << 0x1d < 0) {
      *(undefined4 *)(*param_1 + 0x24) = 0xff;
      *(undefined1 *)((int)param_1 + 0x29) = 1;
      *(undefined1 *)(param_1 + 10) = 0;
      return 0;
    }
    iVar2 = FUN_08004eac();
  } while ((uint)(iVar2 - iVar1) < 0x3e9);
  *(undefined4 *)(*param_1 + 0x24) = 0xff;
  *(undefined1 *)((int)param_1 + 0x29) = 3;
  *(undefined1 *)(param_1 + 10) = 0;
  return 3;
}



/* FUN 0x0800598c FUN_0800598c */

longlong FUN_0800598c(int *param_1,undefined4 param_2,uint param_3)

{
  int iVar1;
  int iVar2;
  
  if ((char)param_1[10] == '\x01') {
    return CONCAT44(param_1,2);
  }
  *(undefined1 *)(param_1 + 10) = 1;
  *(undefined1 *)((int)param_1 + 0x29) = 2;
  *(undefined4 *)(*param_1 + 0x24) = 0xca;
  *(undefined4 *)(*param_1 + 0x24) = 0x53;
  *(uint *)(*param_1 + 0x18) = *(uint *)(*param_1 + 0x18) & 0xfffffbff;
  *(uint *)(*param_1 + 0x5c) = *(uint *)(*param_1 + 0x5c) | 4;
  if (-1 < *(int *)(DAT_08005a48 + 0xc) << 0x19) {
    iVar1 = FUN_08004eac();
    while (-1 < *(int *)(*param_1 + 0xc) << 0x1d) {
      iVar2 = FUN_08004eac();
      if (1000 < (uint)(iVar2 - iVar1)) {
        *(undefined4 *)(*param_1 + 0x24) = 0xff;
        *(undefined1 *)((int)param_1 + 0x29) = 3;
        *(undefined1 *)(param_1 + 10) = 0;
        return CONCAT44(param_1,3);
      }
    }
  }
  *(undefined4 *)(*param_1 + 0x14) = param_2;
  *(uint *)(*param_1 + 0x18) = *(uint *)(*param_1 + 0x18) & 0xfffffff8;
  *(uint *)(*param_1 + 0x18) = *(uint *)(*param_1 + 0x18) | param_3;
  *DAT_08005a4c = *DAT_08005a4c | 0x80000;
  *(uint *)(*param_1 + 0x18) = *(uint *)(*param_1 + 0x18) | 0x4000;
  *(uint *)(*param_1 + 0x18) = *(uint *)(*param_1 + 0x18) | 0x400;
  *(undefined4 *)(*param_1 + 0x24) = 0xff;
  *(undefined1 *)((int)param_1 + 0x29) = 1;
  *(undefined1 *)(param_1 + 10) = 0;
  return ZEXT48(param_1) << 0x20;
}



/* FUN 0x08005a50 FUN_08005a50 */

void FUN_08005a50(void)

{
  return;
}



/* FUN 0x08005a52 FUN_08005a52 */

void FUN_08005a52(int *param_1)

{
  int iVar1;
  
  iVar1 = *param_1;
  if (*(int *)(iVar1 + 0x50) << 0x1d < 0) {
    *(uint *)(iVar1 + 0x5c) = *(uint *)(iVar1 + 0x5c) | 4;
    FUN_08005a50(param_1);
  }
  *(undefined1 *)((int)param_1 + 0x29) = 1;
  return;
}



/* FUN 0x08005a74 FUN_08005a74 */

int FUN_08005a74(int *param_1)

{
  int iVar1;
  
  if (param_1 == (int *)0x0) {
    return 1;
  }
  if (*(char *)((int)param_1 + 0x29) == '\0') {
    *(undefined1 *)(param_1 + 10) = 0;
    param_1[1] = 0x8800;
    FUN_08005b24(param_1);
  }
  *(undefined1 *)((int)param_1 + 0x29) = 2;
  if ((int)(~*(uint *)(*param_1 + 0xc) << 0x1b) < 0) {
    *(undefined4 *)(*param_1 + 0x24) = 0xca;
    *(undefined4 *)(*param_1 + 0x24) = 0x53;
    iVar1 = FUN_08006d72(param_1);
    if (iVar1 == 0) {
      *(uint *)(*param_1 + 0x18) = *(uint *)(*param_1 + 0x18) & DAT_08005b20;
      *(uint *)(*param_1 + 0x18) = *(uint *)(*param_1 + 0x18) | param_1[2] | param_1[5] | param_1[7]
      ;
      *(int *)(*param_1 + 0x10) = param_1[4];
      *(uint *)(*param_1 + 0x10) =
           *(uint *)(*param_1 + 0x10) | (uint)*(ushort *)(param_1 + 3) << 0x10;
      iVar1 = FUN_08006db8(param_1);
      if (iVar1 == 0) {
        *(uint *)(*param_1 + 0x18) = *(uint *)(*param_1 + 0x18) & 0x1fffffff;
        *(uint *)(*param_1 + 0x18) =
             *(uint *)(*param_1 + 0x18) | param_1[9] | param_1[8] | param_1[6];
      }
    }
    *(undefined4 *)(*param_1 + 0x24) = 0xff;
    if (iVar1 != 0) {
      return iVar1;
    }
  }
  *(undefined1 *)((int)param_1 + 0x29) = 1;
  return 0;
}



/* FUN 0x08005b24 FUN_08005b24 */

void FUN_08005b24(int *param_1)

{
  int iVar1;
  undefined4 local_38 [9];
  undefined4 local_14;
  uint local_c;
  
  FUN_080001e6(local_38,0x2c);
  if (*param_1 == DAT_08005b84) {
    local_38[0] = 0x20000;
    local_14 = 0x200;
    iVar1 = FUN_08005128(local_38);
    if (iVar1 != 0) {
      FUN_08003e90();
    }
    *(uint *)(DAT_08005b88 + 0x1c) = *(uint *)(DAT_08005b88 + 0x1c) | 0x8000;
    iVar1 = DAT_08005b88;
    local_c = DAT_08005b88 + -0x40 >> 0x14;
    *(uint *)(DAT_08005b88 + -4) = *(uint *)(DAT_08005b88 + -4) | local_c;
    local_c = *(uint *)(iVar1 + -4) & local_c;
    FUN_08005024(2,3,0);
    FUN_0800500c(2);
  }
  return;
}



/* FUN 0x08005b8c FUN_08005b8c */

undefined4 FUN_08005b8c(int *param_1)

{
  int iVar1;
  int iVar2;
  
  *(uint *)(*param_1 + 0xc) = *(uint *)(*param_1 + 0xc) & 0xffffff5f;
  iVar1 = FUN_08004eac();
  do {
    if (*(int *)(*param_1 + 0xc) << 0x1a < 0) {
      return 0;
    }
    iVar2 = FUN_08004eac();
  } while ((uint)(iVar2 - iVar1) < 0x3e9);
  return 3;
}



/* FUN 0x08005bc0 FUN_08005bc0 */

void FUN_08005bc0(uint param_1)

{
  *DAT_08005bd0 = *DAT_08005bd0 & 0xfffff9ff | param_1;
  return;
}



/* FUN 0x08005bd4 FUN_08005bd4 */

void FUN_08005bd4(void)

{
  return;
}



/* FUN 0x08005bd6 FUN_08005bd6 */

void FUN_08005bd6(void)

{
  return;
}



/* FUN 0x08005bd8 FUN_08005bd8 */

void FUN_08005bd8(void)

{
  return;
}



/* FUN 0x08005bda FUN_08005bda */

undefined4 FUN_08005bda(undefined4 *param_1)

{
  if (param_1 == (undefined4 *)0x0) {
    return 1;
  }
  if (*(char *)((int)param_1 + 0x3d) == '\0') {
    *(undefined1 *)(param_1 + 0xf) = 0;
    FUN_08005c26(param_1);
  }
  *(undefined1 *)((int)param_1 + 0x3d) = 2;
  FUN_080084c0(*param_1,param_1 + 1);
  *(undefined1 *)(param_1 + 0x12) = 1;
  *(undefined1 *)((int)param_1 + 0x3e) = 1;
  *(undefined1 *)((int)param_1 + 0x3f) = 1;
  *(undefined1 *)(param_1 + 0x10) = 1;
  *(undefined1 *)((int)param_1 + 0x41) = 1;
  *(undefined1 *)((int)param_1 + 0x42) = 1;
  *(undefined1 *)((int)param_1 + 0x43) = 1;
  *(undefined1 *)(param_1 + 0x11) = 1;
  *(undefined1 *)((int)param_1 + 0x45) = 1;
  *(undefined1 *)((int)param_1 + 0x46) = 1;
  *(undefined1 *)((int)param_1 + 0x47) = 1;
  *(undefined1 *)((int)param_1 + 0x3d) = 1;
  return 0;
}



/* FUN 0x08005c26 FUN_08005c26 */

void FUN_08005c26(void)

{
  return;
}



/* FUN 0x08005c28 FUN_08005c28 */

undefined4 FUN_08005c28(int *param_1)

{
  uint *puVar1;
  
  if (*(char *)((int)param_1 + 0x3d) != '\x01') {
    return 1;
  }
  *(undefined1 *)((int)param_1 + 0x3d) = 2;
  *(uint *)(*param_1 + 0xc) = *(uint *)(*param_1 + 0xc) | 1;
  puVar1 = (uint *)*param_1;
  if ((((puVar1 == DAT_08005c78) || (puVar1 == DAT_08005c7c)) || (puVar1 == DAT_08005c80)) ||
     (puVar1 == DAT_08005c84)) {
    if ((puVar1[2] & DAT_08005c88) == 6) {
      return 0;
    }
    if ((puVar1[2] & DAT_08005c88) == DAT_08005c88 - 7) {
      return 0;
    }
  }
  *puVar1 = *puVar1 | 1;
  return 0;
}



/* FUN 0x08005c8c FUN_08005c8c */

void FUN_08005c8c(void)

{
  return;
}



/* FUN 0x08005c90 FUN_08005c90 */

void FUN_08005c90(int *param_1)

{
  int iVar1;
  
  iVar1 = *param_1;
  if ((-1 < (int)(~*(uint *)(iVar1 + 0x10) * 0x40000000)) &&
     (-1 < (int)(~*(uint *)(iVar1 + 0xc) << 0x1e))) {
    *(undefined4 *)(iVar1 + 0x10) = 0xfffffffd;
    *(undefined1 *)(param_1 + 7) = 1;
    if ((*(uint *)(*param_1 + 0x18) & 3) == 0) {
      FUN_08005e14(param_1);
      FUN_08005e16(param_1);
    }
    else {
      FUN_08005c8c();
    }
    *(undefined1 *)(param_1 + 7) = 0;
  }
  iVar1 = *param_1;
  if ((-1 < (int)(~*(uint *)(iVar1 + 0x10) << 0x1d)) &&
     (-1 < (int)(~*(uint *)(iVar1 + 0xc) << 0x1d))) {
    *(undefined4 *)(iVar1 + 0x10) = 0xfffffffb;
    *(undefined1 *)(param_1 + 7) = 2;
    if ((*(uint *)(*param_1 + 0x18) & 0x3ff) >> 8 == 0) {
      FUN_08005e14(param_1);
      FUN_08005e16(param_1);
    }
    else {
      FUN_08005c8c();
    }
    *(undefined1 *)(param_1 + 7) = 0;
  }
  iVar1 = *param_1;
  if ((-1 < (int)(~*(uint *)(iVar1 + 0x10) << 0x1c)) &&
     (-1 < (int)(~*(uint *)(iVar1 + 0xc) << 0x1c))) {
    *(undefined4 *)(iVar1 + 0x10) = 0xfffffff7;
    *(undefined1 *)(param_1 + 7) = 4;
    if ((*(uint *)(*param_1 + 0x1c) & 3) == 0) {
      FUN_08005e14(param_1);
      FUN_08005e16(param_1);
    }
    else {
      FUN_08005c8c();
    }
    *(undefined1 *)(param_1 + 7) = 0;
  }
  iVar1 = *param_1;
  if ((-1 < (int)(~*(uint *)(iVar1 + 0x10) << 0x1b)) &&
     (-1 < (int)(~*(uint *)(iVar1 + 0xc) << 0x1b))) {
    *(undefined4 *)(iVar1 + 0x10) = 0xffffffef;
    *(undefined1 *)(param_1 + 7) = 8;
    if ((*(uint *)(*param_1 + 0x1c) & 0x3ff) >> 8 == 0) {
      FUN_08005e14(param_1);
      FUN_08005e16(param_1);
    }
    else {
      FUN_08005c8c();
    }
    *(undefined1 *)(param_1 + 7) = 0;
  }
  iVar1 = *param_1;
  if (((~*(uint *)(iVar1 + 0x10) & 1) == 0) && ((~*(uint *)(iVar1 + 0xc) & 1) == 0)) {
    *(undefined4 *)(iVar1 + 0x10) = 0xfffffffe;
    FUN_08005e18(param_1);
  }
  iVar1 = *param_1;
  if ((-1 < (int)(~*(uint *)(iVar1 + 0x10) << 0x18)) &&
     (-1 < (int)(~*(uint *)(iVar1 + 0xc) << 0x18))) {
    *(undefined4 *)(iVar1 + 0x10) = 0xffffff7f;
    FUN_08005bd6(param_1);
  }
  iVar1 = *param_1;
  if ((-1 < (int)(~*(uint *)(iVar1 + 0x10) << 0x17)) &&
     (-1 < (int)(~*(uint *)(iVar1 + 0xc) << 0x18))) {
    *(undefined4 *)(iVar1 + 0x10) = DAT_08005e10;
    FUN_08005bd4(param_1);
  }
  iVar1 = *param_1;
  if ((-1 < (int)(~*(uint *)(iVar1 + 0x10) << 0x19)) &&
     (-1 < (int)(~*(uint *)(iVar1 + 0xc) << 0x19))) {
    *(undefined4 *)(iVar1 + 0x10) = 0xffffffbf;
    FUN_08005e2c(param_1);
  }
  iVar1 = *param_1;
  if ((-1 < (int)(~*(uint *)(iVar1 + 0x10) << 0x1a)) &&
     (-1 < (int)(~*(uint *)(iVar1 + 0xc) << 0x1a))) {
    *(undefined4 *)(iVar1 + 0x10) = 0xffffffdf;
    FUN_08005bd8(param_1);
  }
  return;
}



/* FUN 0x08005e14 FUN_08005e14 */

void FUN_08005e14(void)

{
  return;
}



/* FUN 0x08005e16 FUN_08005e16 */

void FUN_08005e16(void)

{
  return;
}



/* FUN 0x08005e18 FUN_08005e18 */

void FUN_08005e18(int *param_1)

{
  if (*param_1 == DAT_08005e28) {
    FUN_08004edc();
  }
  return;
}



/* FUN 0x08005e2c FUN_08005e2c */

void FUN_08005e2c(void)

{
  return;
}



/* FUN 0x08005e2e FUN_08005e2e */

undefined4 FUN_08005e2e(undefined4 *param_1)

{
  uint *puVar1;
  uint uVar2;
  
  if (*(char *)(param_1 + 0x21) != '\x01') {
    *(undefined1 *)(param_1 + 0x21) = 1;
    param_1[0x22] = 0x24;
    puVar1 = (uint *)*param_1;
    uVar2 = *puVar1;
    *puVar1 = *puVar1 & 0xfffffffe;
    param_1[0x19] = 0;
    *(uint *)*param_1 = uVar2 & 0xdfffffff;
    param_1[0x22] = 0x20;
    *(undefined1 *)(param_1 + 0x21) = 0;
    return 0;
  }
  return 2;
}



/* FUN 0x08005e6a FUN_08005e6a */

void FUN_08005e6a(void)

{
  return;
}



/* FUN 0x08005e6c FUN_08005e6c */

void FUN_08005e6c(void)

{
  return;
}



/* FUN 0x08005e6e FUN_08005e6e */

undefined4 FUN_08005e6e(int *param_1,uint param_2)

{
  uint *puVar1;
  uint uVar2;
  
  if ((char)param_1[0x21] != '\x01') {
    *(undefined1 *)(param_1 + 0x21) = 1;
    param_1[0x22] = 0x24;
    puVar1 = (uint *)*param_1;
    uVar2 = *puVar1;
    *puVar1 = *puVar1 & 0xfffffffe;
    *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & 0xf1ffffff | param_2;
    FUN_0800856c(param_1);
    *(uint *)*param_1 = uVar2;
    param_1[0x22] = 0x20;
    *(undefined1 *)(param_1 + 0x21) = 0;
    return 0;
  }
  return 2;
}



/* FUN 0x08005eb6 FUN_08005eb6 */

undefined4 FUN_08005eb6(int *param_1,uint param_2)

{
  uint *puVar1;
  uint uVar2;
  
  if ((char)param_1[0x21] != '\x01') {
    *(undefined1 *)(param_1 + 0x21) = 1;
    param_1[0x22] = 0x24;
    puVar1 = (uint *)*param_1;
    uVar2 = *puVar1;
    *puVar1 = *puVar1 & 0xfffffffe;
    *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & 0x1fffffff | param_2;
    FUN_0800856c(param_1);
    *(uint *)*param_1 = uVar2;
    param_1[0x22] = 0x20;
    *(undefined1 *)(param_1 + 0x21) = 0;
    return 0;
  }
  return 2;
}



/* FUN 0x08005efc FUN_08005efc */

void FUN_08005efc(void)

{
  return;
}



/* FUN 0x08005efe FUN_08005efe */

void FUN_08005efe(void)

{
  return;
}



/* FUN 0x08005f00 FUN_08005f00 */

undefined4 FUN_08005f00(int *param_1)

{
  if (param_1 != (int *)0x0) {
    param_1[0x22] = 0x24;
    *(uint *)*param_1 = *(uint *)*param_1 & 0xfffffffe;
    *(undefined4 *)*param_1 = 0;
    *(undefined4 *)(*param_1 + 4) = 0;
    *(undefined4 *)(*param_1 + 8) = 0;
    FUN_080062ac(param_1);
    param_1[0x24] = 0;
    param_1[0x22] = 0;
    param_1[0x23] = 0;
    param_1[0x1b] = 0;
    param_1[0x1c] = 0;
    *(undefined1 *)(param_1 + 0x21) = 0;
    return 0;
  }
  return 1;
}



/* FUN 0x08005f42 FUN_08005f42 */

void FUN_08005f42(void)

{
  return;
}



/* FUN 0x08005f44 FUN_08005f44 */

uint FUN_08005f44(int param_1)

{
  return *(uint *)(param_1 + 0x88) | *(uint *)(param_1 + 0x8c);
}



/* FUN 0x08005f50 FUN_08005f50 */

void FUN_08005f50(int *param_1)

{
  bool bVar1;
  short sVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  code *pcVar6;
  uint uVar7;
  uint *puVar8;
  int *piVar9;
  uint uVar10;
  
  puVar8 = (uint *)*param_1;
  uVar4 = puVar8[7];
  uVar3 = *puVar8;
  uVar7 = puVar8[2];
  piVar9 = param_1 + 0x20;
  if ((uVar4 & DAT_08006230) == 0) {
    if ((-1 < (int)(uVar4 << 0x1a)) || ((uVar3 & 0x20) == 0 && (uVar7 & 0x10000000) == 0))
    goto LAB_08006086;
    pcVar6 = (code *)param_1[0x1d];
  }
  else {
    uVar10 = DAT_08006234 & uVar7;
    if ((DAT_08006238 & uVar3) != 0 || uVar10 != 0) {
      if (((uVar4 & 1) != 0) && ((int)(uVar3 << 0x17) < 0)) {
        puVar8[8] = 1;
        param_1[0x24] = param_1[0x24] | 1;
      }
      if (((int)(uVar4 << 0x1e) < 0) && ((uVar7 & 1) != 0)) {
        *(undefined4 *)(*param_1 + 0x20) = 2;
        param_1[0x24] = param_1[0x24] | 4;
      }
      if (((int)(uVar4 << 0x1d) < 0) && ((uVar7 & 1) != 0)) {
        *(undefined4 *)(*param_1 + 0x20) = 4;
        param_1[0x24] = param_1[0x24] | 2;
      }
      if (((int)(uVar4 << 0x1c) < 0) && ((uVar3 & 0x20) != 0 || uVar10 != 0)) {
        *(undefined4 *)(*param_1 + 0x20) = 8;
        param_1[0x24] = param_1[0x24] | 8;
      }
      if (((int)(uVar4 << 0x14) < 0) && ((int)(uVar3 << 5) < 0)) {
        *(undefined4 *)(*param_1 + 0x20) = 0x800;
        param_1[0x24] = param_1[0x24] | 0x20;
      }
      if (param_1[0x24] == 0) {
        return;
      }
      if ((((int)(uVar4 << 0x1a) < 0) && ((uVar3 & 0x20) != 0 || (uVar7 & 0x10000000) != 0)) &&
         ((code *)param_1[0x1d] != (code *)0x0)) {
        (*(code *)param_1[0x1d])(param_1);
      }
      if ((-1 < *(int *)(*param_1 + 8) << 0x19) && ((param_1[0x24] & 0x28U) == 0)) {
        FUN_08005f42(param_1);
        param_1[0x24] = 0;
        return;
      }
      FUN_080086f4(param_1);
      iVar5 = *param_1;
      if (-1 < *(int *)(iVar5 + 8) << 0x19) {
LAB_08006072:
        FUN_08005f42(param_1);
        return;
      }
      uVar3 = 0;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        uVar3 = isIRQinterruptsEnabled();
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts(1);
      }
      *(uint *)(iVar5 + 8) = *(uint *)(iVar5 + 8) & 0xffffffbf;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((uVar3 & 1) == 1);
      }
      if (*piVar9 == 0) goto LAB_08006072;
      *(undefined4 *)(*piVar9 + 0x38) = DAT_0800623c;
      iVar5 = FUN_080048e6(*piVar9);
      if (iVar5 == 0) {
        return;
      }
      param_1 = (int *)*piVar9;
      pcVar6 = (code *)param_1[0xe];
      goto LAB_0800606e;
    }
LAB_08006086:
    if (((param_1[0x1b] == 1) && ((int)(uVar4 << 0x1b) < 0)) && ((int)(uVar3 << 0x1b) < 0)) {
      puVar8[8] = 0x10;
      puVar8 = (uint *)*param_1;
      if ((int)(puVar8[2] * 0x2000000) < 0) {
        uVar3 = *(uint *)(*(int *)*piVar9 + 4);
        uVar4 = uVar3 & 0xffff;
        if ((uVar4 != 0) && (uVar4 < *(ushort *)(param_1 + 0x17))) {
          *(short *)((int)param_1 + 0x5e) = (short)uVar3;
          if (-1 < **(int **)*piVar9 << 0x1a) {
            uVar3 = 0;
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              uVar3 = isIRQinterruptsEnabled();
            }
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              enableIRQinterrupts(1);
            }
            *puVar8 = *puVar8 & 0xfffffeff;
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              enableIRQinterrupts((uVar3 & 1) == 1);
            }
            uVar3 = 0;
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              uVar3 = isIRQinterruptsEnabled();
            }
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              enableIRQinterrupts(1);
            }
            *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & 0xfffffffe;
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              enableIRQinterrupts((uVar3 & 1) == 1);
            }
            uVar3 = 0;
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              uVar3 = isIRQinterruptsEnabled();
            }
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              enableIRQinterrupts(1);
            }
            *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & 0xffffffbf;
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              enableIRQinterrupts((uVar3 & 1) == 1);
            }
            param_1[0x23] = 0x20;
            param_1[0x1b] = 0;
            uVar3 = 0;
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              uVar3 = isIRQinterruptsEnabled();
            }
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              enableIRQinterrupts(1);
            }
            *(uint *)*param_1 = *(uint *)*param_1 & 0xffffffef;
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              enableIRQinterrupts((uVar3 & 1) == 1);
            }
            FUN_0800487a(*piVar9);
          }
          param_1[0x1c] = 2;
          sVar2 = (short)param_1[0x17] - *(short *)((int)param_1 + 0x5e);
LAB_080061a6:
          FUN_08005e6a(param_1,sVar2);
          return;
        }
      }
      else {
        sVar2 = (short)param_1[0x17] - *(short *)((int)param_1 + 0x5e);
        if ((*(short *)((int)param_1 + 0x5e) != 0) && (sVar2 != 0)) {
          uVar3 = 0;
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            uVar3 = isIRQinterruptsEnabled();
          }
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            enableIRQinterrupts(1);
          }
          *puVar8 = *puVar8 & 0xfffffedf;
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            enableIRQinterrupts((uVar3 & 1) == 1);
          }
          uVar3 = 0;
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            uVar3 = isIRQinterruptsEnabled();
          }
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            enableIRQinterrupts(1);
          }
          *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & ~DAT_08006234;
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            enableIRQinterrupts((uVar3 & 1) == 1);
          }
          param_1[0x23] = 0x20;
          param_1[0x1b] = 0;
          param_1[0x1d] = 0;
          uVar3 = 0;
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            uVar3 = isIRQinterruptsEnabled();
          }
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            enableIRQinterrupts(1);
          }
          *(uint *)*param_1 = *(uint *)*param_1 & 0xffffffef;
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            enableIRQinterrupts((uVar3 & 1) == 1);
          }
          param_1[0x1c] = 2;
          goto LAB_080061a6;
        }
      }
      return;
    }
    if (((int)(uVar4 << 0xb) < 0) && ((int)(uVar7 << 9) < 0)) {
      puVar8[8] = 0x100000;
      FUN_08005efe(param_1);
      return;
    }
    if ((-1 < (int)(uVar4 << 0x18)) || ((uVar3 & 0x80) == 0 && (uVar7 & 0x800000) == 0)) {
      if (((int)(uVar4 << 0x19) < 0) && ((int)(uVar3 << 0x19) < 0)) {
        uVar3 = 0;
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          uVar3 = isIRQinterruptsEnabled();
        }
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts(1);
        }
        *puVar8 = *puVar8 & 0xffffffbf;
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts((uVar3 & 1) == 1);
        }
        param_1[0x22] = 0x20;
        param_1[0x1e] = 0;
        FUN_08006776();
        return;
      }
      if (((int)(uVar4 << 8) < 0) && ((int)(uVar3 << 1) < 0)) {
        FUN_08005efc(param_1);
      }
      else if (((int)(uVar4 << 7) < 0) && ((int)uVar3 < 0)) {
        FUN_08005e6c(param_1);
        return;
      }
      return;
    }
    pcVar6 = (code *)param_1[0x1e];
  }
  if (pcVar6 == (code *)0x0) {
    return;
  }
LAB_0800606e:
  (*pcVar6)(param_1);
  return;
}



/* FUN 0x08006240 FUN_08006240 */

undefined4 FUN_08006240(int *param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  if (param_1 != (int *)0x0) {
    if (param_1[0x22] == 0) {
      *(undefined1 *)(param_1 + 0x21) = 0;
      FUN_08006308(param_1);
    }
    param_1[0x22] = 0x24;
    *(uint *)*param_1 = *(uint *)*param_1 & 0xfffffffe;
    iVar1 = FUN_08008bd8(param_1);
    if (iVar1 != 1) {
      if (param_1[10] != 0) {
        FUN_080085b0(param_1);
      }
      *(uint *)(*param_1 + 4) = *(uint *)(*param_1 + 4) & 0xffffb7ff;
      *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & 0xffffffd5;
      *(uint *)*param_1 = *(uint *)*param_1 | 1;
      uVar2 = FUN_0800867c(param_1);
      return uVar2;
    }
  }
  return 1;
}



/* FUN 0x080062ac FUN_080062ac */

void FUN_080062ac(int *param_1)

{
  if (*param_1 == DAT_080062f8) {
    *DAT_080062fc = *DAT_080062fc & 0xffffbfff;
    FUN_08004c1c(0x50000000,0x600);
    FUN_08004fec(0x1b);
  }
  else if (*param_1 == DAT_08006300) {
    DAT_080062fc[-1] = DAT_080062fc[-1] & 0xfffbffff;
    FUN_08004c1c(DAT_08006304,0x300);
    return;
  }
  return;
}



/* FUN 0x08006308 FUN_08006308 */

void FUN_08006308(int *param_1)

{
  int iVar1;
  int iVar2;
  undefined4 local_58;
  undefined4 local_54;
  undefined4 local_4c;
  undefined4 local_2c;
  undefined4 uStack_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  uint local_18;
  
  FUN_080001e6(&local_2c,0x14);
  FUN_080001e6(&local_58,0x2c);
  iVar1 = DAT_080063e0;
  if (*param_1 == DAT_080063dc) {
    local_58 = 1;
    local_54 = 2;
    iVar2 = FUN_08005128(&local_58);
    if (iVar2 != 0) {
      FUN_08003e90();
    }
    *(uint *)(DAT_080063e0 + 0x40) = *(uint *)(DAT_080063e0 + 0x40) | 0x4000;
    *(uint *)(iVar1 + 0x34) = *(uint *)(iVar1 + 0x34) | 1;
    local_24 = 0;
    local_18 = *(uint *)(iVar1 + 0x34) & 1;
    local_1c = 1;
    local_20 = 0;
    local_2c = 0x600;
    uStack_28 = 2;
    FUN_08004d30(0x50000000,&local_2c);
    FUN_08005024(0x1b,3,0);
    FUN_0800500c(0x1b);
  }
  else if (*param_1 == DAT_080063e4) {
    local_58 = 4;
    local_4c = 0;
    iVar2 = FUN_08005128(&local_58);
    if (iVar2 != 0) {
      FUN_08003e90();
    }
    *(uint *)(iVar1 + 0x3c) = *(uint *)(iVar1 + 0x3c) | 0x40000;
    *(uint *)(iVar1 + 0x34) = *(uint *)(iVar1 + 0x34) | 2;
    local_24 = 0;
    local_18 = *(uint *)(iVar1 + 0x34) & 2;
    local_1c = 4;
    local_20 = 0;
    local_2c = 0x300;
    uStack_28 = 2;
    FUN_08004d30(DAT_080063e8,&local_2c);
  }
  return;
}



/* FUN 0x080063ec FUN_080063ec */

undefined4 FUN_080063ec(int *param_1,ushort *param_2,int param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  ushort uVar3;
  ushort *puVar4;
  ushort *local_34;
  
  if (param_1[0x23] != 0x20) {
    return 2;
  }
  if (((param_2 == (ushort *)0x0) || (param_3 == 0)) ||
     ((param_1[2] == 0x1000 && ((param_1[4] == 0 && (((uint)param_2 & 1) != 0)))))) {
    return 1;
  }
  param_1[0x24] = 0;
  param_1[0x23] = 0x22;
  param_1[0x1b] = 0;
  uVar1 = FUN_08004eac();
  *(short *)(param_1 + 0x17) = (short)param_3;
  *(short *)((int)param_1 + 0x5e) = (short)param_3;
  iVar2 = param_1[2];
  uVar3 = 0xff;
  if (iVar2 == 0x1000) {
    if (param_1[4] == 0) {
      uVar3 = (ushort)DAT_080064e8;
    }
    goto LAB_0800646c;
  }
  if (iVar2 == 0) {
    if (param_1[4] == 0) goto LAB_0800646c;
  }
  else {
    if (iVar2 != 0x10000000) {
      uVar3 = 0;
      goto LAB_0800646c;
    }
    if (param_1[4] != 0) {
      uVar3 = 0x3f;
      goto LAB_0800646c;
    }
  }
  uVar3 = 0x7f;
LAB_0800646c:
  *(ushort *)(param_1 + 0x18) = uVar3;
  if ((iVar2 == 0x1000) && (param_1[4] == 0)) {
    local_34 = (ushort *)0x0;
    puVar4 = param_2;
  }
  else {
    puVar4 = (ushort *)0x0;
    local_34 = param_2;
  }
  while( true ) {
    if (*(short *)((int)param_1 + 0x5e) == 0) {
      param_1[0x23] = 0x20;
      return 0;
    }
    iVar2 = FUN_08008ec4(param_1,0x20,0,uVar1,param_4);
    if (iVar2 != 0) break;
    if (local_34 == (ushort *)0x0) {
      *puVar4 = (ushort)*(undefined4 *)(*param_1 + 0x24) & uVar3;
      puVar4 = puVar4 + 1;
    }
    else {
      *(byte *)local_34 = (byte)*(undefined4 *)(*param_1 + 0x24) & (byte)uVar3;
      local_34 = (ushort *)((int)local_34 + 1);
    }
    *(short *)((int)param_1 + 0x5e) = *(short *)((int)param_1 + 0x5e) + -1;
  }
  return 3;
}



/* FUN 0x080064ec FUN_080064ec */

undefined4 FUN_080064ec(int *param_1,uint param_2,int param_3)

{
  bool bVar1;
  undefined4 uVar2;
  uint uVar3;
  uint *puVar4;
  
  if (param_1[0x23] != 0x20) {
    return 2;
  }
  if (((param_2 != 0) && (param_3 != 0)) &&
     ((param_1[2] != 0x1000 || ((param_1[4] != 0 || ((param_2 & 1) == 0)))))) {
    param_1[0x1b] = 0;
    puVar4 = (uint *)*param_1;
    if ((int)(puVar4[1] << 8) < 0) {
      uVar3 = 0;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        uVar3 = isIRQinterruptsEnabled();
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts(1);
      }
      *puVar4 = *puVar4 | 0x4000000;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((uVar3 & 1) == 1);
      }
    }
    uVar2 = FUN_08008d98();
    return uVar2;
  }
  return 1;
}



/* FUN 0x08006544 FUN_08006544 */

/* WARNING: Type propagation algorithm not settling */

void FUN_08006544(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  char *pcVar2;
  char *pcVar3;
  undefined4 *puVar4;
  short sVar5;
  ushort uVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  
  puVar4 = DAT_080066a4;
  pcVar3 = DAT_080066a0;
  pcVar2 = DAT_0800669c;
  if (*param_1 != DAT_08006698) {
    return;
  }
  uVar6 = *(ushort *)(DAT_0800669c + 2);
  uVar8 = (uint)uVar6;
  cVar1 = *DAT_0800669c;
  if (uVar8 == 0) {
    if (((cVar1 != 'Z') && (cVar1 != 'D')) && (cVar1 != 'd')) goto LAB_08006580;
LAB_08006566:
    DAT_080066a0[uVar8] = cVar1;
    *(ushort *)(pcVar2 + 2) = uVar6 + 1;
    pcVar2[1] = cVar1;
  }
  else if (uVar8 < 0x4b0) goto LAB_08006566;
  if ((cVar1 == '\n') && (iVar7 = FUN_0800be74(DAT_080066a0), iVar7 != 0)) {
LAB_08006674:
    FUN_0800a888(*puVar4,8);
    goto LAB_08006686;
  }
  uVar8 = (uint)*(ushort *)(pcVar2 + 2);
  if (*pcVar3 != 'Z') {
    if (((uVar8 < 2) || (iVar7 = FUN_0800be74(DAT_080066a0), iVar7 != 0)) &&
       (*(ushort *)(pcVar2 + 2) < 0x3d)) goto LAB_08006580;
    goto LAB_08006682;
  }
  if (uVar8 == 1) goto LAB_08006580;
  if (uVar8 == 2) {
    if (pcVar3[1] == -0x5b) goto LAB_08006580;
LAB_08006682:
    FUN_0800a358();
  }
  else {
    if (uVar8 == 3) {
      if (pcVar3[1] == -0x5b) {
        cVar1 = pcVar3[2];
        if (cVar1 == '\x7f') goto LAB_08006580;
joined_r0x080065f6:
        if (cVar1 == -0x31) goto LAB_08006580;
      }
      goto LAB_08006682;
    }
    if (uVar8 != 4) {
      if (uVar8 == 5) {
        if (pcVar3[2] == -0x31) {
          sVar5 = (ushort)(byte)pcVar3[3] + (ushort)(byte)pcVar3[4] * 0x100;
          iVar7 = FUN_080063ec(DAT_080066a8,pcVar3 + 5,sVar5,0x14,param_4);
          if (iVar7 != 3) {
            uVar6 = *(short *)(pcVar2 + 2) + sVar5;
            goto LAB_08006648;
          }
        }
        else if (pcVar3[2] == '\x7f') goto LAB_08006580;
      }
      else {
        if (pcVar3[2] == '\x7f') {
          uVar9 = (byte)pcVar3[3] + 5;
        }
        else {
          if (pcVar3[2] != -0x31) goto LAB_08006682;
          uVar9 = (ushort)((ushort)(byte)pcVar3[4] * 0x100 + (ushort)(byte)pcVar3[3]) + 6;
        }
        if (uVar9 == uVar8) goto LAB_08006674;
        if (uVar8 <= uVar9) goto LAB_08006686;
      }
      goto LAB_08006682;
    }
    cVar1 = pcVar3[2];
    if (cVar1 != '\x7f') goto joined_r0x080065f6;
    iVar7 = FUN_080063ec(DAT_080066a8,pcVar3 + 4,pcVar3[3],10,param_4);
    if (iVar7 == 3) goto LAB_08006682;
    uVar6 = (ushort)(byte)pcVar3[3] + *(short *)(pcVar2 + 2);
LAB_08006648:
    *(ushort *)(pcVar2 + 2) = uVar6;
    pcVar2[1] = pcVar3[uVar6 - 1];
  }
LAB_08006686:
  if (*(short *)(pcVar2 + 2) == 0x4b0) {
    FUN_0800a358();
  }
LAB_08006580:
  iVar7 = FUN_080064ec(DAT_080066a8,DAT_0800669c,1);
  if (iVar7 != 0) {
    FUN_0800a888(*puVar4,0x40);
  }
  return;
}



/* FUN 0x080066ac FUN_080066ac */

undefined4 FUN_080066ac(int *param_1,ushort *param_2,int param_3,undefined4 param_4)

{
  undefined4 uVar1;
  ushort *puVar2;
  int iVar3;
  ushort *puVar4;
  int *piVar5;
  ushort *puVar6;
  
  if (param_1[0x22] == 0x20) {
    if (((param_2 == (ushort *)0x0) || (param_3 == 0)) ||
       ((param_1[2] == 0x1000 && ((param_1[4] == 0 && (((uint)param_2 & 1) != 0)))))) {
      uVar1 = 1;
    }
    else {
      param_1[0x24] = 0;
      param_1[0x22] = 0x21;
      piVar5 = param_1;
      puVar6 = param_2;
      uVar1 = FUN_08004eac();
      *(short *)(param_1 + 0x15) = (short)param_3;
      *(short *)((int)param_1 + 0x56) = (short)param_3;
      if ((param_1[2] == 0x1000) && (param_1[4] == 0)) {
        puVar2 = (ushort *)0x0;
        puVar4 = param_2;
      }
      else {
        puVar4 = (ushort *)0x0;
        puVar2 = param_2;
      }
      while( true ) {
        if (*(short *)((int)param_1 + 0x56) == 0) break;
        iVar3 = FUN_08008ec4(param_1,0x80,0,uVar1,param_4,uVar1,puVar2,piVar5,puVar6);
        if (iVar3 != 0) goto LAB_0800675c;
        if (puVar2 == (ushort *)0x0) {
          *(uint *)(*param_1 + 0x28) = *puVar4 & 0x1ff;
          puVar4 = puVar4 + 1;
          puVar2 = (ushort *)0x0;
        }
        else {
          *(uint *)(*param_1 + 0x28) = (uint)(byte)*puVar2;
          puVar2 = (ushort *)((int)puVar2 + 1);
        }
        *(short *)((int)param_1 + 0x56) = *(short *)((int)param_1 + 0x56) + -1;
      }
      iVar3 = FUN_08008ec4(param_1,0x40,0,uVar1,param_4,uVar1,puVar2,piVar5,puVar6);
      if (iVar3 == 0) {
        param_1[0x22] = 0x20;
        uVar1 = 0;
      }
      else {
LAB_0800675c:
        uVar1 = 3;
      }
    }
  }
  else {
    uVar1 = 2;
  }
  return uVar1;
}



/* FUN 0x08006776 FUN_08006776 */

void FUN_08006776(void)

{
  return;
}



/* FUN 0x08006778 FUN_08006778 */

void FUN_08006778(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* FUN 0x0800677a FUN_0800677a */

uint FUN_0800677a(int param_1)

{
  return *(uint *)(param_1 + 8) & 1;
}



/* FUN 0x08006782 FUN_08006782 */

uint FUN_08006782(int param_1)

{
  return *(uint *)(param_1 + 8) & 1;
}



/* FUN 0x0800678a FUN_0800678a */

uint FUN_0800678a(int param_1)

{
  return (*(uint *)(param_1 + 8) & 7) >> 2;
}



/* FUN 0x08006792 FUN_08006792 */

undefined4 FUN_08006792(int param_1)

{
  if ((*(uint *)(param_1 + 0xc) & 0xfff) >> 10 != 0) {
    return 0;
  }
  return 1;
}



/* FUN 0x080067a2 FUN_080067a2 */

void FUN_080067a2(uint *param_1,uint param_2)

{
  *param_1 = *param_1 & 0xfe3fffff | param_2;
  return;
}



/* FUN 0x080067b0 FUN_080067b0 */

void FUN_080067b0(int param_1,uint param_2,int param_3)

{
  *(uint *)(param_1 + 0x14) =
       *(uint *)(param_1 + 0x14) & ~(7 << (param_2 & 4)) | param_3 << (param_2 & 4);
  return;
}



/* FUN 0x080067c8 FUN_080067c8 */

void FUN_080067c8(int param_1,uint param_2)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = DAT_080067fc;
  if (*(char *)(DAT_080067fc + 7) == '\0') {
    for (uVar2 = 0; uVar2 < param_2; uVar2 = uVar2 + 1 & 0xffff) {
      if (*(char *)(iVar1 + 7) == '\0') {
        FUN_08009170(s__02x_08006800,*(undefined1 *)(param_1 + uVar2));
      }
    }
    if (*(char *)(iVar1 + 7) == '\0') {
      FUN_08009170(&DAT_08006808);
    }
  }
  return;
}



/* FUN 0x0800680c FUN_0800680c */

void FUN_0800680c(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  uint uVar2;
  uint uVar3;
  undefined1 local_18;
  undefined3 uStack_17;
  
  uVar1 = DAT_080068b4;
  uVar2 = param_2 - 2;
  uStack_17 = (undefined3)((uint)param_4 >> 8);
  local_18 = 0x5a;
  FUN_080066ac(DAT_080068b8,&local_18,1,DAT_080068b4);
  local_18 = 0xa5;
  FUN_080066ac(DAT_080068b8,&local_18,1,uVar1);
  local_18 = 0xff;
  FUN_080066ac(DAT_080068b8,&local_18,1,uVar1);
  _local_18 = CONCAT31(uStack_17,(char)param_2);
  FUN_080066ac(DAT_080068b8,&local_18,1,uVar1);
  for (uVar3 = 0; uVar3 < param_2; uVar3 = uVar3 + 1 & 0xffff) {
    _local_18 = CONCAT31(uStack_17,*(undefined1 *)(param_1 + uVar3));
    FUN_080066ac(DAT_080068b8,&local_18,1,DAT_080068b4);
    uVar2 = (uint)*(byte *)(param_1 + uVar3) + (uVar2 & 0xff);
  }
  _local_18 = CONCAT31(uStack_17,(char)uVar2);
  FUN_080066ac(DAT_080068b8,&local_18,1,DAT_080068b4);
  if (*(char *)(DAT_080068bc + 0x19) == '\0') {
    if (*(char *)(DAT_080068c0 + 7) == '\0') {
      FUN_08009170(s_____02x____080068c4,uVar2 & 0xff);
    }
    FUN_080067c8(param_1,param_2);
  }
  return;
}



/* FUN 0x080068d0 FUN_080068d0 */

void FUN_080068d0(undefined1 param_1)

{
  undefined1 local_10;
  undefined3 uStack_f;
  undefined4 local_c;
  
  local_c = DAT_080068ec;
  _local_10 = CONCAT31((int3)((uint)DAT_080068e8 >> 8),param_1);
  FUN_0800680c(&local_10,5);
  return;
}



/* FUN 0x080068f0 FUN_080068f0 */

void FUN_080068f0(void)

{
  int *piVar1;
  int iVar2;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  
  piVar1 = DAT_08006960;
  iVar2 = DAT_0800695c;
  local_18 = 0;
  local_14 = 0;
  local_10 = 0;
  *DAT_08006960 = DAT_0800695c;
  piVar1[2] = 0;
  piVar1[3] = 0;
  piVar1[4] = 0;
  piVar1[1] = iVar2 << 0x14;
  piVar1[5] = 4;
  *(undefined1 *)(piVar1 + 6) = 0;
  *(undefined1 *)((int)piVar1 + 0x19) = 0;
  *(undefined1 *)((int)piVar1 + 0x1a) = 1;
  piVar1[7] = 1;
  *(undefined1 *)(piVar1 + 8) = 0;
  piVar1[9] = 0;
  piVar1[10] = 0;
  *(undefined1 *)(piVar1 + 0xb) = 0;
  piVar1[0xc] = 0;
  piVar1[0xe] = 0;
  piVar1[0xd] = 5;
  *(undefined1 *)(piVar1 + 0xf) = 0;
  piVar1[0x13] = 0;
  iVar2 = FUN_08004480();
  if (iVar2 != 0) {
    FUN_08003e90();
  }
  local_18 = DAT_08006964;
  local_14 = 0;
  local_10 = 0;
  iVar2 = FUN_08004100(DAT_08006960,&local_18);
  if (iVar2 != 0) {
    FUN_08003e90();
  }
  FUN_08003fd0(DAT_08006960);
  return;
}



/* FUN 0x08006968 FUN_08006968 */

void FUN_08006968(void)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  uVar3 = FUN_0800aa48(DAT_08006a14,0,0,DAT_08006a10);
  iVar2 = DAT_08006a18;
  iVar1 = DAT_08006a10;
  *(undefined4 *)(DAT_08006a18 + 0x10) = uVar3;
  uVar3 = FUN_0800aa48(DAT_08006a1c,1,0,iVar1 + 0x20);
  iVar1 = DAT_08006a10;
  *(undefined4 *)(iVar2 + 0x18) = uVar3;
  uVar3 = FUN_0800aa48(DAT_08006a20,1,0,iVar1 + 0x30);
  iVar1 = DAT_08006a10;
  *(undefined4 *)(iVar2 + 0x1c) = uVar3;
  uVar3 = FUN_0800aa48(DAT_08006a24,1,0,iVar1 + 0x40);
  iVar1 = DAT_08006a10;
  *(undefined4 *)(iVar2 + 0x20) = uVar3;
  uVar3 = FUN_0800aa48(DAT_08006a28,0,0,iVar1 + 0x10);
  iVar1 = DAT_08006a10;
  *(undefined4 *)(iVar2 + 0x14) = uVar3;
  uVar3 = FUN_0800aa48(DAT_08006a2c,0,0,iVar1 + 0x50);
  iVar1 = DAT_08006a10;
  *(undefined4 *)(iVar2 + 0x24) = uVar3;
  uVar3 = FUN_0800a93c(DAT_08006a30,0,iVar1 + 0x84);
  iVar1 = DAT_08006a10;
  *(undefined4 *)(iVar2 + 0x2c) = uVar3;
  uVar3 = FUN_0800a93c(DAT_08006a34,0,iVar1 + 0xa8);
  iVar1 = DAT_08006a10;
  *(undefined4 *)(iVar2 + 0x30) = uVar3;
  uVar3 = FUN_0800a93c(DAT_08006a38,0,iVar1 + 0xcc);
  iVar1 = DAT_08006a10;
  *(undefined4 *)(iVar2 + 0x34) = uVar3;
  uVar3 = FUN_0800a93c(DAT_08006a3c,0,iVar1 + 0x60);
  *(undefined4 *)(iVar2 + 0x28) = uVar3;
  uVar3 = FUN_0800a836(DAT_08006a10 + 0xf0);
  *(undefined4 *)(iVar2 + 0x38) = uVar3;
  return;
}



/* FUN 0x08006a40 FUN_08006a40 */

void FUN_08006a40(void)

{
  int iVar1;
  undefined4 local_30;
  undefined4 local_2c;
  undefined4 local_28;
  undefined4 local_24;
  uint local_1c;
  
  FUN_080001e6(&local_30,0x14);
  iVar1 = DAT_08006b6c;
  *(uint *)(DAT_08006b6c + 0x34) = *(uint *)(DAT_08006b6c + 0x34) | 2;
  *(uint *)(iVar1 + 0x34) = *(uint *)(iVar1 + 0x34) | 4;
  *(uint *)(iVar1 + 0x34) = *(uint *)(iVar1 + 0x34) | 1;
  local_1c = *(uint *)(iVar1 + 0x34) & 1;
  FUN_08004e9e(0x50000000,0xca,0);
  FUN_08004e9e(DAT_08006b70,4,0);
  local_30 = DAT_08006b74;
  local_2c = 3;
  local_28 = 0;
  FUN_08004d30(DAT_08006b78,&local_30);
  local_2c = 0x210000;
  local_30 = 1;
  local_28 = 0;
  FUN_08004d30(0x50000000,&local_30);
  local_30 = 0xca;
  local_28 = 0;
  local_2c = 1;
  local_24 = 0;
  FUN_08004d30(0x50000000,&local_30);
  local_2c = 0x310000;
  local_30 = 4;
  local_28 = 0;
  FUN_08004d30(0x50000000,&local_30);
  local_30 = DAT_08006b7c;
  local_2c = 3;
  local_28 = 0;
  FUN_08004d30(0x50000000,&local_30);
  local_30 = 0xc1;
  local_2c = 3;
  local_28 = 0;
  FUN_08004d30(DAT_08006b70,&local_30);
  local_2c = 0x110000;
  local_30 = 2;
  local_28 = 0;
  FUN_08004d30(DAT_08006b70,&local_30);
  local_28 = 0;
  local_2c = 1;
  local_30 = 4;
  local_24 = 0;
  FUN_08004d30(DAT_08006b70,&local_30);
  local_30 = 0x20;
  local_2c = 0x310000;
  local_28 = 0;
  FUN_08004d30(DAT_08006b70,&local_30);
  FUN_08005024(5,3,0);
  FUN_0800500c(5);
  FUN_08005024(6,3,0);
  FUN_0800500c(6);
  FUN_08005024(7,3,0);
  FUN_0800500c(7);
  return;
}



/* FUN 0x08006b80 FUN_08006b80 */

void FUN_08006b80(int param_1)

{
  FUN_08004e9e(0x50000000,0x40,param_1 != 0);
  return;
}



/* FUN 0x08006b98 FUN_08006b98 */

void FUN_08006b98(int param_1)

{
  FUN_08004e9e(0x50000000,0x80,param_1 != 0);
  return;
}



/* FUN 0x08006bb0 FUN_08006bb0 */

void FUN_08006bb0(void)

{
  undefined4 *puVar1;
  int iVar2;
  
  puVar1 = DAT_08006bfc;
  *DAT_08006bfc = DAT_08006bf8;
  puVar1[3] = 0x7f;
  puVar1[2] = 0;
  puVar1[5] = 0;
  puVar1[6] = 0;
  puVar1[4] = 0x1f;
  puVar1[7] = 0;
  puVar1[8] = 0x40000000;
  puVar1[9] = 0;
  iVar2 = FUN_08005a74();
  if (iVar2 != 0) {
    FUN_08003e90();
  }
  iVar2 = FUN_0800598c(DAT_08006bfc,0xf0,4);
  if (iVar2 != 0) {
    FUN_08003e90();
  }
  FUN_08005910(DAT_08006bfc);
  return;
}



/* FUN 0x08006c00 FUN_08006c00 */

void FUN_08006c00(void)

{
  undefined4 *puVar1;
  int iVar2;
  
  puVar1 = DAT_08006c74;
  *DAT_08006c74 = DAT_08006c70;
  puVar1[1] = DAT_08006c78;
  puVar1[2] = 0;
  puVar1[3] = 0;
  puVar1[4] = 0;
  puVar1[6] = 0;
  puVar1[7] = 0;
  puVar1[8] = 0;
  puVar1[5] = 0xc;
  puVar1[9] = 0;
  puVar1[10] = 0x10;
  puVar1[0xf] = 0x1000;
  iVar2 = FUN_08006240();
  if (iVar2 != 0) {
    FUN_08003e90();
  }
  iVar2 = FUN_08005eb6(DAT_08006c74,0);
  if (iVar2 != 0) {
    FUN_08003e90();
  }
  iVar2 = FUN_08005e6e(DAT_08006c74,0);
  if (iVar2 != 0) {
    FUN_08003e90();
  }
  iVar2 = FUN_08005e2e(DAT_08006c74);
  if (iVar2 != 0) {
    FUN_08003e90();
  }
  FUN_080064ec(DAT_08006c74,DAT_08006c7c,1);
  return;
}



/* FUN 0x08006c80 FUN_08006c80 */

void FUN_08006c80(void)

{
  undefined4 *puVar1;
  int iVar2;
  
  FUN_08005f00(DAT_08006cec);
  puVar1 = DAT_08006cec;
  *DAT_08006cec = DAT_08006cf0;
  puVar1[1] = DAT_08006cf4;
  puVar1[2] = 0;
  puVar1[3] = 0;
  puVar1[4] = 0;
  puVar1[6] = 0;
  puVar1[7] = 0;
  puVar1[8] = 0;
  puVar1[5] = 4;
  puVar1[9] = 0;
  puVar1[10] = 0x10;
  puVar1[0xf] = 0x1000;
  iVar2 = FUN_08006240();
  if (iVar2 != 0) {
    FUN_08003e90();
  }
  iVar2 = FUN_08005eb6(DAT_08006cec,0);
  if (iVar2 != 0) {
    FUN_08003e90();
  }
  iVar2 = FUN_08005e6e(DAT_08006cec,0);
  if (iVar2 != 0) {
    FUN_08003e90();
  }
  iVar2 = FUN_08005e2e(DAT_08006cec);
  if (iVar2 != 0) {
    FUN_08003e90();
  }
  return;
}



/* FUN 0x08006cf8 FUN_08006cf8 */

void FUN_08006cf8(void)

{
  undefined4 *puVar1;
  int iVar2;
  
  FUN_08005f00(DAT_08006d64);
  puVar1 = DAT_08006d64;
  *DAT_08006d64 = DAT_08006d68;
  puVar1[1] = DAT_08006d6c;
  puVar1[2] = 0;
  puVar1[3] = 0;
  puVar1[4] = 0;
  puVar1[6] = 0;
  puVar1[7] = 0;
  puVar1[8] = 0;
  puVar1[5] = 8;
  puVar1[9] = 0;
  puVar1[10] = 0x10;
  puVar1[0xf] = 0x1000;
  iVar2 = FUN_08006240();
  if (iVar2 != 0) {
    FUN_08003e90();
  }
  iVar2 = FUN_08005eb6(DAT_08006d64,0);
  if (iVar2 != 0) {
    FUN_08003e90();
  }
  iVar2 = FUN_08005e6e(DAT_08006d64,0);
  if (iVar2 != 0) {
    FUN_08003e90();
  }
  iVar2 = FUN_08005e2e(DAT_08006d64);
  if (iVar2 != 0) {
    FUN_08003e90();
  }
  return;
}



/* FUN 0x08006d70 FUN_08006d70 */

void FUN_08006d70(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* FUN 0x08006d72 FUN_08006d72 */

int FUN_08006d72(int *param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = *param_1;
  iVar3 = 0;
  if (-1 < *(int *)(iVar1 + 0xc) << 0x19) {
    *(uint *)(iVar1 + 0xc) = *(uint *)(iVar1 + 0xc) | 0x80;
    iVar1 = FUN_08004eac();
    while ((-1 < *(int *)(*param_1 + 0xc) << 0x19 && (iVar3 != 3))) {
      iVar2 = FUN_08004eac();
      if (1000 < (uint)(iVar2 - iVar1)) {
        iVar3 = 3;
        *(undefined1 *)((int)param_1 + 0x29) = 3;
      }
    }
  }
  return iVar3;
}



/* FUN 0x08006db8 FUN_08006db8 */

undefined4 FUN_08006db8(int param_1)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar1 = DAT_08006e04;
  uVar3 = 0;
  *(uint *)(DAT_08006e04 + 0xc) = *(uint *)(DAT_08006e04 + 0xc) & 0xffffff7f;
  if (*(int *)(iVar1 + 0x18) * 0x4000000 < 0) {
    *(uint *)(iVar1 + 0x18) = *(uint *)(iVar1 + 0x18) & 0xffffffdf;
    iVar2 = FUN_08005b8c();
    if (iVar2 != 0) {
      *(undefined1 *)(param_1 + 0x29) = 3;
      uVar3 = 3;
    }
    *(uint *)(iVar1 + 0x18) = *(uint *)(iVar1 + 0x18) | 0x20;
  }
  else {
    iVar1 = FUN_08005b8c();
    if (iVar1 != 0) {
      *(undefined1 *)(param_1 + 0x29) = 3;
      uVar3 = 3;
    }
  }
  return uVar3;
}



/* FUN 0x08006e08 FUN_08006e08 */

void FUN_08006e08(void)

{
  FUN_08005a52(DAT_08006e14);
  return;
}



/* FUN 0x08006e18 FUN_08006e18 */

void FUN_08006e18(void)

{
  return;
}



/* FUN 0x08007214 FUN_08007214 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08007214(void)

{
  char cVar1;
  byte bVar2;
  ushort uVar3;
  byte bVar4;
  int iVar5;
  undefined4 uVar6;
  int extraout_r1;
  undefined4 extraout_r1_00;
  undefined4 extraout_r1_01;
  int extraout_r1_02;
  int extraout_r1_03;
  int extraout_r1_04;
  int extraout_r1_05;
  undefined1 extraout_r2;
  undefined1 extraout_r3;
  int unaff_r4;
  int unaff_r5;
  int unaff_r6;
  int iVar7;
  char *pcVar8;
  int in_stack_00000000;
  int in_stack_00000004;
  uint in_stack_00000008;
  uint in_stack_0000000c;
  uint in_stack_00000010;
  uint in_stack_00000014;
  undefined4 in_stack_00000018;
  undefined4 in_stack_0000001c;
  
  *(int *)(unaff_r4 + 0xc) = *(int *)(unaff_r4 + 0xc) + 1;
  iVar7 = *(int *)(unaff_r4 + 8);
  FUN_08000160(iVar7,5);
  *(int *)(unaff_r4 + 8) = iVar7 + 1;
  if ((extraout_r1 == 0) && (*(char *)(_DAT_080075ec + 6) != '\0')) {
    FUN_08002cb8();
  }
  if ((((*(char *)(unaff_r4 + 4) == '\0') && (*(char *)(unaff_r4 + 3) == '\0')) &&
      (*(char *)(unaff_r4 + 0x10) == '\0')) && (*(char *)(unaff_r4 + 0x11) == '\0')) {
    if (unaff_r6 == 10) {
      if (*(char *)(_DAT_080075ec + 7) == '\0') {
        FUN_08009170(s_Standby__reason__idle__080075ef + 1);
        FUN_08009170(&DAT_08007608);
      }
      FUN_080035d4(0x10,&stack0x00000008,1);
      FUN_080035d4(0x11,&stack0x00000008,1);
      FUN_08002c8e(0);
      FUN_08002c30(0);
      FUN_08005094(0x2b);
      FUN_080050a8(DAT_0800760c);
      *(undefined4 *)(DAT_08007614 + 0x18) = DAT_08007610;
      FUN_080050c4();
      goto LAB_08007252;
    }
LAB_080072bc:
    if (((((*(char *)(_DAT_080075ec + 0x3d) == '\0') && (*(char *)(unaff_r4 + 0x10) != '\0')) &&
         (*(char *)(in_stack_00000004 + 0x11) != '\0')) &&
        ((*(char *)(in_stack_00000004 + 0x13) == '\0' && (*(char *)(unaff_r4 + 0x11) != '\0')))) &&
       ((*(char *)(in_stack_00000000 + 0xd) != '\0' && (*(char *)(in_stack_00000000 + 0xf) == '\0'))
       )) {
      *(short *)(unaff_r4 + 0x38) = *(short *)(unaff_r4 + 0x38) + 1;
      *(short *)(in_stack_00000000 + 0x14) = *(short *)(in_stack_00000000 + 0x14) + 1;
      if (unaff_r5 == 5) {
        FUN_0800598c(_DAT_08007618,0x3840,4);
        if (*(char *)(_DAT_080075ec + 7) == '\0') {
          FUN_08009170(s_Standby__reason__gls_bat_full__0800761b + 1);
          FUN_08009170(&DAT_08007608);
        }
        FUN_080035d4(0x10,&stack0x00000008,1);
        FUN_080035d4(0x11,&stack0x00000008,1);
        FUN_08002c8e(0);
        FUN_08002c30(0);
        FUN_08005094(0x2b);
        FUN_080050a8(DAT_0800760c);
        *(undefined4 *)(DAT_08007614 + 0x18) = DAT_08007610;
        FUN_080050c4();
      }
    }
LAB_08007376:
    cVar1 = *(char *)(unaff_r4 + 0x19);
    if (cVar1 != '\0') {
      *(undefined1 *)(unaff_r4 + 0x10) = 1;
      *(undefined1 *)(unaff_r4 + 0x11) = 1;
      if (*(char *)(unaff_r4 + 0x1a) == '\0') {
        if (cVar1 == '\x01') {
          if (*(char *)(_DAT_080075ec + 7) == '\0') {
            FUN_08009170(s_ota_gls_ready_L_08007730);
            FUN_08009170(&DAT_08007608);
          }
          FUN_0800be90();
        }
        else {
          if (cVar1 != '\x02') {
            if (*(char *)(_DAT_080075ec + 7) == '\0') {
              FUN_08009170(s_ota_box_ready_08007750);
              FUN_08009170(&DAT_08007608);
            }
            FUN_0800be90();
            *(undefined1 *)(unaff_r4 + 0x1a) = 1;
            iVar7 = FUN_08001574();
            if (iVar7 == 0) {
              if (*(char *)(_DAT_080075ec + 7) == '\0') {
                FUN_08009170(s__OTA_BOX___get_bin_file_fail__ex_08007b50);
                FUN_08009170(&DAT_08007b84);
              }
              FUN_08001d68(0);
              *(undefined1 *)(unaff_r4 + 0x1c) = 0;
              *(undefined1 *)(unaff_r4 + 0x1d) = 0;
              *(undefined4 *)(unaff_r4 + 0x20) = 0;
              *(undefined4 *)(unaff_r4 + 0x24) = 0;
              *(undefined4 *)(unaff_r4 + 0x28) = 0;
              *(undefined1 *)(in_stack_00000004 + 0xc) = 0;
              *(undefined1 *)(unaff_r4 + 0x19) = 0;
              *(undefined1 *)(unaff_r4 + 0x18) = 0;
              FUN_080012e4();
            }
            else {
              if (*(char *)(_DAT_080075ec + 7) == '\0') {
                FUN_08009170(s__OTA_BOX___Get_bin_file_success_08007760);
                FUN_08009170(&DAT_08007608);
              }
              FUN_08001d68(1);
              FUN_0800a7b0(100);
              FUN_080038e0();
            }
            goto LAB_08007eda;
          }
          if (*(char *)(_DAT_080075ec + 7) == '\0') {
            FUN_08009170(s_ota_gls_ready_R_08007740);
            FUN_08009170(&DAT_08007608);
          }
          FUN_0800bede();
        }
        *(undefined1 *)(unaff_r4 + 0x1a) = 1;
        FUN_080068d0(0x56);
      }
      goto LAB_08007eda;
    }
  }
  else {
LAB_08007252:
    iVar7 = _DAT_080075ec;
    if (*(char *)(unaff_r4 + 4) == '\0') {
      if (*(char *)(unaff_r4 + 3) != '\0') goto LAB_0800736a;
      goto LAB_080072bc;
    }
    if ((*(char *)(unaff_r4 + 3) == '\0') && (*(char *)(unaff_r4 + 4) == '\0')) goto LAB_08007376;
LAB_0800736a:
    pcVar8 = (char *)(_DAT_080075ec + 0x3c);
    if (*(char *)(_DAT_080075ec + 0x3d) != '\0') goto LAB_08007376;
    if ((*(char *)(unaff_r4 + 0x10) == '\0') || (*(char *)(in_stack_00000004 + 0x11) == '\0')) {
      if ((*(char *)(unaff_r4 + 0x11) != '\0') && (*(char *)(in_stack_00000000 + 0xd) != '\0')) {
        if (*(char *)(unaff_r4 + 0x10) == '\0') {
          if (*(char *)(in_stack_00000004 + 0x11) != '\0') goto LAB_080073d8;
        }
        else if (*(char *)(in_stack_00000004 + 0x11) != '\0') goto LAB_080073b2;
        goto LAB_0800742c;
      }
      *(undefined2 *)(unaff_r4 + 0x38) = 0;
LAB_08007462:
      *(undefined2 *)(in_stack_00000000 + 0x14) = 0;
    }
    else {
LAB_080073b2:
      if ((*(char *)(unaff_r4 + 0x11) != '\0') && (*(char *)(in_stack_00000000 + 0xd) != '\0')) {
        if (*(ushort *)(unaff_r4 + 0x38) < *(ushort *)(in_stack_00000000 + 0x14)) {
          *(ushort *)(in_stack_00000000 + 0x14) = *(ushort *)(unaff_r4 + 0x38);
        }
        else {
          *(ushort *)(unaff_r4 + 0x38) = *(ushort *)(in_stack_00000000 + 0x14);
        }
      }
LAB_080073d8:
      uVar3 = *(ushort *)(unaff_r4 + 0x38);
      *(ushort *)(unaff_r4 + 0x38) = uVar3 + 1;
      iVar5 = _DAT_080075ec;
      if (300 < uVar3) {
        if (*(char *)(in_stack_00000004 + 0x13) == '\0') {
          if (*(char *)(_DAT_080075ec + 7) == '\0') {
            FUN_08009170(s_L_fake_standby_cnt_300s__now_che_08007664);
            FUN_08009170(&DAT_08007608);
          }
          FUN_08003a00(1);
          if (*(char *)(iVar5 + 3) != '\0') {
            FUN_080013b8();
          }
        }
        else {
          if (*(char *)(_DAT_080075ec + 7) == '\0') {
            FUN_08009170(s_L_water_detected__only_clear_tim_0800763c);
            FUN_08009170(&DAT_08007608);
          }
          *(undefined2 *)(unaff_r4 + 0x38) = 0;
        }
      }
LAB_0800742c:
      if ((*(char *)(in_stack_00000000 + 0xd) != '\0') &&
         (uVar3 = *(ushort *)(in_stack_00000000 + 0x14),
         *(ushort *)(in_stack_00000000 + 0x14) = uVar3 + 1, 300 < uVar3)) {
        if (*(char *)(in_stack_00000000 + 0xf) != '\0') {
          if (*(char *)(_DAT_080075ec + 7) == '\0') {
            FUN_08009170(s_R_water_detected__only_clear_tim_08007694);
            FUN_08009170(&DAT_08007608);
          }
          goto LAB_08007462;
        }
        if (*(char *)(_DAT_080075ec + 7) == '\0') {
          FUN_08009170(s_R_fake_standby_cnt_300s__now_che_080076bc);
          FUN_08009170(&DAT_08007608);
        }
        FUN_08003a00(0);
      }
    }
    if ((*(char *)(unaff_r4 + 3) != '\0') || (*(char *)(unaff_r4 + 4) == '\0')) {
LAB_08007508:
      *(undefined1 *)(unaff_r4 + 0x17) = 0;
      goto LAB_08007376;
    }
    if (*(char *)(unaff_r4 + 0x10) == '\0') {
      if (((*(char *)(unaff_r4 + 0x11) == '\0') && (*(char *)(iVar7 + 0x3d) == '\0')) &&
         (*pcVar8 == '\0')) {
        bVar2 = *(byte *)(unaff_r4 + 0x17);
        if (((bVar2 < 0x1f) && (*(byte *)(unaff_r4 + 0x17) = bVar2 + 1, bVar2 == 0x1d)) &&
           (*(char *)(_DAT_080075ec + 7) == '\0')) {
          pcVar8 = s_Box_idle_mode_ON___empty_box__080076ec;
          goto LAB_0800754c;
        }
        goto LAB_08007376;
      }
      goto LAB_08007508;
    }
    if (((*(char *)(unaff_r4 + 0x11) == '\0') || (*(char *)(iVar7 + 0x3d) != '\0')) ||
       (((*pcVar8 != '\0' ||
         (((*(char *)(in_stack_00000004 + 0x11) == '\0' ||
           (*(char *)(in_stack_00000000 + 0xd) == '\0')) ||
          (*(char *)(in_stack_00000004 + 0x13) != '\0')))) ||
        ((*(char *)(in_stack_00000000 + 0xf) != '\0' || (*(char *)(unaff_r4 + 0x19) != '\0'))))))
    goto LAB_08007508;
    bVar2 = *(byte *)(unaff_r4 + 0x17);
    if (((bVar2 < 0x1f) && (*(byte *)(unaff_r4 + 0x17) = bVar2 + 1, bVar2 == 0x1d)) &&
       (*(char *)(_DAT_080075ec + 7) == '\0')) {
      pcVar8 = s_Box_idle_mode_ON___gls_bat_full__0800770c;
LAB_0800754c:
      FUN_08009170(pcVar8);
      FUN_08009170(&DAT_08007608);
      goto LAB_08007376;
    }
  }
  if (*(char *)(unaff_r4 + 0x1a) != '\0') {
    *(undefined1 *)(unaff_r4 + 0x10) = 0;
    *(undefined1 *)(unaff_r4 + 0x11) = 0;
    *(undefined1 *)(unaff_r4 + 0x1a) = 0;
    FUN_08009a14();
  }
  iVar7 = _DAT_08007b88;
  if (*(char *)(_DAT_080075ec + 0x3d) != '\0') {
    *(undefined1 *)(unaff_r4 + 0x10) = 1;
    *(undefined1 *)(unaff_r4 + 0x11) = 1;
    goto LAB_08007eda;
  }
  if (*(char *)(unaff_r4 + 0x15) == '\0') {
    *(undefined1 *)(unaff_r4 + 0x10) = 1;
    *(undefined1 *)(unaff_r4 + 0x11) = 1;
    FUN_0800d154();
    goto LAB_08007eda;
  }
  in_stack_0000000c = (uint)*(byte *)(unaff_r4 + 0x10);
  in_stack_00000014 = (uint)*(byte *)(unaff_r4 + 0x11);
  while (iVar5 = _DAT_08007b88, *(char *)(iVar7 + 4) != '\0') {
    FUN_0800a7b0(0x32);
  }
  *(undefined1 *)(_DAT_08007b88 + 4) = 1;
  FUN_0800ce34();
  *(undefined1 *)(iVar5 + 4) = 0;
  if ((*(byte *)(unaff_r4 + 0x10) == 0) && (*(char *)(unaff_r4 + 0x1b) != '\0')) {
    *(undefined1 *)(unaff_r4 + 0x1b) = 0;
  }
  iVar7 = _DAT_08007b88;
  if ((*(byte *)(unaff_r4 + 0x10) == in_stack_0000000c) &&
     (*(byte *)(unaff_r4 + 0x11) == in_stack_00000014)) {
LAB_08007850:
    iVar7 = _DAT_08007b88;
    *(undefined1 *)(_DAT_08007b88 + 4) = 1;
    if ((((*(uint *)(unaff_r4 + 0x3c) < 10) || (*(uint *)(unaff_r4 + 0x58) < 10)) &&
        (*(char *)(_DAT_08007b88 + 0x3d) == '\0')) ||
       (in_stack_00000010 = in_stack_00000010 + 1 & 0xff, 9 < in_stack_00000010)) {
      FUN_080018e4();
      in_stack_00000010 = 0;
    }
    *(undefined1 *)(iVar7 + 4) = 0;
  }
  else {
    if (*(char *)(_DAT_08007b88 + 3) != '\0') {
      FUN_080013b8();
    }
    if (*(char *)(unaff_r4 + 0x10) == '\0') {
      FUN_08003a3c();
      *(undefined1 *)(in_stack_00000004 + 0x12) = extraout_r3;
      *(undefined1 *)(unaff_r4 + 0x12) = 0;
      uVar6 = extraout_r1_01;
    }
    else {
      FUN_08003a3c();
      uVar6 = extraout_r1_00;
    }
    if (*(char *)(unaff_r4 + 0x11) == '\0') {
      FUN_08003a60(in_stack_00000000,uVar6,*(undefined1 *)(in_stack_00000000 + 0xe));
      *(undefined1 *)(in_stack_00000000 + 0xe) = extraout_r2;
      *(undefined1 *)(unaff_r4 + 0x13) = 0;
    }
    else {
      FUN_08003a60();
    }
    if (*(char *)(iVar7 + 4) == '\0') goto LAB_08007850;
  }
  if ((*(byte *)(unaff_r4 + 0x10) == in_stack_0000000c) &&
     (*(byte *)(unaff_r4 + 0x11) == in_stack_00000014)) {
    if (10 < *(uint *)(unaff_r4 + 0xc)) {
      if (*(char *)(unaff_r4 + 0x14) == '\x01') {
        if ((((*(char *)(in_stack_00000004 + 0x10) != '\0') &&
             (*(char *)(in_stack_00000000 + 0xc) != '\0')) &&
            (*(char *)(in_stack_00000004 + 0x13) == '\0')) &&
           (*(char *)(in_stack_00000000 + 0xf) == '\0')) {
          if (*(char *)(_DAT_08007b88 + 7) == '\0') {
            pcVar8 = s_Switch_charging_result__ERROR__>_08007c98;
            goto LAB_08007936;
          }
          goto LAB_080079b0;
        }
      }
      else if (*(char *)(unaff_r4 + 0x14) == '\x02') {
        if ((*(char *)(in_stack_00000004 + 0x14) == '\0') ||
           (bVar2 = 0, *(char *)(in_stack_00000004 + 0x10) != '\0')) {
          bVar2 = 1;
        }
        if ((*(char *)(in_stack_00000000 + 0x10) == '\0') ||
           (bVar4 = 0, *(char *)(in_stack_00000000 + 0xc) != '\0')) {
          bVar4 = 1;
        }
        if (!(bool)(bVar2 & bVar4)) {
          if (*(char *)(_DAT_08007b88 + 7) == '\0') {
            pcVar8 = s_Switch_charging_result__GOOD__>_E_08007cc0;
            goto LAB_08007936;
          }
          goto LAB_080079b0;
        }
      }
    }
  }
  else {
    *(undefined4 *)(unaff_r4 + 0xc) = 0;
    if (*(byte *)(unaff_r4 + 2) < 3) {
      FUN_08006b80(0);
      FUN_08006b98(0);
      *(undefined1 *)(unaff_r4 + 2) = 2;
      if (*(char *)(_DAT_08007b88 + 7) == '\0') {
        FUN_08009170(s_clear_led_since_gls_status_updat_08007b8b + 1);
        FUN_08009170(&DAT_08007b84);
      }
    }
    iVar7 = _DAT_08007b88;
    if (*(char *)(unaff_r4 + 0x11) == '\0') {
      if (*(char *)(unaff_r4 + 0x10) == '\0') {
        if (*(char *)(_DAT_08007b88 + 7) == '\0') {
          pcVar8 = s_L___R_GLS_OUT__show_led_after_1s_08007c2c;
          goto LAB_08007936;
        }
      }
      else if (*(char *)(_DAT_08007b88 + 7) == '\0') {
        pcVar8 = s_L_IN__R_OUT__wait_1s_to_confirm__08007c74;
LAB_08007936:
        FUN_08009170(pcVar8);
        FUN_08009170(&DAT_08007b84);
      }
    }
    else if (*(char *)(unaff_r4 + 0x10) == '\0') {
      if (*(char *)(_DAT_08007b88 + 7) == '\0') {
        pcVar8 = s_L_OUT__R_IN__wait_1s_to_confirm__08007c50;
        goto LAB_08007936;
      }
    }
    else if ((*(char *)(in_stack_00000004 + 0x10) == '\0') ||
            (*(char *)(in_stack_00000000 + 0xc) == '\0')) {
      if (*(char *)(_DAT_08007b88 + 7) == '\0') {
        FUN_08009170(s_L___R_GLS_IN__Charging_status_un_08007bf0);
        FUN_08009170(&DAT_08007b84);
      }
      *(undefined1 *)(iVar7 + 1) = 8;
    }
    else if (*(char *)(_DAT_08007b88 + 7) == '\0') {
      pcVar8 = s_L___R_GLS_IN__Charging_status_co_08007bb0;
      goto LAB_08007936;
    }
LAB_080079b0:
    FUN_0800bb74();
  }
  if (7 < *(uint *)(unaff_r4 + 0x40)) {
    FUN_08000160(*(undefined4 *)(unaff_r4 + 0x44),0xf);
    if ((extraout_r1_02 == 0) && (*(char *)(_DAT_08007b88 + 7) == '\0')) {
      FUN_08009170(s_No_reply_from_GLS_L__wait_for__d_08007ce8,0xf);
      FUN_08009170(&DAT_08007b84);
    }
    *(int *)(unaff_r4 + 0x44) = *(int *)(unaff_r4 + 0x44) + 1;
  }
  if (7 < *(uint *)(unaff_r4 + 0x5c)) {
    FUN_08000160(*(undefined4 *)(unaff_r4 + 0x60),0xf);
    if ((extraout_r1_03 == 0) && (*(char *)(_DAT_08007b88 + 7) == '\0')) {
      FUN_08009170(s_No_reply_from_GLS_R__wait_for__d_08007d0c,0xf);
      FUN_08009170(&DAT_08007b84);
    }
    *(int *)(unaff_r4 + 0x60) = *(int *)(unaff_r4 + 0x60) + 1;
  }
  if (7 < *(uint *)(unaff_r4 + 0x40)) {
    uVar6 = *(undefined4 *)(unaff_r4 + 0x44);
    FUN_08000160(uVar6,0xb4);
    if (extraout_r1_04 == 0) {
      if (*(char *)(_DAT_08007b88 + 8) == '\0') {
        FUN_08009a9c(1,0);
        if (*(char *)(_DAT_08007b88 + 7) == '\0') {
          pcVar8 = s_No_reply_from_GLS_L_for__ds__res_08007d5c;
          uVar6 = *(undefined4 *)(unaff_r4 + 0x44);
          goto LAB_08007a54;
        }
      }
      else if (*(char *)(_DAT_08007b88 + 7) == '\0') {
        pcVar8 = s_No_reply_from_GLS_L_for__ds__do_n_08007d30;
LAB_08007a54:
        FUN_08009170(pcVar8,uVar6);
        FUN_08009170(&DAT_08007b84);
      }
    }
  }
  if ((7 < *(uint *)(unaff_r4 + 0x5c)) &&
     (FUN_08000160(*(undefined4 *)(unaff_r4 + 0x60),0xb4), iVar7 = _DAT_08007b88,
     extraout_r1_05 == 0)) {
    if (*(char *)(_DAT_08007b88 + 8) == '\0') {
      FUN_08009a9c(0,1);
      if (*(char *)(iVar7 + 7) == '\0') {
        pcVar8 = s_No_reply_from_GLS_R_for__ds__res_08007db4;
        uVar6 = *(undefined4 *)(unaff_r4 + 0x60);
        goto LAB_08007a96;
      }
    }
    else if (*(char *)(_DAT_08007b88 + 7) == '\0') {
      pcVar8 = s_No_reply_from_GLS_R_for__ds__do_n_08007d88;
      uVar6 = *(undefined4 *)(unaff_r4 + 0x44);
LAB_08007a96:
      FUN_08009170(pcVar8,uVar6);
      FUN_08009170(&DAT_08007b84);
    }
  }
  if (((7 < *(uint *)(unaff_r4 + 0x40)) && (*(int *)(unaff_r4 + 0x44) == 0xd2)) ||
     ((7 < *(uint *)(unaff_r4 + 0x5c) && (*(int *)(unaff_r4 + 0x60) == 0xd2)))) {
    FUN_0800bb74();
  }
  iVar7 = _DAT_08007b88;
  if ((((((*(char *)(unaff_r4 + 0x10) != '\0') && (*(char *)(unaff_r4 + 0x11) != '\0')) &&
        (0x14 < *(uint *)(unaff_r4 + 0xc))) &&
       ((0x32 < *(byte *)(in_stack_00000004 + 0x12) && (0x14 < *(byte *)(unaff_r4 + 1))))) &&
      (*(char *)(unaff_r4 + 0x1b) == '\0')) && (*(char *)(_DAT_08007b88 + 4) == '\0')) {
    *(undefined1 *)(_DAT_08007b88 + 4) = 1;
    if (*(char *)(iVar7 + 7) == '\0') {
      FUN_08009170(s__OTA_BOX___check_box_ota_firmwar_08007de0);
      FUN_08009170(&DAT_08007b84);
    }
    FUN_0800a7b0(100);
    in_stack_00000014 = DAT_08007e04;
    in_stack_00000018 = DAT_08007e08;
    in_stack_0000001c = CONCAT31((int3)((uint)DAT_08007e0c >> 8),0x1e);
    FUN_0800258c(1,&stack0x00000014,9);
    *(undefined1 *)(unaff_r4 + 0x1b) = 1;
    *(undefined1 *)(iVar7 + 4) = 0;
    FUN_08001e94(1);
  }
  iVar7 = _DAT_08007b88;
  if (*(char *)(_DAT_08007b88 + 3) != '\0') {
    in_stack_00000008 = FUN_0800a816(*(undefined4 *)(_DAT_08007b88 + 0x38));
    if ((int)(in_stack_00000008 << 0x1e) < 0) {
      FUN_0800a7d2(*(undefined4 *)(iVar7 + 0x38),2);
      FUN_0800aaf0(*(undefined4 *)(iVar7 + 0x10),DAT_08007ee4);
    }
    if ((int)(in_stack_00000008 << 0x13) < 0) {
      FUN_0800a7d2(*(undefined4 *)(iVar7 + 0x38),0x1000);
      FUN_080013b8();
    }
    if (((*(char *)(unaff_r4 + 1) == '\0') && (*(byte *)(unaff_r4 + 3) == 0)) &&
       (in_stack_00000008 = (uint)*(byte *)(unaff_r4 + 3), FUN_0800a01e(&stack0x00000008),
       in_stack_00000008 < DAT_08007ee8)) {
      if (*(char *)(iVar7 + 7) == '\0') {
        FUN_08009170(s_Standby_from_idle_mode__reason__l_08007eec);
        FUN_08009170(&DAT_08007f18);
      }
      FUN_080035d4(0x10,&stack0x0000000c,1);
      FUN_080035d4(0x11,&stack0x0000000c,1);
      FUN_08002c8e(0);
      FUN_08002c30(0);
      FUN_08005094(0x2b);
      FUN_080050a8(DAT_08007f1c);
      *(undefined4 *)(DAT_08007f24 + 0x18) = DAT_08007f20;
      FUN_080050c4();
    }
  }
  if (0x1d < *(byte *)(unaff_r4 + 0x17)) {
    if (*(char *)(iVar7 + 3) == '\0') {
      FUN_0800aa24(*(undefined4 *)(iVar7 + 0x2c));
      FUN_0800aa24(*(undefined4 *)(iVar7 + 0x30));
      FUN_0800aa24(*(undefined4 *)(iVar7 + 0x28));
      *(undefined1 *)(iVar7 + 3) = 1;
    }
    FUN_0800598c(DAT_08007f28,7,4);
    FUN_08005094(0x2b);
    FUN_080050a8(DAT_08007f1c + 8);
    FUN_080050e8(0,1);
    FUN_0800b600();
    goto LAB_08007ed6;
  }
LAB_08007eda:
  do {
    FUN_0800a7b0(1000);
LAB_08007ed6:
    FUN_08007214();
  } while( true );
}



/* FUN 0x08008420 FUN_08008420 */

void FUN_08008420(void)

{
  int iVar1;
  
  iVar1 = FUN_0800ca4c(*(undefined4 *)(DAT_08008434 + 0x10));
  if (iVar1 != 1) {
    FUN_0800c5ac();
  }
  return;
}



/* FUN 0x08008438 FUN_08008438 */

void FUN_08008438(void)

{
  int iVar1;
  undefined4 local_58 [3];
  undefined4 local_4c;
  undefined4 local_48;
  undefined4 local_44;
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 local_38;
  undefined4 local_34;
  undefined4 local_30;
  undefined4 local_2c;
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  
  FUN_080001e6(local_58,0x38);
  local_20 = 0;
  local_1c = 0;
  local_18 = 0;
  local_14 = 0;
  FUN_08005048(0x200);
  local_58[0] = 10;
  local_4c = 0x100;
  local_44 = 0x40;
  local_40 = 1;
  local_30 = 8;
  local_2c = 0x20000;
  local_3c = 2;
  local_28 = 0x2000000;
  local_38 = 2;
  local_48 = 0;
  local_24 = 0x20000000;
  local_34 = 0;
  iVar1 = FUN_08005528(local_58);
  if (iVar1 != 0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  local_20 = 7;
  local_18 = 0;
  local_1c = 2;
  local_14 = 0;
  iVar1 = FUN_080052e4(&local_20,2);
  if (iVar1 != 0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  return;
}



/* FUN 0x080084ae FUN_080084ae */

void FUN_080084ae(void)

{
  return;
}



/* FUN 0x080084b0 FUN_080084b0 */

void FUN_080084b0(void)

{
  FUN_08005c90(DAT_080084bc);
  return;
}



/* FUN 0x080084c0 FUN_080084c0 */

void FUN_080084c0(uint *param_1,uint *param_2)

{
  uint *puVar1;
  uint *puVar2;
  uint *puVar3;
  uint uVar4;
  
  puVar3 = DAT_0800854c;
  puVar2 = DAT_08008548;
  puVar1 = DAT_0800853c;
  uVar4 = *param_1;
  if (((param_1 == DAT_0800853c) || (param_1 == DAT_08008540)) || (param_1 == DAT_08008544)) {
    uVar4 = uVar4 & 0xffffff8f | param_2[1];
  }
  if ((((param_1 == DAT_0800853c) || (param_1 == DAT_08008540)) ||
      ((param_1 == DAT_08008544 || ((param_1 == DAT_08008550 || (param_1 == DAT_08008548)))))) ||
     ((param_1 == DAT_0800854c || (param_1 == DAT_08008554)))) {
    uVar4 = uVar4 & 0xfffffcff | param_2[3];
  }
  *param_1 = uVar4 & 0xffffff7f | param_2[5];
  param_1[0xb] = param_2[2];
  param_1[10] = *param_2;
  if ((((param_1 == puVar1) || (param_1 == puVar2)) || (param_1 == puVar3)) ||
     (param_1 == DAT_08008554)) {
    param_1[0xc] = param_2[4];
  }
  param_1[5] = 1;
  return;
}



/* FUN 0x0800856c FUN_0800856c */

void FUN_0800856c(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined2 uVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  
  iVar1 = DAT_080085ac;
  if (param_1[0x19] == 0) {
    uVar2 = 1;
    *(undefined2 *)((int)param_1 + 0x6a) = 1;
  }
  else {
    uVar4 = (*(uint *)(*param_1 + 8) & 0xfffffff) >> 0x19;
    uVar3 = *(uint *)(*param_1 + 8) >> 0x1d;
    iVar5 = DAT_080085ac + -8;
    uVar2 = FUN_08000160((uint)*(byte *)(iVar5 + uVar3) << 3,*(undefined1 *)(DAT_080085ac + uVar3),
                         param_3,param_4,param_4);
    *(undefined2 *)((int)param_1 + 0x6a) = uVar2;
    uVar2 = FUN_08000160((uint)*(byte *)(iVar5 + uVar4) << 3,*(undefined1 *)(iVar1 + uVar4));
  }
  *(undefined2 *)(param_1 + 0x1a) = uVar2;
  return;
}



/* FUN 0x080085b0 FUN_080085b0 */

void FUN_080085b0(int *param_1)

{
  if ((*(ushort *)(param_1 + 10) & 1) != 0) {
    *(uint *)(*param_1 + 4) = *(uint *)(*param_1 + 4) & 0xfffdffff | param_1[0xb];
  }
  if ((int)((uint)*(ushort *)(param_1 + 10) << 0x1e) < 0) {
    *(uint *)(*param_1 + 4) = *(uint *)(*param_1 + 4) & 0xfffeffff | param_1[0xc];
  }
  if ((int)((uint)*(ushort *)(param_1 + 10) << 0x1d) < 0) {
    *(uint *)(*param_1 + 4) = *(uint *)(*param_1 + 4) & 0xfffbffff | param_1[0xd];
  }
  if ((int)((uint)*(ushort *)(param_1 + 10) << 0x1c) < 0) {
    *(uint *)(*param_1 + 4) = *(uint *)(*param_1 + 4) & 0xffff7fff | param_1[0xe];
  }
  if ((int)((uint)*(ushort *)(param_1 + 10) << 0x1b) < 0) {
    *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & 0xffffefff | param_1[0xf];
  }
  if ((int)((uint)*(ushort *)(param_1 + 10) << 0x1a) < 0) {
    *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & 0xffffdfff | param_1[0x10];
  }
  if (((int)((uint)*(ushort *)(param_1 + 10) << 0x19) < 0) &&
     (*(uint *)(*param_1 + 4) = *(uint *)(*param_1 + 4) & 0xffefffff | param_1[0x11],
     param_1[0x11] == 0x100000)) {
    *(uint *)(*param_1 + 4) = *(uint *)(*param_1 + 4) & 0xff9fffff | param_1[0x12];
  }
  if ((int)((uint)*(ushort *)(param_1 + 10) << 0x18) < 0) {
    *(uint *)(*param_1 + 4) = *(uint *)(*param_1 + 4) & 0xfff7ffff | param_1[0x13];
  }
  return;
}



/* FUN 0x0800867c FUN_0800867c */

longlong FUN_0800867c(undefined4 *param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  
  param_1[0x24] = 0;
  uVar1 = FUN_08004eac();
  uVar3 = DAT_080086dc;
  if (*(int *)*param_1 << 0x1c < 0) {
    param_2 = DAT_080086dc;
    iVar2 = FUN_08008ec4(param_1,0x200000,0,uVar1,DAT_080086dc,uVar1,param_4);
    if (iVar2 != 0) goto LAB_080086c8;
  }
  if (*(int *)*param_1 << 0x1d < 0) {
    iVar2 = FUN_08008ec4(param_1,0x400000,0,uVar1,uVar3,uVar1,param_4);
    param_2 = uVar3;
    if (iVar2 != 0) {
LAB_080086c8:
      return CONCAT44(param_2,3);
    }
  }
  param_1[0x22] = 0x20;
  param_1[0x23] = 0x20;
  param_1[0x1b] = 0;
  param_1[0x1c] = 0;
  *(undefined1 *)(param_1 + 0x21) = 0;
  return (ulonglong)param_2 << 0x20;
}



/* FUN 0x080086e0 FUN_080086e0 */

void FUN_080086e0(int param_1)

{
  int iVar1;
  
  iVar1 = *(int *)(param_1 + 0x28);
  *(undefined2 *)(iVar1 + 0x5e) = 0;
  *(undefined2 *)(iVar1 + 0x56) = 0;
  FUN_08005f42();
  return;
}



/* FUN 0x080086f4 FUN_080086f4 */

void FUN_080086f4(int *param_1)

{
  bool bVar1;
  uint uVar2;
  
  uVar2 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar2 = isIRQinterruptsEnabled();
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts(1);
  }
  *(uint *)*param_1 = *(uint *)*param_1 & 0xfffffedf;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar2 & 1) == 1);
  }
  uVar2 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar2 = isIRQinterruptsEnabled();
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts(1);
  }
  *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & DAT_08008754;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar2 & 1) == 1);
  }
  if (param_1[0x1b] == 1) {
    uVar2 = 0;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      uVar2 = isIRQinterruptsEnabled();
    }
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts(1);
    }
    *(uint *)*param_1 = *(uint *)*param_1 & 0xffffffef;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((uVar2 & 1) == 1);
    }
  }
  param_1[0x23] = 0x20;
  param_1[0x1b] = 0;
  param_1[0x1d] = 0;
  return;
}



/* FUN 0x08008758 FUN_08008758 */

void FUN_08008758(int *param_1)

{
  bool bVar1;
  int iVar2;
  uint uVar3;
  
  iVar2 = *param_1;
  if (param_1[0x23] == 0x22) {
    *(ushort *)param_1[0x16] = (ushort)*(undefined4 *)(iVar2 + 0x24) & *(ushort *)(param_1 + 0x18);
    param_1[0x16] = param_1[0x16] + 2;
    *(short *)((int)param_1 + 0x5e) = *(short *)((int)param_1 + 0x5e) + -1;
    if (*(short *)((int)param_1 + 0x5e) == 0) {
      uVar3 = 0;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        uVar3 = isIRQinterruptsEnabled();
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts(1);
      }
      *(uint *)*param_1 = *(uint *)*param_1 & 0xfffffedf;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((uVar3 & 1) == 1);
      }
      uVar3 = 0;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        uVar3 = isIRQinterruptsEnabled();
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts(1);
      }
      *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & 0xfffffffe;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((uVar3 & 1) == 1);
      }
      param_1[0x23] = 0x20;
      param_1[0x1d] = 0;
      param_1[0x1c] = 0;
      if (param_1[0x1b] != 1) {
        FUN_08006544();
        return;
      }
      param_1[0x1b] = 0;
      uVar3 = 0;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        uVar3 = isIRQinterruptsEnabled();
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts(1);
      }
      *(uint *)*param_1 = *(uint *)*param_1 & 0xffffffef;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((uVar3 & 1) == 1);
      }
      if (-1 < (int)(~*(uint *)(*param_1 + 0x1c) << 0x1b)) {
        *(undefined4 *)(*param_1 + 0x20) = 0x10;
      }
      FUN_08005e6a(param_1,(short)param_1[0x17]);
      return;
    }
  }
  else {
    *(uint *)(iVar2 + 0x18) = *(uint *)(iVar2 + 0x18) | 8;
  }
  return;
}



/* FUN 0x08008808 FUN_08008808 */

int * FUN_08008808(uint *param_1)

{
  bool bVar1;
  uint uVar2;
  int *piVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  
  uVar5 = param_1[0x18];
  piVar3 = (int *)*param_1;
  uVar8 = piVar3[7];
  iVar6 = *piVar3;
  uVar7 = piVar3[2];
  if (param_1[0x23] == 0x22) {
    uVar2 = param_1[0x1a];
    while (((short)uVar2 != 0 && ((int)(uVar8 << 0x1a) < 0))) {
      *(ushort *)param_1[0x16] = (ushort)*(undefined4 *)(*param_1 + 0x24) & (ushort)uVar5;
      param_1[0x16] = param_1[0x16] + 2;
      *(short *)((int)param_1 + 0x5e) = *(short *)((int)param_1 + 0x5e) + -1;
      uVar8 = *(uint *)(*param_1 + 0x1c);
      if ((uVar8 & 7) != 0) {
        if (((uVar8 & 1) != 0) && (iVar6 << 0x17 < 0)) {
          *(undefined4 *)(*param_1 + 0x20) = 1;
          param_1[0x24] = param_1[0x24] | 1;
        }
        if (((int)(uVar8 << 0x1e) < 0) && ((uVar7 & 1) != 0)) {
          *(undefined4 *)(*param_1 + 0x20) = 2;
          param_1[0x24] = param_1[0x24] | 4;
        }
        if (((int)(uVar8 << 0x1d) < 0) && ((uVar7 & 1) != 0)) {
          *(undefined4 *)(*param_1 + 0x20) = 4;
          param_1[0x24] = param_1[0x24] | 2;
        }
        if (param_1[0x24] != 0) {
          FUN_08005f42(param_1);
          param_1[0x24] = 0;
        }
      }
      if (*(short *)((int)param_1 + 0x5e) == 0) {
        uVar4 = 0;
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          uVar4 = isIRQinterruptsEnabled();
        }
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts(1);
        }
        *(uint *)*param_1 = *(uint *)*param_1 & 0xfffffeff;
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts((uVar4 & 1) == 1);
        }
        uVar4 = 0;
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          uVar4 = isIRQinterruptsEnabled();
        }
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts(1);
        }
        *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & DAT_08008990;
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts((uVar4 & 1) == 1);
        }
        param_1[0x23] = 0x20;
        param_1[0x1d] = 0;
        param_1[0x1c] = 0;
        if (param_1[0x1b] == 1) {
          param_1[0x1b] = 0;
          uVar4 = 0;
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            uVar4 = isIRQinterruptsEnabled();
          }
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            enableIRQinterrupts(1);
          }
          *(uint *)*param_1 = *(uint *)*param_1 & 0xffffffef;
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            enableIRQinterrupts((uVar4 & 1) == 1);
          }
          if (-1 < (int)(~*(uint *)(*param_1 + 0x1c) << 0x1b)) {
            *(undefined4 *)(*param_1 + 0x20) = 0x10;
          }
          FUN_08005e6a(param_1,(short)param_1[0x17]);
        }
        else {
          FUN_08006544(param_1);
        }
      }
    }
    piVar3 = (int *)(uint)*(ushort *)((int)param_1 + 0x5e);
    if ((piVar3 != (int *)0x0) && (piVar3 < (int *)(uint)(ushort)param_1[0x1a])) {
      uVar5 = 0;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        uVar5 = isIRQinterruptsEnabled();
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts(1);
      }
      *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & 0xefffffff;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((uVar5 & 1) == 1);
      }
      param_1[0x1d] = DAT_08008994;
      piVar3 = (int *)0x0;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        piVar3 = (int *)isIRQinterruptsEnabled();
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts(1);
      }
      *(uint *)*param_1 = *(uint *)*param_1 | 0x20;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts(((uint)piVar3 & 1) == 1);
      }
    }
  }
  else {
    piVar3[6] = piVar3[6] | 8;
  }
  return piVar3;
}



/* FUN 0x08008998 FUN_08008998 */

void FUN_08008998(int *param_1)

{
  bool bVar1;
  int iVar2;
  uint uVar3;
  
  iVar2 = *param_1;
  if (param_1[0x23] == 0x22) {
    *(byte *)param_1[0x16] = (byte)*(undefined4 *)(iVar2 + 0x24) & (byte)(short)param_1[0x18];
    param_1[0x16] = param_1[0x16] + 1;
    *(short *)((int)param_1 + 0x5e) = *(short *)((int)param_1 + 0x5e) + -1;
    if (*(short *)((int)param_1 + 0x5e) == 0) {
      uVar3 = 0;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        uVar3 = isIRQinterruptsEnabled();
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts(1);
      }
      *(uint *)*param_1 = *(uint *)*param_1 & 0xfffffedf;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((uVar3 & 1) == 1);
      }
      uVar3 = 0;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        uVar3 = isIRQinterruptsEnabled();
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts(1);
      }
      *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & 0xfffffffe;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((uVar3 & 1) == 1);
      }
      param_1[0x23] = 0x20;
      param_1[0x1d] = 0;
      param_1[0x1c] = 0;
      if (param_1[0x1b] != 1) {
        FUN_08006544();
        return;
      }
      param_1[0x1b] = 0;
      uVar3 = 0;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        uVar3 = isIRQinterruptsEnabled();
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts(1);
      }
      *(uint *)*param_1 = *(uint *)*param_1 & 0xffffffef;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((uVar3 & 1) == 1);
      }
      if (-1 < (int)(~*(uint *)(*param_1 + 0x1c) << 0x1b)) {
        *(undefined4 *)(*param_1 + 0x20) = 0x10;
      }
      FUN_08005e6a(param_1,(short)param_1[0x17]);
      return;
    }
  }
  else {
    *(uint *)(iVar2 + 0x18) = *(uint *)(iVar2 + 0x18) | 8;
  }
  return;
}



/* FUN 0x08008a48 FUN_08008a48 */

uint FUN_08008a48(int *param_1)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  int *piVar7;
  uint uVar8;
  
  iVar2 = param_1[0x18];
  piVar7 = (int *)*param_1;
  uVar8 = piVar7[7];
  iVar4 = *piVar7;
  uVar5 = piVar7[2];
  if (param_1[0x23] == 0x22) {
    iVar3 = param_1[0x1a];
    while (((short)iVar3 != 0 && ((int)(uVar8 << 0x1a) < 0))) {
      *(byte *)param_1[0x16] = (byte)*(undefined4 *)(*param_1 + 0x24) & (byte)(short)iVar2;
      param_1[0x16] = param_1[0x16] + 1;
      *(short *)((int)param_1 + 0x5e) = *(short *)((int)param_1 + 0x5e) + -1;
      uVar8 = *(uint *)(*param_1 + 0x1c);
      if ((uVar8 & 7) != 0) {
        if (((uVar8 & 1) != 0) && (iVar4 << 0x17 < 0)) {
          *(undefined4 *)(*param_1 + 0x20) = 1;
          param_1[0x24] = param_1[0x24] | 1;
        }
        if (((int)(uVar8 << 0x1e) < 0) && ((uVar5 & 1) != 0)) {
          *(undefined4 *)(*param_1 + 0x20) = 2;
          param_1[0x24] = param_1[0x24] | 4;
        }
        if (((int)(uVar8 << 0x1d) < 0) && ((uVar5 & 1) != 0)) {
          *(undefined4 *)(*param_1 + 0x20) = 4;
          param_1[0x24] = param_1[0x24] | 2;
        }
        if (param_1[0x24] != 0) {
          FUN_08005f42(param_1);
          param_1[0x24] = 0;
        }
      }
      if (*(short *)((int)param_1 + 0x5e) == 0) {
        uVar6 = 0;
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          uVar6 = isIRQinterruptsEnabled();
        }
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts(1);
        }
        *(uint *)*param_1 = *(uint *)*param_1 & 0xfffffeff;
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts((uVar6 & 1) == 1);
        }
        uVar6 = 0;
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          uVar6 = isIRQinterruptsEnabled();
        }
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts(1);
        }
        *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & DAT_08008bd0;
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts((uVar6 & 1) == 1);
        }
        param_1[0x23] = 0x20;
        param_1[0x1d] = 0;
        param_1[0x1c] = 0;
        if (param_1[0x1b] == 1) {
          param_1[0x1b] = 0;
          uVar6 = 0;
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            uVar6 = isIRQinterruptsEnabled();
          }
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            enableIRQinterrupts(1);
          }
          *(uint *)*param_1 = *(uint *)*param_1 & 0xffffffef;
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            enableIRQinterrupts((uVar6 & 1) == 1);
          }
          if (-1 < (int)(~*(uint *)(*param_1 + 0x1c) << 0x1b)) {
            *(undefined4 *)(*param_1 + 0x20) = 0x10;
          }
          FUN_08005e6a(param_1,(short)param_1[0x17]);
        }
        else {
          FUN_08006544(param_1);
        }
      }
    }
    uVar5 = (uint)*(ushort *)((int)param_1 + 0x5e);
    if ((uVar5 != 0) && (uVar5 < *(ushort *)(param_1 + 0x1a))) {
      uVar5 = 0;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        uVar5 = isIRQinterruptsEnabled();
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts(1);
      }
      *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & 0xefffffff;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((uVar5 & 1) == 1);
      }
      param_1[0x1d] = DAT_08008bd4;
      uVar5 = 0;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        uVar5 = isIRQinterruptsEnabled();
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts(1);
      }
      *(uint *)*param_1 = *(uint *)*param_1 | 0x20;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((uVar5 & 1) == 1);
      }
    }
  }
  else {
    uVar5 = piVar7[6] | 8;
    piVar7[6] = uVar5;
  }
  return uVar5;
}



/* FUN 0x08008bd8 FUN_08008bd8 */

undefined4 FUN_08008bd8(int *param_1)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  
  uVar6 = 0;
  *(uint *)*param_1 =
       *(uint *)*param_1 & DAT_08008d68 | param_1[2] | param_1[4] | param_1[5] | param_1[7];
  *(uint *)(*param_1 + 4) = *(uint *)(*param_1 + 4) & 0xffffcfff | param_1[3];
  *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & DAT_08008d6c | param_1[8] | param_1[6];
  *(uint *)(*param_1 + 0x2c) = *(uint *)(*param_1 + 0x2c) & 0xfffffff0 | param_1[9];
  uVar1 = DAT_08008d94;
  iVar5 = DAT_08008d90;
  iVar2 = *param_1;
  if (iVar2 == DAT_08008d70) {
    uVar3 = *(uint *)(DAT_08008d74 + 0x14) & 3;
    if (uVar3 != 0) {
      if (uVar3 == 1) {
LAB_08008c84:
        uVar3 = 4;
      }
      else if (uVar3 != 2) {
        if (uVar3 != 3) goto LAB_08008ca2;
LAB_08008c88:
        uVar3 = 8;
      }
    }
  }
  else if (iVar2 == DAT_08008d78) {
    uVar3 = *(uint *)(DAT_08008d74 + 0x14) & 0xc;
    if ((uVar3 != 0) && (uVar3 != 4)) {
      if (uVar3 != 8) {
        if (uVar3 == 0xc) goto LAB_08008c88;
        goto LAB_08008ca2;
      }
LAB_08008c80:
      uVar3 = 2;
    }
  }
  else if (iVar2 == DAT_08008d7c) {
    uVar4 = *(uint *)(DAT_08008d74 + 0x14) & 0x30;
    uVar3 = 0;
    if (uVar4 != 0) {
      if (uVar4 == 0x10) goto LAB_08008c84;
      if (uVar4 == 0x20) goto LAB_08008c80;
      if (uVar4 == 0x30) goto LAB_08008c88;
LAB_08008ca2:
      uVar3 = 0x10;
    }
  }
  else {
    if (((iVar2 != DAT_08008d80) && (iVar2 != DAT_08008d84)) && (iVar2 != DAT_08008d88))
    goto LAB_08008ca2;
    uVar3 = 0;
  }
  if (param_1[7] == 0x8000) {
    if (uVar3 == 0) {
      iVar2 = FUN_08005474();
LAB_08008cd4:
      if (iVar2 == 0) goto LAB_08008d52;
    }
    else {
      iVar2 = DAT_08008d8c;
      if (uVar3 != 2) {
        if (uVar3 != 4) {
          iVar2 = 0x8000;
          if (uVar3 == 8) goto LAB_08008cd8;
          goto LAB_08008d48;
        }
        iVar2 = FUN_0800549c();
        goto LAB_08008cd4;
      }
    }
LAB_08008cd8:
    iVar5 = FUN_08000160(iVar2,*(undefined2 *)(iVar5 + param_1[9] * 2));
    uVar3 = FUN_08000160(iVar5 * 2 + ((uint)param_1[1] >> 1));
    if (uVar1 < uVar3 - 0x10) {
LAB_08008d48:
      uVar6 = 1;
      goto LAB_08008d52;
    }
    uVar3 = (uVar3 & 0xf) >> 1 | DAT_08008d94 + 1 & uVar3;
  }
  else {
    if (uVar3 == 0) {
      iVar2 = FUN_08005474();
LAB_08008d26:
      if (iVar2 == 0) goto LAB_08008d52;
    }
    else {
      iVar2 = DAT_08008d8c;
      if (uVar3 != 2) {
        if (uVar3 == 4) {
          iVar2 = FUN_0800549c();
          goto LAB_08008d26;
        }
        iVar2 = 0x8000;
        if (uVar3 != 8) goto LAB_08008d48;
      }
    }
    iVar5 = FUN_08000160(iVar2,*(undefined2 *)(iVar5 + param_1[9] * 2));
    uVar3 = FUN_08000160(iVar5 + ((uint)param_1[1] >> 1));
    if (uVar1 < uVar3 - 0x10) goto LAB_08008d48;
    uVar3 = uVar3 & 0xffff;
  }
  *(uint *)(*param_1 + 0xc) = uVar3;
LAB_08008d52:
  *(undefined2 *)((int)param_1 + 0x6a) = 1;
  *(undefined2 *)(param_1 + 0x1a) = 1;
  param_1[0x1d] = 0;
  param_1[0x1e] = 0;
  return uVar6;
}



/* FUN 0x08008d98 FUN_08008d98 */

longlong FUN_08008d98(int *param_1,int param_2,uint param_3)

{
  bool bVar1;
  uint *puVar2;
  uint uVar3;
  undefined2 uVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  
  param_1[0x16] = param_2;
  *(short *)(param_1 + 0x17) = (short)param_3;
  *(short *)((int)param_1 + 0x5e) = (short)param_3;
  param_1[0x1d] = 0;
  iVar5 = param_1[2];
  if (iVar5 == 0x1000) {
    if (param_1[4] == 0) {
      uVar4 = (undefined2)DAT_08008eb0;
LAB_08008dd4:
      *(undefined2 *)(param_1 + 0x18) = uVar4;
    }
    else {
LAB_08008de2:
      *(undefined2 *)(param_1 + 0x18) = 0xff;
    }
  }
  else {
    if (iVar5 == 0) {
      if (param_1[4] == 0) goto LAB_08008de2;
    }
    else {
      if (iVar5 != 0x10000000) {
        *(undefined2 *)(param_1 + 0x18) = 0;
        goto LAB_08008de8;
      }
      if (param_1[4] != 0) {
        uVar4 = 0x3f;
        goto LAB_08008dd4;
      }
    }
    *(undefined2 *)(param_1 + 0x18) = 0x7f;
  }
LAB_08008de8:
  param_1[0x24] = 0;
  param_1[0x23] = 0x22;
  uVar6 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar6 = isIRQinterruptsEnabled();
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts(1);
  }
  *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) | 1;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar6 & 1) == 1);
  }
  if ((param_1[0x19] == 0x20000000) && (*(ushort *)(param_1 + 0x1a) <= param_3)) {
    if ((param_1[2] == 0x1000) && (param_1[4] == 0)) {
      param_1[0x1d] = DAT_08008eb8;
    }
    else {
      param_1[0x1d] = DAT_08008eb4;
      if (param_1[4] != 0) {
        uVar6 = 0;
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          uVar6 = isIRQinterruptsEnabled();
        }
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts(1);
        }
        *(uint *)*param_1 = *(uint *)*param_1 | 0x100;
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts((uVar6 & 1) == 1);
        }
      }
    }
    uVar6 = 0;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      uVar6 = isIRQinterruptsEnabled();
    }
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts(1);
    }
    *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) | 0x10000000;
    goto LAB_08008ea8;
  }
  if ((param_1[2] == 0x1000) && (param_1[4] == 0)) {
    param_1[0x1d] = DAT_08008ec0;
LAB_08008e94:
    uVar6 = 0;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      uVar6 = isIRQinterruptsEnabled();
    }
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts(1);
    }
    puVar2 = (uint *)*param_1;
    uVar3 = *puVar2;
    uVar7 = 0x20;
  }
  else {
    param_1[0x1d] = DAT_08008ebc;
    if (param_1[4] == 0) goto LAB_08008e94;
    uVar6 = 0;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      uVar6 = isIRQinterruptsEnabled();
    }
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts(1);
    }
    puVar2 = (uint *)*param_1;
    uVar3 = *puVar2;
    uVar7 = 0x120;
  }
  *puVar2 = uVar3 | uVar7;
LAB_08008ea8:
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar6 & 1) == 1);
  }
  return (ulonglong)uVar6 << 0x20;
}



/* FUN 0x08008ec4 FUN_08008ec4 */

undefined4 FUN_08008ec4(int *param_1,uint param_2,uint param_3,int param_4,uint param_5)

{
  bool bVar1;
  int iVar2;
  uint uVar3;
  
  while( true ) {
    do {
      if (((param_2 & ~*(uint *)(*param_1 + 0x1c)) == 0) != param_3) {
        return 0;
      }
    } while (param_5 == 0xffffffff);
    iVar2 = FUN_08004eac();
    if ((param_5 < (uint)(iVar2 - param_4)) || (param_5 == 0)) break;
    if ((*(int *)*param_1 << 0x1d < 0) && (-1 < ~((int *)*param_1)[7] << 0x14)) {
      *(undefined4 *)(*param_1 + 0x20) = 0x800;
      uVar3 = 0;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        uVar3 = isIRQinterruptsEnabled();
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts(1);
      }
      *(uint *)*param_1 = *(uint *)*param_1 & 0xfffffe5f;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((uVar3 & 1) == 1);
      }
      uVar3 = 0;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        uVar3 = isIRQinterruptsEnabled();
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts(1);
      }
      *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & 0xfffffffe;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((uVar3 & 1) == 1);
      }
      param_1[0x22] = 0x20;
      param_1[0x23] = 0x20;
      param_1[0x24] = 0x20;
LAB_08008f3a:
      *(undefined1 *)(param_1 + 0x21) = 0;
      return 3;
    }
  }
  uVar3 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar3 = isIRQinterruptsEnabled();
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts(1);
  }
  *(uint *)*param_1 = *(uint *)*param_1 & 0xfffffe5f;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar3 & 1) == 1);
  }
  uVar3 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar3 = isIRQinterruptsEnabled();
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts(1);
  }
  *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & 0xfffffffe;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar3 & 1) == 1);
  }
  param_1[0x22] = 0x20;
  param_1[0x23] = 0x20;
  goto LAB_08008f3a;
}



/* FUN 0x08008f98 FUN_08008f98 */

void FUN_08008f98(void)

{
  FUN_08005f50(DAT_08008fa4);
  return;
}



/* FUN 0x08008fa8 FUN_08008fa8 */

undefined8 FUN_08008fa8(undefined4 param_1,int param_2,int param_3)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  piVar1 = DAT_08008ffc;
  iVar4 = 1;
  iVar2 = param_2;
  iVar5 = param_3;
  do {
    disableIRQinterrupts();
    FUN_0800a2e6();
    iVar3 = FUN_08000420(0x5a,param_1,param_2,param_3,param_1,iVar2,iVar5);
    enableIRQinterrupts();
    if (iVar3 != 0) goto LAB_08008fc4;
    *piVar1 = *piVar1 + 1;
    if (piVar1[4] == 1) {
      FUN_08009170(DAT_08009000,piVar1[1],piVar1[2],piVar1[3]);
    }
    iVar4 = iVar4 + 1;
  } while (iVar4 != 10);
  for (iVar2 = 0; iVar2 < param_2; iVar2 = iVar2 + 1) {
    *(undefined1 *)(param_3 + iVar2) = 0xff;
  }
  iVar3 = 0;
LAB_08008fc4:
  return CONCAT44(param_1,iVar3);
}



/* FUN 0x08009004 FUN_08009004 */

undefined8 FUN_08009004(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  
  piVar1 = DAT_0800903c;
  iVar3 = 1;
  uVar4 = param_2;
  uVar5 = param_3;
  do {
    disableIRQinterrupts();
    FUN_0800a2e6();
    iVar2 = FUN_0800056c(0x5a,param_1,param_2,param_3,param_1,uVar4,uVar5);
    enableIRQinterrupts();
    if (iVar2 != 0) goto LAB_08009012;
    iVar3 = iVar3 + 1;
    *piVar1 = *piVar1 + 1;
  } while (iVar3 != 10);
  iVar2 = 0;
LAB_08009012:
  return CONCAT44(param_1,iVar2);
}



/* FUN 0x08009040 FUN_08009040 */

int FUN_08009040(undefined4 param_1,int param_2,int param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = DAT_080090a0;
  iVar3 = 1;
  do {
    disableIRQinterrupts();
    iVar2 = FUN_080004c0(0x42,param_1,param_2,param_3);
    enableIRQinterrupts();
    if (iVar2 != 0) {
      return iVar2;
    }
    iVar3 = iVar3 + 1;
    *(int *)(iVar1 + 4) = *(int *)(iVar1 + 4) + 1;
  } while (iVar3 != 10);
  for (iVar3 = 0; iVar3 < param_2; iVar3 = iVar3 + 1) {
    *(undefined1 *)(param_3 + iVar3) = 0xff;
  }
  if (*DAT_080090a4 == '\0') {
    FUN_08009170(DAT_080090a8,10,*(undefined4 *)(iVar1 + 8),*(undefined4 *)(iVar1 + 0xc),
                 *(undefined4 *)(iVar1 + 0x10));
  }
  return 0;
}



/* FUN 0x080090ac FUN_080090ac */

int FUN_080090ac(undefined4 param_1,int param_2,int param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = DAT_08009100;
  iVar3 = 1;
  do {
    disableIRQinterrupts();
    iVar2 = FUN_08000310(2,param_1,param_2,param_3);
    enableIRQinterrupts();
    if (iVar2 != 0) {
      return iVar2;
    }
    *(int *)(iVar1 + 4) = *(int *)(iVar1 + 4) + 1;
    FUN_08009170(DAT_08009104,iVar3,*(undefined4 *)(iVar1 + 8),*(undefined4 *)(iVar1 + 0xc),
                 *(undefined4 *)(iVar1 + 0x10));
    iVar3 = iVar3 + 1;
  } while (iVar3 != 10);
  for (iVar1 = 0; iVar1 < param_2; iVar1 = iVar1 + 1) {
    *(undefined1 *)(param_3 + iVar1) = 0xff;
  }
  return 0;
}



/* FUN 0x08009108 FUN_08009108 */

int FUN_08009108(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = DAT_08009160;
  iVar3 = 1;
  do {
    disableIRQinterrupts();
    iVar2 = FUN_08000610(0x42,param_1,param_2,param_3);
    enableIRQinterrupts();
    if (iVar2 != 0) {
      return iVar2;
    }
    iVar3 = iVar3 + 1;
    *(int *)(iVar1 + 4) = *(int *)(iVar1 + 4) + 1;
  } while (iVar3 != 10);
  if (*DAT_08009164 == '\0') {
    FUN_08009170(DAT_08009168,10,*(undefined4 *)(iVar1 + 8),*(undefined4 *)(iVar1 + 0xc),
                 *(undefined4 *)(iVar1 + 0x10));
    FUN_08009170(&DAT_0800916c);
  }
  return 0;
}



/* FUN 0x08009170 FUN_08009170 */

void FUN_08009170(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uStack_c;
  undefined4 uStack_8;
  undefined4 uStack_4;
  
  uStack_c = param_2;
  uStack_8 = param_3;
  uStack_4 = param_4;
  FUN_08009210(param_1,&uStack_c,DAT_0800918c,DAT_08009188);
  return;
}



/* FUN 0x08009190 __ARM_common_switch8 */

/* WARNING: This is an inlined function */

void __ARM_common_switch8(void)

{
  uint in_r3;
  uint uVar1;
  int unaff_lr;
  
  uVar1 = (uint)*(byte *)(unaff_lr + -1);
  if (in_r3 < *(byte *)(unaff_lr + -1)) {
    uVar1 = in_r3;
  }
                    /* WARNING: Could not recover jumptable at 0x080091a8. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)(unaff_lr + (uint)*(byte *)(unaff_lr + uVar1) * 2))();
  return;
}



/* FUN 0x080091ac FUN_080091ac */

void FUN_080091ac(uint param_1,uint param_2)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  uint *puVar4;
  
  iVar3 = (param_1 & 3) << 3;
  uVar2 = 0xff << iVar3;
  uVar1 = ((param_2 & 3) << 6) << iVar3;
  if (-1 < (int)param_1) {
    puVar4 = (uint *)((param_1 & 0xfffffffc) + DAT_080091e8);
    *puVar4 = *puVar4 & ~uVar2 | uVar1;
    return;
  }
  iVar3 = ((param_1 & 0xf) - 8 & 0xfffffffc) + DAT_080091ec;
  *(uint *)(iVar3 + 0x1c) = *(uint *)(iVar3 + 0x1c) & ~uVar2 | uVar1;
  return;
}



/* FUN 0x08009210 FUN_08009210 */

int FUN_08009210(byte *param_1,uint *param_2,undefined4 param_3,code *param_4)

{
  byte bVar1;
  char cVar2;
  uint uVar3;
  int *piVar4;
  uint uVar5;
  int iVar6;
  char *pcVar7;
  int extraout_r2;
  uint uVar8;
  byte *pbVar9;
  int iVar10;
  uint uVar11;
  bool bVar12;
  longlong lVar13;
  uint local_68;
  int local_64;
  uint local_60;
  int *local_5c;
  int local_58;
  undefined4 local_54;
  byte local_50 [36];
  undefined4 *****local_2c [2];
  byte *pbStack_24;
  uint *puStack_20;
  undefined4 local_1c;
  code *local_18;
  
  local_18 = param_4;
  local_1c = param_3;
  puStack_20 = param_2;
  pbStack_24 = param_1;
  iVar10 = 0;
  do {
    while( true ) {
      bVar1 = *param_1;
      if (bVar1 == 0) {
        return iVar10;
      }
      if (bVar1 == 0x25) break;
      (*local_18)(bVar1,local_1c);
      param_1 = param_1 + 1;
      iVar10 = iVar10 + 1;
    }
    uVar8 = 0;
    local_68 = 0;
    local_60 = 0;
    while( true ) {
      pbVar9 = param_1 + 1;
      uVar3 = 1 << (*pbVar9 - 0x20 & 0xff);
      if ((uVar3 & DAT_0800960c) == 0) break;
      uVar8 = uVar8 | uVar3;
      param_1 = pbVar9;
    }
    if (*pbVar9 == 0x2a) {
      local_68 = *param_2;
      param_2 = param_2 + 1;
      if ((int)local_68 < 0) {
        uVar8 = uVar8 | 0x2000;
        local_68 = -local_68;
      }
      uVar8 = uVar8 | 2;
      pbVar9 = param_1 + 2;
    }
    else {
      for (; *pbVar9 - 0x30 < 10; pbVar9 = pbVar9 + 1) {
        local_68 = (uint)*pbVar9 + local_68 * 10 + -0x30;
        uVar8 = uVar8 | 2;
      }
    }
    if (*pbVar9 == 0x2e) {
      uVar8 = uVar8 | 4;
      if (pbVar9[1] == 0x2a) {
        local_60 = *param_2;
        param_2 = param_2 + 1;
        pbVar9 = pbVar9 + 2;
      }
      else {
        while( true ) {
          pbVar9 = pbVar9 + 1;
          if (9 < *pbVar9 - 0x30) break;
          local_60 = (uint)*pbVar9 + local_60 * 10 + -0x30;
        }
      }
    }
    bVar1 = *pbVar9;
    if (bVar1 == 0x6c) {
      uVar3 = 0x100000;
LAB_080092f4:
      uVar8 = uVar8 | uVar3;
      if (pbVar9[1] == bVar1) {
        uVar8 = uVar8 + 0x100000;
        pbVar9 = pbVar9 + 1;
      }
LAB_08009304:
      pbVar9 = pbVar9 + 1;
    }
    else {
      if (bVar1 < 0x6d) {
        if (bVar1 != 0x4c) {
          if (bVar1 == 0x68) {
            uVar3 = 0x300000;
            goto LAB_080092f4;
          }
          if (bVar1 != 0x6a) goto LAB_08009306;
          uVar8 = uVar8 | 0x200000;
        }
        goto LAB_08009304;
      }
      if ((bVar1 == 0x74) || (bVar1 == 0x7a)) goto LAB_08009304;
    }
LAB_08009306:
    bVar1 = *pbVar9;
    if (bVar1 == 0x6e) {
      uVar8 = (uVar8 & 0x7fffff) >> 0x14;
      if (uVar8 == 2) {
        piVar4 = (int *)*param_2;
        *piVar4 = iVar10;
        piVar4[1] = iVar10 >> 0x1f;
      }
      else if (uVar8 == 3) {
        *(short *)*param_2 = (short)iVar10;
      }
      else if (uVar8 == 4) {
        *(char *)*param_2 = (char)iVar10;
      }
      else {
        *(int *)*param_2 = iVar10;
      }
      param_2 = param_2 + 1;
    }
    else {
      if (bVar1 < 0x6f) {
        if (bVar1 != 99) {
          if (bVar1 < 100) {
            if (bVar1 == 0) {
              return iVar10;
            }
            if (bVar1 == 0x58) {
LAB_08009486:
              local_58 = 0x10;
              goto LAB_0800949e;
            }
          }
          else if ((bVar1 == 100) || (bVar1 == 0x69)) {
            local_58 = 10;
            local_54 = 0;
            uVar3 = (uVar8 & 0x7fffff) >> 0x14;
            if (uVar3 == 2) {
              param_2 = (uint *)((uint)((int)param_2 + 7) & 0xfffffff8);
              uVar5 = *param_2;
              uVar11 = param_2[1];
              param_2 = param_2 + 2;
            }
            else {
              uVar5 = *param_2;
              param_2 = param_2 + 1;
              if (uVar3 == 3) {
                uVar5 = (uint)(short)uVar5;
              }
              uVar11 = (int)uVar5 >> 0x1f;
              if (uVar3 == 4) {
                uVar5 = (uint)(char)uVar5;
                uVar11 = (int)uVar5 >> 0x1f;
              }
            }
            if ((int)uVar11 < 0) {
              bVar12 = uVar5 != 0;
              uVar5 = -uVar5;
              uVar11 = -(uint)bVar12 - uVar11;
              local_50[0] = 0x2d;
LAB_0800946e:
              local_64 = 1;
            }
            else {
              if ((int)(uVar8 << 0x14) < 0) {
                local_50[0] = 0x2b;
                goto LAB_0800946e;
              }
              local_64 = 0;
              if ((uVar8 & 1) != 0) {
                local_50[0] = 0x20;
                goto LAB_0800946e;
              }
            }
            goto LAB_0800952c;
          }
LAB_08009342:
          (*local_18)(bVar1,local_1c);
          iVar10 = iVar10 + 1;
          goto LAB_08009412;
        }
        local_58._0_2_ = (ushort)(byte)*param_2;
        local_5c = &local_58;
        iVar6 = 1;
LAB_08009392:
        param_2 = param_2 + 1;
        if ((int)(uVar8 << 0x1d) < 0) {
          for (local_64 = 0;
              (local_64 < (int)local_60 &&
              ((local_64 < iVar6 || (*(char *)((int)local_5c + local_64) != '\0'))));
              local_64 = local_64 + 1) {
          }
        }
        else {
          for (local_64 = 0; (local_64 < iVar6 || (*(char *)((int)local_5c + local_64) != '\0'));
              local_64 = local_64 + 1) {
          }
        }
        local_68 = local_68 - local_64;
        iVar6 = FUN_08009658(local_68,uVar8,local_1c,local_18);
        iVar10 = iVar6 + iVar10 + local_64;
        while (local_64 = local_64 + -1, local_64 != -1) {
          iVar6 = *local_5c;
          local_5c = (int *)((int)local_5c + 1);
          (*local_18)((char)iVar6,local_1c);
        }
      }
      else {
        if (bVar1 == 0x73) {
          local_5c = (int *)*param_2;
          iVar6 = -1;
          goto LAB_08009392;
        }
        if (bVar1 < 0x74) {
          if (bVar1 == 0x6f) {
            local_58 = 8;
            goto LAB_0800949e;
          }
          if (bVar1 != 0x70) goto LAB_08009342;
          local_58 = 0x10;
          uVar8 = uVar8 | 4;
          local_54 = 0;
          local_60 = 8;
        }
        else {
          if (bVar1 != 0x75) {
            if (bVar1 == 0x78) goto LAB_08009486;
            goto LAB_08009342;
          }
          local_58 = 10;
LAB_0800949e:
          local_54 = 0;
        }
        uVar3 = (uVar8 & 0x7fffff) >> 0x14;
        if (uVar3 == 2) {
          param_2 = (uint *)((uint)((int)param_2 + 7) & 0xfffffff8);
          uVar5 = *param_2;
          uVar11 = param_2[1];
          param_2 = param_2 + 2;
        }
        else {
          uVar5 = *param_2;
          param_2 = param_2 + 1;
          uVar11 = 0;
          if (uVar3 == 3) {
            uVar5 = uVar5 & 0xffff;
          }
          if (uVar3 == 4) {
            uVar5 = uVar5 & 0xff;
          }
        }
        local_64 = 0;
        if ((int)(uVar8 << 0x1c) < 0) {
          if (bVar1 == 0x70) {
            local_50[0] = 0x40;
            local_64 = 1;
          }
          else if ((local_58 == 0x10) && (uVar11 != 0 || uVar5 != 0)) {
            local_50[0] = 0x30;
            local_50[1] = bVar1;
            local_64 = 2;
          }
          if ((local_58 == 8) && ((uVar11 != 0 || uVar5 != 0 || ((int)(uVar8 << 0x1d) < 0)))) {
            local_50[0] = 0x30;
            local_64 = 1;
            local_60 = local_60 - 1;
          }
        }
LAB_0800952c:
        lVar13 = CONCAT44(uVar11,uVar5);
        local_54 = 0;
        if (bVar1 == 0x58) {
          pcVar7 = s_0123456789ABCDEF_08009624;
        }
        else {
          pcVar7 = s_0123456789abcdef_08009610;
        }
        local_2c[0] = local_2c;
        while( true ) {
          if (lVar13 == 0) break;
          lVar13 = FUN_08000210((int)lVar13,(int)((ulonglong)lVar13 >> 0x20),local_58,local_54);
          local_2c[0] = (undefined4 *****)((int)local_2c[0] + -1);
          *(char *)local_2c[0] = pcVar7[extraout_r2];
        }
        local_5c = (int *)((int)local_2c - (int)local_2c[0]);
        if ((int)(uVar8 << 0x1d) < 0) {
          uVar8 = uVar8 & 0xfffeffff;
        }
        else {
          local_60 = 1;
        }
        if ((int)local_5c < (int)local_60) {
          local_60 = local_60 - (int)local_5c;
        }
        else {
          local_60 = 0;
        }
        local_68 = local_68 - (local_60 + (int)local_5c + local_64);
        if (-1 < (int)(uVar8 << 0xf)) {
          iVar6 = FUN_08009658(local_68,uVar8,local_1c,local_18);
          iVar10 = iVar6 + iVar10;
        }
        for (local_58 = 0; local_58 < local_64; local_58 = local_58 + 1) {
          (*local_18)(local_50[local_58],local_1c);
          iVar10 = iVar10 + 1;
        }
        if ((int)(uVar8 << 0xf) < 0) {
          iVar6 = FUN_08009658(local_68,uVar8,local_1c,local_18);
          iVar10 = iVar6 + iVar10;
        }
        while (0 < (int)local_60) {
          (*local_18)(0x30,local_1c);
          iVar10 = iVar10 + 1;
          local_60 = local_60 + -1;
        }
        while (0 < (int)local_5c) {
          cVar2 = *(char *)local_2c[0];
          local_2c[0] = (undefined4 *****)((int)local_2c[0] + 1);
          (*local_18)(cVar2,local_1c);
          iVar10 = iVar10 + 1;
          local_5c = (int *)((int)local_5c + -1);
        }
      }
      iVar6 = FUN_08009638(local_68,uVar8,local_1c,local_18);
      iVar10 = iVar6 + iVar10;
    }
LAB_08009412:
    param_1 = pbVar9 + 1;
  } while( true );
}



/* FUN 0x08009638 FUN_08009638 */

int FUN_08009638(int param_1,int param_2,undefined4 param_3,code *param_4)

{
  int iVar1;
  
  iVar1 = 0;
  if (param_2 << 0x12 < 0) {
    while (param_1 = param_1 + -1, -1 < param_1) {
      (*param_4)(0x20,param_3);
      iVar1 = iVar1 + 1;
    }
  }
  return iVar1;
}



/* FUN 0x08009658 FUN_08009658 */

int FUN_08009658(int param_1,int param_2,undefined4 param_3,code *param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = 0;
  if (param_2 << 0xf < 0) {
    uVar2 = 0x30;
  }
  else {
    uVar2 = 0x20;
  }
  if (-1 < param_2 << 0x12) {
    while (param_1 = param_1 + -1, -1 < param_1) {
      (*param_4)(uVar2,param_3);
      iVar1 = iVar1 + 1;
    }
  }
  return iVar1;
}



/* FUN 0x08009684 FUN_08009684 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08009684(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  char *pcVar4;
  undefined4 uVar5;
  
  iVar3 = _DAT_08009838;
  iVar2 = DAT_08009834;
  if (*(char *)(DAT_08009834 + 6) != '\x01') {
    return;
  }
  *(int *)(DAT_08009834 + 0xc) = *(int *)(DAT_08009834 + 0xc) + 5;
  cVar1 = *(char *)(iVar2 + 7);
  if (cVar1 == '\x01') {
    FUN_08009bc0();
    if ((((DAT_080098b4 < *(ushort *)(iVar3 + 0x36)) && (0x28 < *(byte *)(iVar3 + 0x32))) &&
        (DAT_080098b4 < *(ushort *)(iVar3 + 0x52))) &&
       ((0x28 < *(byte *)(iVar3 + 0x4e) && (*(char *)(iVar2 + -0x32) == '\0')))) {
      *(undefined1 *)(iVar2 + -0x3a) = 0;
    }
    else {
      if (*(byte *)(iVar2 + -0x3a) < 2) {
        *(byte *)(iVar2 + -0x3a) = *(byte *)(iVar2 + -0x3a) + 1;
        if (*(char *)(iVar2 + -0x35) != '\0') goto LAB_080097c8;
        FUN_08009170(s__AGING_RUNNING___GLS_bat_low__de_080098b8);
      }
      else {
        *(undefined1 *)(iVar2 + -0x3a) = 0;
        *(undefined1 *)(iVar2 + 7) = 2;
        *(undefined1 *)(iVar3 + 0x15) = 1;
        FUN_0800d154();
        *(undefined1 *)(iVar3 + 0x10) = 0;
        *(undefined1 *)(iVar3 + 0x11) = 0;
        if (*(char *)(iVar2 + -0x35) != '\0') goto LAB_080097c8;
        FUN_08009170(s__AGING_RUNNING___GLS_bat_low__go_080098f8);
      }
      FUN_08009170(&DAT_0800992c);
    }
    if (*(char *)(iVar2 + -0x35) != '\0') goto LAB_080097c8;
    pcVar4 = s__AGING_RUNNING___AGING_ONLY__tim_08009930;
    uVar5 = *(undefined4 *)(iVar2 + 0xc);
LAB_080097be:
    FUN_08009170(pcVar4,uVar5);
  }
  else {
    if (cVar1 == '\x02') {
      FUN_08009bc0();
      if (((*(char *)(iVar3 + 0x31) != '\0') && (*(char *)(iVar3 + 0x4d) != '\0')) ||
         (*(char *)(iVar2 + -0x33) != '\0')) {
        *(undefined1 *)(iVar2 + 7) = 1;
        *(undefined1 *)(iVar2 + -0x3a) = 0;
        *(undefined1 *)(iVar3 + 0x15) = 0;
        FUN_0800d154();
        *(undefined1 *)(iVar3 + 0x10) = 0;
        *(undefined1 *)(iVar3 + 0x11) = 0;
        if (*(char *)(iVar2 + -0x35) != '\0') goto LAB_080097c8;
        FUN_08009170(s__AGING_RUNNING___GLS_charge_done_08009958);
        FUN_08009170(&DAT_0800992c);
      }
      if (*(char *)(iVar2 + -0x35) != '\0') goto LAB_080097c8;
      pcVar4 = s__AGING_RUNNING___CHARGING_AGING__0800998c;
      uVar5 = *(undefined4 *)(iVar2 + 0xc);
      goto LAB_080097be;
    }
    if (cVar1 != '\x04') goto LAB_080097c8;
    FUN_08009cc8();
    if ((*(char *)(iVar3 + 0x10) == '\0') || (*(char *)(iVar3 + 0x11) == '\0')) {
      if (*(char *)(iVar2 + -0x35) != '\0') goto LAB_080097c8;
      FUN_08009170(s__AGING_RUNNING___GLS_not_inbox___0800987c,*(char *)(iVar3 + 0x10),
                   *(undefined1 *)(iVar3 + 0x11));
    }
    else {
      if (*(char *)(iVar2 + 4) != '\0') goto LAB_080097c8;
      *(undefined1 *)(iVar3 + 0x15) = 0;
      FUN_0800d154();
      *(undefined1 *)(iVar3 + 0x10) = 0;
      *(undefined1 *)(iVar3 + 0x11) = 0;
      *(undefined1 *)(iVar2 + 4) = 1;
      *(undefined1 *)(iVar2 + 5) = 0;
      if (*(char *)(iVar2 + -0x35) != '\0') goto LAB_080097c8;
      FUN_08009170(s__AGING_RUNNING___GLS_ready__disa_0800983b + 1);
    }
  }
  FUN_08009170(&DAT_0800992c);
LAB_080097c8:
  if ((*(uint *)(iVar2 + 0xc) + *(uint *)(iVar2 + 8) < 0x3840) && (*(char *)(iVar2 + -0x31) == '\0')
     ) {
    if ((0x1c1f < *(uint *)(iVar2 + 8)) && (0x3b < *(uint *)(iVar2 + 0xc))) {
      *(undefined1 *)(iVar2 + 6) = 2;
      *(undefined1 *)(iVar3 + 2) = 4;
      FUN_0800a888(*(undefined4 *)(iVar2 + -4),4);
      if (*(char *)(iVar2 + -0x35) == '\0') {
        FUN_08009170(DAT_080099e4);
        FUN_08009170(&DAT_0800992c);
        return;
      }
    }
  }
  else {
    if (*(char *)(iVar2 + -0x35) == '\0') {
      FUN_08009170(s__AGING_RUNNING___Timeout__go_to_A_080099b8);
      FUN_08009170(&DAT_0800992c);
    }
    *(undefined1 *)(iVar2 + 6) = 3;
    *(undefined1 *)(iVar3 + 2) = 4;
    FUN_08006b80(0);
    FUN_08006b98(1);
  }
  return;
}



/* FUN 0x080099e8 FUN_080099e8 */

void FUN_080099e8(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 local_14;
  
  iVar1 = DAT_08009a10;
  local_14._0_1_ = (char)param_2;
  if ((*(char *)(DAT_08009a10 + param_1) != (char)local_14) &&
     (local_14 = param_2, iVar2 = FUN_08009108(param_1,1,&local_14,param_4,param_1), iVar2 != 0)) {
    *(char *)(iVar1 + param_1) = (char)local_14;
  }
  return;
}



/* FUN 0x08009a14 FUN_08009a14 */

void FUN_08009a14(void)

{
  int iVar1;
  char *pcVar2;
  undefined4 uVar3;
  
  FUN_080099e8(5,3);
  FUN_080099e8(6,0x81);
  FUN_080099e8(7,0x20);
  pcVar2 = DAT_08009a98;
  iVar1 = DAT_08009a94;
  if ((((*(char *)(DAT_08009a94 + 0x10) == '\0') || (*(char *)(DAT_08009a94 + 0x15) == '\0')) ||
      (*(char *)(DAT_08009a94 + 0x31) != '\0')) ||
     ((*DAT_08009a98 != '\0' && (*(char *)(DAT_08009a94 + 0x11) == '\0')))) {
    uVar3 = 0xae;
  }
  else {
    uVar3 = 0xaf;
  }
  FUN_080099e8(3,uVar3);
  if (((*(char *)(iVar1 + 0x11) == '\0') || (*(char *)(iVar1 + 0x15) == '\0')) ||
     ((*(char *)(DAT_08009a94 + 0x4d) != '\0' ||
      ((*pcVar2 != '\0' && (*(char *)(iVar1 + 0x10) == '\0')))))) {
    uVar3 = 0xae;
  }
  else {
    uVar3 = 0xaf;
  }
  FUN_080099e8(4,uVar3);
  return;
}



/* FUN 0x08009a9c FUN_08009a9c */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08009a9c(int param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined1 auStack_28 [4];
  undefined4 local_24;
  
  iVar1 = _DAT_08009b34;
  if (param_1 != 0 || param_2 != 0) {
    if (*(char *)(_DAT_08009b34 + 4) == '\0') {
      *(undefined1 *)(_DAT_08009b34 + 4) = 1;
      FUN_0800d250();
      iVar3 = FUN_08005f44(DAT_08009b64);
      if (iVar3 << 0x1a < 0) {
        FUN_08005f00(DAT_08009b64);
      }
      FUN_080001b4(auStack_28,DAT_08009b68,0x14);
      uVar2 = DAT_08009b6c;
      FUN_08004d30(DAT_08009b6c,auStack_28);
      if (param_1 != 0) {
        FUN_0800be90();
        FUN_0800b678();
        FUN_0800beba();
        FUN_0800a7b0(10);
      }
      if (param_2 != 0) {
        FUN_0800bede();
        FUN_0800b678();
        FUN_0800bf08();
        FUN_0800a7b0(10);
      }
      local_24 = 0;
      FUN_08004d30(uVar2,auStack_28);
      FUN_08009a14();
      *(undefined1 *)(iVar1 + 4) = 0;
    }
    else if (*(char *)(_DAT_08009b34 + 7) == '\0') {
      FUN_08009170(s_Cannot_reset_gls_since_2510_is_b_08009b37 + 1);
      FUN_08009170(&DAT_08009b60);
    }
  }
  return;
}



/* FUN 0x08009b70 FUN_08009b70 */

void FUN_08009b70(int param_1,int param_2)

{
  uint uVar1;
  int iVar2;
  
  iVar2 = param_1 + param_2;
  *(char *)(iVar2 + -1) = (char)param_2 + '}';
  for (uVar1 = 0; (int)uVar1 < param_2 + -1; uVar1 = uVar1 + 1 & 0xff) {
    *(char *)(iVar2 + -1) = *(char *)(iVar2 + -1) + *(char *)(param_1 + uVar1);
  }
  return;
}



/* FUN 0x08009b94 FUN_08009b94 */

uint FUN_08009b94(int param_1)

{
  byte bVar1;
  
  if (param_1 - 0x30U < 10) {
    return param_1 - 0x30U & 0xff;
  }
  if (param_1 - 0x61U < 6) {
    bVar1 = (char)param_1 + 0xa9;
  }
  else {
    if (5 < param_1 - 0x41U) {
      return 0;
    }
    bVar1 = (char)param_1 - 0x37;
  }
  return (uint)bVar1;
}



/* FUN 0x08009bc0 FUN_08009bc0 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08009bc0(void)

{
  int iVar1;
  int iVar2;
  byte *pbVar3;
  
  iVar2 = FUN_08001408();
  iVar1 = _DAT_08009c44;
  pbVar3 = (byte *)(_DAT_08009c44 + -0x3c);
  if (iVar2 == 0) {
    *pbVar3 = *pbVar3 + 1;
    if (*(char *)(iVar1 + -0x35) == '\0') {
      FUN_08009170(s_Cannot_get_aging_status__err_cnt_08009c74);
      FUN_08009170(&DAT_08009c70);
    }
  }
  else {
    *pbVar3 = 0;
    if (*(char *)(iVar1 + -0x35) == '\0') {
      FUN_08009170(s_Get_aging_status_success__L__d__R_08009c47 + 1,*(undefined1 *)(iVar1 + 2),
                   *(undefined1 *)(iVar1 + 3));
      FUN_08009170(&DAT_08009c70);
    }
    if ((*(char *)(iVar1 + 2) == '\0') || (*(char *)(iVar1 + 3) == '\0')) {
      *pbVar3 = 10;
      goto LAB_08009c1c;
    }
  }
  if (*pbVar3 < 10) {
    return;
  }
LAB_08009c1c:
  *(undefined1 *)(iVar1 + 6) = 2;
  *(undefined1 *)(_DAT_08009c9c + 2) = 4;
  FUN_0800a888(*(undefined4 *)(iVar1 + -4),4);
  if (*(char *)(iVar1 + -0x35) == '\0') {
    FUN_08009170(s__AGING_ERROR__Get_Aging_Status_E_08009c9f + 1);
    FUN_08009170(&DAT_08009c70);
  }
  return;
}



/* FUN 0x08009cc8 FUN_08009cc8 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08009cc8(void)

{
  int iVar1;
  byte *pbVar2;
  
  pbVar2 = _DAT_08009d2c;
  iVar1 = DAT_08009d28;
  if ((*(char *)(DAT_08009d28 + 0x10) == '\0') || (*(char *)(DAT_08009d28 + 0x11) == '\0')) {
    *_DAT_08009d2c = *_DAT_08009d2c + 1;
    if (pbVar2[7] == 0) {
      FUN_08009170(s_Gls_not_inbox__err_cnt___d_08009d2f + 1);
      FUN_08009170(&DAT_08009d4c);
    }
    if (9 < *pbVar2) {
      _DAT_08009d2c[0x42] = 2;
      *(undefined1 *)(iVar1 + 2) = 4;
      FUN_0800a888(*(undefined4 *)(pbVar2 + 0x38),4);
      if (pbVar2[7] == 0) {
        FUN_08009170(s__AGING_ERROR__Not_Inbox_Error_08009d50);
        FUN_08009170(&DAT_08009d4c);
        return;
      }
    }
  }
  else {
    *_DAT_08009d2c = 0;
  }
  return;
}



/* FUN 0x08009df4 FUN_08009df4 */

void FUN_08009df4(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = 0;
  do {
    iVar1 = FUN_0800a046();
    if (2 < iVar2) {
      return;
    }
    iVar2 = iVar2 + 1;
  } while (iVar1 != 0);
  return;
}



/* FUN 0x08009e0c FUN_08009e0c */

int FUN_08009e0c(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined1 local_28 [12];
  byte local_1c [8];
  
  iVar5 = 0;
  iVar1 = FUN_0800a0ea();
  iVar3 = DAT_08009eb8;
  if (-1 < iVar1) {
    iVar4 = 0;
    iVar1 = -1;
    do {
      iVar2 = FUN_0800a13a(iVar4 + 0x10U & 0xff,iVar3 + iVar4);
      if (iVar2 != 0) {
        return -1;
      }
      iVar4 = iVar4 + 1;
    } while (iVar4 < 0x50);
    local_1c[0] = 0x80;
    iVar3 = FUN_0800a13a(0xb,local_1c);
    if (iVar3 == 0) {
      local_1c[0] = 0;
      iVar3 = FUN_0800a13a(10,local_1c);
      if (iVar3 == 0) {
        local_28[0] = 0x30;
        iVar3 = FUN_0800a13a(8);
        if (iVar3 == 0) {
          FUN_0800a148(0x15);
          local_28[0] = 0;
          iVar3 = FUN_0800a13a(8,local_28);
          if (-1 < iVar3) {
            FUN_0800a148(0xb);
            do {
              FUN_0800a148(0x65);
              FUN_0800a124(0xa7,local_1c);
              if ((local_1c[0] & 0xf) >> 2 == 3) {
                return 0;
              }
              iVar5 = iVar5 + 1;
            } while (iVar5 < 0x32);
            FUN_0800a0ea();
          }
        }
      }
    }
  }
  return iVar1;
}



/* FUN 0x08009ebc FUN_08009ebc */

undefined4 FUN_08009ebc(uint *param_1)

{
  int iVar1;
  uint uVar2;
  uint local_10;
  
  local_10 = 0;
  iVar1 = FUN_0800a074(4,&local_10);
  if (iVar1 != 0) {
    return 0xffffffff;
  }
  uVar2 = FUN_08000160(((local_10 & 0xffffff00) + (local_10 & 0xff)) * 100,0x6300);
  if (99 < uVar2) {
    uVar2 = 100;
  }
  *param_1 = uVar2;
  return 0;
}



/* FUN 0x08009ef8 FUN_08009ef8 */

undefined4 FUN_08009ef8(uint *param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  uint local_10;
  
  local_10 = param_4;
  iVar1 = FUN_0800a124(0,&local_10);
  if (iVar1 != 0) {
    return 0xffffffff;
  }
  *param_1 = local_10 & 0xff;
  return 0;
}



/* FUN 0x08009f18 FUN_08009f18 */

undefined4 FUN_08009f18(undefined4 *param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint local_18;
  uint local_14;
  
  local_18 = 0;
  local_14 = param_4 & 0xffffff00;
  iVar1 = FUN_0800a124(0xab,&local_14);
  if ((iVar1 != 0) || (iVar1 = FUN_0800a074(0xe,&local_18), iVar1 != 0)) {
    return 0xffffffff;
  }
  iVar1 = FUN_0800a3ba(local_18 & 0xffff);
  if ((byte)local_14 >> 6 == 0) {
    uVar2 = DAT_08009f7c;
    iVar3 = DAT_08009f78;
    if ((byte)local_14 == 0) goto LAB_08009f6c;
  }
  else {
    iVar3 = 0x640;
  }
  uVar2 = FUN_0800018c(iVar3 * iVar1,DAT_08009f74);
LAB_08009f6c:
  *param_1 = uVar2;
  return 0;
}



/* FUN 0x08009f80 FUN_08009f80 */

undefined4 FUN_08009f80(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int in_r3;
  int local_18;
  
  local_18 = in_r3;
  iVar1 = FUN_0800a124(8,&local_18);
  if (iVar1 == 0) {
    if ((char)local_18 != '\0') {
      return 1;
    }
    iVar2 = FUN_0800a124(0xb,&local_18);
    iVar1 = DAT_08009fec;
    if (iVar2 == 0) {
      if (-1 < local_18 << 0x18) {
        return 2;
      }
      iVar2 = 0;
      while (iVar3 = FUN_0800a124(iVar2 + 0x10U & 0xff,&local_18), iVar3 == 0) {
        if ((*(char *)(iVar1 + iVar2) != (char)local_18) || (iVar2 = iVar2 + 1, 0x4f < iVar2)) {
          if (iVar2 != 0x50) {
            return 3;
          }
          return 0;
        }
      }
    }
  }
  return 0xffffffff;
}



/* FUN 0x08009ff0 FUN_08009ff0 */

undefined4 FUN_08009ff0(undefined4 *param_1)

{
  int iVar1;
  
  iVar1 = FUN_0800a124(6);
  if (iVar1 != 0) {
    return 0xffffffff;
  }
  *param_1 = 0xfffffe70;
  return 0;
}



/* FUN 0x0800a01e FUN_0800a01e */

undefined4 FUN_0800a01e(uint *param_1)

{
  int iVar1;
  int local_10;
  
  local_10 = 0;
  iVar1 = FUN_0800a074(2,&local_10);
  if (iVar1 != 0) {
    return 0xffffffff;
  }
  *param_1 = (uint)(local_10 * 5) >> 4;
  return 0;
}



/* FUN 0x0800a046 FUN_0800a046 */

int FUN_0800a046(void)

{
  int iVar1;
  int in_r3;
  int local_8;
  
  local_8 = in_r3;
  iVar1 = FUN_08009ef8(&local_8);
  if (iVar1 == 0) {
    if (local_8 == 0xa0) {
      iVar1 = FUN_08009f80();
      if ((-1 < iVar1) && ((iVar1 == 0 || (iVar1 = FUN_08009e0c(), -1 < iVar1)))) {
        return 0;
      }
    }
    else {
      iVar1 = -2;
    }
  }
  return iVar1;
}



/* FUN 0x0800a074 FUN_0800a074 */

undefined4 FUN_0800a074(undefined4 param_1,int *param_2)

{
  int iVar1;
  int iVar2;
  uint local_18;
  
  local_18 = 0;
  iVar1 = FUN_0800a130(param_1,&local_18,2);
  if (iVar1 == 0) {
    iVar2 = (local_18 & 0xff) * 0x100 + (local_18 >> 8 & 0xff);
    FUN_0800a148(5);
    iVar1 = FUN_0800a130(param_1,&local_18,2);
    if (iVar1 == 0) {
      if (iVar2 != (local_18 & 0xff) * 0x100 + (local_18 >> 8 & 0xff)) {
        FUN_0800a148(5);
        iVar1 = FUN_0800a130(param_1,&local_18,2);
        if (iVar1 != 0) {
          return 0xffffffff;
        }
        iVar2 = (local_18 & 0xff) * 0x100 + (local_18 >> 8 & 0xff);
      }
      *param_2 = iVar2;
      return 0;
    }
  }
  return 0xffffffff;
}



/* FUN 0x0800a0ea FUN_0800a0ea */

undefined4 FUN_0800a0ea(void)

{
  int iVar1;
  
  iVar1 = FUN_0800a13a(8);
  if (iVar1 == 0) {
    FUN_0800a148(0x15);
    iVar1 = FUN_0800a13a(8);
    if (iVar1 == 0) {
      FUN_0800a148(0xb);
      return 0;
    }
  }
  return 0xffffffff;
}



/* FUN 0x0800a124 FUN_0800a124 */

undefined4 FUN_0800a124(undefined4 param_1,undefined4 param_2)

{
  FUN_080035b8(param_1,param_2,1);
  return 0;
}



/* FUN 0x0800a130 FUN_0800a130 */

undefined4 FUN_0800a130(void)

{
  FUN_080035b8();
  return 0;
}



/* FUN 0x0800a13a FUN_0800a13a */

undefined4 FUN_0800a13a(undefined4 param_1,undefined1 *param_2)

{
  FUN_080039c8(param_1,*param_2);
  return 0;
}



/* FUN 0x0800a148 FUN_0800a148 */

void FUN_0800a148(int param_1)

{
  int iVar1;
  int iVar2;
  
  for (iVar2 = 0; iVar2 < param_1; iVar2 = iVar2 + 1) {
    iVar1 = 0;
    do {
      iVar1 = iVar1 + 1;
    } while (iVar1 < DAT_0800a160);
  }
  return;
}



/* FUN 0x0800a164 FUN_0800a164 */

void FUN_0800a164(void)

{
  int iVar1;
  
  iVar1 = FUN_0800c3f8();
  FUN_0800a188(iVar1 == 1);
  return;
}



/* FUN 0x0800a176 FUN_0800a176 */

void FUN_0800a176(void)

{
  int iVar1;
  
  iVar1 = FUN_0800c412();
  FUN_0800a19a(iVar1 == 1);
  return;
}



/* FUN 0x0800a188 FUN_0800a188 */

void FUN_0800a188(int param_1)

{
  if (param_1 != 0) {
    FUN_0800a1e8();
    return;
  }
  FUN_0800a1ac();
  return;
}



/* FUN 0x0800a19a FUN_0800a19a */

void FUN_0800a19a(int param_1)

{
  if (param_1 != 0) {
    FUN_0800a206();
    return;
  }
  FUN_0800a1ca();
  return;
}



/* FUN 0x0800a1ac FUN_0800a1ac */

void FUN_0800a1ac(void)

{
  FUN_0800bac4();
  FUN_0800ba84();
  FUN_0800bac4();
  FUN_0800bae8();
  FUN_0800a794(0x17);
  FUN_0800bac4();
  return;
}



/* FUN 0x0800a1ca FUN_0800a1ca */

void FUN_0800a1ca(void)

{
  FUN_0800bad8();
  FUN_0800baa4();
  FUN_0800bad8();
  FUN_0800bafc();
  FUN_0800a7a2(0x17);
  FUN_0800bad8();
  return;
}



/* FUN 0x0800a1e8 FUN_0800a1e8 */

void FUN_0800a1e8(void)

{
  FUN_0800bac4();
  FUN_0800ba84();
  FUN_0800bac4();
  FUN_0800bae8();
  FUN_0800a794(0x5a);
  FUN_0800bac4();
  return;
}



/* FUN 0x0800a206 FUN_0800a206 */

void FUN_0800a206(void)

{
  FUN_0800bad8();
  FUN_0800baa4();
  FUN_0800bad8();
  FUN_0800bafc();
  FUN_0800a7a2(0x5a);
  FUN_0800bad8();
  return;
}



/* FUN 0x0800a224 FUN_0800a224 */

void FUN_0800a224(void)

{
  FUN_0800bac4();
  FUN_0800ba84();
  FUN_0800bac4();
  FUN_0800a794(0x17);
  FUN_0800bae8();
  FUN_0800a794(0x15e);
  FUN_0800bac4();
  return;
}



/* FUN 0x0800a24a FUN_0800a24a */

void FUN_0800a24a(void)

{
  FUN_0800bad8();
  FUN_0800baa4();
  FUN_0800bad8();
  FUN_0800a7a2(0x17);
  FUN_0800bafc();
  FUN_0800a7a2(0x15e);
  FUN_0800bad8();
  return;
}



/* FUN 0x0800a270 FUN_0800a270 */

void FUN_0800a270(void)

{
  undefined4 extraout_r1;
  undefined4 uVar1;
  undefined4 extraout_r1_00;
  uint uVar2;
  int extraout_r2;
  
  FUN_0800bac4();
  FUN_0800ba84();
  FUN_0800bac4();
  FUN_0800a794(0x15e);
  FUN_0800bae8();
  uVar2 = 0;
  uVar1 = extraout_r1;
  do {
    FUN_0800a794(0x15e,uVar1,uVar2);
    uVar2 = extraout_r2 + 1U & 0xff;
    uVar1 = extraout_r1_00;
  } while (uVar2 < 0x28);
  FUN_0800bac4();
  return;
}



/* FUN 0x0800a2a2 FUN_0800a2a2 */

void FUN_0800a2a2(uint param_1,int param_2)

{
  uint uVar1;
  
  if (param_2 == 1) {
    uVar1 = 6;
  }
  else {
    uVar1 = 7;
  }
  do {
    FUN_0800a188((param_1 >> (uVar1 & 0xff) & 1) != 0);
    uVar1 = uVar1 - 1;
  } while (-1 < (int)uVar1);
  return;
}



/* FUN 0x0800a2c4 FUN_0800a2c4 */

void FUN_0800a2c4(uint param_1,int param_2)

{
  uint uVar1;
  
  if (param_2 == 1) {
    uVar1 = 6;
  }
  else {
    uVar1 = 7;
  }
  do {
    FUN_0800a19a((param_1 >> (uVar1 & 0xff) & 1) != 0);
    uVar1 = uVar1 - 1;
  } while (-1 < (int)uVar1);
  return;
}



/* FUN 0x0800a2e6 FUN_0800a2e6 */

void FUN_0800a2e6(void)

{
  undefined4 extraout_r1;
  undefined4 uVar1;
  undefined4 extraout_r1_00;
  int iVar2;
  int extraout_r2;
  undefined4 uVar3;
  undefined4 extraout_r3;
  
  FUN_0800bac4();
  FUN_0800ba84();
  FUN_0800bac4();
  FUN_0800bae8();
  iVar2 = 0;
  uVar3 = 0x15e;
  uVar1 = extraout_r1;
  do {
    FUN_0800a794(uVar3,uVar1,iVar2);
    iVar2 = extraout_r2 + 1;
    uVar3 = extraout_r3;
    uVar1 = extraout_r1_00;
  } while (iVar2 < 0x28);
  FUN_0800bac4();
  return;
}



/* FUN 0x0800a310 FUN_0800a310 */

void FUN_0800a310(void)

{
  undefined4 extraout_r1;
  undefined4 extraout_r1_00;
  undefined4 extraout_r1_01;
  undefined4 uVar1;
  undefined4 extraout_r1_02;
  int iVar2;
  int extraout_r2;
  int extraout_r2_00;
  
  FUN_0800bad8();
  FUN_0800baa4();
  FUN_0800bad8();
  FUN_0800bafc();
  iVar2 = 0;
  uVar1 = extraout_r1;
  do {
    FUN_0800a7a2(0x15e,uVar1,iVar2);
    iVar2 = extraout_r2 + 1;
    uVar1 = extraout_r1_00;
  } while (iVar2 < 10);
  FUN_0800bad8();
  FUN_0800a7a2(0x17);
  FUN_0800bafc();
  iVar2 = 0;
  uVar1 = extraout_r1_01;
  do {
    FUN_0800a7a2(0x15e,uVar1,iVar2);
    iVar2 = extraout_r2_00 + 1;
    uVar1 = extraout_r1_02;
  } while (iVar2 < 10);
  FUN_0800bad8();
  return;
}



/* FUN 0x0800a358 FUN_0800a358 */

void FUN_0800a358(void)

{
  int iVar1;
  undefined2 uVar2;
  
  iVar1 = DAT_0800a378;
  if ((*(ushort *)(DAT_0800a378 + 2) < 2) || (*(char *)(DAT_0800a378 + 1) != 'Z')) {
    uVar2 = 0;
  }
  else {
    *DAT_0800a37c = 0x5a;
    uVar2 = 1;
  }
  *(undefined2 *)(iVar1 + 2) = uVar2;
  return;
}



/* FUN 0x0800a39c FUN_0800a39c */

void FUN_0800a39c(void)

{
  FUN_08004e94(DAT_0800a3a8,4);
  return;
}



/* FUN 0x0800a3ac FUN_0800a3ac */

void FUN_0800a3ac(void)

{
  FUN_08004e94(0x50000000,8);
  return;
}



/* FUN 0x0800a3ba FUN_0800a3ba */

int FUN_0800a3ba(uint param_1)

{
  int iVar1;
  
  if ((int)(param_1 << 0x10) < 0) {
    iVar1 = -1;
    param_1 = -param_1 & 0xffff;
  }
  else {
    iVar1 = 1;
  }
  return iVar1 * param_1;
}



/* FUN 0x0800a3d2 FUN_0800a3d2 */

void FUN_0800a3d2(void)

{
  FUN_0800a550(0);
  FUN_0800a408();
  FUN_0800a574(0);
  FUN_0800a408();
  FUN_0800a550(1);
  FUN_0800a408();
  FUN_0800a550(0);
  FUN_0800a408();
  FUN_0800a574(1);
  FUN_0800a408();
  return;
}



/* FUN 0x0800a408 FUN_0800a408 */

void FUN_0800a408(void)

{
  byte bVar1;
  
  bVar1 = 0;
  do {
    bVar1 = bVar1 + 1;
  } while (bVar1 < 10);
  return;
}



/* FUN 0x0800a414 FUN_0800a414 */

void FUN_0800a414(void)

{
  FUN_0800a574(1);
  FUN_0800a408();
  FUN_0800a550(1);
  FUN_0800a408();
  FUN_0800a550(0);
  FUN_0800a408();
  return;
}



/* FUN 0x0800a436 FUN_0800a436 */

uint FUN_0800a436(void)

{
  int iVar1;
  uint uVar2;
  byte bVar3;
  
  uVar2 = 0;
  bVar3 = 0;
  do {
    uVar2 = (uVar2 & 0x7f) * 2;
    FUN_0800a550(1);
    FUN_0800a408();
    iVar1 = FUN_0800a528();
    if (iVar1 != 0) {
      uVar2 = uVar2 + 1;
    }
    FUN_0800a550(0);
    FUN_0800a408();
    bVar3 = bVar3 + 1;
  } while (bVar3 < 8);
  return uVar2;
}



/* FUN 0x0800a46c FUN_0800a46c */

void FUN_0800a46c(uint param_1)

{
  byte bVar1;
  
  bVar1 = 0;
  do {
    FUN_0800a574((int)(param_1 << 0x18) < 0);
    FUN_0800a408();
    FUN_0800a550(1);
    FUN_0800a408();
    FUN_0800a550(0);
    FUN_0800a408();
    if (bVar1 == 7) {
      FUN_0800a574(1);
      FUN_0800a408();
    }
    bVar1 = bVar1 + 1;
    param_1 = (param_1 & 0x7f) << 1;
  } while (bVar1 < 8);
  return;
}



/* FUN 0x0800a4b4 FUN_0800a4b4 */

void FUN_0800a4b4(void)

{
  FUN_0800a550(1);
  FUN_0800a574(1);
  FUN_0800a408();
  FUN_0800a574(0);
  FUN_0800a408();
  FUN_0800a550(0);
  FUN_0800a408();
  return;
}



/* FUN 0x0800a4dc FUN_0800a4dc */

void FUN_0800a4dc(void)

{
  FUN_0800a574(0);
  FUN_0800a550(1);
  FUN_0800a408();
  FUN_0800a574(1);
  FUN_0800a408();
  return;
}



/* FUN 0x0800a4fa FUN_0800a4fa */

bool FUN_0800a4fa(void)

{
  int iVar1;
  
  FUN_0800a574(1);
  FUN_0800a550(1);
  FUN_0800a408();
  iVar1 = FUN_0800a528();
  FUN_0800a550(0);
  FUN_0800a408();
  return iVar1 != 0;
}



/* FUN 0x0800a528 FUN_0800a528 */

bool FUN_0800a528(void)

{
  int iVar1;
  undefined4 uVar2;
  
  if (*DAT_0800a548 == '\0') {
    uVar2 = 0x10;
  }
  else {
    uVar2 = 8;
  }
  iVar1 = FUN_08004e94(DAT_0800a54c,uVar2);
  return iVar1 != 0;
}



/* FUN 0x0800a550 FUN_0800a550 */

void FUN_0800a550(undefined4 param_1)

{
  undefined4 uVar1;
  
  if (*DAT_0800a56c == '\0') {
    uVar1 = 8;
  }
  else {
    uVar1 = 0x10;
  }
  FUN_08004e9e(DAT_0800a570,uVar1,param_1);
  return;
}



/* FUN 0x0800a574 FUN_0800a574 */

void FUN_0800a574(undefined4 param_1)

{
  undefined4 uVar1;
  
  if (*DAT_0800a590 == '\0') {
    uVar1 = 0x10;
  }
  else {
    uVar1 = 8;
  }
  FUN_08004e9e(DAT_0800a594,uVar1,param_1);
  return;
}



/* FUN 0x0800a598 FUN_0800a598 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0800a598(void)

{
  char *pcVar1;
  char *pcVar2;
  int iVar3;
  undefined4 auStack_1c [4];
  int iStack_c;
  uint uStack_4;
  
  FUN_08004eec();
  FUN_08008438();
  FUN_08006a40();
  FUN_08002888();
  FUN_08006bb0();
  FUN_08006c00();
  FUN_080068f0();
  FUN_08004a00(auStack_1c);
  pcVar1 = _DAT_0800a6d8;
  if (((int)(uStack_4 << 7) < 0) || (iStack_c != 0xaa)) {
    if (*_DAT_0800a6d8 == '\0') {
      FUN_08009170(s_Option_Bytes_check_fail__UPDATE___0800a6db + 1,uStack_4);
      FUN_08009170(&DAT_0800a70c);
    }
    auStack_1c[0] = 6;
    uStack_4 = uStack_4 & 0xfeffff00 | 0xaa;
    iStack_c = 0xaa;
    FUN_08004bf4();
    FUN_08004b6c();
    FUN_08004a6c(auStack_1c);
    FUN_08004b3c();
    FUN_08004b50();
    FUN_08004b20();
  }
  else if (*_DAT_0800a6d8 == '\0') {
    FUN_08009170(s_Option_Bytes_check_done__0x_x__l_0800a710,uStack_4,0xaa);
    FUN_08009170(&DAT_0800a70c);
  }
  *(uint *)(DAT_0800a73c + 0x3c) = *(uint *)(DAT_0800a73c + 0x3c) | DAT_0800a73c << 0x10;
  iVar3 = DAT_0800a744;
  pcVar2 = DAT_0800a740;
  *DAT_0800a740 = '\0';
  if (-1 < (int)(~*(uint *)(iVar3 + 0x10) << 0x17)) {
    *(int *)(iVar3 + 0x18) = DAT_0800a748;
    if (-1 < (int)(~*(uint *)(iVar3 + 0x10) << 0x1c)) {
      *(int *)(iVar3 + 0x18) = DAT_0800a748 + -0xf8;
      *pcVar2 = '\x01';
      if (*pcVar1 == '\0') {
        FUN_08009170(s_wake_up_from_HALL_0800a74c);
        FUN_08009170(&DAT_0800a70c);
      }
    }
    if (-1 < (int)(~*(uint *)(iVar3 + 0x10) << 0x1a)) {
      *(int *)(iVar3 + 0x18) = DAT_0800a748 + -0xe0;
      *pcVar2 = '\x02';
      if (*pcVar1 != '\0') goto LAB_0800a6c6;
      FUN_08009170(s_wake_up_from_USB_0800a760);
      FUN_08009170(&DAT_0800a70c);
    }
    if (*pcVar2 != '\0') goto LAB_0800a6c6;
    *pcVar2 = '\x03';
    if (*pcVar1 != '\0') goto LAB_0800a6c6;
    FUN_08009170(s_wake_up_from_RTC_0800a774);
    FUN_08009170(&DAT_0800a70c);
    if (*pcVar2 != '\0') goto LAB_0800a6c6;
  }
  if (*pcVar1 == '\0') {
    FUN_08009170(s_Power_up____0800a788);
    FUN_08009170(&DAT_0800a70c);
  }
LAB_0800a6c6:
  FUN_08002fc8();
  FUN_0800a8d8();
  FUN_08006968();
  FUN_0800a900();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* FUN 0x0800a794 FUN_0800a794 */

void FUN_0800a794(int param_1)

{
  int iVar1;
  
  for (iVar1 = 0; iVar1 < param_1; iVar1 = iVar1 + 1) {
  }
  return;
}



/* FUN 0x0800a7a2 FUN_0800a7a2 */

void FUN_0800a7a2(int param_1)

{
  int iVar1;
  
  for (iVar1 = 0; iVar1 < param_1; iVar1 = iVar1 + 1) {
  }
  return;
}



/* FUN 0x0800a7b0 FUN_0800a7b0 */

undefined4 FUN_0800a7b0(int param_1)

{
  bool bVar1;
  uint uVar2;
  undefined4 uVar3;
  
  uVar2 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar2 = getCurrentExceptionNumber();
    uVar2 = uVar2 & 0x1f;
  }
  if (uVar2 == 0) {
    uVar3 = 0;
    if (param_1 != 0) {
      FUN_0800c128(param_1);
    }
  }
  else {
    uVar3 = 0xfffffffa;
  }
  return uVar3;
}



/* FUN 0x0800a7d2 FUN_0800a7d2 */

undefined4 FUN_0800a7d2(int param_1,uint param_2)

{
  bool bVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  
  if ((param_1 == 0) || (param_2 >> 0x18 != 0)) {
    uVar4 = 0xfffffffc;
  }
  else {
    uVar2 = 0;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      uVar2 = getCurrentExceptionNumber();
      uVar2 = uVar2 & 0x1f;
    }
    if (uVar2 == 0) {
      uVar4 = FUN_0800c44c(param_1,param_2);
    }
    else {
      uVar4 = FUN_0800c4cc(param_1);
      iVar3 = FUN_0800c478(param_1,param_2);
      if (iVar3 == 0) {
        uVar4 = 0xfffffffd;
      }
    }
  }
  return uVar4;
}



/* FUN 0x0800a816 FUN_0800a816 */

undefined4 FUN_0800a816(int param_1)

{
  bool bVar1;
  undefined4 uVar2;
  uint uVar3;
  
  if (param_1 == 0) {
    return 0;
  }
  uVar3 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar3 = getCurrentExceptionNumber();
    uVar3 = uVar3 & 0x1f;
  }
  if (uVar3 != 0) {
    uVar2 = FUN_0800c4cc();
    return uVar2;
  }
  uVar2 = FUN_0800c44c(param_1,0);
  return uVar2;
}



/* FUN 0x0800a836 FUN_0800a836 */

undefined4 FUN_0800a836(int param_1)

{
  bool bVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar4 = 0;
  uVar2 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar2 = getCurrentExceptionNumber();
    uVar2 = uVar2 & 0x1f;
  }
  if (uVar2 == 0) {
    iVar3 = -1;
    if (param_1 == 0) {
      iVar3 = 0;
    }
    else if ((*(int *)(param_1 + 8) == 0) || (*(uint *)(param_1 + 0xc) < 0x20)) {
      if ((*(int *)(param_1 + 8) == 0) && (*(int *)(param_1 + 0xc) == 0)) {
        iVar3 = 0;
      }
    }
    else {
      iVar3 = 1;
    }
    if (iVar3 == 1) {
      uVar4 = FUN_0800c4aa(*(undefined4 *)(param_1 + 8));
    }
    else if (iVar3 == 0) {
      uVar4 = FUN_0800c48c();
    }
  }
  return uVar4;
}



/* FUN 0x0800a888 FUN_0800a888 */

uint FUN_0800a888(int param_1,uint param_2,undefined4 param_3,int param_4)

{
  bool bVar1;
  int iVar2;
  uint uVar3;
  int local_10;
  
  if ((param_1 == 0) || (param_2 >> 0x18 != 0)) {
    param_2 = 0xfffffffc;
  }
  else {
    uVar3 = 0;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      uVar3 = getCurrentExceptionNumber();
      uVar3 = uVar3 & 0x1f;
    }
    if (uVar3 == 0) {
      local_10 = param_4;
      uVar3 = FUN_0800c4de(param_1,param_2);
      return uVar3;
    }
    local_10 = 0;
    iVar2 = FUN_0800c568(param_1,param_2,&local_10);
    if (iVar2 == 0) {
      return 0xfffffffd;
    }
    if (local_10 != 0) {
      *(undefined4 *)(DAT_0800a8d4 + 4) = 0x10000000;
      return param_2;
    }
  }
  return param_2;
}



/* FUN 0x0800a8d8 FUN_0800a8d8 */

undefined4 FUN_0800a8d8(void)

{
  bool bVar1;
  uint uVar2;
  
  uVar2 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar2 = getCurrentExceptionNumber();
    uVar2 = uVar2 & 0x1f;
  }
  if (uVar2 != 0) {
    return 0xfffffffa;
  }
  if (*DAT_0800a8fc != 0) {
    return 0xffffffff;
  }
  *DAT_0800a8fc = 1;
  return 0;
}



/* FUN 0x0800a900 FUN_0800a900 */

undefined4 FUN_0800a900(void)

{
  bool bVar1;
  int *piVar2;
  uint uVar3;
  
  piVar2 = DAT_0800a934;
  uVar3 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar3 = getCurrentExceptionNumber();
    uVar3 = uVar3 & 0x1f;
  }
  if (uVar3 != 0) {
    return 0xfffffffa;
  }
  if (*DAT_0800a934 != 1) {
    return 0xffffffff;
  }
  *(uint *)(DAT_0800a938 + 0x1c) = *(uint *)(DAT_0800a938 + 0x1c) & 0xffffff;
  *piVar2 = 2;
  FUN_0800c284();
  return 0;
}



/* FUN 0x0800a93c FUN_0800a93c */

undefined4 FUN_0800a93c(int param_1,undefined4 param_2,int *param_3)

{
  bool bVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  undefined4 local_18;
  
  local_18 = 0;
  uVar2 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar2 = getCurrentExceptionNumber();
    uVar2 = uVar2 & 0x1f;
  }
  if ((uVar2 == 0) && (param_1 != 0)) {
    uVar2 = 0x80;
    iVar4 = 0x18;
    iVar5 = 0;
    iVar3 = -1;
    if (param_3 == (int *)0x0) {
      iVar3 = 0;
    }
    else {
      if (*param_3 != 0) {
        iVar5 = *param_3;
      }
      if (param_3[6] != 0) {
        iVar4 = param_3[6];
      }
      if ((0x37 < iVar4 - 1U) || ((*(byte *)(param_3 + 1) & 1) != 0)) {
        return 0;
      }
      uVar6 = param_3[5];
      if (uVar6 != 0) {
        uVar2 = uVar6 >> 2;
      }
      if ((((param_3[2] == 0) || ((uint)param_3[3] < 0x5c)) || (param_3[4] == 0)) || (uVar6 == 0)) {
        if (((param_3[2] == 0) && (param_3[3] == 0)) && (param_3[4] == 0)) {
          iVar3 = 0;
        }
      }
      else {
        iVar3 = 1;
      }
    }
    if (iVar3 == 1) {
      local_18 = FUN_0800ca06(param_1,iVar5,uVar2,param_2,iVar4,param_3[4],param_3[2]);
    }
    else if ((iVar3 == 0) &&
            (iVar4 = FUN_0800c9a8(param_1,iVar5,uVar2 & 0xffff,param_2,iVar4,&local_18), iVar4 != 1)
            ) {
      local_18 = 0;
    }
  }
  return local_18;
}



/* FUN 0x0800aa00 FUN_0800aa00 */

undefined4 FUN_0800aa00(int param_1)

{
  bool bVar1;
  uint uVar2;
  undefined4 uVar3;
  
  uVar2 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar2 = getCurrentExceptionNumber();
    uVar2 = uVar2 & 0x1f;
  }
  if (uVar2 == 0) {
    if (param_1 == 0) {
      uVar3 = 0xfffffffc;
    }
    else {
      uVar3 = 0;
      FUN_0800c228();
    }
  }
  else {
    uVar3 = 0xfffffffa;
  }
  return uVar3;
}



/* FUN 0x0800aa24 FUN_0800aa24 */

undefined4 FUN_0800aa24(int param_1)

{
  bool bVar1;
  uint uVar2;
  undefined4 uVar3;
  
  uVar2 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar2 = getCurrentExceptionNumber();
    uVar2 = uVar2 & 0x1f;
  }
  if (uVar2 == 0) {
    if (param_1 == 0) {
      uVar3 = 0xfffffffc;
    }
    else {
      uVar3 = 0;
      FUN_0800c2f8();
    }
  }
  else {
    uVar3 = 0xfffffffa;
  }
  return uVar3;
}



/* FUN 0x0800aa48 FUN_0800aa48 */

int FUN_0800aa48(int param_1,int param_2,int param_3,int *param_4)

{
  bool bVar1;
  uint uVar2;
  int *piVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  iVar5 = 0;
  uVar2 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar2 = getCurrentExceptionNumber();
    uVar2 = uVar2 & 0x1f;
  }
  if (((uVar2 == 0) && (param_1 != 0)) && (piVar3 = (int *)FUN_0800b3e8(8), piVar3 != (int *)0x0)) {
    *piVar3 = param_1;
    piVar3[1] = param_3;
    iVar4 = -1;
    iVar6 = 0;
    if (param_4 == (int *)0x0) {
      iVar4 = 0;
    }
    else {
      if (*param_4 != 0) {
        iVar6 = *param_4;
      }
      if ((param_4[2] == 0) || ((uint)param_4[3] < 0x2c)) {
        if ((param_4[2] == 0) && (param_4[3] == 0)) {
          iVar4 = 0;
        }
      }
      else {
        iVar4 = 1;
      }
    }
    if (iVar4 == 1) {
      iVar5 = FUN_0800ccf2(iVar6,1,param_2 != 0,piVar3,DAT_0800aaec,param_4[2]);
    }
    else if (iVar4 == 0) {
      iVar5 = FUN_0800ccc0(iVar6,1,param_2 != 0,piVar3,DAT_0800aaec);
    }
    if (iVar5 == 0) {
      FUN_0800c030(piVar3);
    }
  }
  return iVar5;
}



/* FUN 0x0800aaf0 FUN_0800aaf0 */

undefined4 FUN_0800aaf0(int param_1,undefined4 param_2)

{
  bool bVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar3 = getCurrentExceptionNumber();
    uVar3 = uVar3 & 0x1f;
  }
  if (uVar3 != 0) {
    return 0xfffffffa;
  }
  if (param_1 == 0) {
    return 0xfffffffc;
  }
  iVar2 = FUN_0800cd80(param_1,4,param_2,0,0);
  if (iVar2 != 1) {
    return 0xfffffffd;
  }
  return 0;
}



/* FUN 0x0800ab26 FUN_0800ab26 */

undefined4 FUN_0800ab26(int param_1)

{
  bool bVar1;
  uint uVar2;
  int iVar3;
  
  uVar2 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar2 = getCurrentExceptionNumber();
    uVar2 = uVar2 & 0x1f;
  }
  if (uVar2 != 0) {
    return 0xfffffffa;
  }
  if (param_1 == 0) {
    return 0xfffffffc;
  }
  iVar3 = FUN_0800cde4(param_1);
  if (iVar3 != 0) {
    iVar3 = FUN_0800cd80(param_1,3,0,0,0);
    if (iVar3 != 1) {
      return 0xffffffff;
    }
    return 0;
  }
  return 0xfffffffd;
}



/* FUN 0x0800ab70 FUN_0800ab70 */

void FUN_0800ab70(void)

{
  char *pcVar1;
  
  pcVar1 = DAT_0800aba4;
  if ((((DAT_0800aba4[0x10] == '\0') && (DAT_0800aba4[0x11] == '\0')) && (DAT_0800aba4[2] == '\0'))
     && (*DAT_0800aba4 != '\x03')) {
    FUN_08003848(0);
    pcVar1[2] = '\x01';
    FUN_0800aaf0(*(undefined4 *)(DAT_0800abac + 0x10),DAT_0800aba8);
  }
  return;
}



/* FUN 0x0800abb0 FUN_0800abb0 */

void FUN_0800abb0(int param_1,int param_2)

{
  int *piVar1;
  uint uVar2;
  uint uVar3;
  
  piVar1 = DAT_0800ac00;
  uVar3 = DAT_0800ac00[3];
  FUN_0800bf2c(*DAT_0800ac00 + 4);
  if ((param_1 == -1) && (param_2 != 0)) {
    FUN_0800bfe2(DAT_0800ac04,*piVar1 + 4);
    return;
  }
  uVar2 = uVar3 + param_1;
  *(uint *)(*piVar1 + 4) = uVar2;
  if (uVar2 < uVar3) {
    FUN_0800bfb0(piVar1[0xe],*piVar1 + 4);
  }
  else {
    FUN_0800bfb0(piVar1[0xd],*piVar1 + 4);
    if (uVar2 < (uint)piVar1[10]) {
      piVar1[10] = uVar2;
      return;
    }
  }
  return;
}



/* FUN 0x0800ac08 FUN_0800ac08 */

void FUN_0800ac08(int param_1)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  
  FUN_0800bffc();
  piVar1 = DAT_0800ac7c;
  DAT_0800ac7c[2] = DAT_0800ac7c[2] + 1;
  if (*piVar1 == 0) {
    *piVar1 = param_1;
    if (piVar1[2] == 1) {
      FUN_0800af70();
    }
  }
  else if ((piVar1[5] == 0) && (*(uint *)(*piVar1 + 0x2c) <= *(uint *)(param_1 + 0x2c))) {
    *piVar1 = param_1;
  }
  iVar2 = piVar1[9];
  piVar1[9] = iVar2 + 1;
  *(int *)(param_1 + 0x44) = iVar2 + 1;
  uVar3 = *(uint *)(param_1 + 0x2c);
  if ((uint)piVar1[4] < uVar3) {
    piVar1[4] = uVar3;
  }
  FUN_0800bfe2(uVar3 * 0x14 + DAT_0800ac80,param_1 + 4);
  FUN_0800c014();
  if ((piVar1[5] != 0) && (*(uint *)(*piVar1 + 0x2c) < *(uint *)(param_1 + 0x2c))) {
    FUN_0800c0a0();
  }
  return;
}



/* FUN 0x0800ac84 FUN_0800ac84 */

void FUN_0800ac84(void)

{
  int *piVar1;
  int iVar2;
  
  FUN_0800bffc();
  piVar1 = DAT_0800acc8;
  if (*DAT_0800acc8 == 0) {
    FUN_0800bf94(DAT_0800accc);
    FUN_0800bf94(DAT_0800acd0);
    iVar2 = DAT_0800accc;
    piVar1[3] = DAT_0800accc;
    piVar1[4] = iVar2 + 0x14;
    iVar2 = FUN_0800c5d0(10,0x10,DAT_0800acd8,DAT_0800acd4,0);
    *piVar1 = iVar2;
    if (iVar2 != 0) {
      FUN_0800c0b8(iVar2,&LAB_0800acdc);
    }
  }
  FUN_0800c014();
  return;
}



/* FUN 0x0800ace4 FUN_0800ace4 */

void FUN_0800ace4(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = DAT_0800ad20;
  iVar1 = DAT_0800ad1c;
  iVar3 = *(int *)(DAT_0800ad1c + 4);
  while (iVar3 != 0) {
    FUN_0800bffc();
    iVar3 = *(int *)(*(int *)(iVar2 + 0xc) + 0xc);
    FUN_0800bf2c(iVar3 + 4);
    *(int *)(iVar1 + 8) = *(int *)(iVar1 + 8) + -1;
    *(int *)(iVar1 + 4) = *(int *)(iVar1 + 4) + -1;
    FUN_0800c014();
    FUN_0800adb8(iVar3);
    iVar3 = *(int *)(iVar1 + 4);
  }
  return;
}



/* FUN 0x0800ad24 FUN_0800ad24 */

void FUN_0800ad24(undefined4 *param_1,undefined4 param_2)

{
  uint uVar1;
  
  if (param_1[0x10] != 0) {
    uVar1 = param_1[3] + param_1[0x10];
    param_1[3] = uVar1;
    if ((uint)param_1[2] <= uVar1) {
      param_1[3] = *param_1;
    }
    FUN_080001b4(param_2,param_1[3]);
  }
  return;
}



/* FUN 0x0800ad48 FUN_0800ad48 */

undefined4 FUN_0800ad48(uint *param_1,undefined4 param_2,int param_3)

{
  uint uVar1;
  uint uVar2;
  undefined4 uVar3;
  
  uVar3 = 0;
  uVar2 = param_1[0xe];
  if (param_1[0x10] == 0) {
    if (*param_1 == 0) {
      uVar3 = FUN_0800cb38(param_1[2]);
      param_1[2] = 0;
    }
  }
  else if (param_3 == 0) {
    FUN_080001b4(param_1[1]);
    uVar1 = param_1[1];
    param_1[1] = uVar1 + param_1[0x10];
    if (param_1[2] <= uVar1 + param_1[0x10]) {
      param_1[1] = *param_1;
    }
  }
  else {
    FUN_080001b4(param_1[3]);
    uVar1 = param_1[3] - param_1[0x10];
    param_1[3] = uVar1;
    if (uVar1 < *param_1) {
      param_1[3] = param_1[2] - param_1[0x10];
    }
    if ((param_3 == 2) && (uVar2 != 0)) {
      uVar2 = uVar2 - 1;
    }
  }
  param_1[0xe] = uVar2 + 1;
  return uVar3;
}



/* FUN 0x0800adb8 FUN_0800adb8 */

void FUN_0800adb8(int param_1)

{
  char cVar1;
  
  cVar1 = *(char *)(param_1 + 0x59);
  if (cVar1 == '\0') {
    FUN_0800c030(*(undefined4 *)(param_1 + 0x30));
    FUN_0800c030(param_1);
  }
  else {
    if (cVar1 == '\x01') {
      FUN_0800c030(param_1);
      return;
    }
    if (cVar1 != '\x02') {
      disableIRQinterrupts();
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
  }
  return;
}



/* FUN 0x0800ae0c FUN_0800ae0c */

void FUN_0800ae0c(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 *puVar5;
  
  puVar1 = DAT_0800ae54;
  iVar4 = 0xc00;
  puVar2 = DAT_0800ae50;
  if (((uint)DAT_0800ae50 & 7) != 0) {
    puVar2 = (undefined4 *)((int)DAT_0800ae50 + 7U & 0xfffffff8);
    iVar4 = 0xc00 - ((int)puVar2 - (int)DAT_0800ae50);
  }
  *DAT_0800ae54 = puVar2;
  puVar1[1] = 0;
  puVar1 = DAT_0800ae58;
  puVar5 = (undefined4 *)((int)puVar2 + iVar4 + -8 & 0xfffffff8);
  *DAT_0800ae58 = puVar5;
  puVar5[1] = 0;
  *puVar5 = 0;
  puVar2[1] = (int)puVar5 - (int)puVar2;
  *puVar2 = puVar5;
  uVar3 = puVar2[1];
  puVar1[2] = uVar3;
  puVar1[1] = uVar3;
  puVar1[5] = 0x80000000;
  return;
}



/* FUN 0x0800ae74 FUN_0800ae74 */

void FUN_0800ae74(undefined4 param_1,int param_2,undefined4 param_3,undefined1 param_4,
                 undefined4 *param_5)

{
  if (param_2 == 0) {
    *param_5 = param_5;
  }
  else {
    *param_5 = param_3;
  }
  param_5[0xf] = param_1;
  param_5[0x10] = param_2;
  FUN_0800c616(param_5,1);
  *(undefined1 *)(param_5 + 0x13) = param_4;
  return;
}



/* FUN 0x0800ae96 FUN_0800ae96 */

/* WARNING: Removing unreachable block (ram,0x0800aec0) */
/* WARNING: Removing unreachable block (ram,0x0800aec2) */

void FUN_0800ae96(undefined4 param_1,int param_2,int param_3,undefined4 param_4,uint param_5,
                 undefined4 *param_6,undefined4 *param_7)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  FUN_080001d8(param_7[0xc],param_3 << 2,0xa5);
  iVar1 = param_7[0xc];
  if (param_2 == 0) {
    *(undefined1 *)(param_7 + 0xd) = 0;
  }
  else {
    uVar3 = 0;
    do {
      *(undefined1 *)((int)param_7 + uVar3 + 0x34) = *(undefined1 *)(param_2 + uVar3);
      if (*(char *)(param_2 + uVar3) == '\0') break;
      uVar3 = uVar3 + 1;
    } while (uVar3 < 0x10);
    *(undefined1 *)((int)param_7 + 0x43) = 0;
  }
  if (0x37 < param_5) {
    param_5 = 0x37;
  }
  param_7[0xb] = param_5;
  param_7[0x13] = param_5;
  param_7[0x14] = 0;
  FUN_0800bfaa(param_7 + 1);
  FUN_0800bfaa(param_7 + 6);
  param_7[4] = param_7;
  param_7[6] = 0x38 - param_5;
  param_7[9] = param_7;
  param_7[0x15] = 0;
  *(undefined1 *)(param_7 + 0x16) = 0;
  uVar2 = FUN_0800b4c0(iVar1 + (param_3 + -1) * 4 & 0xfffffff8,param_1,param_4);
  *param_7 = uVar2;
  if (param_6 != (undefined4 *)0x0) {
    *param_6 = param_7;
  }
  return;
}



/* FUN 0x0800af30 FUN_0800af30 */

void FUN_0800af30(undefined4 param_1,int param_2,int param_3,undefined4 param_4,undefined4 param_5,
                 undefined4 *param_6)

{
  if (param_2 != 0) {
    if (param_6 != (undefined4 *)0x0) {
      FUN_0800ac84();
      *param_6 = param_1;
      param_6[6] = param_2;
      param_6[7] = param_4;
      param_6[8] = param_5;
      FUN_0800bfaa(param_6 + 1);
      if (param_3 != 0) {
        *(byte *)(param_6 + 10) = *(byte *)(param_6 + 10) | 4;
      }
    }
    return;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* FUN 0x0800af70 FUN_0800af70 */

void FUN_0800af70(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  iVar1 = DAT_0800afb0;
  uVar3 = 0;
  do {
    FUN_0800bf94(uVar3 * 0x14 + iVar1);
    uVar3 = uVar3 + 1;
  } while (uVar3 < 0x38);
  FUN_0800bf94(DAT_0800afb4);
  FUN_0800bf94(DAT_0800afb8);
  FUN_0800bf94(DAT_0800afbc);
  FUN_0800bf94(DAT_0800afc0);
  FUN_0800bf94(DAT_0800afc4);
  iVar2 = DAT_0800afc8;
  iVar1 = DAT_0800afb4;
  *(int *)(DAT_0800afc8 + 0x34) = DAT_0800afb4;
  *(int *)(iVar2 + 0x38) = iVar1 + 0x14;
  return;
}



/* FUN 0x0800afcc FUN_0800afcc */

void FUN_0800afcc(uint *param_1)

{
  uint *puVar1;
  uint *puVar2;
  
  puVar2 = DAT_0800b01c;
  do {
    puVar1 = puVar2;
    puVar2 = (uint *)*puVar1;
  } while (puVar2 < param_1);
  if ((uint *)(puVar1[1] + (int)puVar1) == param_1) {
    puVar1[1] = puVar1[1] + param_1[1];
    param_1 = puVar1;
  }
  if (param_1[1] + (int)param_1 == *puVar1) {
    if (puVar2 == (uint *)*DAT_0800b020) {
      *param_1 = (uint)*DAT_0800b020;
    }
    else {
      param_1[1] = param_1[1] + puVar2[1];
      *param_1 = *(uint *)*puVar1;
    }
  }
  else {
    *param_1 = (uint)puVar2;
  }
  if (puVar1 != param_1) {
    *puVar1 = (uint)param_1;
  }
  return;
}



/* FUN 0x0800b024 FUN_0800b024 */

undefined4 FUN_0800b024(int param_1,uint param_2,uint param_3,uint param_4)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  *(uint *)(param_1 + 4) = param_2;
  *(int *)(param_1 + 0x10) = param_1;
  if (param_3 < param_2) {
    if ((param_3 < param_4) && (param_4 <= param_2)) {
      uVar1 = 1;
    }
    else {
      FUN_0800bfb0(*(undefined4 *)(DAT_0800b060 + 0xc),param_1 + 4);
    }
  }
  else if (param_3 - param_4 < *(uint *)(param_1 + 0x18)) {
    FUN_0800bfb0(*(undefined4 *)(DAT_0800b060 + 0x10),param_1 + 4);
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}



/* FUN 0x0800b064 FUN_0800b064 */

bool FUN_0800b064(int param_1)

{
  int iVar1;
  
  FUN_0800bffc();
  iVar1 = *(int *)(param_1 + 0x38);
  FUN_0800c014();
  return iVar1 == 0;
}



/* FUN 0x0800b080 FUN_0800b080 */

bool FUN_0800b080(int param_1)

{
  int iVar1;
  int iVar2;
  
  FUN_0800bffc();
  iVar1 = *(int *)(param_1 + 0x38);
  iVar2 = *(int *)(param_1 + 0x3c);
  FUN_0800c014();
  return iVar1 == iVar2;
}



/* FUN 0x0800b0a0 FUN_0800b0a0 */

void FUN_0800b0a0(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = *(int *)(*(int *)(*(int *)(DAT_0800b0f8 + 0xc) + 0xc) + 0xc);
  FUN_0800bf2c(iVar2 + 4);
  if ((int)((uint)*(byte *)(iVar2 + 0x28) << 0x1d) < 0) {
    iVar1 = FUN_0800b024(iVar2,*(int *)(iVar2 + 0x18) + param_1,param_2,param_1,param_4);
    if (iVar1 != 0) {
      iVar1 = FUN_0800cd80(iVar2,0,param_1,0,0);
      if (iVar1 == 0) {
        disableIRQinterrupts();
        do {
                    /* WARNING: Do nothing block with infinite loop */
        } while( true );
      }
    }
  }
  else {
    *(byte *)(iVar2 + 0x28) = *(byte *)(iVar2 + 0x28) & 0xfe;
  }
  (**(code **)(iVar2 + 0x20))(iVar2);
  return;
}



/* FUN 0x0800b0fc FUN_0800b0fc */

void FUN_0800b0fc(void)

{
  undefined4 *puVar1;
  int iVar2;
  int iVar3;
  undefined1 auStack_24 [4];
  int local_20;
  code *local_1c;
  int local_18;
  undefined4 local_14;
  
  puVar1 = DAT_0800b1f8;
  iVar2 = FUN_0800c83a(*DAT_0800b1f8,&local_20,0);
  do {
    if (iVar2 == 0) {
      return;
    }
    if (local_20 < 0) {
      (*local_1c)(local_18,local_14);
    }
    iVar2 = local_18;
    if (-1 < local_20) {
      if (*(int *)(local_18 + 0x14) != 0) {
        FUN_0800bf2c(local_18 + 4);
      }
      iVar3 = FUN_0800b284(auStack_24);
      switch(local_20) {
      case 0:
      case 1:
      case 2:
      case 6:
      case 7:
        *(byte *)(iVar2 + 0x28) = *(byte *)(iVar2 + 0x28) | 1;
        iVar3 = FUN_0800b024(iVar2,local_1c + *(int *)(iVar2 + 0x18),iVar3,local_1c);
        if (((iVar3 != 0) &&
            ((**(code **)(iVar2 + 0x20))(iVar2), (int)((uint)*(byte *)(iVar2 + 0x28) << 0x1d) < 0))
           && (iVar2 = FUN_0800cd80(iVar2,0,local_1c + *(int *)(iVar2 + 0x18),0,0), iVar2 == 0)) {
          disableIRQinterrupts();
          do {
                    /* WARNING: Do nothing block with infinite loop */
          } while( true );
        }
        break;
      case 3:
      case 8:
        *(byte *)(iVar2 + 0x28) = *(byte *)(iVar2 + 0x28) & 0xfe;
        break;
      case 4:
      case 9:
        *(byte *)(iVar2 + 0x28) = *(byte *)(iVar2 + 0x28) | 1;
        *(code **)(iVar2 + 0x18) = local_1c;
        if (local_1c == (code *)0x0) {
          disableIRQinterrupts();
          do {
                    /* WARNING: Do nothing block with infinite loop */
          } while( true );
        }
        FUN_0800b024(iVar2,local_1c + iVar3,iVar3,iVar3);
        break;
      case 5:
        if ((int)((uint)*(byte *)(iVar2 + 0x28) << 0x1e) < 0) {
          *(byte *)(iVar2 + 0x28) = *(byte *)(iVar2 + 0x28) & 0xfe;
        }
        else {
          FUN_0800c030(iVar2);
        }
      }
    }
    iVar2 = FUN_0800c83a(*puVar1,&local_20,0);
  } while( true );
}



/* FUN 0x0800b260 FUN_0800b260 */

void FUN_0800b260(void)

{
  if (**(int **)(DAT_0800b280 + 0x34) != 0) {
    *(undefined4 *)(DAT_0800b280 + 0x28) =
         *(undefined4 *)(*(int *)(*(int *)(*(int *)(DAT_0800b280 + 0x34) + 0xc) + 0xc) + 4);
    return;
  }
  *(undefined4 *)(DAT_0800b280 + 0x28) = 0xffffffff;
  return;
}



/* FUN 0x0800b284 FUN_0800b284 */

uint FUN_0800b284(undefined4 *param_1)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = FUN_0800ca6c();
  iVar1 = DAT_0800b2ac;
  if (uVar2 < *(uint *)(DAT_0800b2ac + 8)) {
    FUN_0800b2b0();
    *param_1 = 1;
  }
  else {
    *param_1 = 0;
  }
  *(uint *)(iVar1 + 8) = uVar2;
  return uVar2;
}



/* FUN 0x0800b2b0 FUN_0800b2b0 */

void FUN_0800b2b0(void)

{
  int iVar1;
  int iVar2;
  uint *puVar3;
  uint uVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  
  iVar1 = DAT_0800b318;
  iVar2 = **(int **)(DAT_0800b318 + 0xc);
  do {
    if (iVar2 == 0) {
      uVar5 = *(undefined4 *)(iVar1 + 0xc);
      *(undefined4 *)(iVar1 + 0xc) = *(undefined4 *)(iVar1 + 0x10);
      *(undefined4 *)(iVar1 + 0x10) = uVar5;
      return;
    }
    puVar3 = *(uint **)(*(int *)(iVar1 + 0xc) + 0xc);
    uVar7 = *puVar3;
    uVar6 = puVar3[3];
    FUN_0800bf2c(uVar6 + 4);
    (**(code **)(uVar6 + 0x20))(uVar6);
    if ((int)((uint)*(byte *)(uVar6 + 0x28) << 0x1d) < 0) {
      uVar4 = *(int *)(uVar6 + 0x18) + uVar7;
      if (uVar7 < uVar4) {
        *(uint *)(uVar6 + 4) = uVar4;
        *(uint *)(uVar6 + 0x10) = uVar6;
        FUN_0800bfb0(*(undefined4 *)(iVar1 + 0xc),uVar6 + 4);
      }
      else {
        iVar2 = FUN_0800cd80(uVar6,0,uVar7,0,0);
        if (iVar2 == 0) {
          disableIRQinterrupts();
          do {
                    /* WARNING: Do nothing block with infinite loop */
          } while( true );
        }
      }
    }
    iVar2 = **(int **)(iVar1 + 0xc);
  } while( true );
}



/* FUN 0x0800b330 FUN_0800b330 */

undefined4 FUN_0800b330(int param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if (param_1 == 0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if (((*(int *)(param_1 + 0x14) == DAT_0800b358) && (*(int *)(param_1 + 0x28) != DAT_0800b35c)) &&
     (*(int *)(param_1 + 0x28) == 0)) {
    uVar1 = 1;
  }
  return uVar1;
}



/* FUN 0x0800b374 FUN_0800b374 */

void FUN_0800b374(int param_1)

{
  int iVar1;
  char cVar2;
  
  FUN_0800bffc();
  cVar2 = *(char *)(param_1 + 0x45);
  if ('\0' < cVar2) {
    do {
      if (*(int *)(param_1 + 0x24) == 0) break;
      iVar1 = FUN_0800cba0(param_1 + 0x24);
      if (iVar1 != 0) {
        FUN_0800c16c();
      }
      cVar2 = cVar2 + -1;
    } while ('\0' < cVar2);
  }
  *(undefined1 *)(param_1 + 0x45) = 0xff;
  FUN_0800c014();
  FUN_0800bffc();
  cVar2 = *(char *)(param_1 + 0x44);
  if ('\0' < cVar2) {
    do {
      if (*(int *)(param_1 + 0x10) == 0) break;
      iVar1 = FUN_0800cba0(param_1 + 0x10);
      if (iVar1 != 0) {
        FUN_0800c16c();
      }
      cVar2 = cVar2 + -1;
    } while ('\0' < cVar2);
  }
  *(undefined1 *)(param_1 + 0x44) = 0xff;
  FUN_0800c014();
  return;
}



/* FUN 0x0800b3e8 FUN_0800b3e8 */

uint FUN_0800b3e8(uint param_1)

{
  int *piVar1;
  int *piVar2;
  int *piVar3;
  int *piVar4;
  uint uVar5;
  int *piVar6;
  uint uVar7;
  uint uVar8;
  
  uVar8 = 0;
  FUN_0800c380();
  piVar1 = DAT_0800b49c;
  if (*DAT_0800b49c == 0) {
    FUN_0800ae0c();
  }
  if ((param_1 & piVar1[5]) == 0) {
    uVar7 = param_1;
    if (((param_1 != 0) && (uVar7 = param_1 + 8, (param_1 & 7) != 0)) &&
       (uVar7 = (8 - (param_1 & 7)) + uVar7, (uVar7 & 7) != 0)) {
      disableIRQinterrupts();
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
    if ((uVar7 != 0) && (uVar7 <= (uint)piVar1[1])) {
      piVar2 = DAT_0800b4a0;
      piVar3 = (int *)*DAT_0800b4a0;
      do {
        piVar6 = piVar3;
        piVar4 = piVar2;
        if (uVar7 <= (uint)piVar6[1]) break;
        piVar2 = piVar6;
        piVar3 = (int *)*piVar6;
      } while ((int *)*piVar6 != (int *)0x0);
      if (piVar6 != (int *)*piVar1) {
        uVar8 = *piVar4 + 8;
        *piVar4 = *piVar6;
        if (0x10 < piVar6[1] - uVar7) {
          if (((int)piVar6 + uVar7 & 7) != 0) {
            disableIRQinterrupts();
            do {
                    /* WARNING: Do nothing block with infinite loop */
            } while( true );
          }
          *(uint *)((int)piVar6 + uVar7 + 4) = piVar6[1] - uVar7;
          piVar6[1] = uVar7;
          FUN_0800afcc();
        }
        uVar5 = piVar6[1];
        uVar7 = piVar1[1] - uVar5;
        piVar1[1] = uVar7;
        if (uVar7 < (uint)piVar1[2]) {
          piVar1[2] = uVar7;
        }
        piVar6[1] = uVar5 | piVar1[5];
        *piVar6 = 0;
        piVar1[3] = piVar1[3] + 1;
      }
    }
  }
  FUN_0800cc0c();
  if ((uVar8 & 7) == 0) {
    return uVar8;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* FUN 0x0800b4a4 FUN_0800b4a4 */

undefined4 FUN_0800b4a4(int param_1)

{
  undefined4 uVar1;
  
  if (param_1 != 0) {
    FUN_0800bffc();
    uVar1 = *(undefined4 *)(param_1 + 0x1c);
    FUN_0800c014();
    return uVar1;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* FUN 0x0800b4c0 FUN_0800b4c0 */

int FUN_0800b4c0(int param_1,undefined4 param_2,undefined4 param_3)

{
  *(undefined4 *)(param_1 + -4) = 0x1000000;
  *(undefined4 *)(param_1 + -8) = param_2;
  *(undefined4 *)(param_1 + -0xc) = DAT_0800b4dc;
  *(undefined4 *)(param_1 + -0x20) = param_3;
  return param_1 + -0x40;
}



/* FUN 0x0800b4e0 FUN_0800b4e0 */

undefined4 FUN_0800b4e0(uint *param_1)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  
  iVar1 = DAT_0800b534;
  *(undefined4 *)(DAT_0800b534 + 8) = 0;
  iVar5 = 0;
  *(undefined4 *)(iVar1 + 0xc) = 0;
  FUN_0800bb0c();
  FUN_0800bac4();
  FUN_0800ba84();
  FUN_0800bac4();
  FUN_0800bae8();
  FUN_0800ba44();
  FUN_0800a794(0x17);
  uVar3 = FUN_0800a39c();
  *param_1 = ~uVar3 & 1;
  iVar2 = DAT_0800b538;
  do {
    iVar5 = iVar5 + 1;
    if (iVar2 < iVar5) {
      *(undefined4 *)(iVar1 + 0xc) = 1;
      return 0;
    }
    iVar4 = FUN_0800a39c();
  } while (iVar4 == 0);
  return 1;
}



/* FUN 0x0800b53c FUN_0800b53c */

ulonglong FUN_0800b53c(uint *param_1)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  undefined4 uVar7;
  
  iVar1 = DAT_0800b5a4;
  *(undefined4 *)(DAT_0800b5a4 + 0xc) = 0;
  uVar7 = 1;
  iVar6 = 0;
  *(undefined4 *)(iVar1 + 0x10) = 0;
  FUN_0800ba64();
  FUN_0800bb2c();
  iVar2 = DAT_0800b5a8;
  do {
    iVar6 = iVar6 + 1;
    if (iVar2 < iVar6) {
      uVar7 = 0;
      *(undefined4 *)(iVar1 + 0xc) = 1;
      break;
    }
    iVar5 = FUN_0800a3ac();
  } while (iVar5 == 1);
  FUN_0800a7a2(0x32);
  uVar3 = FUN_0800a3ac();
  uVar4 = ~uVar3 & 1;
  iVar6 = 0;
  *param_1 = uVar4;
  do {
    iVar6 = iVar6 + 1;
    if (iVar2 < iVar6) {
      uVar7 = 0;
      *(undefined4 *)(iVar1 + 0x10) = 1;
      break;
    }
    iVar5 = FUN_0800a3ac();
  } while (iVar5 == 0);
  *param_1 = uVar4;
  return CONCAT44(~uVar3,uVar7) & 0x1ffffffff;
}



/* FUN 0x0800b5ac FUN_0800b5ac */

undefined4 FUN_0800b5ac(undefined1 *param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  undefined1 uVar4;
  uint uVar5;
  undefined4 uVar6;
  int local_18;
  
  uVar6 = 1;
  uVar5 = 0;
  uVar3 = 7;
  local_18 = param_4;
  do {
    uVar4 = (undefined1)uVar5;
    iVar1 = FUN_0800b4e0(&local_18);
    if (iVar1 == 0) {
      uVar6 = 0;
      break;
    }
    uVar2 = (local_18 << (uVar3 & 0xff)) + uVar5;
    uVar5 = uVar2 & 0xff;
    uVar4 = (undefined1)uVar2;
    uVar3 = uVar3 - 1;
  } while (-1 < (int)uVar3);
  *param_1 = uVar4;
  return uVar6;
}



/* FUN 0x0800b5d6 FUN_0800b5d6 */

undefined4 FUN_0800b5d6(undefined1 *param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  undefined1 uVar4;
  uint uVar5;
  undefined4 uVar6;
  int local_18;
  
  uVar6 = 1;
  uVar5 = 0;
  uVar3 = 7;
  local_18 = param_4;
  do {
    uVar4 = (undefined1)uVar5;
    iVar1 = FUN_0800b53c(&local_18);
    if (iVar1 == 0) {
      uVar6 = 0;
      break;
    }
    uVar2 = (local_18 << (uVar3 & 0xff)) + uVar5;
    uVar5 = uVar2 & 0xff;
    uVar4 = (undefined1)uVar2;
    uVar3 = uVar3 - 1;
  } while (-1 < (int)uVar3);
  *param_1 = uVar4;
  return uVar6;
}



/* FUN 0x0800b600 FUN_0800b600 */

void FUN_0800b600(void)

{
  int iVar1;
  undefined4 local_58 [3];
  undefined4 local_4c;
  undefined4 local_48;
  undefined4 local_44;
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 local_38;
  undefined4 local_34;
  undefined4 local_30;
  undefined4 local_2c;
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  
  FUN_080001e6(local_58,0x38);
  local_20 = 0;
  local_1c = 0;
  local_18 = 0;
  local_14 = 0;
  FUN_08005048(0x200);
  local_58[0] = 10;
  local_4c = 0x100;
  local_44 = 0x40;
  local_40 = 1;
  local_30 = 8;
  local_2c = 0x20000;
  local_3c = 2;
  local_28 = 0x2000000;
  local_38 = 2;
  local_48 = 0;
  local_24 = 0x20000000;
  local_34 = 0;
  iVar1 = FUN_08005528(local_58);
  if (iVar1 != 0) {
    FUN_08003e90();
  }
  local_20 = 7;
  local_18 = 0;
  local_1c = 2;
  local_14 = 0;
  iVar1 = FUN_080052e4(&local_20,2);
  if (iVar1 != 0) {
    FUN_08003e90();
  }
  return;
}



/* FUN 0x0800b678 FUN_0800b678 */

void FUN_0800b678(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 in_r3;
  int iVar3;
  byte bVar4;
  
  FUN_08004e9e(0x50000000,8,1,in_r3,in_r3);
  FUN_0800a7b0(10);
  iVar1 = DAT_0800b7e4;
  FUN_08004e9e(DAT_0800b7e4,0x200);
  FUN_0800a7b0(10);
  FUN_08004e9e(iVar1,0x200,0);
  FUN_0800a7a2(0x26c);
  FUN_08004e9e(iVar1,0x200,1);
  FUN_0800a7a2(DAT_0800b7e8);
  bVar4 = 0;
  iVar3 = iVar1 >> 0x13;
  do {
    FUN_08004e9e(iVar1,0x200,0);
    FUN_0800a7a2(iVar3);
    FUN_08004e9e(iVar1,0x200,1);
    FUN_0800a7a2(iVar3);
    bVar4 = bVar4 + 1;
  } while (bVar4 < 5);
  FUN_08004e9e(iVar1,0x200,1);
  uVar2 = DAT_0800b7e8;
  FUN_0800a7a2(DAT_0800b7e8);
  FUN_08004e9e(iVar1,0x200,0);
  FUN_0800a7b0(0x28);
  FUN_08004e9e(iVar1,0x200,1);
  FUN_0800a7b0(1);
  FUN_08004e9e(iVar1,0x200,0);
  FUN_0800a7a2(0x26c);
  FUN_08004e9e(iVar1,0x200,1);
  FUN_0800a7a2(uVar2);
  bVar4 = 0;
  do {
    FUN_08004e9e(iVar1,0x200,0);
    FUN_0800a7a2(iVar3);
    FUN_08004e9e(iVar1,0x200,1);
    FUN_0800a7a2(iVar3);
    bVar4 = bVar4 + 1;
  } while (bVar4 < 7);
  FUN_08004e9e(iVar1,0x200,1);
  uVar2 = DAT_0800b7e8;
  FUN_0800a7a2(DAT_0800b7e8);
  FUN_0800a7b0(1);
  FUN_08004e9e(iVar1,0x200,0);
  FUN_0800a7a2(0x26c);
  FUN_08004e9e(iVar1,0x200,1);
  FUN_0800a7a2(uVar2);
  bVar4 = 0;
  do {
    FUN_08004e9e(iVar1,0x200,0);
    FUN_0800a7a2(iVar3);
    FUN_08004e9e(iVar1,0x200,1);
    FUN_0800a7a2(iVar3);
    bVar4 = bVar4 + 1;
  } while (bVar4 < 7);
  FUN_08004e9e(iVar1,0x200,1);
  FUN_0800a7a2(DAT_0800b7e8);
  return;
}



/* FUN 0x0800ba44 FUN_0800ba44 */

void FUN_0800ba44(void)

{
  int iVar1;
  
  iVar1 = DAT_0800ba5c;
  if (*(int *)(DAT_0800ba5c + 4) != 0) {
    *(undefined4 *)(DAT_0800ba5c + 4) = 0;
    FUN_08004d30(DAT_0800ba60,iVar1);
  }
  return;
}



/* FUN 0x0800ba64 FUN_0800ba64 */

void FUN_0800ba64(void)

{
  int iVar1;
  
  iVar1 = DAT_0800ba80;
  if (*(int *)(DAT_0800ba80 + 4) != 0) {
    *(undefined4 *)(DAT_0800ba80 + 4) = 0;
    FUN_08004d30(0x50000000,iVar1);
  }
  return;
}



/* FUN 0x0800ba84 FUN_0800ba84 */

void FUN_0800ba84(void)

{
  int iVar1;
  
  iVar1 = DAT_0800ba9c;
  if (*(int *)(DAT_0800ba9c + 4) != 1) {
    *(undefined4 *)(DAT_0800ba9c + 4) = 1;
    FUN_08004d30(DAT_0800baa0,iVar1);
  }
  return;
}



/* FUN 0x0800baa4 FUN_0800baa4 */

void FUN_0800baa4(void)

{
  int iVar1;
  
  iVar1 = DAT_0800bac0;
  if (*(int *)(DAT_0800bac0 + 4) != 1) {
    *(undefined4 *)(DAT_0800bac0 + 4) = 1;
    FUN_08004d30(0x50000000,iVar1);
  }
  return;
}



/* FUN 0x0800bac4 FUN_0800bac4 */

void FUN_0800bac4(void)

{
  FUN_08004e9e(DAT_0800bad4,4,1);
  return;
}



/* FUN 0x0800bad8 FUN_0800bad8 */

void FUN_0800bad8(void)

{
  FUN_08004e9e(0x50000000,8,1);
  return;
}



/* FUN 0x0800bae8 FUN_0800bae8 */

void FUN_0800bae8(void)

{
  FUN_08004e9e(DAT_0800baf8,4,0);
  return;
}



/* FUN 0x0800bafc FUN_0800bafc */

void FUN_0800bafc(void)

{
  FUN_08004e9e(0x50000000,8,0);
  return;
}



/* FUN 0x0800bb0c FUN_0800bb0c */

void FUN_0800bb0c(void)

{
  int iVar1;
  
  iVar1 = DAT_0800bb24;
  if (*(int *)(DAT_0800bb24 + 8) != 1) {
    *(undefined4 *)(DAT_0800bb24 + 8) = 1;
    FUN_08004d30(DAT_0800bb28,iVar1);
  }
  return;
}



/* FUN 0x0800bb2c FUN_0800bb2c */

void FUN_0800bb2c(void)

{
  int iVar1;
  
  iVar1 = DAT_0800bb48;
  if (*(int *)(DAT_0800bb48 + 8) != 1) {
    *(undefined4 *)(DAT_0800bb48 + 8) = 1;
    FUN_08004d30(0x50000000,iVar1);
  }
  return;
}



/* FUN 0x0800bb4c FUN_0800bb4c */

void FUN_0800bb4c(void)

{
  if ((*(char *)(DAT_0800bb6c + 2) == '\x04') || (*(char *)(DAT_0800bb6c + 2) == '\x03')) {
    *(byte *)(DAT_0800bb70 + 0xc) = *(byte *)(DAT_0800bb70 + 0xc) ^ 1;
    FUN_08006b80();
  }
  return;
}



/* FUN 0x0800bb74 FUN_0800bb74 */

void FUN_0800bb74(void)

{
  int iVar1;
  
  iVar1 = DAT_0800bb8c;
  FUN_0800ab26(*(undefined4 *)(DAT_0800bb8c + 0x14));
  FUN_0800aaf0(*(undefined4 *)(iVar1 + 0x14),1000);
  return;
}



/* FUN 0x0800be74 FUN_0800be74 */

undefined4 FUN_0800be74(char *param_1)

{
  if (((*param_1 == 'd') || (*param_1 == 'D')) && ((param_1[1] == 'e' || (param_1[1] == 'E')))) {
    return 1;
  }
  return 0;
}



/* FUN 0x0800be90 FUN_0800be90 */

void FUN_0800be90(void)

{
  FUN_080099e8(5,3);
  FUN_080099e8(6,0xc1);
  FUN_080099e8(3,0xa6);
  FUN_0800a7b0(0x1e);
  FUN_080099e8(7,3);
  return;
}



/* FUN 0x0800beba FUN_0800beba */

void FUN_0800beba(void)

{
  FUN_080099e8(7,0x20);
  FUN_080099e8(6,0x81);
  FUN_080099e8(5,3);
  FUN_080099e8(3,0xff);
  return;
}



/* FUN 0x0800bede FUN_0800bede */

void FUN_0800bede(void)

{
  FUN_080099e8(5,3);
  FUN_080099e8(6,0xc1);
  FUN_080099e8(4,0xa6);
  FUN_0800a7b0(0x1e);
  FUN_080099e8(7,5);
  return;
}



/* FUN 0x0800bf08 FUN_0800bf08 */

void FUN_0800bf08(void)

{
  FUN_080099e8(7,0x20);
  FUN_080099e8(6,0x81);
  FUN_080099e8(5,3);
  FUN_080099e8(4,0xff);
  return;
}



/* FUN 0x0800bf2c FUN_0800bf2c */

int FUN_0800bf2c(int param_1)

{
  int *piVar1;
  
  piVar1 = *(int **)(param_1 + 0x10);
  *(undefined4 *)(*(int *)(param_1 + 4) + 8) = *(undefined4 *)(param_1 + 8);
  *(undefined4 *)(*(int *)(param_1 + 8) + 4) = *(undefined4 *)(param_1 + 4);
  if (piVar1[1] == param_1) {
    piVar1[1] = *(int *)(param_1 + 8);
  }
  *(undefined4 *)(param_1 + 0x10) = 0;
  *piVar1 = *piVar1 + -1;
  return *piVar1;
}



/* FUN 0x0800bf54 FUN_0800bf54 */

void FUN_0800bf54(undefined4 *param_1,undefined4 *param_2,undefined4 *param_3)

{
  *param_1 = DAT_0800bf64;
  *param_2 = DAT_0800bf68;
  *param_3 = 0x80;
  return;
}



/* FUN 0x0800bf6c FUN_0800bf6c */

void FUN_0800bf6c(undefined4 *param_1,undefined4 *param_2,undefined4 *param_3)

{
  *param_1 = DAT_0800bf7c;
  *param_2 = DAT_0800bf80;
  *param_3 = 0x100;
  return;
}



/* FUN 0x0800bf94 FUN_0800bf94 */

void FUN_0800bf94(undefined4 *param_1)

{
  undefined4 *puVar1;
  
  puVar1 = param_1 + 2;
  param_1[1] = puVar1;
  param_1[2] = 0xffffffff;
  param_1[3] = puVar1;
  param_1[4] = puVar1;
  *param_1 = 0;
  return;
}



/* FUN 0x0800bfaa FUN_0800bfaa */

void FUN_0800bfaa(int param_1)

{
  *(undefined4 *)(param_1 + 0x10) = 0;
  return;
}



/* FUN 0x0800bfb0 FUN_0800bfb0 */

void FUN_0800bfb0(int *param_1,uint *param_2)

{
  uint *puVar1;
  uint *puVar2;
  uint uVar3;
  
  if (*param_2 == 0xffffffff) {
    puVar2 = (uint *)param_1[4];
  }
  else {
    puVar1 = (uint *)(param_1 + 2);
    do {
      puVar2 = puVar1;
      puVar1 = (uint *)puVar2[1];
    } while (*(uint *)puVar2[1] <= *param_2);
  }
  uVar3 = puVar2[1];
  param_2[1] = uVar3;
  *(uint **)(uVar3 + 8) = param_2;
  param_2[2] = (uint)puVar2;
  puVar2[1] = (uint)param_2;
  param_2[4] = (uint)param_1;
  *param_1 = *param_1 + 1;
  return;
}



/* FUN 0x0800bfe2 FUN_0800bfe2 */

void FUN_0800bfe2(int *param_1,int param_2)

{
  int iVar1;
  
  iVar1 = param_1[1];
  *(int *)(param_2 + 4) = iVar1;
  *(undefined4 *)(param_2 + 8) = *(undefined4 *)(iVar1 + 8);
  *(int *)(*(int *)(iVar1 + 8) + 4) = param_2;
  *(int *)(iVar1 + 8) = param_2;
  *(int **)(param_2 + 0x10) = param_1;
  *param_1 = *param_1 + 1;
  return;
}



/* FUN 0x0800bffc FUN_0800bffc */

void FUN_0800bffc(void)

{
  disableIRQinterrupts();
  *DAT_0800c010 = *DAT_0800c010 + 1;
  DataSynchronizationBarrier(0xf);
  InstructionSynchronizationBarrier(0xf);
  return;
}



/* FUN 0x0800c014 FUN_0800c014 */

void FUN_0800c014(void)

{
  int iVar1;
  
  if (*DAT_0800c02c != 0) {
    iVar1 = *DAT_0800c02c + -1;
    *DAT_0800c02c = iVar1;
    if (iVar1 == 0) {
      enableIRQinterrupts();
    }
    return;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* FUN 0x0800c030 FUN_0800c030 */

void FUN_0800c030(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_0800c074;
  if (param_1 != 0) {
    if ((*(uint *)(param_1 + -4) & *(uint *)(DAT_0800c074 + 0x14)) == 0) {
      disableIRQinterrupts();
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
    if (*(int *)(param_1 + -8) != 0) {
      disableIRQinterrupts();
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
    *(uint *)(param_1 + -4) = *(uint *)(param_1 + -4) & ~*(uint *)(DAT_0800c074 + 0x14);
    FUN_0800c380();
    *(int *)(iVar1 + 4) = *(int *)(param_1 + -4) + *(int *)(iVar1 + 4);
    FUN_0800afcc((int *)(param_1 + -8));
    *(int *)(iVar1 + 0x10) = *(int *)(iVar1 + 0x10) + 1;
    FUN_0800cc0c();
  }
  return;
}



/* FUN 0x0800c078 FUN_0800c078 */

void FUN_0800c078(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_0800c098;
  *(undefined4 *)(DAT_0800c098 + 0x10) = 0;
  *(undefined4 *)(iVar1 + 0x18) = 0;
  iVar2 = FUN_08000160(*DAT_0800c09c,1000);
  *(int *)(iVar1 + 0x14) = iVar2 + -1;
  *(undefined4 *)(iVar1 + 0x10) = 7;
  return;
}



/* FUN 0x0800c0a0 FUN_0800c0a0 */

void FUN_0800c0a0(void)

{
  *(undefined4 *)(DAT_0800c0b4 + 4) = 0x10000000;
  DataSynchronizationBarrier(0xf);
  InstructionSynchronizationBarrier(0xf);
  return;
}



/* FUN 0x0800c0b8 FUN_0800c0b8 */

void FUN_0800c0b8(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = DAT_0800c0dc;
  uVar2 = 0;
  do {
    if (*(int *)(DAT_0800c0dc + uVar2 * 8) == 0) {
      *(undefined4 *)(DAT_0800c0dc + uVar2 * 8) = param_2;
      *(undefined4 *)(uVar2 * 8 + iVar1 + 4) = param_1;
      return;
    }
    uVar2 = uVar2 + 1;
  } while (uVar2 < 8);
  return;
}



/* FUN 0x0800c0e0 FUN_0800c0e0 */

void FUN_0800c0e0(int param_1,undefined4 param_2,undefined4 param_3)

{
  FUN_0800bffc();
  if (*(char *)(param_1 + 0x44) == -1) {
    *(undefined1 *)(param_1 + 0x44) = 0;
  }
  if (*(char *)(param_1 + 0x45) == -1) {
    *(undefined1 *)(param_1 + 0x45) = 0;
  }
  FUN_0800c014();
  if (*(int *)(param_1 + 0x38) == 0) {
    FUN_0800c19c(param_1 + 0x24,param_2,param_3);
  }
  FUN_0800b374(param_1);
  return;
}



/* FUN 0x0800c128 FUN_0800c128 */

void FUN_0800c128(int param_1)

{
  int iVar1;
  undefined4 extraout_r2;
  
  iVar1 = 0;
  if (param_1 != 0) {
    if (*(int *)(DAT_0800c158 + 0x30) != 0) {
      disableIRQinterrupts();
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
    FUN_0800c380();
    FUN_0800abb0(extraout_r2,0);
    iVar1 = FUN_0800cc0c();
  }
  if (iVar1 == 0) {
    FUN_0800c0a0();
  }
  return;
}



/* FUN 0x0800c15c FUN_0800c15c */

void FUN_0800c15c(undefined4 *param_1)

{
  int iVar1;
  
  iVar1 = DAT_0800c168;
  *param_1 = *(undefined4 *)(DAT_0800c168 + 0x20);
  param_1[1] = *(undefined4 *)(iVar1 + 0xc);
  return;
}



/* FUN 0x0800c16c FUN_0800c16c */

void FUN_0800c16c(void)

{
  *(undefined4 *)(DAT_0800c174 + 0x1c) = 1;
  return;
}



/* FUN 0x0800c178 FUN_0800c178 */

void FUN_0800c178(int param_1,undefined4 param_2)

{
  if (param_1 != 0) {
    FUN_0800bfb0(param_1,*DAT_0800c198 + 0x18);
    FUN_0800abb0(param_2,1);
    return;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* FUN 0x0800c19c FUN_0800c19c */

void FUN_0800c19c(int param_1,undefined4 param_2,int param_3)

{
  if (param_1 != 0) {
    FUN_0800bfe2(param_1,*DAT_0800c1c8 + 0x18);
    if (param_3 != 0) {
      param_2 = 0xffffffff;
    }
    FUN_0800abb0(param_2,param_3);
    return;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* FUN 0x0800c1cc FUN_0800c1cc */

void FUN_0800c1cc(uint *param_1,uint param_2)

{
  int *piVar1;
  uint uVar2;
  uint uVar3;
  
  piVar1 = DAT_0800c220;
  if (DAT_0800c220[0xc] == 0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  *param_1 = param_2 | 0x80000000;
  uVar3 = param_1[3];
  if (uVar3 != 0) {
    FUN_0800bf2c();
    FUN_0800bf2c(uVar3 + 4);
    uVar2 = *(uint *)(uVar3 + 0x2c);
    if ((uint)piVar1[4] < uVar2) {
      piVar1[4] = uVar2;
    }
    FUN_0800bfe2(uVar2 * 0x14 + DAT_0800c224,uVar3 + 4);
    if (*(uint *)(*piVar1 + 0x2c) < *(uint *)(uVar3 + 0x2c)) {
      piVar1[7] = 1;
    }
    return;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* FUN 0x0800c228 FUN_0800c228 */

void FUN_0800c228(int param_1)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  
  piVar1 = DAT_0800c27c;
  if (param_1 != 0) {
    if (param_1 != *DAT_0800c27c) {
      FUN_0800bffc();
      iVar2 = FUN_0800b330(param_1);
      if (iVar2 != 0) {
        FUN_0800bf2c(param_1 + 4);
        uVar3 = *(uint *)(param_1 + 0x2c);
        if ((uint)piVar1[4] < uVar3) {
          piVar1[4] = uVar3;
        }
        FUN_0800bfe2(uVar3 * 0x14 + DAT_0800c280,param_1 + 4);
        if (*(uint *)(*piVar1 + 0x2c) <= *(uint *)(param_1 + 0x2c)) {
          FUN_0800c0a0();
        }
      }
      FUN_0800c014();
    }
    return;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* FUN 0x0800c284 FUN_0800c284 */

void FUN_0800c284(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  
  local_10 = 0;
  local_14 = 0;
  FUN_0800bf54(&local_10,&local_14,&local_18);
  iVar2 = FUN_0800ca06(DAT_0800c2f0,&DAT_0800c2e8,local_18,0,0,local_14,local_10);
  iVar1 = DAT_0800c2f4;
  *(int *)(DAT_0800c2f4 + 0x2c) = iVar2;
  uVar3 = (uint)(iVar2 != 0);
  if (uVar3 == 1) {
    uVar3 = FUN_0800cd20();
  }
  if (uVar3 == 1) {
    disableIRQinterrupts();
    *(undefined4 *)(iVar1 + 0x28) = 0xffffffff;
    *(undefined4 *)(iVar1 + 0x14) = 1;
    *(undefined4 *)(iVar1 + 0xc) = 0;
    FUN_0800c57c();
  }
  else if (uVar3 == 0xffffffff) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  return;
}



/* FUN 0x0800c2f8 FUN_0800c2f8 */

void FUN_0800c2f8(int param_1)

{
  int *piVar1;
  
  FUN_0800bffc();
  piVar1 = DAT_0800c378;
  if (param_1 == 0) {
    param_1 = *DAT_0800c378;
  }
  FUN_0800bf2c(param_1 + 4);
  if (*(int *)(param_1 + 0x28) != 0) {
    FUN_0800bf2c(param_1 + 0x18);
  }
  FUN_0800bfe2(DAT_0800c37c,param_1 + 4);
  if (*(char *)(param_1 + 0x58) == '\x01') {
    *(undefined1 *)(param_1 + 0x58) = 0;
  }
  FUN_0800c014();
  if (piVar1[5] != 0) {
    FUN_0800bffc();
    FUN_0800b260();
    FUN_0800c014();
  }
  if (param_1 == *piVar1) {
    if (piVar1[5] == 0) {
      if (*DAT_0800c37c == piVar1[2]) {
        *piVar1 = 0;
        return;
      }
      FUN_0800c390();
      return;
    }
    if (piVar1[0xc] != 0) {
      disableIRQinterrupts();
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
    FUN_0800c0a0();
  }
  return;
}



/* FUN 0x0800c380 FUN_0800c380 */

void FUN_0800c380(void)

{
  *(int *)(DAT_0800c38c + 0x30) = *(int *)(DAT_0800c38c + 0x30) + 1;
  return;
}



/* FUN 0x0800c390 FUN_0800c390 */

void FUN_0800c390(void)

{
  undefined4 *puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  puVar1 = DAT_0800c3f0;
  if (DAT_0800c3f0[0xc] != 0) {
    DAT_0800c3f0[7] = 1;
    return;
  }
  DAT_0800c3f0[7] = 0;
  iVar2 = puVar1[4];
  iVar3 = *(int *)(DAT_0800c3f4 + iVar2 * 0x14);
  while( true ) {
    if (iVar3 != 0) {
      iVar3 = iVar2 * 0x14 + DAT_0800c3f4;
      iVar4 = *(int *)(*(int *)(iVar3 + 4) + 4);
      *(int *)(iVar3 + 4) = iVar4;
      if (iVar4 == iVar3 + 8) {
        *(undefined4 *)(iVar3 + 4) = *(undefined4 *)(iVar4 + 4);
      }
      *puVar1 = *(undefined4 *)(*(int *)(iVar3 + 4) + 0xc);
      puVar1[4] = iVar2;
      return;
    }
    if (iVar2 == 0) break;
    iVar2 = iVar2 + -1;
    iVar3 = *(int *)(DAT_0800c3f4 + iVar2 * 0x14);
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* FUN 0x0800c3f8 FUN_0800c3f8 */

uint FUN_0800c3f8(uint param_1)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 0;
  uVar1 = 0;
  do {
    uVar2 = uVar2 ^ param_1 >> (uVar1 & 0xff) & 1;
    uVar1 = uVar1 + 1;
  } while ((int)uVar1 < 8);
  return uVar2;
}



/* FUN 0x0800c412 FUN_0800c412 */

uint FUN_0800c412(uint param_1)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 0;
  uVar1 = 0;
  do {
    uVar2 = uVar2 ^ param_1 >> (uVar1 & 0xff) & 1;
    uVar1 = uVar1 + 1;
  } while ((int)uVar1 < 8);
  return uVar2;
}



/* FUN 0x0800c42c FUN_0800c42c */

void FUN_0800c42c(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 local_10;
  
  local_10 = param_4;
  FUN_0800b4e0(&local_10);
  *param_1 = local_10;
  return;
}



/* FUN 0x0800c43c FUN_0800c43c */

void FUN_0800c43c(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 local_10;
  
  local_10 = param_4;
  FUN_0800b53c(&local_10);
  *param_1 = local_10;
  return;
}



/* FUN 0x0800c44c FUN_0800c44c */

uint FUN_0800c44c(uint *param_1,uint param_2)

{
  uint uVar1;
  
  if (param_1 == (uint *)0x0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if (param_2 >> 0x18 != 0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  FUN_0800bffc();
  uVar1 = *param_1;
  *param_1 = uVar1 & ~param_2;
  FUN_0800c014();
  return uVar1;
}



/* FUN 0x0800c478 FUN_0800c478 */

void FUN_0800c478(undefined4 param_1,undefined4 param_2)

{
  FUN_0800ce0c(DAT_0800c488,param_1,param_2,0);
  return;
}



/* FUN 0x0800c48c FUN_0800c48c */

undefined4 * FUN_0800c48c(void)

{
  undefined4 *puVar1;
  
  puVar1 = (undefined4 *)FUN_0800b3e8(0x20);
  if (puVar1 != (undefined4 *)0x0) {
    *puVar1 = 0;
    FUN_0800bf94(puVar1 + 1);
    *(undefined1 *)(puVar1 + 7) = 0;
  }
  return puVar1;
}



/* FUN 0x0800c4aa FUN_0800c4aa */

undefined4 * FUN_0800c4aa(undefined4 *param_1)

{
  if (param_1 != (undefined4 *)0x0) {
    *param_1 = 0;
    FUN_0800bf94(param_1 + 1);
    *(undefined1 *)(param_1 + 7) = 1;
    return param_1;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* FUN 0x0800c4cc FUN_0800c4cc */

undefined4 FUN_0800c4cc(undefined4 *param_1)

{
  undefined4 uVar1;
  
  FUN_080000f4();
  uVar1 = *param_1;
  FUN_080000fc();
  return uVar1;
}



/* FUN 0x0800c4de FUN_0800c4de */

uint FUN_0800c4de(uint *param_1,uint param_2)

{
  bool bVar1;
  uint *puVar2;
  uint *puVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  uVar6 = 0;
  if (param_1 == (uint *)0x0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if (param_2 >> 0x18 != 0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  FUN_0800c380();
  *param_1 = *param_1 | param_2;
  puVar3 = (uint *)param_1[4];
  while (puVar2 = puVar3, puVar2 != param_1 + 3) {
    puVar3 = (uint *)puVar2[1];
    bVar1 = false;
    uVar5 = *puVar2 & 0xff000000;
    uVar4 = *puVar2 & 0xffffff;
    if ((int)(uVar5 << 5) < 0) {
      if ((uVar4 & ~*param_1) == 0) {
        bVar1 = true;
      }
    }
    else if ((*param_1 & uVar4) != 0) {
      bVar1 = true;
    }
    if (bVar1) {
      if ((int)(uVar5 << 7) < 0) {
        uVar6 = uVar6 | uVar4;
      }
      FUN_0800c1cc(puVar2,*param_1 | 0x2000000);
    }
  }
  *param_1 = *param_1 & ~uVar6;
  FUN_0800cc0c();
  return *param_1;
}



/* FUN 0x0800c568 FUN_0800c568 */

void FUN_0800c568(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  FUN_0800ce0c(DAT_0800c578,param_1,param_2,param_3);
  return;
}



/* FUN 0x0800c57c FUN_0800c57c */

undefined4 FUN_0800c57c(void)

{
  int iVar1;
  
  iVar1 = DAT_0800c5a4;
  *(uint *)(DAT_0800c5a4 + 0x20) = *(uint *)(DAT_0800c5a4 + 0x20) | 0xff0000;
  *(uint *)(iVar1 + 0x20) = *(uint *)(iVar1 + 0x20) | 0xff000000;
  FUN_0800c078();
  *DAT_0800c5a8 = 0;
  FUN_080000cc();
  return 0;
}



/* FUN 0x0800c5ac FUN_0800c5ac */

void FUN_0800c5ac(void)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = FUN_080000f4();
  iVar2 = FUN_0800ca78();
  if (iVar2 != 0) {
    *(undefined4 *)(DAT_0800c5cc + 4) = 0x10000000;
  }
  FUN_080000fc(uVar1);
  return;
}



/* FUN 0x0800c5d0 FUN_0800c5d0 */

int FUN_0800c5d0(int param_1,int param_2,int param_3,int param_4)

{
  if (param_1 == 0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if (param_4 == 0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if ((param_3 != 0) && (param_2 == 0)) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if ((param_3 == 0) && (param_2 != 0)) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  *(undefined1 *)(param_4 + 0x46) = 1;
  FUN_0800ae74();
  return param_4;
}



/* FUN 0x0800c616 FUN_0800c616 */

undefined4 FUN_0800c616(int *param_1,int param_2)

{
  int iVar1;
  
  if (param_1 != (int *)0x0) {
    FUN_0800bffc();
    param_1[2] = param_1[0x10] * param_1[0xf] + *param_1;
    param_1[0xe] = 0;
    param_1[1] = *param_1;
    param_1[3] = param_1[0x10] * (param_1[0xf] + -1) + *param_1;
    *(undefined1 *)(param_1 + 0x11) = 0xff;
    *(undefined1 *)((int)param_1 + 0x45) = 0xff;
    if (param_2 == 0) {
      if ((param_1[4] != 0) && (iVar1 = FUN_0800cba0(param_1 + 4), iVar1 != 0)) {
        FUN_0800c0a0();
      }
    }
    else {
      FUN_0800bf94();
      FUN_0800bf94(param_1 + 9);
    }
    FUN_0800c014();
    return 1;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* FUN 0x0800c686 FUN_0800c686 */

undefined4 FUN_0800c686(int param_1,int param_2,int param_3,int param_4)

{
  bool bVar1;
  int iVar2;
  undefined1 auStack_30 [8];
  int local_28;
  int iStack_24;
  int local_20;
  int local_1c;
  int iStack_18;
  
  bVar1 = false;
  if (param_1 == 0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if ((param_2 == 0) && (*(int *)(param_1 + 0x40) != 0)) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if ((param_4 == 2) && (*(int *)(param_1 + 0x3c) != 1)) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  iStack_24 = param_1;
  local_20 = param_2;
  local_1c = param_3;
  iStack_18 = param_4;
  iVar2 = FUN_0800ca4c();
  if ((iVar2 == 0) && (local_1c != 0)) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  local_28 = param_1 + 0x10;
  while( true ) {
    FUN_0800bffc();
    if ((*(uint *)(param_1 + 0x38) < *(uint *)(param_1 + 0x3c)) || (param_4 == 2)) {
      iVar2 = FUN_0800ad48(param_1,local_20,param_4);
      if (*(int *)(param_1 + 0x24) == 0) {
        if (iVar2 != 0) {
          FUN_0800c0a0();
        }
      }
      else {
        iVar2 = FUN_0800cba0(param_1 + 0x24);
        if (iVar2 != 0) {
          FUN_0800c0a0();
        }
      }
      FUN_0800c014();
      return 1;
    }
    if (local_1c == 0) {
      FUN_0800c014();
      return 0;
    }
    if (!bVar1) {
      FUN_0800c15c(auStack_30);
      bVar1 = true;
    }
    FUN_0800c014();
    FUN_0800c380();
    FUN_0800bffc();
    if (*(char *)(param_1 + 0x44) == -1) {
      *(undefined1 *)(param_1 + 0x44) = 0;
    }
    if (*(char *)(param_1 + 0x45) == -1) {
      *(undefined1 *)(param_1 + 0x45) = 0;
    }
    FUN_0800c014();
    iVar2 = FUN_0800c948(auStack_30,&local_1c);
    if (iVar2 != 0) break;
    iVar2 = FUN_0800b080(param_1);
    if (iVar2 == 0) {
      FUN_0800b374(param_1);
      FUN_0800cc0c();
    }
    else {
      FUN_0800c178(local_28,local_1c);
      FUN_0800b374(param_1);
      iVar2 = FUN_0800cc0c();
      if (iVar2 == 0) {
        FUN_0800c0a0();
      }
    }
  }
  FUN_0800b374(param_1);
  FUN_0800cc0c();
  return 0;
}



/* FUN 0x0800c7a8 FUN_0800c7a8 */

undefined4 FUN_0800c7a8(int param_1,int param_2,undefined4 *param_3,int param_4)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  
  if (param_1 == 0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if ((param_2 == 0) && (*(int *)(param_1 + 0x40) != 0)) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if ((param_4 == 2) && (*(int *)(param_1 + 0x3c) != 1)) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  uVar2 = FUN_080000f4();
  if ((*(uint *)(param_1 + 0x38) < *(uint *)(param_1 + 0x3c)) || (param_4 == 2)) {
    cVar1 = *(char *)(param_1 + 0x45);
    FUN_0800ad48(param_1,param_2,param_4);
    if (cVar1 == -1) {
      if (((*(int *)(param_1 + 0x24) != 0) && (iVar3 = FUN_0800cba0(param_1 + 0x24), iVar3 != 0)) &&
         (param_3 != (undefined4 *)0x0)) {
        *param_3 = 1;
      }
    }
    else {
      *(char *)(param_1 + 0x45) = cVar1 + '\x01';
    }
    uVar4 = 1;
  }
  else {
    uVar4 = 0;
  }
  FUN_080000fc(uVar2);
  return uVar4;
}



/* FUN 0x0800c83a FUN_0800c83a */

undefined4 FUN_0800c83a(int param_1,int param_2,int param_3)

{
  bool bVar1;
  int iVar2;
  undefined1 auStack_30 [8];
  int local_28;
  int iStack_20;
  int local_1c;
  int local_18;
  
  bVar1 = false;
  if (param_1 == 0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if ((param_2 == 0) && (*(int *)(param_1 + 0x40) != 0)) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  iStack_20 = param_1;
  local_1c = param_2;
  local_18 = param_3;
  iVar2 = FUN_0800ca4c();
  if ((iVar2 == 0) && (local_18 != 0)) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  local_28 = param_1 + 0x24;
  while( true ) {
    FUN_0800bffc();
    iVar2 = *(int *)(param_1 + 0x38);
    if (iVar2 != 0) {
      FUN_0800ad24(param_1,local_1c);
      *(int *)(param_1 + 0x38) = iVar2 + -1;
      if ((*(int *)(param_1 + 0x10) != 0) && (iVar2 = FUN_0800cba0(param_1 + 0x10), iVar2 != 0)) {
        FUN_0800c0a0();
      }
      FUN_0800c014();
      return 1;
    }
    if (local_18 == 0) break;
    if (!bVar1) {
      FUN_0800c15c(auStack_30);
      bVar1 = true;
    }
    FUN_0800c014();
    FUN_0800c380();
    FUN_0800bffc();
    if (*(char *)(param_1 + 0x44) == -1) {
      *(undefined1 *)(param_1 + 0x44) = 0;
    }
    if (*(char *)(param_1 + 0x45) == -1) {
      *(undefined1 *)(param_1 + 0x45) = 0;
    }
    FUN_0800c014();
    iVar2 = FUN_0800c948(auStack_30,&local_18);
    if (iVar2 == 0) {
      iVar2 = FUN_0800b064(param_1);
      if (iVar2 == 0) {
        FUN_0800b374(param_1);
        FUN_0800cc0c();
      }
      else {
        FUN_0800c178(local_28,local_18);
        FUN_0800b374(param_1);
        iVar2 = FUN_0800cc0c();
        if (iVar2 == 0) {
          FUN_0800c0a0();
        }
      }
    }
    else {
      FUN_0800b374(param_1);
      FUN_0800cc0c();
      iVar2 = FUN_0800b064(param_1);
      if (iVar2 != 0) {
        return 0;
      }
    }
  }
  FUN_0800c014();
  return 0;
}



/* FUN 0x0800c948 FUN_0800c948 */

undefined4 FUN_0800c948(int *param_1,uint *param_2)

{
  uint uVar1;
  uint uVar2;
  undefined4 uVar3;
  
  if (param_1 == (int *)0x0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if (param_2 != (uint *)0x0) {
    FUN_0800bffc();
    uVar1 = *(uint *)(DAT_0800c9a4 + 0xc) - param_1[1];
    uVar2 = *param_2;
    if (uVar2 == 0xffffffff) {
      uVar3 = 0;
    }
    else if ((*param_1 == *(int *)(DAT_0800c9a4 + 0x20)) ||
            (*(uint *)(DAT_0800c9a4 + 0xc) < (uint)param_1[1])) {
      if (uVar1 < uVar2) {
        *param_2 = uVar2 - uVar1;
        FUN_0800c15c(param_1);
        uVar3 = 0;
      }
      else {
        *param_2 = 0;
        uVar3 = 1;
      }
    }
    else {
      uVar3 = 1;
    }
    FUN_0800c014();
    return uVar3;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* FUN 0x0800c9a8 FUN_0800c9a8 */

undefined4
FUN_0800c9a8(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4,undefined4 param_5
            ,undefined4 param_6)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_0800b3e8(param_3 << 2);
  if (iVar1 == 0) {
    iVar2 = 0;
  }
  else {
    iVar2 = FUN_0800b3e8(0x5c);
    if (iVar2 == 0) {
      FUN_0800c030(iVar1);
    }
    else {
      *(int *)(iVar2 + 0x30) = iVar1;
    }
  }
  if (iVar2 != 0) {
    *(undefined1 *)(iVar2 + 0x59) = 0;
    FUN_0800ae96(param_1,param_2,param_3,param_4,param_5,param_6,iVar2,0);
    FUN_0800ac08(iVar2);
    return 1;
  }
  return 0xffffffff;
}



/* FUN 0x0800ca06 FUN_0800ca06 */

undefined4 FUN_0800ca06(undefined4 param_1)

{
  int in_stack_00000004;
  int in_stack_00000008;
  undefined4 local_18;
  
  if (in_stack_00000004 == 0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if (in_stack_00000008 != 0) {
    *(int *)(in_stack_00000008 + 0x30) = in_stack_00000004;
    *(undefined1 *)(in_stack_00000008 + 0x59) = 2;
    FUN_0800ae96(param_1);
    FUN_0800ac08(in_stack_00000008);
    return local_18;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* FUN 0x0800ca4c FUN_0800ca4c */

undefined4 FUN_0800ca4c(void)

{
  if (*(int *)(DAT_0800ca68 + 0x14) == 0) {
    return 1;
  }
  if (*(int *)(DAT_0800ca68 + 0x30) != 0) {
    return 0;
  }
  return 2;
}



/* FUN 0x0800ca6c FUN_0800ca6c */

undefined4 FUN_0800ca6c(void)

{
  return *(undefined4 *)(DAT_0800ca74 + 0xc);
}



/* FUN 0x0800ca78 FUN_0800ca78 */

undefined4 FUN_0800ca78(void)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  undefined4 uVar5;
  
  piVar1 = DAT_0800cb30;
  uVar5 = 0;
  if (DAT_0800cb30[0xc] == 0) {
    uVar4 = DAT_0800cb30[3] + 1;
    DAT_0800cb30[3] = uVar4;
    if (uVar4 == 0) {
      if (*(int *)piVar1[0xd] != 0) {
        disableIRQinterrupts();
        do {
                    /* WARNING: Do nothing block with infinite loop */
        } while( true );
      }
      iVar2 = piVar1[0xd];
      piVar1[0xd] = piVar1[0xe];
      piVar1[0xe] = iVar2;
      piVar1[8] = piVar1[8] + 1;
      FUN_0800b260();
    }
    if ((uint)piVar1[10] <= uVar4) {
      while (*(int *)piVar1[0xd] != 0) {
        iVar2 = *(int *)(*(int *)(piVar1[0xd] + 0xc) + 0xc);
        if (uVar4 < *(uint *)(iVar2 + 4)) {
          piVar1[10] = *(uint *)(iVar2 + 4);
          goto LAB_0800cada;
        }
        FUN_0800bf2c(iVar2 + 4);
        if (*(int *)(iVar2 + 0x28) != 0) {
          FUN_0800bf2c(iVar2 + 0x18);
        }
        uVar3 = *(uint *)(iVar2 + 0x2c);
        if ((uint)piVar1[4] < uVar3) {
          piVar1[4] = uVar3;
        }
        FUN_0800bfe2(uVar3 * 0x14 + DAT_0800cb34,iVar2 + 4);
        if (*(uint *)(*piVar1 + 0x2c) <= *(uint *)(iVar2 + 0x2c)) {
          uVar5 = 1;
        }
      }
      piVar1[10] = -1;
    }
LAB_0800cada:
    if (1 < *(uint *)(DAT_0800cb34 + *(int *)(*piVar1 + 0x2c) * 0x14)) {
      uVar5 = 1;
    }
    if (piVar1[7] != 0) {
      uVar5 = 1;
    }
  }
  else {
    DAT_0800cb30[6] = DAT_0800cb30[6] + 1;
  }
  return uVar5;
}



/* FUN 0x0800cb38 FUN_0800cb38 */

undefined4 FUN_0800cb38(int param_1)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  
  piVar1 = DAT_0800cb98;
  uVar4 = 0;
  if (param_1 != 0) {
    if (param_1 != *DAT_0800cb98) {
      disableIRQinterrupts();
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
    if (*(int *)(param_1 + 0x50) == 0) {
      disableIRQinterrupts();
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
    iVar2 = *(int *)(param_1 + 0x50) + -1;
    *(int *)(param_1 + 0x50) = iVar2;
    if ((*(int *)(param_1 + 0x2c) != *(int *)(param_1 + 0x4c)) && (iVar2 == 0)) {
      FUN_0800bf2c(param_1 + 4);
      *(int *)(param_1 + 0x2c) = *(int *)(param_1 + 0x4c);
      *(int *)(param_1 + 0x18) = 0x38 - *(int *)(param_1 + 0x4c);
      uVar3 = *(uint *)(param_1 + 0x2c);
      if ((uint)piVar1[4] < uVar3) {
        piVar1[4] = uVar3;
      }
      FUN_0800bfe2(uVar3 * 0x14 + DAT_0800cb9c,param_1 + 4);
      uVar4 = 1;
    }
  }
  return uVar4;
}



/* FUN 0x0800cba0 FUN_0800cba0 */

undefined4 FUN_0800cba0(int param_1)

{
  int *piVar1;
  uint uVar2;
  int iVar3;
  
  iVar3 = *(int *)(*(int *)(param_1 + 0xc) + 0xc);
  if (iVar3 == 0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  FUN_0800bf2c();
  piVar1 = DAT_0800cc00;
  if (DAT_0800cc00[0xc] == 0) {
    FUN_0800bf2c(iVar3 + 4);
    uVar2 = *(uint *)(iVar3 + 0x2c);
    if ((uint)piVar1[4] < uVar2) {
      piVar1[4] = uVar2;
    }
    FUN_0800bfe2(uVar2 * 0x14 + DAT_0800cc08,iVar3 + 4);
  }
  else {
    FUN_0800bfe2(DAT_0800cc04,iVar3 + 0x18);
  }
  if (*(uint *)(*piVar1 + 0x2c) < *(uint *)(iVar3 + 0x2c)) {
    piVar1[7] = 1;
    return 1;
  }
  return 0;
}



/* FUN 0x0800cc0c FUN_0800cc0c */

undefined4 FUN_0800cc0c(void)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  
  piVar1 = DAT_0800ccb4;
  iVar5 = 0;
  uVar6 = 0;
  if (DAT_0800ccb4[0xc] != 0) {
    FUN_0800bffc();
    piVar1[0xc] = piVar1[0xc] + -1;
    piVar2 = DAT_0800ccb8;
    if ((piVar1[0xc] == 0) && (piVar1[2] != 0)) {
      iVar3 = *DAT_0800ccb8;
      while (iVar3 != 0) {
        iVar5 = *(int *)(piVar2[3] + 0xc);
        FUN_0800bf2c(iVar5 + 0x18);
        FUN_0800bf2c(iVar5 + 4);
        uVar4 = *(uint *)(iVar5 + 0x2c);
        if ((uint)piVar1[4] < uVar4) {
          piVar1[4] = uVar4;
        }
        FUN_0800bfe2(uVar4 * 0x14 + DAT_0800ccbc,iVar5 + 4);
        if (*(uint *)(*piVar1 + 0x2c) <= *(uint *)(iVar5 + 0x2c)) {
          piVar1[7] = 1;
        }
        iVar3 = *piVar2;
      }
      if (iVar5 != 0) {
        FUN_0800b260();
      }
      iVar5 = piVar1[6];
      if (iVar5 != 0) {
        do {
          iVar3 = FUN_0800ca78();
          if (iVar3 != 0) {
            piVar1[7] = 1;
          }
          iVar5 = iVar5 + -1;
        } while (iVar5 != 0);
        piVar1[6] = 0;
      }
      if (piVar1[7] != 0) {
        uVar6 = 1;
        FUN_0800c0a0();
      }
    }
    FUN_0800c014();
    return uVar6;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* FUN 0x0800ccc0 FUN_0800ccc0 */

int FUN_0800ccc0(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined4 param_5)

{
  int iVar1;
  
  iVar1 = FUN_0800b3e8(0x2c);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 0x28) = 0;
    FUN_0800af30(param_1,param_2,param_3,param_4,param_5,iVar1);
  }
  return iVar1;
}



/* FUN 0x0800ccf2 FUN_0800ccf2 */

int FUN_0800ccf2(undefined4 param_1)

{
  int in_stack_00000004;
  
  if (in_stack_00000004 != 0) {
    *(undefined1 *)(in_stack_00000004 + 0x28) = 2;
    FUN_0800af30(param_1);
    return in_stack_00000004;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* FUN 0x0800cd20 FUN_0800cd20 */

int FUN_0800cd20(void)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  
  iVar3 = 0;
  FUN_0800ac84();
  piVar1 = DAT_0800cd70;
  if (*DAT_0800cd70 != 0) {
    local_10 = 0;
    local_14 = 0;
    FUN_0800bf6c(&local_10,&local_14,&local_18);
    iVar2 = FUN_0800ca06(DAT_0800cd7c,s_Tmr_Svc_0800cd74,local_18,0,2,local_14,local_10);
    piVar1[1] = iVar2;
    if (iVar2 != 0) {
      iVar3 = 1;
    }
  }
  if (iVar3 != 0) {
    return iVar3;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* FUN 0x0800cd80 FUN_0800cd80 */

undefined4
FUN_0800cd80(int param_1,int param_2,undefined4 param_3,undefined4 param_4,undefined4 param_5)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  int local_28;
  undefined4 local_24;
  int local_20;
  
  piVar1 = DAT_0800cde0;
  uVar3 = 0;
  if (param_1 != 0) {
    if (*DAT_0800cde0 != 0) {
      local_28 = param_2;
      local_24 = param_3;
      local_20 = param_1;
      if (param_2 < 6) {
        iVar2 = FUN_0800ca4c();
        if (iVar2 == 2) {
          uVar3 = FUN_0800c686(*piVar1,&local_28,param_5,0);
        }
        else {
          uVar3 = FUN_0800c686(*piVar1,&local_28,0);
        }
      }
      else {
        uVar3 = FUN_0800c7a8(*DAT_0800cde0,&local_28,param_4,0);
      }
    }
    return uVar3;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* FUN 0x0800cde4 FUN_0800cde4 */

bool FUN_0800cde4(int param_1)

{
  byte bVar1;
  
  if (param_1 != 0) {
    FUN_0800bffc();
    bVar1 = *(byte *)(param_1 + 0x28);
    FUN_0800c014();
    return (bVar1 & 1) != 0;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* FUN 0x0800ce0c FUN_0800ce0c */

void FUN_0800ce0c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  
  local_20 = 0xfffffffe;
  local_1c = param_1;
  local_18 = param_2;
  local_14 = param_3;
  FUN_0800c7a8(*DAT_0800ce30,&local_20,param_4,0);
  return;
}



/* FUN 0x0800ce34 FUN_0800ce34 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0800ce34(void)

{
  bool bVar1;
  bool bVar2;
  bool bVar3;
  bool bVar4;
  int iVar5;
  byte *pbVar6;
  int iVar7;
  uint uVar8;
  
  iVar5 = DAT_0800d0ec;
  bVar1 = true;
  bVar3 = false;
  bVar2 = true;
  bVar4 = false;
  if ((*(char *)(DAT_0800d0ec + 0x10) == '\0') || (*(char *)(DAT_0800d0ec + 0x31) != '\0')) {
LAB_0800ceac:
    if (((*(char *)(iVar5 + 0x11) != '\0') && (*(char *)(iVar5 + 0x4d) == '\0')) &&
       ((*DAT_0800d0f0 == '\0' || (*(char *)(iVar5 + 0x10) != '\0')))) {
      FUN_080099e8(5,3);
      FUN_080099e8(4,0xaf);
      FUN_080099e8(6,0x8d);
      FUN_0800a7b0(3);
      iVar7 = FUN_08002edc();
      uVar8 = FUN_08000160(iVar7 * 1000,*DAT_0800d0f4);
      if (uVar8 < 0x79) {
        if (uVar8 < 0x50) {
          bVar4 = true;
        }
      }
      else {
        *(undefined1 *)(iVar5 + 0x11) = 1;
        bVar2 = false;
        DAT_0800d0f8[1] = 0;
      }
    }
  }
  else if ((*DAT_0800d0f0 == '\0') || (*(char *)(DAT_0800d0ec + 0x11) != '\0')) {
    FUN_080099e8(5,3);
    FUN_080099e8(3,0xaf);
    FUN_080099e8(6,0x8b);
    FUN_0800a7b0(3);
    iVar7 = FUN_08002edc();
    uVar8 = FUN_08000160(iVar7 * 1000,*DAT_0800d0f4);
    pbVar6 = DAT_0800d0f8;
    if (uVar8 < 0x79) {
      if (uVar8 < 0x50) {
        bVar3 = true;
      }
    }
    else {
      *(undefined1 *)(iVar5 + 0x10) = 1;
      bVar1 = false;
      *pbVar6 = 0;
    }
    goto LAB_0800ceac;
  }
  if (!bVar2 && !bVar1) {
    return;
  }
  FUN_0800d250();
  if (bVar1) {
    if (*(char *)(iVar5 + 0x10) != '\0') {
      FUN_080099e8(6,0xc1);
    }
    FUN_080099e8(3,0xae);
    FUN_0800a7b0(3);
  }
  if (bVar2) {
    if (*(char *)(iVar5 + 0x11) != '\0') {
      FUN_080099e8(6,0xc1);
    }
    FUN_080099e8(4,0xae);
    FUN_0800a7b0(3);
  }
  if (bVar1) {
    FUN_080099e8(6,0x85);
    FUN_0800a7b0(2);
    uVar8 = FUN_08002edc();
    if (uVar8 < 0x26d) {
      FUN_080099e8(5,0xb);
      FUN_0800a7b0(3);
      uVar8 = FUN_08002edc();
      *(bool *)(iVar5 + 0x10) = uVar8 < 0x26c;
      if (uVar8 < 0x26c) goto LAB_0800cfa2;
LAB_0800cfd2:
      *DAT_0800d0f8 = 0;
    }
    else {
      *(undefined1 *)(iVar5 + 0x10) = 1;
LAB_0800cfa2:
      if (!bVar3) goto LAB_0800cfd2;
      if (*DAT_0800d0f8 < 6) {
        *DAT_0800d0f8 = *DAT_0800d0f8 + 1;
      }
      else {
        if (*_DAT_0800d0fc == '\0') {
          FUN_08009170(s_L_water_detected__disable_5V_out_0800d0ff + 1);
          FUN_08009170(&DAT_0800d128);
        }
        *(undefined1 *)(iVar5 + 0x31) = 1;
        *(undefined1 *)(iVar5 + 0x33) = 1;
      }
    }
    if ((((*(char *)(iVar5 + 0x10) != '\0') && (*(char *)(iVar5 + 0x11) != '\0')) &&
        (*(char *)(iVar5 + 0x31) != '\0')) && (*(char *)(iVar5 + 0x33) == '\0')) {
      FUN_080099e8(5,3);
      FUN_080099e8(6,0x81);
      FUN_080099e8(7,0x20);
      FUN_080099e8(3,0xaf);
      FUN_0800a7b0(5);
      FUN_080099e8(3,0xae);
    }
  }
  if (!bVar2) goto LAB_0800d0e6;
  FUN_080099e8(6,0x87);
  FUN_0800a7b0(2);
  uVar8 = FUN_08002edc();
  if (uVar8 < 0x26d) {
    FUN_080099e8(5,7);
    FUN_0800a7b0(3);
    uVar8 = FUN_08002edc();
    *(bool *)(iVar5 + 0x11) = uVar8 < 0x26c;
    if (uVar8 < 0x26c) goto LAB_0800d06a;
LAB_0800d09a:
    DAT_0800d0f8[1] = 0;
  }
  else {
    *(undefined1 *)(iVar5 + 0x11) = 1;
LAB_0800d06a:
    if (!bVar4) goto LAB_0800d09a;
    if (DAT_0800d0f8[1] < 6) {
      DAT_0800d0f8[1] = DAT_0800d0f8[1] + 1;
    }
    else {
      if (*_DAT_0800d0fc == '\0') {
        FUN_08009170(s_R_water_detected__disable_5V_out_0800d12c);
        FUN_08009170(&DAT_0800d128);
      }
      *(undefined1 *)(iVar5 + 0x4d) = 1;
      *(undefined1 *)(iVar5 + 0x4f) = 1;
    }
  }
  if (((*(char *)(iVar5 + 0x10) != '\0') && (*(char *)(iVar5 + 0x11) != '\0')) &&
     ((*(char *)(iVar5 + 0x4d) != '\0' && (*(char *)(iVar5 + 0x4f) == '\0')))) {
    FUN_080099e8(5,3);
    FUN_080099e8(6,0x81);
    FUN_080099e8(7,0x20);
    FUN_080099e8(4,0xaf);
    FUN_0800a7b0(5);
    FUN_080099e8(4,0xae);
  }
LAB_0800d0e6:
  FUN_08009a14();
  return;
}



/* FUN 0x0800d154 FUN_0800d154 */

void FUN_0800d154(void)

{
  FUN_080099e8(3,0xae);
  FUN_080099e8(4,0xae);
  FUN_080099e8(5,3);
  FUN_080099e8(6,0x81);
  return;
}



/* FUN 0x0800d178 FUN_0800d178 */

void FUN_0800d178(void)

{
  FUN_080099e8(5,3);
  FUN_080099e8(6,0x81);
  FUN_080099e8(3,0xae);
  FUN_080099e8(4,0xae);
  FUN_080099e8(7,0x20);
  FUN_08009170(s_Init_YHM2510_0800d1ac);
  return;
}



/* FUN 0x0800d218 FUN_0800d218 */

void FUN_0800d218(void)

{
  if (*DAT_0800d234 == '\0') {
    FUN_08009170(s_2510__0x00_0x07__0800d238);
  }
  FUN_080067c8(DAT_0800d24c,8);
  return;
}



/* FUN 0x0800d250 FUN_0800d250 */

void FUN_0800d250(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  iVar1 = DAT_0800d268;
  uVar2 = 0;
  iVar3 = DAT_0800d268 + 8;
  do {
    *(undefined1 *)(iVar3 + uVar2) = *(undefined1 *)(iVar1 + uVar2);
    uVar2 = uVar2 + 1 & 0xff;
  } while (uVar2 < 8);
  return;
}



