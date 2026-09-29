
void hciCoreRecv(undefined1 param_1,undefined4 param_2)

{
  int iVar1;
  
  iVar1 = DAT_00530d6c;
  WsfMsgEnq(DAT_00530d6c,param_1,param_2);
  WsfSetEvent(*(undefined1 *)(iVar1 + 0x20),1);
  return;
}

