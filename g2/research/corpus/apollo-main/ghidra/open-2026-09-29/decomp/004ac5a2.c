
undefined8 FUN_004ac5a2(uint param_1,undefined *param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = param_1;
  if ((uint)*DAT_004acb00 == (param_1 & 0xff)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_3 = param_1 & 0xff;
      uVar2 = 0x195;
      param_2 = PTR_s_force_out_box_flag_already__d_004acd90;
      FUN_0043d574(3,PTR_s_box_detect_004ac81c,DAT_004ac818,PTR_s_BoxDetect_SetForceOutBox_004acd94,
                   0x195,PTR_s_force_out_box_flag_already__d_004acd90,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__box_detect_force_out_box_flag_a_004acd98,
                          PTR_s__box_detect_force_out_box_flag_a_004acd98,param_1 & 0xff,uVar2,
                          param_2,param_3);
    }
  }
  else {
    *DAT_004acb00 = (byte)param_1;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar2 = 0x19a;
      param_2 = PTR_s_force_out_box_flag_set_to__d_004acd9c;
      FUN_0043d574(3,PTR_s_box_detect_004ac81c,DAT_004ac818,PTR_s_BoxDetect_SetForceOutBox_004acd94,
                   0x19a,PTR_s_force_out_box_flag_set_to__d_004acd9c,param_1 & 0xff);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__box_detect_force_out_box_flag_s_004acda0,
                          PTR_s__box_detect_force_out_box_flag_s_004acda0,param_1 & 0xff);
    }
    FUN_004ac798();
    FUN_004abf86();
    FUN_004abec8();
    FUN_0047243a();
    if ((param_1 & 0xff) != 0) {
      FUN_004ac19c(0);
    }
  }
  return CONCAT44(param_2,uVar2);
}

