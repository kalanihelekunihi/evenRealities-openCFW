
undefined4 DmSecEncryptReq(byte param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  ushort *puVar1;
  
  puVar1 = (ushort *)WsfMsgAlloc(0x20);
  if (puVar1 != (ushort *)0x0) {
    *(undefined1 *)(puVar1 + 1) = 0x28;
    *puVar1 = (ushort)param_1;
    FUN_00439be4(puVar1 + 2,param_3,0x1a);
    *(undefined1 *)(puVar1 + 0xf) = param_2;
    WsfMsgSend(*(undefined1 *)(DAT_0055bc58 + 0xc),puVar1);
  }
  return param_4;
}

