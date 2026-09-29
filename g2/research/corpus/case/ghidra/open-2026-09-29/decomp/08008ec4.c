
undefined4 case_wait_condition(int *param_1,uint param_2,uint param_3,int param_4,uint param_5)

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
    iVar2 = case_tick_word2();
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

