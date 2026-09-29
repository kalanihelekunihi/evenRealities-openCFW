
undefined4 FUN_0055876a(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = DAT_00558920;
  iVar1 = file_open(DAT_00558920,&DAT_005588a4,param_3,param_4,param_1,param_2,param_3,param_4);
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005588bc,DAT_005588b8,DAT_00558928,0x13f,DAT_00558924,uVar2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0055892c,DAT_0055892c,uVar2);
    }
    uVar2 = 0;
  }
  else {
    file_close();
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005588bc,DAT_005588b8,DAT_00558928,0x143,DAT_00558930,uVar2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00558934,DAT_00558934,uVar2);
    }
    uVar2 = 1;
  }
  return uVar2;
}

