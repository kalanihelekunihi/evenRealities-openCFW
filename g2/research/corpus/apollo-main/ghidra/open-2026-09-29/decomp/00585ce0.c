
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_00585ce0(undefined4 param_1,int param_2,undefined *param_3,undefined4 *param_4)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  undefined4 *puVar4;
  
  if ((*_DAT_00586398 == 0) && (param_2 != 0)) {
    *_DAT_00586398 = param_2;
  }
  if (param_3 == (undefined1 *)0x42) {
    *_DAT_0058639c = 1;
    puVar4 = (undefined4 *)0x0;
    if (param_4 != (undefined4 *)0x0) {
      puVar4 = (undefined4 *)*param_4;
    }
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x85;
      param_3 = PTR_s_foregroundID____d_005863a0;
      param_4 = puVar4;
      FUN_0043d574(3,PTR_s_navigation_main_005863ac,PTR_s_D__01_workspace_s200_ap510b_iar__005863a8,
                   PTR_s_navigation_page_event_handler_005863a4,0x85,
                   PTR_s_foregroundID____d_005863a0,puVar4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__navigation_main_foregroundID_____005863b0,
                          PTR_s__navigation_main_foregroundID_____005863b0,puVar4,param_2,param_3,
                          param_4);
    }
    piVar1 = _DAT_005863b4;
    if (((*_DAT_005863b4 != 0) && (puVar4 != (undefined4 *)0x0)) && (puVar4 != (undefined4 *)0x21))
    {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_2 = 0x88;
        FUN_0043d574(4,PTR_s_navigation_main_005863ac,
                     PTR_s_D__01_workspace_s200_ap510b_iar__005863a8,
                     PTR_s_navigation_page_event_handler_005863a4,0x88,_DAT_005863b8);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,_DAT_005863bc,_DAT_005863bc);
      }
      FUN_00441488(*piVar1,0x7f,0);
      *_DAT_005863c0 = 1;
    }
  }
  else if (param_3 == (undefined1 *)0x43) {
    *_DAT_0058639c = 0;
    piVar2 = _DAT_005863c0;
    piVar1 = _DAT_005863b4;
    if ((*_DAT_005863b4 != 0) && (*_DAT_005863c0 == 1)) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_2 = 0x92;
        FUN_0043d574(4,PTR_s_navigation_main_005863ac,
                     PTR_s_D__01_workspace_s200_ap510b_iar__005863a8,
                     PTR_s_navigation_page_event_handler_005863a4,0x92,_DAT_005863c4);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,_DAT_005863c8,_DAT_005863c8);
      }
      FUN_00441488(*piVar1,0xff,0);
      *piVar2 = 0;
    }
    if ((*_DAT_005863cc == 1) && (iVar3 = FUN_0045a568(), iVar3 == 1)) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_2 = 0x99;
        FUN_0043d574(3,PTR_s_navigation_main_005863ac,
                     PTR_s_D__01_workspace_s200_ap510b_iar__005863a8,
                     PTR_s_navigation_page_event_handler_005863a4,0x99,
                     PTR_s_stop_process_break_RequestDispla_005863d0);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__navigation_main__stop_process_b_005863d4,
                            PTR_s__navigation_main__stop_process_b_005863d4);
      }
      FUN_00464c36(8,0,0,0);
    }
  }
  else if (param_3 == (undefined1 *)0xa) {
    iVar3 = FUN_0045a568();
    if (iVar3 != 2) {
      FUN_00548f80(10,param_4);
    }
  }
  else if (param_3 == (undefined1 *)0x44) {
    iVar3 = FUN_0045a568();
    if (iVar3 != 2) {
      FUN_00548f80(0x44,param_4);
    }
  }
  else if (param_3 == (undefined1 *)0x45) {
    iVar3 = FUN_0045a568();
    if (iVar3 != 2) {
      FUN_00548f80(0x45,param_4);
    }
  }
  else if (param_3 == &SUB_00000048) {
    iVar3 = FUN_0045a568();
    if (iVar3 != 2) {
      FUN_00548f80(0x48,param_4);
    }
  }
  else if (param_3 == &IRQ) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0xbb;
      FUN_0043d574(4,PTR_s_navigation_main_005863ac,PTR_s_D__01_workspace_s200_ap510b_iar__005863a8,
                   PTR_s_navigation_page_event_handler_005863a4,0xbb,
                   PTR_s_IMU_Reflash_Event__005863d8);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__navigation_main_IMU_Reflash_Eve_005863dc,
                          PTR_s__navigation_main_IMU_Reflash_Eve_005863dc);
    }
    iVar3 = FUN_0045a568();
    if (iVar3 != 2) {
      FUN_00548f80(0x40,param_4);
    }
  }
  else if (param_3 == (undefined1 *)0x41) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0xc3;
      FUN_0043d574(4,PTR_s_navigation_main_005863ac,PTR_s_D__01_workspace_s200_ap510b_iar__005863a8,
                   PTR_s_navigation_page_event_handler_005863a4,0xc3,
                   PTR_s_IMU_compass_Event__005863e0);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__navigation_main_IMU_compass_Eve_005863e4,
                          PTR_s__navigation_main_IMU_compass_Eve_005863e4);
    }
    iVar3 = FUN_0045a568();
    if (iVar3 != 2) {
      FUN_00548f80(0x41,param_4);
    }
  }
  else if (param_3 == (undefined1 *)0x50) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0xcb;
      FUN_0043d574(4,PTR_s_navigation_main_005863ac,PTR_s_D__01_workspace_s200_ap510b_iar__005863a8,
                   PTR_s_navigation_page_event_handler_005863a4,0xcb,
                   PTR_s_IMU_compass_Event__005863e0);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__navigation_main_IMU_compass_Eve_005863e4,
                          PTR_s__navigation_main_IMU_compass_Eve_005863e4);
    }
    iVar3 = FUN_0045a568();
    if (iVar3 != 2) {
      FUN_00548f80(0x50,param_4);
    }
  }
  else if (param_3 == (undefined1 *)0x4f) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0xd3;
      FUN_0043d574(4,PTR_s_navigation_main_005863ac,PTR_s_D__01_workspace_s200_ap510b_iar__005863a8,
                   PTR_s_navigation_page_event_handler_005863a4,0xd3,
                   PTR_s_PAGE_EVENT_SYSTEM_EXIT_NOTIFY_Ev_005863e8);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__navigation_main_PAGE_EVENT_SYST_005863ec,
                          PTR_s__navigation_main_PAGE_EVENT_SYST_005863ec);
    }
    iVar3 = FUN_0045a568();
    if (iVar3 != 2) {
      FUN_00548f80(0x4f,param_4);
    }
  }
  return CONCAT44(param_2,1);
}

