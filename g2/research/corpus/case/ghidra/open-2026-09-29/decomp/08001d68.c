
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void ota_result_inform_glasses(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  char *pcVar2;
  undefined1 uVar3;
  uint uVar4;
  byte bVar5;
  undefined4 local_20;
  undefined4 local_1c;
  uint local_18;
  
  pcVar2 = DAT_08001e18;
  local_20 = param_2;
  local_1c = param_3;
  local_18 = param_4;
  while (*pcVar2 != '\0') {
    osDelay(100);
  }
  if (*_DAT_08001e1c == '\0') {
    g2_log_printf(s__OTA_BOX___Inform_GLS_ota_result_08001e1f + 1,param_1);
    g2_log_printf(&DAT_08001e48);
  }
  local_20 = DAT_08001e4c;
  if (param_1 == 0) {
    local_1c._0_3_ = 0x20100;
    uVar3 = 0x39;
    uVar4 = DAT_08001e54;
  }
  else {
    local_1c._0_3_ = CONCAT12(*(byte *)(_DAT_08001e58 + 0x1c),0x101);
    uVar3 = *(undefined1 *)(_DAT_08001e58 + 0x1d);
    uVar4 = (uint)*(byte *)(_DAT_08001e58 + 0x1c);
  }
  local_1c = CONCAT13(uVar3,(undefined3)local_1c);
  local_18 = DAT_08001e54 & 0xffffff00;
  case_finalize_length_checksum(&local_20,10,uVar4,&stack0xffffffec);
  bVar5 = 0;
  do {
    if (*pcVar2 == '\0') {
      *pcVar2 = '\x01';
      gls_uart_transfer_uncontrolled(1,&local_20,10);
      *pcVar2 = '\0';
      iVar1 = gls_frame_validate_dispatch(1);
      if (iVar1 == 0x5b) {
        if (*_DAT_08001e1c != '\0') {
          return;
        }
        pcVar2 = s__OTA_BOX___Inform_GLS_done__08001e78;
        goto LAB_08001e00;
      }
    }
    osDelay(200);
    bVar5 = bVar5 + 1;
  } while (bVar5 < 3);
  if (*_DAT_08001e1c == '\0') {
    pcVar2 = s__OTA_BOX___Inform_GLS_fail__08001e5b + 1;
LAB_08001e00:
    g2_log_printf(pcVar2);
    g2_log_printf(&DAT_08001e48);
  }
  return;
}

