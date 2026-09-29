
undefined8 FUN_0045e8d0(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int *piVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  
  cVar2 = FUN_0045a578();
  if (cVar2 == '\x01') {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_3 = 0x62c;
      FUN_0043d574(3,PTR_s_sync_module_framework_0045ec24,
                   PTR_s_D__01_workspace_s200_ap510b_iar__0045ec20,PTR_s_SyncModuleInit_0045ec1c,
                   0x62c,PTR_s_Sync_module_start_up_as_Master_0045ec18);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__sync_module_framework_Sync_modu_0045ec28,
                          PTR_s__sync_module_framework_Sync_modu_0045ec28);
    }
    piVar1 = DAT_0045ebdc;
    iVar3 = FUN_004917d2(1);
    *piVar1 = iVar3;
    if (*piVar1 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_3 = 0x62f;
        FUN_0043d574(2,PTR_s_sync_module_framework_0045ec24,
                     PTR_s_D__01_workspace_s200_ap510b_iar__0045ec20,PTR_s_SyncModuleInit_0045ec1c,
                     0x62f,PTR_s_____TF_Module_Master_Mode__start_0045ec2c);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__sync_module_framework_____TF_Mo_0045ec30);
      }
      uVar4 = 0xffffffff;
      goto LAB_0045eb74;
    }
    FUN_0045d1ec();
    FUN_00491962(*piVar1,0,PTR_FUN_0045b14c_1_0045ec34);
    FUN_00491962(*piVar1,1,PTR_FUN_0045b588_1_0045ec38);
    FUN_00491962(*piVar1,4,PTR_FUN_0045b6e4_1_0045ec3c);
  }
  else {
    if (cVar2 != '\x02') {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_3 = 0x646;
        FUN_0043d574(2,PTR_s_sync_module_framework_0045ec24,
                     PTR_s_D__01_workspace_s200_ap510b_iar__0045ec20,PTR_s_SyncModuleInit_0045ec1c,
                     0x646,PTR_s_unknown_role_init_failed____0045ec64);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__sync_module_framework_unknown_r_0045ec68);
      }
      uVar4 = 0xffffffff;
      goto LAB_0045eb74;
    }
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_3 = 0x638;
      FUN_0043d574(3,PTR_s_sync_module_framework_0045ec24,
                   PTR_s_D__01_workspace_s200_ap510b_iar__0045ec20,PTR_s_SyncModuleInit_0045ec1c,
                   0x638,PTR_s_Sync_module_start_up_as_Slave_0045ec4c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__sync_module_framework_Sync_modu_0045ec50);
    }
    piVar1 = DAT_0045ebdc;
    iVar3 = FUN_004917d2(0);
    *piVar1 = iVar3;
    if (*piVar1 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_3 = 0x63b;
        FUN_0043d574(2,PTR_s_sync_module_framework_0045ec24,
                     PTR_s_D__01_workspace_s200_ap510b_iar__0045ec20,PTR_s_SyncModuleInit_0045ec1c,
                     0x63b,PTR_s_____TF_Module_Slave_Mode__start_f_0045ec54);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__sync_module_framework_____TF_Mo_0045ec58);
      }
      uVar4 = 0xffffffff;
      goto LAB_0045eb74;
    }
    FUN_00491962(*piVar1,2,PTR_FUN_0045adf4_1_0045ec5c);
    FUN_00491962(*piVar1,3,PTR_FUN_0045b850_1_0045ec60);
    FUN_00491962(*piVar1,1,PTR_FUN_0045b588_1_0045ec38);
    FUN_00491962(*piVar1,4,PTR_FUN_0045b6e4_1_0045ec3c);
  }
  piVar1 = DAT_0045ebc8;
  iVar3 = osMessageQueueNew(0x96,4,PTR_DAT_0045ec40);
  *piVar1 = iVar3;
  if (*piVar1 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_3 = 0x64e;
      FUN_0043d574(1,PTR_s_sync_module_framework_0045ec24,
                   PTR_s_D__01_workspace_s200_ap510b_iar__0045ec20,PTR_s_SyncModuleInit_0045ec1c,
                   0x64e,PTR_s_create_send_data_msg_queue_faile_0045ec44);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__sync_module_framework_create_se_0045ec48);
    }
    uVar4 = 0xffffffff;
  }
  else {
    iVar3 = FUN_0049137a();
    if (iVar3 == 0) {
      iVar3 = FUN_0045d34c();
      if (iVar3 == 0) {
        uVar4 = 0;
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          param_3 = 0x658;
          FUN_0043d574(1,PTR_s_sync_module_framework_0045ec24,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0045ec20,PTR_s_SyncModuleInit_0045ec1c
                       ,0x658,PTR_s_create_sync_timeout_detection_ti_0045ec74);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4000000,PTR_s__sync_module_framework_create_sy_0045ec78);
        }
        uVar4 = 0xffffffff;
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_3 = 0x653;
        FUN_0043d574(1,PTR_s_sync_module_framework_0045ec24,
                     PTR_s_D__01_workspace_s200_ap510b_iar__0045ec20,PTR_s_SyncModuleInit_0045ec1c,
                     0x653,PTR_s_create_thread_poll_failed__0045ec6c);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__sync_module_framework_create_th_0045ec70);
      }
      uVar4 = 0xffffffff;
    }
  }
LAB_0045eb74:
  return CONCAT44(param_3,uVar4);
}

