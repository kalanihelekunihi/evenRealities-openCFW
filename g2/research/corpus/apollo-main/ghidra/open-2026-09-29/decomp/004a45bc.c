
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 semantic_imu_init(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  if (param_1 < 5) {
    semantic_sensor_power_cycle();
    semantic_device_context_init();
    iVar1 = _DAT_004a50d0;
    semantic_apply_odr_config((uint)param_1 * 0x10 + _DAT_004a50d0);
    DRV_IMUSetSensorParameters((uint)param_1 * 0x10 + iVar1);
    *_DAT_004a5290 = param_1;
    uVar2 = 0;
  }
  else {
    uVar2 = 0xffffffff;
  }
  return CONCAT44(param_4,uVar2);
}

