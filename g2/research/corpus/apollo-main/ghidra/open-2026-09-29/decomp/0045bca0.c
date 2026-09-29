
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0045bca0(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  short *psVar2;
  int *piVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  
  iVar4 = FUN_0045a568();
  piVar3 = _DAT_0045c018;
  piVar1 = DAT_0045bff0;
  if (iVar4 == 2) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_sync_module_framework_0045c010,
                   PTR_s_D__01_workspace_s200_ap510b_iar__0045c00c,
                   PTR_s_DispStartBlockingEn_0045c008,0x2bd,
                   PTR_s_slave_role_don_t_need_to_block_0045c004,param_3,param_4);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__sync_module_framework_slave_rol_0045c014,
                          PTR_s__sync_module_framework_slave_rol_0045c014);
    }
    uVar5 = 0xfffffffe;
  }
  else {
    if ((*_DAT_0045c018 != 0) && (*DAT_0045bff0 != 0)) {
      if (15000 < param_1) {
        param_1 = 15000;
      }
      iVar4 = osMutexAcquire(*DAT_0045bff0,0xffffffff);
      psVar2 = DAT_0045bff4;
      if (iVar4 != 0) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_sync_module_framework_0045c010,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0045c00c,
                       PTR_s_DispStartBlockingEn_0045c008,0x2ca,
                       PTR_s_DispStartBlockingEn__mutex_acqui_0045c024,param_3,param_4);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x4000000,PTR_s__sync_module_framework_DispStart_0045c028,
                              PTR_s__sync_module_framework_DispStart_0045c028);
        }
        return 0xffffffff;
      }
      uVar5 = 0;
      if (*DAT_0045bff4 == 0) {
        *DAT_0045bff4 = 1;
        iVar4 = osTimerStart(*piVar3,param_1);
        if (iVar4 == 0) {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(3,PTR_s_sync_module_framework_0045c010,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0045c00c,
                         PTR_s_DispStartBlockingEn_0045c008,0x2d9,
                         PTR_s_DispStartBlockingEn__timeout__u_m_0045c034,param_1,param_4);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0xc400000,PTR_s__sync_module_framework_DispStart_0045c038,
                                PTR_s__sync_module_framework_DispStart_0045c038,param_1);
          }
        }
        else {
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            FUN_0043d574(1,PTR_s_sync_module_framework_0045c010,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0045c00c,
                         PTR_s_DispStartBlockingEn_0045c008,0x2d5,
                         PTR_s_DispStartBlockingEn__osTimerStar_0045c02c,iVar4,param_4);
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x4400000,PTR_s__sync_module_framework_DispStart_0045c030,
                                PTR_s__sync_module_framework_DispStart_0045c030,iVar4);
          }
          *psVar2 = 0;
          uVar5 = 0xffffffff;
        }
      }
      else {
        uVar5 = 0xffffffff;
      }
      osMutexRelease(*piVar1);
      return uVar5;
    }
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_sync_module_framework_0045c010,
                   PTR_s_D__01_workspace_s200_ap510b_iar__0045c00c,
                   PTR_s_DispStartBlockingEn_0045c008,0x2c1,
                   PTR_s_DispStartBlockingEn__timer_mutex_0045c01c,param_3,param_4);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__sync_module_framework_DispStart_0045c020);
    }
    uVar5 = 0xffffffff;
  }
  return uVar5;
}

