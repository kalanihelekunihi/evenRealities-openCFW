
bool FUN_00536774(int param_1,undefined1 param_2,undefined2 param_3,undefined4 param_4)

{
  undefined2 *puVar1;
  undefined1 auStack_58 [32];
  undefined1 auStack_38 [32];
  undefined4 uStack_18;
  
  uStack_18 = param_4;
  puVar1 = (undefined2 *)WsfMsgAlloc(0x9c);
  if (puVar1 != (undefined2 *)0x0) {
    *puVar1 = param_3;
    *(char *)(puVar1 + 1) = (char)param_4;
    *(undefined1 *)(puVar1 + 0x1a) = 2;
    WsfMsgEnq(DAT_005367d8,param_2,puVar1);
    WStrReverseCpy(auStack_38,param_1,0x20);
    WStrReverseCpy(auStack_58,param_1 + 0x20,0x20);
    HciLeGenerateDHKey(auStack_38,auStack_58);
  }
  return puVar1 != (undefined2 *)0x0;
}

