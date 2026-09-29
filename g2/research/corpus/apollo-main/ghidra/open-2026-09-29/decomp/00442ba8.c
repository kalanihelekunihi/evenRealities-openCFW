
undefined4 FUN_00442ba8(char param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  undefined1 uVar3;
  undefined4 uVar4;
  
  if (param_2 == 0) {
    uVar3 = 0;
  }
  else if (param_2 == 1) {
    uVar3 = 1;
  }
  else {
    if (param_2 != 4) {
      return 0;
    }
    uVar3 = 2;
  }
  cVar1 = FUN_0046651e(param_1 == '\x01',uVar3);
  if (cVar1 == '\0') {
    uVar4 = 0;
  }
  else if (cVar1 == '\x01') {
    uVar4 = 3;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00442cf4,DAT_00442cf0,DAT_0044372c,0x156,DAT_00443728,cVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_00443730,DAT_00443730,cVar1);
    }
    uVar4 = 0;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00442cf4,DAT_00442cf0,DAT_0044372c,0x15c,DAT_00443734,param_1,param_2,uVar3,
                 cVar1,uVar4,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x11400000,DAT_00443738,DAT_00443738,param_1,param_2,uVar3,cVar1,uVar4);
  }
  return uVar4;
}

