
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void pmic_boost_status_check(void)

{
  byte bVar1;
  byte *pbVar2;
  char *pcVar3;
  int iVar4;
  uint in_r3;
  bool bVar5;
  uint local_18;
  
  local_18 = in_r3;
  iVar4 = case_register_any_bits(DAT_08002af4,0x20);
  bVar5 = iVar4 == 0;
  local_18._0_1_ = 0xff;
  peripheral_transaction_guard(0x15,&local_18,1);
  pbVar2 = DAT_08002afc;
  iVar4 = DAT_08002af8;
  bVar1 = (byte)local_18 & 1;
  local_18 = CONCAT31(local_18._1_3_,(byte)local_18) & 0xffffff01;
  if (bVar1 == 0) {
    if ((bVar5) && (*(char *)(DAT_08002af8 + 3) != '\0')) goto LAB_08002aec;
  }
  else if ((!bVar5) && (*(char *)(DAT_08002af8 + 3) == '\0')) {
LAB_08002aec:
    *DAT_08002afc = 0;
    return;
  }
  bVar1 = *DAT_08002afc;
  *DAT_08002afc = bVar1 + 1;
  if (2 < (byte)(bVar1 + 1)) {
    *(bool *)(iVar4 + 3) = bVar5;
    peripheral_mode_write_retry(!bVar5);
    pcVar3 = _DAT_08002b00;
    *pbVar2 = 0;
    if (*pcVar3 == '\0') {
      g2_log_printf(s_Check_pmic_boost_status_fail__tr_08002b03 + 1);
      g2_log_printf(&DAT_08002b3c);
    }
  }
  return;
}

