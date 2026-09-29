
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4
gls_uart_transfer_controlled(int param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  short sVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  char *pcVar5;
  uint uVar6;
  uint uVar7;
  
  case_copy_head8_to_tail8();
  iVar2 = case_or_words_88_8c(DAT_080026bc);
  if (-1 < iVar2 << 0x1a) {
    case_initialize_controller_profile();
  }
  case_register_write_channel(0x50000000,8,1);
  if (param_1 == 0) {
    right_indicator_sequence();
  }
  else {
    left_indicator_sequence();
  }
  osDelay(1);
  case_dispatch_tagged(param_2,param_3);
  case_initialize_controller_profile();
  if (param_4 == 0) goto LAB_080026ae;
  iVar3 = case_read_controller_blocking(DAT_080026bc,DAT_080026c0,5,0x50);
  pcVar5 = _DAT_080026c4;
  iVar2 = DAT_080026c0;
  if (iVar3 == 3) {
    if (*_DAT_080026c4 != '\0') goto LAB_080026ae;
    g2_log_printf(s_receive_header_timeout_080026c7 + 1);
  }
  else {
    uVar4 = 0;
    do {
      if (*(char *)(DAT_080026c0 + uVar4) == 'Z') break;
      uVar4 = uVar4 + 1 & 0xff;
    } while (uVar4 < 5);
    if (4 < uVar4) {
      if (*_DAT_080026c4 == '\0') {
        pcVar5 = s_no_header_in_first_5_char__RX__080026e0;
LAB_08002694:
        g2_log_printf(pcVar5);
      }
LAB_0800261e:
      log_hex_buffer(DAT_080026c0,5);
      goto LAB_080026ae;
    }
    uVar7 = 5 - uVar4 & 0xff;
    if (uVar4 != 0) {
      for (uVar6 = 0; uVar6 < uVar7; uVar6 = uVar6 + 1 & 0xff) {
        *(undefined1 *)(iVar2 + uVar6) = *(undefined1 *)(iVar2 + uVar6 + uVar4);
      }
      if (1 < uVar4) {
        iVar3 = case_read_controller_blocking
                          (DAT_080026bc,iVar2 + uVar4 + 1,uVar4 - 1 & 0xffff,0x32);
        if (iVar3 == 3) {
          if (*pcVar5 == '\0') {
            g2_log_printf(s_receive_len_timeout__RX__08002700);
            pcVar5 = &DAT_0800271c;
            goto LAB_08002694;
          }
          goto LAB_0800261e;
        }
        uVar7 = 4;
      }
    }
    uVar4 = 0x113;
    if (*(byte *)(iVar2 + 3) < 0x113) {
      uVar4 = (uint)*(byte *)(iVar2 + 3);
    }
    sVar1 = __aeabi_uidiv(uVar4,0x1e);
    iVar2 = case_read_controller_blocking(DAT_080026bc,iVar2 + uVar7,uVar4,sVar1 * 5 + 5);
    if ((iVar2 != 3) || (*pcVar5 != '\0')) goto LAB_080026ae;
    g2_log_printf(s_receive_data_timeout__RX__len__d_08002720,uVar4);
  }
  g2_log_printf(&DAT_0800271c);
LAB_080026ae:
  case_reset_controller_context(DAT_080026bc);
  dual_side_indicator_update();
  return 1;
}

