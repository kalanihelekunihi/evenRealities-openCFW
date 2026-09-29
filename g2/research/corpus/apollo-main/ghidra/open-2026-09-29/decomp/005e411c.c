
undefined4 smprScActCalcDHKey(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  if (*(char *)(param_1 + 0x3f) == '\r') {
    WStrReverseCpy(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x50,*(int *)(param_2 + 4) + 9,0x10);
  }
  smpScActCalcSharedSecret(param_1,param_2);
  return param_4;
}

