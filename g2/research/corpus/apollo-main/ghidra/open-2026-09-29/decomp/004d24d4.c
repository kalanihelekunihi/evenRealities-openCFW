
undefined4 DmSecAuthRsp(byte param_1,undefined1 param_2,int param_3,undefined4 param_4)

{
  ushort *puVar1;
  
  puVar1 = (ushort *)WsfMsgAlloc(0x16);
  if (puVar1 != (ushort *)0x0) {
    *(undefined1 *)(puVar1 + 1) = 4;
    *puVar1 = (ushort)param_1;
    *(undefined1 *)(puVar1 + 10) = param_2;
    if (param_3 != 0) {
      FUN_00439be4(puVar1 + 2,param_3,param_2);
    }
    SmpDmMsgSend(puVar1);
  }
  return param_4;
}

