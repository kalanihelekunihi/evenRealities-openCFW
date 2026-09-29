
undefined4
DmPrivRemDevFromResList(undefined1 param_1,undefined4 param_2,undefined2 param_3,undefined4 param_4)

{
  undefined2 *puVar1;
  
  puVar1 = (undefined2 *)WsfMsgAlloc(0xc);
  if (puVar1 != (undefined2 *)0x0) {
    *(undefined1 *)(puVar1 + 1) = 0x32;
    *puVar1 = param_3;
    *(undefined1 *)(puVar1 + 2) = param_1;
    FUN_004d293c((int)puVar1 + 5,param_2);
    WsfMsgSend(*(undefined1 *)(DAT_004d2924 + 0xc),puVar1);
  }
  return param_4;
}

