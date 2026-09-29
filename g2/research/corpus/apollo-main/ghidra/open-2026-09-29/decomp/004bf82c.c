
undefined4 APP_BleAnccSvcDiscover(undefined1 param_1,undefined4 param_2)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  
  cVar1 = FUN_0045a568();
  if (cVar1 == '\x01') {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004bf92c,DAT_004bf928,DAT_004bf980,0x34f,DAT_004bf97c,param_1,1);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_004bf984,DAT_004bf984,param_1,1);
    }
    FUN_005332b4(param_1,0x10,DAT_004bf98c,5,DAT_004bf988,param_2);
    uVar2 = 1;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

