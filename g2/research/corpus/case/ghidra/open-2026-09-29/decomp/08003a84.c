
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08003a84(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int in_r3;
  int local_10;
  
  local_10 = in_r3;
  iVar3 = bounded_percentage_convert(&local_10);
  iVar2 = _DAT_08003b34;
  iVar1 = DAT_08003b30;
  if (iVar3 == 0) {
    if (*(char *)(DAT_08003b30 + 3) != '\0') {
      if (local_10 <= (int)(uint)*(byte *)(DAT_08003b30 + 1)) {
        if (*(char *)(_DAT_08003b34 + 7) == '\0') {
          g2_log_printf(s_Bat_change_not_used____d__>__d_08003b70);
          g2_log_printf(&DAT_08003b50);
        }
        goto LAB_08003b24;
      }
    }
    if (*(char *)(_DAT_08003b34 + 7) == '\0') {
      g2_log_printf(s_Bat_change___d__>__d_08003b37 + 1,*(undefined1 *)(DAT_08003b30 + 1),local_10);
      g2_log_printf(&DAT_08003b50);
    }
    *(char *)(iVar1 + 1) = (char)local_10;
    if (*(char *)(iVar2 + 7) == '\0') {
      g2_log_printf(s_Bat_change__send_0x13_soon__08003b54);
      g2_log_printf(&DAT_08003b50);
    }
    if (((*(char *)(DAT_08003b30 + 0x31) == '\0') || (*(short *)(iVar1 + 0x38) == 0)) ||
       (*(char *)(DAT_08003b30 + 0x33) != '\0')) {
      *(undefined4 *)(iVar1 + 0x3c) = 0;
    }
    else {
      glasses_charge_state_reset(1);
    }
    if (((*(char *)(DAT_08003b30 + 0x4d) == '\0') || (*(short *)(DAT_08003b30 + 0x54) == 0)) ||
       (*(char *)(DAT_08003b30 + 0x4f) != '\0')) {
      *(undefined4 *)(iVar1 + 0x58) = 0;
    }
    else {
      glasses_charge_state_reset(0);
    }
  }
LAB_08003b24:
  left_channel_transaction_guard(10,0x40);
  return;
}

