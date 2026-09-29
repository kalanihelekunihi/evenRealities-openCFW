
undefined8
HUB_IMUFuncCloseHandler(int param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = *(uint *)(param_1 + 4);
  if ((uVar3 & 0xff) < 6) {
    uVar2 = uVar3 & 0xff;
    if (uVar2 == 1) {
      semantic_set_state_20074674(0);
    }
    else if (uVar2 != 0) {
      if (uVar2 == 3) {
        semantic_set_state_2007467c(0);
      }
      else if (uVar2 < 3) {
        semantic_set_state_20074678(0);
      }
      else if (uVar2 == 5) {
        semantic_set_state_20074680(0);
      }
      else if (uVar2 < 5) {
        als_function_29();
        goto LAB_004a7342;
      }
    }
    iVar1 = semantic_get_state_2007467c();
    if (iVar1 == 1) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_1 = 0x1fb;
        param_2 = PTR_s_FuncClose_func_type__d__set_work_004a7420;
        FUN_0043d574(2,PTR_s_sensor_hub_004a73ec,PTR_s_D__01_workspace_s200_ap510b_iar__004a73e8,
                     PTR_s_HUB_IMUFuncCloseHandler_004a741c,0x1fb,
                     PTR_s_FuncClose_func_type__d__set_work_004a7420,uVar3 & 0xff);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__sensor_hub_FuncClose_func_type__004a7424,
                            PTR_s__sensor_hub_FuncClose_func_type__004a7424,uVar3 & 0xff);
      }
      hub_msg_send_id1(1);
    }
    else {
      iVar1 = semantic_get_state_20074678();
      if (iVar1 == 1) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          param_1 = 0x1fe;
          param_2 = PTR_s_FuncClose_func_type__d__set_work_004a7428;
          FUN_0043d574(2,PTR_s_sensor_hub_004a73ec,PTR_s_D__01_workspace_s200_ap510b_iar__004a73e8,
                       PTR_s_HUB_IMUFuncCloseHandler_004a741c,0x1fe,
                       PTR_s_FuncClose_func_type__d__set_work_004a7428,uVar3 & 0xff);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__sensor_hub_FuncClose_func_type__004a742c,
                              PTR_s__sensor_hub_FuncClose_func_type__004a742c,uVar3 & 0xff);
        }
        hub_msg_send_id1(2);
      }
      else {
        iVar1 = semantic_get_state_20074674();
        if ((iVar1 == 1) || (iVar1 = semantic_get_state_20074680(), iVar1 == 1)) {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            param_1 = 0x201;
            param_2 = PTR_s_FuncClose_func_type__d__set_work_004a7430;
            FUN_0043d574(2,PTR_s_sensor_hub_004a73ec,PTR_s_D__01_workspace_s200_ap510b_iar__004a73e8
                         ,PTR_s_HUB_IMUFuncCloseHandler_004a741c,0x201,
                         PTR_s_FuncClose_func_type__d__set_work_004a7430,uVar3 & 0xff);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x8400000,PTR_s__sensor_hub_FuncClose_func_type__004a7434,
                                PTR_s__sensor_hub_FuncClose_func_type__004a7434,uVar3 & 0xff);
          }
          hub_msg_send_id1(0);
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            param_1 = 0x204;
            param_2 = PTR_s_FuncClose_func_type__d__power_of_004a7438;
            FUN_0043d574(2,PTR_s_sensor_hub_004a73ec,PTR_s_D__01_workspace_s200_ap510b_iar__004a73e8
                         ,PTR_s_HUB_IMUFuncCloseHandler_004a741c,0x204,
                         PTR_s_FuncClose_func_type__d__power_of_004a7438,uVar3 & 0xff);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x8400000,PTR_s__sensor_hub_FuncClose_func_type__004a743c,
                                PTR_s__sensor_hub_FuncClose_func_type__004a743c,uVar3 & 0xff);
          }
          semantic_sensor_reset_line();
        }
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_1 = 0x1e4;
      param_2 = PTR_s_FuncOpen_func_type_error_004a73e0;
      FUN_0043d574(1,PTR_s_sensor_hub_004a73ec,PTR_s_D__01_workspace_s200_ap510b_iar__004a73e8,
                   PTR_s_HUB_IMUFuncCloseHandler_004a741c,0x1e4,
                   PTR_s_FuncOpen_func_type_error_004a73e0,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__sensor_hub_FuncOpen_func_type_e_004a73f0,
                          PTR_s__sensor_hub_FuncOpen_func_type_e_004a73f0);
    }
  }
LAB_004a7342:
  return CONCAT44(param_2,param_1);
}

