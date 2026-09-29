
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08003d24(void)

{
  int iVar1;
  char *pcVar2;
  undefined4 *puVar3;
  int *piVar4;
  int iVar5;
  
  pcVar2 = _DAT_08003e30;
  iVar1 = DAT_08003e2c;
  *(char *)(DAT_08003e2c + 3) = (char)((*(uint *)(DAT_08003e28 + 0x10) & 0x3f) >> 5);
  if (*pcVar2 == '\0') {
    g2_log_printf(s_USB_int__hasUsb__d_08003e33 + 1);
    g2_log_printf(&DAT_08003e48);
  }
  puVar3 = DAT_08003e4c;
  if (*(char *)(iVar1 + 2) == '\0') {
    glasses_charge_side_select();
    *(undefined1 *)(iVar1 + 2) = 1;
    osEventFlagsSet(*puVar3,2);
  }
  iVar5 = case_read_byte3();
  if (iVar5 == 0) {
    *(undefined1 *)(iVar1 + 0x17) = 0;
  }
  else {
    osEventFlagsSet(*puVar3,0x1000);
  }
  piVar4 = _DAT_08003e50;
  if (*(char *)(iVar1 + 3) == '\0') {
    iVar5 = *(int *)(iVar1 + 8);
    if ((((uint)(iVar5 - *_DAT_08003e50) < 7) && (*_DAT_08003e50 != 0)) && (_DAT_08003e50[1] != 0))
    {
      if (*pcVar2 == '\0') {
        g2_log_printf(s_Reset_GLS_and_BOX__reason__USB__08003e53 + 1);
        g2_log_printf(&DAT_08003e48);
      }
      case_command_a2_set();
      osEventFlagsSet(*puVar3,0x200);
    }
    else {
      *_DAT_08003e50 = _DAT_08003e50[1];
      piVar4[1] = iVar5;
    }
  }
  peripheral_mode_write_retry(*(char *)(iVar1 + 3) == '\0');
  case_dispatch_pending(0x20);
  if (*pcVar2 == '\0') {
    g2_log_printf(s_USB_int__send_0x13_soon__08003e74);
    g2_log_printf(&DAT_08003e48);
  }
  if (((*(char *)(DAT_08003e2c + 0x31) == '\0') || (*(short *)(iVar1 + 0x38) == 0)) ||
     (*(char *)(DAT_08003e2c + 0x33) != '\0')) {
    *(undefined4 *)(iVar1 + 0x3c) = 0;
  }
  else {
    glasses_charge_state_reset(1);
  }
  if (((*(char *)(DAT_08003e2c + 0x4d) != '\0') && (*(short *)(DAT_08003e2c + 0x54) != 0)) &&
     (*(char *)(DAT_08003e2c + 0x4f) == '\0')) {
    glasses_charge_state_reset(0);
    return;
  }
  *(undefined4 *)(iVar1 + 0x58) = 0;
  return;
}

