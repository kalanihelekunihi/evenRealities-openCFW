
undefined4
DmPrivResolveAddr(undefined4 param_1,undefined4 param_2,undefined2 param_3,undefined4 param_4)

{
  undefined2 *puVar1;
  
  puVar1 = (undefined2 *)WsfMsgAlloc(0x1a);
  if (puVar1 != (undefined2 *)0x0) {
    *(undefined1 *)(puVar1 + 1) = 0x30;
    *puVar1 = param_3;
    FUN_00542a44(puVar1 + 2,param_2);
    FUN_004d293c(puVar1 + 10,param_1);
    WsfMsgSend(*(undefined1 *)(DAT_004d2924 + 0xc),puVar1);
  }
  return param_4;
}

