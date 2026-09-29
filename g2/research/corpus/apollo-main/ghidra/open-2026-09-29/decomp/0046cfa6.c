
undefined8 FUN_0046cfa6(byte *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  
  if (param_1 == (byte *)0x0) {
    iVar2 = 0;
  }
  else {
    bVar1 = *param_1;
    if (bVar1 == 0) {
      if (*(int *)(param_1 + 4) == 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          param_2 = 0x11e;
          FUN_0043d574(1,DAT_0046d580,DAT_0046d57c,DAT_0046d5cc,0x11e,DAT_0046d5c8);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_0046d5d0,DAT_0046d5d0);
        }
        iVar2 = 0;
      }
      else {
        iVar2 = *(int *)(param_1 + 4);
      }
    }
    else if (bVar1 == 2) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_2 = 0x147;
        FUN_0043d574(1,DAT_0046d580,DAT_0046d57c,DAT_0046d5cc,0x147,DAT_0046d5e4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0046d5e8,DAT_0046d5e8);
      }
      iVar2 = 0;
    }
    else if (bVar1 < 2) {
      if (*(int *)(param_1 + 4) == 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          param_2 = 0x132;
          FUN_0043d574(1,DAT_0046d580,DAT_0046d57c,DAT_0046d5cc,0x132,DAT_0046d5dc);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_0046d5e0,DAT_0046d5e0);
        }
        iVar2 = 0;
      }
      else {
        iVar2 = FUN_004b1c9c(*(undefined4 *)(param_1 + 4),1,*(undefined2 *)(param_1 + 8),param_1[10]
                             ,param_2,param_3,param_4);
        if (iVar2 == 0) {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            param_2 = 0x12e;
            FUN_0043d574(1,DAT_0046d580,DAT_0046d57c,DAT_0046d5cc,0x12e,DAT_0046d5d4,
                         *(undefined4 *)(param_1 + 4));
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x4400000,DAT_0046d5d8,DAT_0046d5d8,*(undefined4 *)(param_1 + 4));
          }
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_2 = 0x14c;
        FUN_0043d574(1,DAT_0046d580,DAT_0046d57c,DAT_0046d5cc,0x14c,DAT_0046d5ec,*param_1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_0046d5f0,DAT_0046d5f0,*param_1);
      }
      iVar2 = 0;
    }
  }
  return CONCAT44(param_2,iVar2);
}

