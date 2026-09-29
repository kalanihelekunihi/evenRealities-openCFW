
undefined4
FUN_0055b840(undefined2 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar1 = FUN_0055b400(DAT_0055ba00,param_1);
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_0055b9d4,DAT_0055b9d0,DAT_0055ba38,0x18c,DAT_0055ba48,*param_1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_0055ba4c,DAT_0055ba4c,*param_1);
    }
    uVar3 = 0;
  }
  else {
    if (param_1 == (undefined2 *)0x0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0055b9d4,DAT_0055b9d0,DAT_0055ba38,0x187,DAT_0055ba40,iVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_0055ba44,DAT_0055ba44,iVar1);
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0055b9d4,DAT_0055b9d0,DAT_0055ba38,0x185,DAT_0055ba34,*param_1,iVar1,
                     param_4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4800000,DAT_0055ba3c,DAT_0055ba3c,*param_1,iVar1);
      }
    }
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

