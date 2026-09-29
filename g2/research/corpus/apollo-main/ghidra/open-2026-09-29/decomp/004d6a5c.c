
undefined8 SVC_WhitelistManagerInit(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = DAT_004d6b58;
  FUN_0043c0e4(DAT_004d6b58,0x1f42,0);
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0x1b7;
    param_3 = DAT_004d6b98;
    FUN_0043d574(4,DAT_004d6af8,DAT_004d6af4,DAT_004d6b9c,0x1b7,DAT_004d6b98,0x1f43);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004d6ba0,DAT_004d6ba0,0x1f43);
  }
  _parseWhiteListFromFS(DAT_004d6ba4);
  _printAppWhiteListInfo(uVar1);
  return CONCAT44(param_3,param_2);
}

