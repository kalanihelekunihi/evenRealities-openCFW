
undefined4
smprScActJwncSendCnf(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  smpLogByteArray(PTR_s_JWNC_Confirm_005e4218,*(undefined4 *)(param_2 + 4),0x10);
  smpScSendPairCnf(param_1,param_2,*(undefined4 *)(param_2 + 4));
  return param_4;
}

