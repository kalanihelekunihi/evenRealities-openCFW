
undefined8 FUN_00466ea2(undefined4 param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  
  uVar3 = param_1;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uVar3 = 0x14a;
    param_2 = PTR_s_set_x_coordinate_level____d_00467514;
    param_3 = param_1;
    FUN_0043d574(3,PTR_s_setting_004672f0,PTR_s_D__01_workspace_s200_ap510b_iar__004672ec,
                 PTR_s_setting_handle_x_coordinate_sett_00467518,0x14a,
                 PTR_s_set_x_coordinate_level____d_00467514,param_1,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if (-1 < iVar2 << 0x1f) {
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1d) goto LAB_00466eee;
  }
  compress_log_output(0xc400000,PTR_s__setting_set_x_coordinate_level___0046751c,
                      PTR_s__setting_set_x_coordinate_level___0046751c,param_1,uVar3,param_2,param_3
                     );
LAB_00466eee:
  iVar2 = settings_get_config();
  *(char *)(iVar2 + 9) = (char)param_1;
  iVar2 = FUN_00443484();
  if (iVar2 == 0) {
    cVar1 = FUN_0045a570();
    if (cVar1 == '\x01') {
      FUN_00466890();
    }
  }
  else {
    FUN_0049c0dc();
  }
  cVar1 = FUN_0045a570();
  if (cVar1 == '\x01') {
    FUN_00465748(6,0xc,param_1,0);
  }
  return CONCAT44(param_2,uVar3);
}

