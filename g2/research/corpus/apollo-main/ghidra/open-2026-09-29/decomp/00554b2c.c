
undefined8 FUN_00554b2c(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  
  iVar1 = DAT_00554d34;
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    iVar3 = param_1;
    if (iVar1 << 0x1e < 0) {
      iVar3 = 0x264;
      param_2 = DAT_00555594;
      FUN_0043d574(1,DAT_00554d3c,DAT_00554d38,DAT_00555598,0x264,DAT_00555594,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0055559c);
    }
  }
  else if (*(char *)(DAT_00554d34 + 4) == '\0') {
    iVar3 = param_1;
    if (param_2 < *(uint *)(DAT_00554d34 + 0x30)) {
      uVar4 = param_2;
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        iVar3 = 0x271;
        uVar4 = DAT_0055574c;
        FUN_0043d574(1,DAT_00554d3c,DAT_00554d38,DAT_00555598,0x271,DAT_0055574c,param_2);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00555750,DAT_00555750,param_2);
      }
      param_2 = uVar4;
      FUN_00499716(param_1,0);
      FUN_004997f8(param_1);
      uVar2 = FUN_0044a43c();
      FUN_00499752(param_1,uVar2);
    }
    else if (param_2 == *(uint *)(DAT_00554d34 + 0x30)) {
      FUN_00499716(param_1,0);
      FUN_00499752(param_1,*(undefined4 *)(iVar1 + 0x38));
    }
    else {
      FUN_00499716(param_1,0xffff);
      FUN_00499752(param_1,0xffff);
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    iVar3 = param_1;
    if (iVar1 << 0x1e < 0) {
      iVar3 = 0x26c;
      param_2 = DAT_0055570c;
      FUN_0043d574(4,DAT_00554d3c,DAT_00554d38,DAT_00555598);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00555744,DAT_00555744);
    }
  }
  return CONCAT44(param_2,iVar3);
}

