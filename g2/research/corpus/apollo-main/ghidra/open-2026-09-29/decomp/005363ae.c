
void FUN_005363ae(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined1 param_4)

{
  undefined1 auStack_30 [16];
  undefined1 auStack_20 [16];
  
  WStrReverseCpy(auStack_20,param_1,0x10);
  WStrReverseCpy(auStack_30,param_2,0x10);
  WsfMsgEnq(DAT_005363ec,param_4,param_3);
  HciLeEncryptCmd(auStack_20,auStack_30);
  return;
}

