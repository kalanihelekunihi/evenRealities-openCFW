
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0800a598(void)

{
  char *pcVar1;
  char *pcVar2;
  int iVar3;
  undefined4 auStack_1c [4];
  int iStack_c;
  uint uStack_4;
  
  case_initialize_serial_block();
  case_initialize_application_profile();
  case_configure_platform_routes();
  case_configure_record_and_stop();
  case_initialize_channel_profile();
  case_initialize_controller_profile();
  case_initialize_transport_record();
  case_build_register_descriptor(auStack_1c);
  pcVar1 = _DAT_0800a6d8;
  if (((int)(uStack_4 << 7) < 0) || (iStack_c != 0xaa)) {
    if (*_DAT_0800a6d8 == '\0') {
      g2_log_printf(s_Option_Bytes_check_fail__UPDATE___0800a6db + 1,uStack_4);
      g2_log_printf(&DAT_0800a70c);
    }
    auStack_1c[0] = 6;
    uStack_4 = uStack_4 & 0xfeffff00 | 0xaa;
    iStack_c = 0xaa;
    HAL_FLASH_OB_Unlock();
    HAL_FLASH_Unlock();
    FUN_08004a6c(auStack_1c);
    case_flag27_set();
    case_flag30_set();
    case_flag31_set();
  }
  else if (*_DAT_0800a6d8 == '\0') {
    g2_log_printf(s_Option_Bytes_check_done__0x_x__l_0800a710,uStack_4,0xaa);
    g2_log_printf(&DAT_0800a70c);
  }
  *(uint *)(DAT_0800a73c + 0x3c) = *(uint *)(DAT_0800a73c + 0x3c) | DAT_0800a73c << 0x10;
  iVar3 = DAT_0800a744;
  pcVar2 = DAT_0800a740;
  *DAT_0800a740 = '\0';
  if (-1 < (int)(~*(uint *)(iVar3 + 0x10) << 0x17)) {
    *(int *)(iVar3 + 0x18) = DAT_0800a748;
    if (-1 < (int)(~*(uint *)(iVar3 + 0x10) << 0x1c)) {
      *(int *)(iVar3 + 0x18) = DAT_0800a748 + -0xf8;
      *pcVar2 = '\x01';
      if (*pcVar1 == '\0') {
        g2_log_printf(s_wake_up_from_HALL_0800a74c);
        g2_log_printf(&DAT_0800a70c);
      }
    }
    if (-1 < (int)(~*(uint *)(iVar3 + 0x10) << 0x1a)) {
      *(int *)(iVar3 + 0x18) = DAT_0800a748 + -0xe0;
      *pcVar2 = '\x02';
      if (*pcVar1 != '\0') goto LAB_0800a6c6;
      g2_log_printf(s_wake_up_from_USB_0800a760);
      g2_log_printf(&DAT_0800a70c);
    }
    if (*pcVar2 != '\0') goto LAB_0800a6c6;
    *pcVar2 = '\x03';
    if (*pcVar1 != '\0') goto LAB_0800a6c6;
    g2_log_printf(s_wake_up_from_RTC_0800a774);
    g2_log_printf(&DAT_0800a70c);
    if (*pcVar2 != '\0') goto LAB_0800a6c6;
  }
  if (*pcVar1 == '\0') {
    g2_log_printf(s_Power_up____0800a788);
    g2_log_printf(&DAT_0800a70c);
  }
LAB_0800a6c6:
  FUN_08002fc8();
  FUN_0800a8d8();
  app_rtos_init();
  FUN_0800a900();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

