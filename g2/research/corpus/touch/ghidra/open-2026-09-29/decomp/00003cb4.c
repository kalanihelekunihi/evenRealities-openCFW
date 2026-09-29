
void touch_product_09b4_run(void)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar2 = touch_platform_1350_initialize();
  touch_platform_0338_install(0);
  if (iVar2 != 0) {
    software_bkpt(1);
  }
  logger_stub(DAT_00003eac,DAT_00003ea8,DAT_00003ea4);
  enableIRQinterrupts();
  touch_config_065c_bootstrap();
  touch_platform_0358_sample();
  touch_platform_09a4_start();
  *DAT_00003eb0 = '\x01';
  *DAT_00003eb4 = 0x280;
  iVar2 = DAT_00003eb8;
  *(undefined4 *)(DAT_00003eb8 + 0x40) = 1;
  *(undefined4 *)(iVar2 + 0x40) = 2;
  i2c_slave_init();
  touch_product_05e0_bringup();
  uVar3 = DAT_00003ebc;
  touch_sub_2ad8(DAT_00003ebc);
  touch_sub_2a90(DAT_00003ec0,uVar3);
  do {
    while( true ) {
      while( true ) {
        touch_deferred_0780_process();
        memset(DAT_00003ec4,0,0x10);
        cVar1 = *DAT_00003eb0;
        if (cVar1 != '\x02') break;
        touch_terminal_297a_conditional_call(DAT_00003ebc);
        uVar3 = Cy_SysLib_EnterCriticalSection();
        while (iVar2 = touch_state_298e_status80(DAT_00003ebc), iVar2 != 0) {
          Cy_SysPm_CpuEnterDeepSleep();
          Cy_SysLib_ExitCriticalSection(uVar3);
          uVar3 = Cy_SysLib_EnterCriticalSection();
        }
        Cy_SysLib_ExitCriticalSection(uVar3);
        uVar3 = DAT_00003ebc;
        touch_application_1904_process_three(DAT_00003ebc);
        iVar2 = capsense_widget_active_query(1,uVar3);
        if (iVar2 == 0) {
          if (*DAT_00003eb4 == 0) {
            *DAT_00003eb0 = '\x03';
            logger_stub(DAT_00003ed4,DAT_00003ea4);
          }
        }
        else {
          *DAT_00003eb0 = '\x01';
          *DAT_00003eb4 = 0x280;
          logger_stub(DAT_00003ed0,DAT_00003ea4);
          touch_sub_2a90(DAT_00003ec0,DAT_00003ebc);
        }
        report_builder();
      }
      if (cVar1 == '\x03') break;
      if (cVar1 == '\x01') {
        touch_terminal_297a_conditional_call(DAT_00003ebc);
        uVar3 = Cy_SysLib_EnterCriticalSection();
        while (iVar2 = touch_state_298e_status80(DAT_00003ebc), iVar2 != 0) {
          Cy_SysPm_CpuEnterSleep();
          Cy_SysLib_ExitCriticalSection(uVar3);
          uVar3 = Cy_SysLib_EnterCriticalSection();
        }
        Cy_SysLib_ExitCriticalSection(uVar3);
        uVar3 = DAT_00003ebc;
        touch_application_1904_process_three(DAT_00003ebc);
        iVar2 = capsense_widget_active_query(1,uVar3);
        if (iVar2 == 0) {
          iVar2 = *DAT_00003eb4;
          *DAT_00003eb4 = iVar2 + -1;
          if (iVar2 + -1 == 0) {
            *DAT_00003eb0 = '\x02';
            *DAT_00003eb4 = 0xa0;
            logger_stub(DAT_00003ec8,DAT_00003ea4);
            touch_sub_2a90(DAT_00003ecc,DAT_00003ebc);
          }
        }
        else {
          *DAT_00003eb4 = 0x280;
        }
        report_builder();
      }
      else {
        software_bkpt(1);
      }
    }
    touch_sub_3d50(DAT_00003ebc);
    uVar3 = Cy_SysLib_EnterCriticalSection();
    while (iVar2 = touch_state_298e_status80(DAT_00003ebc), iVar2 != 0) {
      Cy_SysPm_CpuEnterDeepSleep();
      Cy_SysLib_ExitCriticalSection(uVar3);
      uVar3 = Cy_SysLib_EnterCriticalSection();
    }
    Cy_SysLib_ExitCriticalSection(uVar3);
    iVar2 = touch_sub_49f8(DAT_00003ebc);
    if (iVar2 == 0) {
      *DAT_00003eb0 = '\x02';
      *DAT_00003eb4 = 0xa0;
      logger_stub(DAT_00003edc,DAT_00003ea4);
      touch_sub_2a90(DAT_00003ecc,DAT_00003ebc);
    }
    else {
      *DAT_00003eb0 = '\x01';
      *DAT_00003eb4 = 0x280;
      logger_stub(DAT_00003ed8,DAT_00003ea4);
      touch_sub_2a90(DAT_00003ec0,DAT_00003ebc);
    }
  } while( true );
}

