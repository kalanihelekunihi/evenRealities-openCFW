
undefined4
APP_PbRxErrorCode(undefined1 param_1,undefined1 *param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004d8ef0,DAT_004d8eec,DAT_004d8f04,0x114,DAT_004d8f00,*param_2,param_1,
                 param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10800000,DAT_004d8f08,DAT_004d8f08,*param_2,param_1);
  }
  cVar1 = param_2[1];
  if (cVar1 == '\x01') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004d8ef0,DAT_004d8eec,DAT_004d8f04,0x117,DAT_004d8f0c,param_2[1]);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004d8f10,DAT_004d8f10,param_2[1]);
    }
  }
  else if (cVar1 == '\x05') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004d8ef0,DAT_004d8eec,DAT_004d8f04,0x11c,DAT_004d8f14,param_2[1]);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004d8f18,DAT_004d8f18,param_2[1]);
    }
  }
  else if (cVar1 == '\a') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004d8ef0,DAT_004d8eec,DAT_004d8f04,0x121,DAT_004d8f1c,param_2[1]);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004d8f20,DAT_004d8f20,param_2[1]);
    }
  }
  else if (cVar1 == '\b') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004d8ef0,DAT_004d8eec,DAT_004d8f04,0x126,DAT_004d8f24,param_2[1]);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004d8f28,DAT_004d8f28,param_2[1]);
    }
  }
  else if (cVar1 == '\t') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004d8ef0,DAT_004d8eec,DAT_004d8f04,299,DAT_004d8f2c,param_2[1]);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004d8f30,DAT_004d8f30,param_2[1]);
    }
  }
  return 0;
}

