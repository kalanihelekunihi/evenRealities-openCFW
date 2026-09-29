
uint attsIndMsgCback(ushort *param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  if ((char)param_1[1] == '!') {
    iVar1 = attsCcbByConnId((char)*param_1,(char)param_1[4]);
    if (iVar1 == 0) {
      WsfMsgFree(*(undefined4 *)(param_1 + 2));
    }
    else {
      iVar2 = attsPendIndNtfHandle(iVar1,*(undefined4 *)(param_1 + 2));
      if (iVar2 == 0) {
        attsSetupMsg(iVar1,(char)*param_1,(char)param_1[4],*(undefined4 *)(param_1 + 2));
      }
      else {
        attsExecCallback((char)*param_1,*(undefined2 *)(*(int *)(param_1 + 2) + 2),0x72);
        WsfMsgFree(*(undefined4 *)(param_1 + 2));
      }
    }
  }
  else if ((char)param_1[1] == '\"') {
    attDecodeMsgParam(*param_1,&uStack_10,(int)&uStack_10 + 1);
    *param_1 = (ushort)(byte)uStack_10;
    attsCcbByConnId(uStack_10 & 0xff,uStack_10._1_1_);
  }
  return uStack_10;
}

