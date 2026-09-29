
undefined8
HUB_ParameterConfig(char param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  
  puVar3 = param_2;
  iVar1 = hub_role_get();
  if (iVar1 == 2) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      puVar3 = (undefined4 *)0x1a1;
      FUN_0043d574(1,DAT_004a6ee0,DAT_004a6edc,DAT_004a73d8,0x1a1,DAT_004a73d4,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__sensor_hub_IMU_open_role_type_i_004a73dc,
                          PTR_s__sensor_hub_IMU_open_role_type_i_004a73dc);
    }
    uVar2 = 0xffffffff;
  }
  else {
    if (param_1 == '\x01') {
      semantic_set_motion_threshold(*param_2);
    }
    else if (param_1 == '\x02') {
      semantic_set_motion_period(*param_2,param_2[1]);
    }
    else if ((param_1 != '\x03') && (param_1 == '\x05')) {
      DRV_IMUAccelConfig(*param_2);
    }
    uVar2 = 0;
  }
  return CONCAT44(puVar3,uVar2);
}

