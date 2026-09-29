
undefined8
HUB_IMUFuncOpenHandler(int param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = *(uint *)(param_1 + 4);
  if (5 < (uVar3 & 0xff)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_1 = 0x1b8;
      param_2 = PTR_s_FuncOpen_func_type_error_004a73e0;
      FUN_0043d574(1,PTR_s_sensor_hub_004a73ec,PTR_s_D__01_workspace_s200_ap510b_iar__004a73e8,
                   PTR_s_HUB_IMUFuncOpenHandler_004a73e4,0x1b8,
                   PTR_s_FuncOpen_func_type_error_004a73e0,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__sensor_hub_FuncOpen_func_type_e_004a73f0,
                          PTR_s__sensor_hub_FuncOpen_func_type_e_004a73f0);
    }
    goto LAB_004a7138;
  }
  uVar2 = uVar3 & 0xff;
  if (uVar2 != 1) {
    if (uVar2 == 0) goto LAB_004a7138;
    if (uVar2 == 3) {
      semantic_set_state_2007467c(1);
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_1 = 0x1d5;
        param_2 = PTR_s_FuncOpen_func_type__d__set_work_m_004a7414;
        FUN_0043d574(2,PTR_s_sensor_hub_004a73ec,PTR_s_D__01_workspace_s200_ap510b_iar__004a73e8,
                     PTR_s_HUB_IMUFuncOpenHandler_004a73e4,0x1d5,
                     PTR_s_FuncOpen_func_type__d__set_work_m_004a7414,uVar3 & 0xff);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__sensor_hub_FuncOpen_func_type___004a7418,
                            PTR_s__sensor_hub_FuncOpen_func_type___004a7418,uVar3 & 0xff);
      }
      hub_msg_send_id1(1);
      goto LAB_004a7138;
    }
    if (uVar2 < 3) {
      semantic_set_state_20074678(1);
      iVar1 = semantic_get_state_2007467c();
      if (iVar1 == 1) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          param_1 = 0x1cd;
          param_2 = PTR_s_FuncOpen_func_type__d__but_dis_i_004a7404;
          FUN_0043d574(2,PTR_s_sensor_hub_004a73ec,PTR_s_D__01_workspace_s200_ap510b_iar__004a73e8,
                       PTR_s_HUB_IMUFuncOpenHandler_004a73e4,0x1cd,
                       PTR_s_FuncOpen_func_type__d__but_dis_i_004a7404,uVar3 & 0xff);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__sensor_hub_FuncOpen_func_type___004a7408,
                              PTR_s__sensor_hub_FuncOpen_func_type___004a7408,uVar3 & 0xff);
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          param_1 = 0x1cf;
          param_2 = PTR_s_FuncOpen_func_type__d__set_work_m_004a740c;
          FUN_0043d574(2,PTR_s_sensor_hub_004a73ec,PTR_s_D__01_workspace_s200_ap510b_iar__004a73e8,
                       PTR_s_HUB_IMUFuncOpenHandler_004a73e4,0x1cf,
                       PTR_s_FuncOpen_func_type__d__set_work_m_004a740c,uVar3 & 0xff);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__sensor_hub_FuncOpen_func_type___004a7410,
                              PTR_s__sensor_hub_FuncOpen_func_type___004a7410,uVar3 & 0xff);
        }
        hub_msg_send_id1(2);
      }
      goto LAB_004a7138;
    }
    if (uVar2 != 5) {
      if (uVar2 < 5) {
        als_function_28();
      }
      goto LAB_004a7138;
    }
  }
  if ((uVar3 & 0xff) == 1) {
    semantic_set_state_20074674(1);
  }
  else if ((uVar3 & 0xff) == 5) {
    semantic_set_state_20074680(1);
  }
  iVar1 = semantic_get_state_2007467c();
  if ((iVar1 == 1) || (iVar1 = semantic_get_state_20074678(), iVar1 == 1)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_1 = 0x1c4;
      param_2 = PTR_s_FuncOpen_func_type__d__but_dis_o_004a73f4;
      FUN_0043d574(2,PTR_s_sensor_hub_004a73ec,PTR_s_D__01_workspace_s200_ap510b_iar__004a73e8,
                   PTR_s_HUB_IMUFuncOpenHandler_004a73e4,0x1c4,
                   PTR_s_FuncOpen_func_type__d__but_dis_o_004a73f4,uVar3 & 0xff);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,PTR_s__sensor_hub_FuncOpen_func_type___004a73f8,
                          PTR_s__sensor_hub_FuncOpen_func_type___004a73f8,uVar3 & 0xff);
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_1 = 0x1c6;
      param_2 = PTR_s_FuncOpen_func_type__d__set_work_m_004a73fc;
      FUN_0043d574(2,PTR_s_sensor_hub_004a73ec,PTR_s_D__01_workspace_s200_ap510b_iar__004a73e8,
                   PTR_s_HUB_IMUFuncOpenHandler_004a73e4,0x1c6,
                   PTR_s_FuncOpen_func_type__d__set_work_m_004a73fc,uVar3 & 0xff);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,PTR_s__sensor_hub_FuncOpen_func_type___004a7400,
                          PTR_s__sensor_hub_FuncOpen_func_type___004a7400,uVar3 & 0xff);
    }
    hub_msg_send_id1(0);
  }
LAB_004a7138:
  return CONCAT44(param_2,param_1);
}

