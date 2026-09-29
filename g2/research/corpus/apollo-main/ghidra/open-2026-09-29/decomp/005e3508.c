
undefined4 smpiScActJwncCalcF4(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  WStrReverseCpy(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x10,*(int *)(param_2 + 4) + 9,0x10);
  smpScActJwncCalcF4(param_1,param_2);
  return param_4;
}

