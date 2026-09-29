
undefined4 FUN_08002e04(int param_1,int param_2,uint param_3)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  if (*DAT_08002eb0 == '\0') {
    g2_log_printf(&DAT_08002eb4);
  }
  if (param_3 != 0) {
    HAL_FLASH_OB_Unlock();
    iVar1 = DAT_08002eb8;
    uVar8 = param_3 >> 3;
    if ((param_3 & 7) != 0) {
      uVar8 = uVar8 + 1;
    }
    for (uVar7 = 0; uVar7 < uVar8; uVar7 = uVar7 + 1 & 0xffff) {
      uVar5 = 0;
      uVar2 = 8;
      uVar6 = 0;
      do {
        iVar3 = uVar7 * 8 + uVar2;
        if (iVar3 + -1 < (int)param_3) {
          uVar6 = uVar6 << 8 | uVar5 >> 0x18;
          uVar4 = (uint)*(byte *)(iVar3 + param_2 + -1);
        }
        else {
          uVar6 = uVar6 << 8 | uVar5 >> 0x18;
          uVar4 = 0xff;
        }
        uVar5 = uVar5 << 8 | uVar4;
        uVar2 = uVar2 - 1 & 0xff;
      } while (uVar2 != 0);
      iVar3 = case_copy_controller_words(1,iVar1 + param_1 + uVar7 * 8,uVar5,uVar6);
      if (iVar3 != 0) {
        if (*DAT_08002eb0 == '\0') {
          g2_log_printf(s__OTA_BOX__fail_to_program__08002ebc);
          g2_log_printf(&DAT_08002ed8);
        }
        case_flag31_set();
        return 0;
      }
    }
    case_flag31_set();
  }
  return 1;
}

