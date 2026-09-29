
undefined4
smpScActPairingCancel(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  smpSendPairingFailed(param_1,*(undefined1 *)(param_2 + 3));
  smpScActPairingFailed(param_1,param_2);
  return param_4;
}

