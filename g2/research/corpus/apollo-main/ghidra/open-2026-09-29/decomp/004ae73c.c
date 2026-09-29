
undefined4 als_function_35(undefined4 param_1,undefined1 *param_2,int param_3)

{
  undefined1 uVar1;
  int iVar2;
  undefined4 uVar3;
  bool bVar4;
  
  if (param_3 == 2) {
    uVar1 = *param_2;
    bVar4 = param_2[1] != '\0';
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004ae9e0,DAT_004ae9dc,PTR_s_ALSSyncHandler_004aea10,0x271,
                   PTR_s_ALSSyncHandler__recv_brightness__004aea18,uVar1,bVar4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc800000,PTR_s__sensor_als_ALSSyncHandler__recv_004aea1c,
                          PTR_s__sensor_als_ALSSyncHandler__recv_004aea1c,uVar1,bVar4);
    }
    settings_set_auto_brightness(uVar1);
    iVar2 = FUN_0047394c();
    (**(code **)(iVar2 + 0x14))(uVar1);
    if (bVar4) {
      setting_notify_device_status_to_app();
    }
    uVar3 = 0;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004ae9e0,DAT_004ae9dc,PTR_s_ALSSyncHandler_004aea10,0x26c,
                   PTR_s_ALSSyncHandler__data_length_erro_004aea0c,param_3);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__sensor_als_ALSSyncHandler__data_004aea14,
                          PTR_s__sensor_als_ALSSyncHandler__data_004aea14,param_3);
    }
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

