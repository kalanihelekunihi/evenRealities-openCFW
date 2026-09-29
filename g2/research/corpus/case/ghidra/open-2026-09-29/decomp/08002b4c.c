
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_08002b4c(void)

{
  char *pcVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  byte local_28 [8];
  byte local_20 [8];
  byte local_18 [8];
  
  FUN_08002f60(local_18);
  FUN_08002f88(local_28);
  HAL_FLASH_OB_Unlock();
  iVar4 = DAT_08002c08;
  uVar5 = 0;
  uVar6 = 0;
  uVar2 = 0;
  do {
    uVar6 = uVar6 << 8 | uVar5 >> 0x18;
    uVar5 = uVar5 << 8 | (uint)local_18[uVar2];
    uVar2 = uVar2 + 1 & 0xff;
  } while (uVar2 < 8);
  iVar3 = case_copy_controller_words(1,DAT_08002c04,uVar5,uVar6);
  pcVar1 = _DAT_08002c0c;
  if (iVar3 == 0) {
    uVar5 = 0;
    uVar6 = 0;
    uVar2 = 0;
    do {
      uVar6 = uVar6 << 8 | uVar5 >> 0x18;
      uVar5 = uVar5 << 8 | (uint)local_28[uVar2];
      uVar2 = uVar2 + 1 & 0xff;
    } while (uVar2 < 8);
    iVar3 = case_copy_controller_words(1,iVar4,uVar5,uVar6);
    if (iVar3 == 0) {
      uVar5 = 0;
      uVar6 = 0;
      uVar2 = 0;
      do {
        uVar6 = uVar6 << 8 | uVar5 >> 0x18;
        uVar5 = uVar5 << 8 | (uint)local_20[uVar2];
        uVar2 = uVar2 + 1 & 0xff;
      } while (uVar2 < 8);
      iVar4 = case_copy_controller_words(1,iVar4 + 8,uVar5,uVar6);
      if (iVar4 == 0) {
        case_flag31_set();
        return 1;
      }
    }
  }
  if (*pcVar1 == '\0') {
    g2_log_printf(s__OTA_BOX___Fail_to_program__08002c0f + 1);
    g2_log_printf(&DAT_08002c2c);
  }
  case_flag31_set();
  return 0;
}

