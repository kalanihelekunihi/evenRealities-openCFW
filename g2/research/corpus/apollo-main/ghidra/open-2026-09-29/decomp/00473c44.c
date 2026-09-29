
void FUN_00473c44(void)

{
  int *piVar1;
  char cVar2;
  int iVar3;
  undefined4 local_38;
  undefined4 local_34;
  int local_30;
  int local_2c;
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  uint local_10;
  int local_c;
  
  FUN_004739fc();
  FUN_00473abc();
  uled_mspi_init();
  FUN_00473ac6();
  FUN_00473ad0();
  do {
    while( true ) {
      do {
        FUN_0043c0e4(&local_2c,0x24,0);
        iVar3 = osMessageQueueGet(*(undefined4 *)(DAT_004742f8 + 0xc),&local_2c,0,0xffffffff);
      } while (iVar3 != 0);
      task_vote_acquire_current();
      if (local_2c == 3) {
        FUN_0046ca14();
        FUN_0047386a();
      }
      iVar3 = SVC_Settings_UledCtrlCheck();
      piVar1 = DAT_004744a8;
      if ((iVar3 != 0) || (local_c != 0)) break;
      task_vote_release_current();
    }
    if (local_2c == 0) {
      uled_driver_power_up();
    }
    else if (local_2c == 1) {
      uled_driver_init();
      FUN_00473b34();
      *DAT_004744a8 = 1;
    }
    else if (local_2c == 2) {
      if (*DAT_004744a8 == 1) {
        uled_clearScreen();
      }
    }
    else if (local_2c == 3) {
      if (*DAT_004744a8 == 1) {
        local_34 = local_14;
        local_38 = local_18;
        uled_QSPI_PartialReflash_async(local_28,local_24,local_20,local_1c);
      }
    }
    else if (local_2c == 4) {
      if (*DAT_004744a8 == 1) {
        local_34 = 0;
        local_38 = 0;
        SVC_Settings_BrightnessLevelToLumAndCurrent(local_10,&local_38,&local_34);
        uled_mspi_setBrightness(local_10,local_34,local_38);
      }
    }
    else if (local_2c == 5) {
      if (*DAT_004744a8 == 1) {
        FUN_00473b46();
        uled_driver_power_down();
        *piVar1 = 0;
      }
    }
    else if (local_2c == 6) {
      if ((*DAT_004744a8 == 1) && (cVar2 = uled_status_check_and_recovery(1), cVar2 == '\0')) {
        FUN_0046ca14();
        FUN_0047386a();
        local_34 = local_14;
        local_38 = local_18;
        uled_QSPI_PartialReflash_async(local_28,local_24,local_20,local_1c);
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          local_34 = DAT_004744ac;
          local_38 = 0x10d;
          FUN_0043d574(3,PTR_s_task_displaydrvmgr_0047430c,DAT_00474308,DAT_004744b0);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_004744b4,DAT_004744b4);
        }
      }
    }
    else if (local_2c == 8) {
      if (*DAT_004744a8 == 1) {
        uled_set_mode(local_10 & 0xff);
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_30 = local_2c;
        local_34 = DAT_004744b8;
        local_38 = 0x117;
        FUN_0043d574(2,PTR_s_task_displaydrvmgr_0047430c,DAT_00474308,DAT_004744b0);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_004744bc,DAT_004744bc,local_2c);
      }
    }
    task_vote_release_current();
  } while( true );
}

