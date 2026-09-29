
undefined4 smpActPairingFailed(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  smpCleanup(param_1);
  DmConnSetIdle(*(undefined1 *)(param_1 + 0x3d),1,0);
  *(undefined1 *)(param_2 + 2) = 0x2b;
  DmSmpCbackExec(param_2);
  return param_4;
}

