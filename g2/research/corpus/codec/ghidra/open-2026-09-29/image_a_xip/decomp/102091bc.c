
undefined4 gx8002_i2s_request_tick(void)

{
  int *piVar1;
  int iVar2;
  char *pcVar3;
  undefined4 uVar4;
  int iVar5;
  
  piVar1 = piRam1020923c;
  gx8002_notification_poll();
  pcVar3 = pcRam10209244;
  iVar2 = iRam10209240;
  if (*piVar1 == 1) {
    gx8002_printf(PTR_s_processing_i2s_status_request__m_10209248,*pcRam10209244);
    if (*pcVar3 == '\x01') {
      gx8002_power_lock(*(undefined4 *)(iVar2 + 8));
      gx8002_printf(PTR_s______I2S_output_requested__lock___1020924c);
      gx8002_start_i2s();
      gx8002_i2s_ack();
      *piVar1 = 0;
    }
    else if (*pcVar3 == '\0') {
      gx8002_stop_i2s();
      gx8002_i2s_ack();
      uVar4 = *(undefined4 *)(iVar2 + 8);
      *piVar1 = 0;
      gx8002_power_unlock(uVar4);
      gx8002_printf(PTR_s______I2S_output_requested__unloc_10209254);
      gx8002_power_suspend(0xd);
    }
  }
  if (0 < *(int *)(iVar2 + 0xc)) {
    iVar5 = *(int *)(iVar2 + 0xc) + -10;
    *(int *)(iVar2 + 0xc) = iVar5;
    if ((iVar5 < 1) && (*(int *)(iVar2 + 0x14) == 0)) {
      gx8002_printf(PTR_s__YW_APP_UART_wakeup_timeout__unl_10209250);
      gx8002_power_unlock(*(undefined4 *)(iVar2 + 8));
      *(undefined4 *)(iVar2 + 0xc) = 0;
    }
  }
  return 0;
}

