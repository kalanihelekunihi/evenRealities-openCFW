
undefined1 FUN_0046651e(uint param_1,uint param_2,uint param_3,undefined4 param_4)

{
  undefined1 uVar1;
  int iVar2;
  uint uVar3;
  
  if ((param_2 & 0xff) < 3) {
    if ((param_1 & 0xff) == 0) {
      uVar1 = *(undefined1 *)(DAT_004667ec + (param_2 & 0xff) + 5);
    }
    else {
      uVar1 = *(undefined1 *)(DAT_004667ec + (param_2 & 0xff) + 8);
    }
  }
  else {
    uVar3 = param_2;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = param_2 & 0xff;
      param_1 = 0x11d;
      uVar3 = DAT_00466848;
      FUN_0043d574(2,DAT_00466800,DAT_004667fc,DAT_0046684c,0x11d,DAT_00466848,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_00466850,DAT_00466850,param_2 & 0xff,param_1,uVar3,param_3);
    }
    uVar1 = 0;
  }
  return uVar1;
}

