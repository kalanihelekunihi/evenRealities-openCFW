
undefined8
APP_BleSlaveDisconnect(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  ushort *puVar2;
  int iVar3;
  undefined4 local_10;
  undefined4 local_c;
  
  puVar2 = (ushort *)WsfMsgAlloc(0xc);
  local_10 = param_3;
  local_c = param_4;
  if (puVar2 != (ushort *)0x0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_c = DAT_0046f460;
      local_10 = 0x304;
      FUN_0043d574(4,DAT_0046f404,DAT_0046f400,DAT_0046f464);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0046f468,DAT_0046f468);
    }
    *(undefined1 *)(puVar2 + 1) = 0xad;
    piVar1 = DAT_0046f3c4;
    *puVar2 = (ushort)*(byte *)(*DAT_0046f3c4 + 0x54);
    puVar2[4] = 0;
    WsfMsgSend(*(undefined1 *)(*piVar1 + 0x56),puVar2);
  }
  return CONCAT44(local_c,local_10);
}

