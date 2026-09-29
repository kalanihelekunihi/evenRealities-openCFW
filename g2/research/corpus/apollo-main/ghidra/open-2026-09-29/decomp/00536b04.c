
undefined4
dmConnSmActAcceptFailed(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  dmAdvConnectFailed();
  dmConnSmActConnFailed(param_1,param_2);
  return param_4;
}

