
undefined8
_masterConnectCancel(ushort param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  ushort *puVar2;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_2 = 0x1c1;
    param_3 = DAT_004a0674;
    FUN_0043d574(4,DAT_004a02d8,DAT_004a02d4,DAT_004a0678,0x1c1,DAT_004a0674,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004a067c,DAT_004a067c);
  }
  puVar2 = (ushort *)WsfMsgAlloc(0xc);
  if (puVar2 != (ushort *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x1c4;
      param_3 = DAT_004a0680;
      FUN_0043d574(4,DAT_004a02d8,DAT_004a02d4,DAT_004a0678);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004a0684);
    }
    *(undefined1 *)(puVar2 + 1) = 0xb0;
    *puVar2 = param_1 & 0xff;
    puVar2[4] = 0;
    WsfMsgSend(*(undefined1 *)(*DAT_004a0518 + 0x56),puVar2);
  }
  return CONCAT44(param_3,param_2);
}

