
longlong case_begin_receive(int *param_1,int param_2,uint param_3)

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

