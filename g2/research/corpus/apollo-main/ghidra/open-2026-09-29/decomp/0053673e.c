
bool FUN_0053673e(undefined1 param_1,undefined2 param_2,undefined1 param_3)

{
  undefined2 *puVar1;
  
  puVar1 = (undefined2 *)WsfMsgAlloc(0x9c);
  if (puVar1 != (undefined2 *)0x0) {
    *puVar1 = param_2;
    *(undefined1 *)(puVar1 + 1) = param_3;
    *(undefined1 *)(puVar1 + 0x1a) = 2;
    WsfMsgEnq(DAT_005367d4,param_1,puVar1);
    HciLeReadLocalP256PubKey();
  }
  return puVar1 != (undefined2 *)0x0;
}

