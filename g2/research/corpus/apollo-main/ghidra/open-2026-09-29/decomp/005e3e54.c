
undefined4 smprScActJwncCalcG2(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  WStrReverseCpy(*(undefined4 *)(*(int *)(param_1 + 0x48) + 0x14),*(int *)(param_2 + 4) + 9,0x10);
  smpScActJwncCalcG2(param_1,param_2);
  return param_4;
}

