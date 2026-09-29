
undefined4
Thread_SendMsgToBleProductionTask(int param_1,undefined2 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int local_20;
  undefined4 uStack_1c;
  
  local_20 = param_3;
  uStack_1c = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00538b54,DAT_00538b50,DAT_00538bfc,0x139,DAT_00538bf8);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_00538c00);
  }
  iVar1 = DAT_00538b5c;
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00538b54,DAT_00538b50,DAT_00538bfc,0x13b,DAT_00538c04);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00538c08,DAT_00538c08);
    }
    uVar2 = 0xffffffff;
  }
  else if ((*(int *)(DAT_00538b5c + 0xc) == 0) || (*(int *)(DAT_00538b5c + 0x18) == 0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00538b54,DAT_00538b50,DAT_00538bfc,0x140,DAT_00538c0c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00538c10,DAT_00538c10);
    }
    uVar2 = 0xffffffff;
  }
  else {
    local_20 = 0;
    local_20 = osMemoryPoolAlloc(*(undefined4 *)(DAT_00538b5c + 0x18),0);
    if (local_20 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00538b54,DAT_00538b50,DAT_00538bfc,0x148,DAT_00538c14);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00538c18,DAT_00538c18);
      }
      uVar2 = 0xffffffff;
    }
    else {
      uVar2 = 0;
      FUN_0043c0e4(local_20,0x100,0);
      FUN_00439be4(local_20,param_1,param_2);
      iVar3 = osMessageQueuePut(*(undefined4 *)(iVar1 + 0xc),&local_20,0,0);
      if (iVar3 == 0) {
        osThreadFlagsSet(*(undefined4 *)(iVar1 + 8),0x400000);
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00538b54,DAT_00538b50,DAT_00538bfc,0x151,DAT_00538c1c);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_00538c20,DAT_00538c20);
        }
        osMemoryPoolFree(*(undefined4 *)(iVar1 + 0x18),local_20);
        uVar2 = 0xffffffff;
      }
    }
  }
  return uVar2;
}

