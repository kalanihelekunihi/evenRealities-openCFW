
undefined4
smprScActSendPubKey(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  smpScActAuthSelect(param_1,param_2);
  smpScSendPubKey(param_1,param_2);
  return param_4;
}

