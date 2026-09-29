
undefined4
dmConnSmEventDispatch(undefined1 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  if (param_2 != 0) {
    _bleSlaveProcMsg(param_2);
  }
  APP_ConnectParamHandler(param_1,param_2);
  APP_EvenOtaProcMsg(param_1,param_2);
  APP_BleEusProcMsg(param_1,param_2);
  APP_BleEssProcMsg(param_1,param_2);
  APP_BleEfsProcMsg(param_1,param_2);
  APP_BleNusProcMsg(param_1,param_2);
  profileAnccProcMsg(param_1,param_2);
  return param_4;
}

