
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void option_byte_bank_swap(void)

{
  uint uVar1;
  char *pcVar2;
  undefined4 uVar3;
  undefined1 auStack_30 [24];
  uint local_18;
  
  case_build_register_descriptor(auStack_30);
  pcVar2 = _DAT_08003960;
  uVar1 = DAT_0800395c;
  if ((int)(local_18 << 0xb) < 0) {
    if (*_DAT_08003960 == '\0') {
      g2_log_printf(s_Swap_bank_1_>2____RESET__cur_ob_v_08003990,local_18);
      g2_log_printf(&DAT_0800398c);
    }
    local_18 = local_18 & ~uVar1;
  }
  else {
    if (*_DAT_08003960 == '\0') {
      g2_log_printf(s_Swap_bank_2_>1____RESET__cur_ob_v_08003963 + 1,local_18);
      g2_log_printf(&DAT_0800398c);
    }
    local_18 = local_18 & ~uVar1 | uVar1;
  }
  HAL_FLASH_OB_Unlock();
  HAL_FLASH_Unlock();
  if (*pcVar2 == '\0') {
    uVar3 = FUN_08004a6c(auStack_30);
    g2_log_printf(s_ob_program___d_080039b8,uVar3);
    g2_log_printf(&DAT_0800398c);
  }
  osDelay(100);
  case_flag27_set();
  case_flag30_set();
  case_flag31_set();
  return;
}

