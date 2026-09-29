
undefined8 APP_MasterUnpairConnIdEvent(byte param_1,undefined4 param_2,undefined4 param_3)

{
  ushort *puVar1;
  int iVar2;
  
  if ((param_1 != 0) && (puVar1 = (ushort *)WsfMsgAlloc(0xc), puVar1 != (ushort *)0x0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x46a;
      param_3 = DAT_004a28e4;
      FUN_0043d574(3,DAT_004a28f0,DAT_004a28ec,DAT_004a28e8,0x46a,DAT_004a28e4,param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_004a28f4,DAT_004a28f4,param_1);
    }
    *(undefined1 *)(puVar1 + 1) = 0xaf;
    *puVar1 = (ushort)param_1;
    puVar1[4] = 0x142;
    WsfMsgSend(*(undefined1 *)(*DAT_004a2648 + 0x56),puVar1);
  }
  return CONCAT44(param_3,param_2);
}

