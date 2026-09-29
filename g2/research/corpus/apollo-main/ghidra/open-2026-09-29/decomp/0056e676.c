
undefined4 smpActSecReqTimeout(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = DmConnSecLevel(*(undefined1 *)(param_1 + 0x3d));
  if (iVar1 == 0) {
    smpActPairingFailed(param_1,param_2);
  }
  else {
    *(undefined1 *)(param_2 + 2) = 0x1f;
    smpSmExecute(param_1,param_2);
  }
  return param_4;
}

