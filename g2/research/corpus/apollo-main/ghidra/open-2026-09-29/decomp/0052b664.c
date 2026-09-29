
undefined8
hciClearCmdQueue(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_10 = param_3;
  uStack_c = param_4;
  while( true ) {
    iVar1 = DAT_0052b6b4;
    iVar2 = WsfMsgDeq(DAT_0052b6b4 + 0x10,&uStack_10);
    if (iVar2 == 0) break;
    WsfMsgFree();
  }
  *(undefined1 *)(iVar1 + 0x1a) = 1;
  return CONCAT44(uStack_c,uStack_10);
}

