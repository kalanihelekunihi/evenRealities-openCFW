
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void aging_status_set_right
               (undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  undefined4 local_18;
  undefined4 local_14;
  
  pcVar1 = _DAT_08002530;
  if (*(char *)(DAT_08002528 + 0x11) == '\0') {
    if (*DAT_0800252c != '\0') {
      return;
    }
    pcVar1 = s_SetAgingStatusR_fail__not_inbox_08002560;
  }
  else {
    if (*_DAT_08002530 == '\0') {
      *_DAT_08002530 = '\x01';
      local_18 = DAT_08002580;
      local_14 = CONCAT31((int3)((uint)DAT_08002584 >> 8),param_1);
      case_finalize_length_checksum(&local_18,6);
      gls_uart_transfer_controlled(0,&local_18,6,1);
      iVar2 = gls_frame_validate_dispatch(0);
      if (iVar2 == 0x3e) {
        *(undefined1 *)(DAT_08002588 + 3) = param_1;
      }
      *pcVar1 = '\0';
      return;
    }
    if (*DAT_0800252c != '\0') {
      return;
    }
    pcVar1 = s_Skip_SetAgingStatusR_since_2510_b_08002533 + 1;
  }
  local_18 = param_3;
  local_14 = param_4;
  g2_log_printf(pcVar1);
  g2_log_printf(&DAT_0800255c);
  return;
}

