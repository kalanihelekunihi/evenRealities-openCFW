
undefined4 FUN_0800373c(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  char *pcVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  byte bVar8;
  undefined4 local_18;
  
  puVar1 = DAT_0800380c;
  *DAT_0800380c = 2;
  local_18 = param_4;
  iVar3 = case_classify_status();
  if (iVar3 == 1) {
    uVar4 = 4;
  }
  else {
    uVar4 = 0x8000;
  }
  puVar1[1] = uVar4;
  puVar1[2] = 0x7e;
  puVar1[3] = 1;
  HAL_FLASH_OB_Unlock();
  bVar8 = 0;
  do {
    iVar3 = case_run_controller_range(DAT_0800380c,&local_18);
    if (iVar3 == 0) break;
    case_wait_elapsed(10);
    bVar8 = bVar8 + 1;
  } while (bVar8 < 3);
  pcVar2 = DAT_08003810;
  if (bVar8 == 3) {
    if (*DAT_08003810 != '\0') goto LAB_080037c8;
    g2_log_printf(s_fail_to_erase__err_0x_x_08003818,local_18);
  }
  else {
    uVar6 = 0;
    uVar7 = 0;
    uVar5 = 0;
    do {
      uVar7 = uVar7 << 8 | uVar6 >> 0x18;
      uVar6 = uVar6 << 8 | (uint)*(byte *)(param_1 + uVar5);
      uVar5 = uVar5 + 1 & 0xff;
    } while (uVar5 < 8);
    iVar3 = case_copy_controller_words(1,DAT_08003814,uVar6,uVar7);
    if (iVar3 == 0) {
      uVar6 = 0;
      uVar7 = 0;
      uVar5 = 0;
      do {
        uVar7 = uVar7 << 8 | uVar6 >> 0x18;
        uVar6 = uVar6 << 8 | (uint)*(byte *)(param_1 + uVar5 + 8);
        uVar5 = uVar5 + 1 & 0xff;
      } while (uVar5 < 8);
      iVar3 = case_copy_controller_words(1,DAT_08003814 + 8,uVar6,uVar7);
      if (iVar3 == 0) {
        case_flag31_set();
        return 1;
      }
    }
    if (*pcVar2 != '\0') goto LAB_080037c8;
    g2_log_printf(s_fail_to_program__08003834);
  }
  g2_log_printf(&DAT_08003830);
LAB_080037c8:
  case_flag31_set();
  return 0;
}

