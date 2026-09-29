
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
HUB_IMUSetModeHandler(int param_1,undefined4 param_2,undefined *param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  
  puVar1 = _DAT_004a738c;
  if (*(uint *)(param_1 + 4) < 5) {
    *_DAT_004a738c = 0;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_4 = *(undefined4 *)(param_1 + 4);
      param_2 = 0x122;
      param_3 = PTR_s__HUB_IMUSetModeHandler_set_mode__004a7390;
      FUN_0043d574(1,DAT_004a6ee0,DAT_004a6edc,PTR_s_HUB_IMUSetModeHandler_004a7394,0x122,
                   PTR_s__HUB_IMUSetModeHandler_set_mode__004a7390,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__sensor_hub__HUB_IMUSetModeHandl_004a7398,
                          PTR_s__sensor_hub__HUB_IMUSetModeHandl_004a7398,
                          *(undefined4 *)(param_1 + 4),param_2,param_3,param_4);
    }
    semantic_imu_init(*(uint *)(param_1 + 4) & 0xff);
    *puVar1 = 1;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x126;
      param_3 = PTR_s__HUB_IMUSetMode_set_mode_error_004a739c;
      FUN_0043d574(1,DAT_004a6ee0,DAT_004a6edc,PTR_s_HUB_IMUSetModeHandler_004a7394);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__sensor_hub__HUB_IMUSetMode_set_m_004a73a0);
    }
  }
  return CONCAT44(param_3,param_2);
}

