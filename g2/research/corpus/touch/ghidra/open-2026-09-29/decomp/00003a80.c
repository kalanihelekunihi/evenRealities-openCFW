
void touch_deferred_0780_process(void)

{
  char cVar1;
  char cVar2;
  char *pcVar3;
  int iVar4;
  undefined2 local_14 [2];
  
  Cy_SysLib_EnterCriticalSection();
  pcVar3 = DAT_00003ae0;
  cVar1 = *DAT_00003adc;
  cVar2 = *DAT_00003ae0;
  local_14[0] = *DAT_00003ae4;
  *DAT_00003adc = '\0';
  *pcVar3 = '\0';
  Cy_SysLib_ExitCriticalSection();
  if (cVar1 != '\0') {
    touch_startup_0d4c_initialize(DAT_00003ae8,local_14);
  }
  if (cVar2 != '\0') {
    iVar4 = touch_config_load_from_eeprom();
    if (iVar4 == 0) {
      logger_stub(DAT_00003af8,*(undefined2 *)(DAT_00003af4 + 6),DAT_00003aec);
    }
    else {
      logger_stub(DAT_00003af0,iVar4,DAT_00003aec);
    }
  }
  return;
}

