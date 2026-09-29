
undefined8
slave_post_unpair_event_0046effc(int param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  ushort *puVar3;
  
  piVar1 = DAT_0046f41c;
  *(bool *)(*DAT_0046f41c + 0x20) = param_1 != 0;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_3 = (uint)*(byte *)(*piVar1 + 0x20);
    param_1 = 0x2e4;
    param_2 = DAT_0046f448;
    FUN_0043d574(4,DAT_0046f404,DAT_0046f400,DAT_0046f44c,0x2e4,DAT_0046f448,param_3,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0046f450,DAT_0046f450,*(undefined1 *)(*piVar1 + 0x20),param_1
                        ,param_2,param_3);
  }
  puVar3 = (ushort *)WsfMsgAlloc(0xc);
  if (puVar3 != (ushort *)0x0) {
    *(undefined1 *)(puVar3 + 1) = 0xb5;
    piVar1 = DAT_0046f3c4;
    *puVar3 = (ushort)*(byte *)(*DAT_0046f3c4 + 0x54);
    puVar3[4] = 1;
    WsfMsgSend(*(undefined1 *)(*piVar1 + 0x56),puVar3);
  }
  return CONCAT44(param_2,param_1);
}

