
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
slave_adv_stop_flag_or_0046f2dc
          (undefined4 param_1,undefined *param_2,uint param_3,undefined4 param_4)

{
  byte *pbVar1;
  int iVar2;
  
  pbVar1 = _DAT_0046f488;
  *_DAT_0046f488 = (byte)param_1 | *_DAT_0046f488;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_3 = (uint)*pbVar1;
    param_1 = 0x327;
    param_2 = PTR_s_APP_BleSlaveSetKeepConnectFlag___0046f48c;
    FUN_0043d574(4,DAT_0046f404,DAT_0046f400,PTR_s_APP_BleSlaveSetKeepConnectFlag_0046f490,0x327,
                 PTR_s_APP_BleSlaveSetKeepConnectFlag___0046f48c,param_3,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__ble_Slave_APP_BleSlaveSetKeepCo_0046f494,
                        PTR_s__ble_Slave_APP_BleSlaveSetKeepCo_0046f494,*pbVar1,param_1,param_2,
                        param_3);
  }
  return CONCAT44(param_2,param_1);
}

