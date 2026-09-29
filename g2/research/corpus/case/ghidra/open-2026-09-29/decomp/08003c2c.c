
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08003c2c(void)

{
  int iVar1;
  undefined1 *puVar2;
  char *pcVar3;
  undefined4 *puVar4;
  int iVar5;
  
  puVar2 = DAT_08003ce4;
  iVar1 = DAT_08003ce0;
  *(char *)(DAT_08003ce0 + 4) = (char)((*(uint *)(DAT_08003cdc + 0xc) & 7) >> 2);
  pcVar3 = _DAT_08003ce8;
  *puVar2 = 1;
  if (*pcVar3 == '\0') {
    g2_log_printf(s_hall_int__isOpen__d_08003ceb + 1);
    g2_log_printf(&DAT_08003d00);
  }
  puVar4 = _DAT_08003d04;
  if (*(char *)(iVar1 + 2) == '\0') {
    glasses_charge_side_select();
    *(undefined1 *)(iVar1 + 2) = 1;
    osEventFlagsSet(*puVar4,2);
  }
  iVar5 = case_read_byte3();
  if (iVar5 == 0) {
    *(undefined1 *)(iVar1 + 0x17) = 0;
  }
  else {
    osEventFlagsSet(*puVar4,0x1000);
  }
  case_dispatch_pending(4);
  if (*pcVar3 == '\0') {
    g2_log_printf(s_Hall_int__send_0x13_soon__08003d07 + 1);
    g2_log_printf(&DAT_08003d00);
  }
  if (((*(char *)(DAT_08003ce0 + 0x31) == '\0') || (*(short *)(iVar1 + 0x38) == 0)) ||
     (*(char *)(DAT_08003ce0 + 0x33) != '\0')) {
    *(undefined4 *)(iVar1 + 0x3c) = 0;
  }
  else {
    glasses_charge_state_reset(1);
  }
  if (((*(char *)(DAT_08003ce0 + 0x4d) != '\0') && (*(short *)(DAT_08003ce0 + 0x54) != 0)) &&
     (*(char *)(DAT_08003ce0 + 0x4f) == '\0')) {
    glasses_charge_state_reset(0);
    return;
  }
  *(undefined4 *)(iVar1 + 0x58) = 0;
  return;
}

