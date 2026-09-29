
undefined8 FUN_0050c528(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  iVar1 = FUN_0050c476(0x120);
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x91b;
      FUN_0043d574(2,DAT_0050c9c8,DAT_0050c9c4,DAT_0050c9e0,0x91b,DAT_0050c9dc,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0050c9e4,DAT_0050c9e4);
    }
    uVar2 = 0;
    goto LAB_0050c644;
  }
  if (*(char *)(iVar1 + 0x29) == '\0') {
    iVar3 = FUN_0050c8cc();
    if (iVar3 < 0) {
      uVar2 = 0;
      goto LAB_0050c644;
    }
    iVar4 = FUN_0050c314(iVar1,iVar3);
    if (iVar4 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_2 = 0x92c;
        FUN_0043d574(2,DAT_0050c9c8,DAT_0050c9c4,DAT_0050c9e0,0x92c,DAT_0050c9f0,iVar3);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_0050c9f4,DAT_0050c9f4,iVar3);
      }
      uVar2 = 0;
      goto LAB_0050c644;
    }
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      param_2 = 0x929;
      FUN_0043d574(3,DAT_0050c9c8,DAT_0050c9c4,DAT_0050c9e0,0x929,DAT_0050c9e8,iVar3);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_0050c9ec,DAT_0050c9ec,iVar3);
    }
  }
  if (*(char *)(iVar1 + 0x29) == '\0') {
    uVar2 = 0;
  }
  else {
    uVar2 = 1;
  }
LAB_0050c644:
  return CONCAT44(param_2,uVar2);
}

