
undefined4
ring_dm_event_dispatch(undefined1 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  if (param_2 != 0) {
    _masterProcMsg(param_2);
  }
  APP_BleRingProcMsg(param_1,param_2);
  return param_4;
}

