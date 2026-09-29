
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void aging_status_set_left
               (undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  undefined4 local_18;
  undefined4 local_14;
  
  pcVar1 = _DAT_08002464;
  if (*(char *)(DAT_0800245c + 0x10) == '\0') {
    if (*DAT_08002460 != '\0') {
      return;
    }
    pcVar1 = s_SetAgingStatusL_fail__not_inbox_08002494;
  }
  else {
    if (*_DAT_08002464 == '\0') {
      *_DAT_08002464 = '\x01';
      local_18 = DAT_080024b4;
      local_14 = CONCAT31((int3)((uint)DAT_080024b8 >> 8),param_1);
      case_finalize_length_checksum(&local_18,6);
      gls_uart_transfer_controlled(1,&local_18,6);
      iVar2 = gls_frame_validate_dispatch(1);
      if (iVar2 == 0x3e) {
        *(undefined1 *)(DAT_080024bc + 2) = param_1;
      }
      *pcVar1 = '\0';
      return;
    }
    if (*DAT_08002460 != '\0') {
      return;
    }
    pcVar1 = s_Skip_SetAgingStatusL_since_2510_b_08002467 + 1;
  }
  local_18 = param_3;
  local_14 = param_4;
  g2_log_printf(pcVar1);
  g2_log_printf(&DAT_08002490);
  return;
}

