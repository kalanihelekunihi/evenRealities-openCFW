
undefined4 FUN_0045d1ec(void)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 in_r3;
  undefined1 auStack_30 [36];
  undefined4 uStack_c;
  
  piVar1 = DAT_0045da98;
  uStack_c = in_r3;
  iVar2 = osMessageQueueNew(0x96,4,DAT_0045da9c);
  *piVar1 = iVar2;
  if (*piVar1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_sync_module_framework_0045d7d0,
                   PTR_s_D__01_workspace_s200_ap510b_iar__0045d7cc,
                   PTR_s_SyncScheduleManagerInit_0045dc68,0x432,
                   PTR_s_create_schedule_manager_queue_fa_0045dc64);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__sync_module_framework_create_sc_0045dc6c);
    }
    uVar3 = 0xffffffff;
  }
  else {
    FUN_00439c04(auStack_30,PTR_DAT_0045dc70,0x24);
    iVar2 = osThreadNew(PTR_FUN_0045c058_1_0045dc74,0,auStack_30);
    if (iVar2 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_sync_module_framework_0045d7d0,
                     PTR_s_D__01_workspace_s200_ap510b_iar__0045d7cc,
                     PTR_s_SyncScheduleManagerInit_0045dc68,0x440,
                     PTR_s_create_schedule_manager_thread_f_0045dc78);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__sync_module_framework_create_sc_0045dc7c);
      }
      uVar3 = 0xffffffff;
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_sync_module_framework_0045d7d0,
                     PTR_s_D__01_workspace_s200_ap510b_iar__0045d7cc,
                     PTR_s_SyncScheduleManagerInit_0045dc68,0x444,
                     PTR_s_sync_schedule_manager_initialize_0045dc80);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_0045df10);
      }
      uVar3 = 0;
    }
  }
  return uVar3;
}

