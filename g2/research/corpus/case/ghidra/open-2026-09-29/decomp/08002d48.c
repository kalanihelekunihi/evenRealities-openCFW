
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_08002d48(void)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 in_r3;
  char cVar4;
  undefined4 local_10;
  
  local_10 = in_r3;
  HAL_FLASH_OB_Unlock();
  puVar1 = DAT_08002dbc;
  local_10 = 0;
  *DAT_08002dbc = 2;
  if (*(char *)(DAT_08002dc0 + 0x18) == '\x01') {
    uVar3 = 0x8000;
  }
  else {
    uVar3 = 4;
  }
  puVar1[1] = uVar3;
  puVar1[2] = 0;
  puVar1[3] = 0x80;
  cVar4 = '\0';
  while( true ) {
    iVar2 = case_run_controller_range(DAT_08002dbc,&local_10);
    if (iVar2 == 0) {
      case_flag31_set();
      return 1;
    }
    if (cVar4 == '\x03') break;
    osDelay(200);
    cVar4 = cVar4 + '\x01';
  }
  if (*_DAT_08002dc4 == '\0') {
    g2_log_printf(s__OTA_BOX__fail_to_erase__d_pages_08002dc7 + 1,0x80,local_10,4);
    g2_log_printf(&DAT_08002e00);
  }
  case_flag31_set();
  return 0;
}

