
undefined4
DmPrivAddDevToResList
          (undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
          undefined1 param_5,undefined2 param_6)

{
  undefined2 *puVar1;
  
  puVar1 = (undefined2 *)WsfMsgAlloc(0x2c);
  if (puVar1 != (undefined2 *)0x0) {
    *(undefined1 *)(puVar1 + 1) = 0x31;
    *puVar1 = param_6;
    *(undefined1 *)(puVar1 + 2) = param_1;
    FUN_004d293c((int)puVar1 + 5,param_2);
    FUN_00542a44((int)puVar1 + 0xb,param_3);
    FUN_00542a44((int)puVar1 + 0x1b,param_4);
    *(undefined1 *)((int)puVar1 + 0x2b) = param_5;
    WsfMsgSend(*(undefined1 *)(DAT_004d2924 + 0xc),puVar1);
  }
  return param_4;
}

