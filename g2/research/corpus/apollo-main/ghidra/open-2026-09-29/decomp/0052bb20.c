
void DmSecLtkRsp(byte param_1,char param_2,undefined1 param_3,undefined4 param_4)

{
  ushort *puVar1;
  
  puVar1 = (ushort *)WsfMsgAlloc(0x16);
  if (puVar1 != (ushort *)0x0) {
    *(undefined1 *)(puVar1 + 1) = 0x29;
    *puVar1 = (ushort)param_1;
    *(char *)(puVar1 + 10) = param_2;
    *(undefined1 *)((int)puVar1 + 0x15) = param_3;
    if (param_2 != '\0') {
      FUN_00542a44(puVar1 + 2,param_4);
    }
    WsfMsgSend(*(undefined1 *)(DAT_0052bb60 + 0xc),puVar1);
  }
  return;
}

