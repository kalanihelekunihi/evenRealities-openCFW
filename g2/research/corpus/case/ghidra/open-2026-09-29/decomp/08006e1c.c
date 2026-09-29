
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void g2_thread_entry_1(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  undefined1 *puVar4;
  int iVar5;
  int iVar6;
  byte bVar7;
  
  iVar2 = DAT_08007138;
  osTimerStart(*(undefined4 *)(DAT_08007138 + 0x10),DAT_08007134);
  osTimerStart(*(undefined4 *)(iVar2 + 0x24),1000);
  iVar3 = DAT_0800713c;
  do {
    iVar5 = osEventFlagsGet(*(undefined4 *)(iVar2 + 0x38));
    if (iVar5 << 0x1e < 0) {
      osEventFlagsClear(*(undefined4 *)(iVar2 + 0x38),2);
      osTimerStart(*(undefined4 *)(iVar2 + 0x10),DAT_08007134);
    }
    if (iVar5 << 0x13 < 0) {
      osEventFlagsClear(*(undefined4 *)(iVar2 + 0x38),0x1000);
      *(undefined1 *)(iVar3 + 0x17) = 0;
    }
    if (iVar5 << 0x1d < 0) {
      osEventFlagsClear(*(undefined4 *)(iVar2 + 0x38),4);
      *(undefined1 *)(iVar2 + 0xc) = 1;
      case_gpio_pa7_write(0);
      case_gpio_pa6_write(*(undefined1 *)(iVar2 + 0xc));
      osTimerStart(*(undefined4 *)(iVar2 + 0x18),800);
    }
    if (iVar5 << 0x1c < 0) {
      osEventFlagsClear(*(undefined4 *)(iVar2 + 0x38),8);
      gls_rx_buffer_parse_dispatch();
      *DAT_08007140 = 0;
    }
    if ((iVar5 << 0x1a < 0) && (*(char *)(iVar2 + 4) == '\0')) {
      if (_DAT_08007144[2] == '\0') {
        cVar1 = *(char *)(iVar3 + 0x10);
      }
      else {
        cVar1 = *(char *)(iVar3 + 0x11);
      }
      if (cVar1 != '\0') {
        osEventFlagsClear(*(undefined4 *)(iVar2 + 0x38),0x20);
        if (*(char *)(iVar3 + 0x19) == '\0') {
          log_hex_buffer(_DAT_08007144,(byte)_DAT_08007144[3] + 5);
        }
        *(undefined1 *)(iVar2 + 4) = 1;
        if ((*(char *)(iVar3 + 0x19) == '\0') || (*(char *)(iVar3 + 0x1a) == '\0')) {
          gls_uart_transfer_controlled
                    (_DAT_08007144[2] == '\0',_DAT_08007144,(byte)_DAT_08007144[3] + 5,1);
        }
        else {
          gls_uart_transfer_uncontrolled
                    (_DAT_08007144[2] == '\0',_DAT_08007144,(byte)_DAT_08007144[3] + 5,1);
        }
        *(undefined1 *)(iVar2 + 4) = 0;
        gls_frame_validate_dispatch(1);
      }
    }
    if ((iVar5 << 0x15 < 0) && (*(char *)(iVar2 + 4) == '\0')) {
      if (_DAT_08007144[2] == '\0') {
        cVar1 = *(char *)(iVar3 + 0x10);
      }
      else {
        cVar1 = *(char *)(iVar3 + 0x11);
      }
      if (cVar1 != '\0') {
        osEventFlagsClear(*(undefined4 *)(iVar2 + 0x38),0x400);
        *(undefined1 *)(iVar2 + 4) = 1;
        if ((*(char *)(iVar3 + 0x19) == '\0') || (*(char *)(iVar3 + 0x1a) == '\0')) {
          gls_uart_transfer_controlled
                    (_DAT_08007144[2] == '\0',_DAT_08007144,
                     (ushort)(byte)_DAT_08007144[3] + (ushort)(byte)_DAT_08007144[4] * 0x100 + 6,1);
        }
        else {
          gls_uart_transfer_uncontrolled
                    (_DAT_08007144[2] == '\0',_DAT_08007144,
                     (ushort)(byte)_DAT_08007144[3] + (ushort)(byte)_DAT_08007144[4] * 0x100 + 6,1);
        }
        *(undefined1 *)(iVar2 + 4) = 0;
        gls_frame_validate_dispatch(1);
      }
    }
    if ((iVar5 << 0x19 < 0) && (iVar6 = peripheral_status_probe(), iVar6 != 0)) {
      if (*(char *)(iVar2 + 7) == '\0') {
        g2_log_printf(s_restart_usb_uart_rx_08007147 + 1);
        g2_log_printf(&DAT_0800715c);
      }
      osEventFlagsClear(*(undefined4 *)(iVar2 + 0x38),0x40);
    }
    if (iVar5 << 0x17 < 0) {
      if (*(char *)(iVar2 + 7) == '\0') {
        g2_log_printf(s_reset_gls_L___R__reason__cmd_08007160);
        g2_log_printf(&DAT_0800715c);
      }
      glasses_sides_reset(1);
      osEventFlagsClear(*(undefined4 *)(iVar2 + 0x38),0x100);
    }
    if (iVar5 << 0x16 < 0) {
      if (*(char *)(iVar2 + 7) == '\0') {
        g2_log_printf(s_reset_gls_and_box__08007180);
        g2_log_printf(&DAT_0800715c);
      }
      glasses_sides_reset(1);
      osEventFlagsClear(*(undefined4 *)(iVar2 + 0x38),0x200);
      NVIC_SystemReset();
    }
    iVar6 = DAT_08007138;
    if (iVar5 << 0x18 < 0) {
      *(undefined1 *)(DAT_08007138 + 0x3c) = 0;
      *(undefined4 *)(iVar6 + 0x44) = 0;
      *(undefined1 *)(iVar6 + 0x3d) = 0;
      *(undefined1 *)(iVar6 + 0x42) = 0;
      if ((*(char *)(iVar3 + 0x10) != '\0') && (bVar7 = 0, *(char *)(DAT_08007138 + 0x3e) != '\0'))
      {
        do {
          if (9 < bVar7) goto LAB_0800705e;
          aging_status_set_left(0);
          bVar7 = bVar7 + 1;
        } while (*(char *)(DAT_08007138 + 0x3e) != '\0');
        if (*(char *)(iVar2 + 7) == '\0') {
          g2_log_printf(s__AGING_NOT___GLS_L_exit_aging__08007194);
          g2_log_printf(&DAT_0800715c);
        }
LAB_0800705e:
        osDelay(0x32);
      }
      if ((*(char *)(iVar3 + 0x11) != '\0') && (bVar7 = 0, *(char *)(DAT_08007138 + 0x3f) != '\0'))
      {
        do {
          if (9 < bVar7) goto LAB_080070a6;
          aging_status_set_right(0);
          bVar7 = bVar7 + 1;
        } while (*(char *)(DAT_08007138 + 0x3f) != '\0');
        if (*(char *)(iVar2 + 7) == '\0') {
          g2_log_printf(s__AGING_NOT___GLS_R_exit_aging__080071b4);
          g2_log_printf(&DAT_0800715c);
        }
LAB_080070a6:
        osDelay(0x32);
      }
      if (((*(char *)(DAT_08007138 + 0x3e) != '\0') || (*(char *)(DAT_08007138 + 0x3f) != '\0')) &&
         (*(char *)(iVar2 + 7) == '\0')) {
        g2_log_printf(s__AGING_NOT___Fail_to_exit_aging__080071d4,*(char *)(DAT_08007138 + 0x3e),
                      *(undefined1 *)(DAT_08007138 + 0x3f));
        g2_log_printf(&DAT_0800715c);
      }
      aging_led_status_clear();
      osTimerStop(*(undefined4 *)(iVar2 + 0x1c));
      osTimerStop(*(undefined4 *)(iVar2 + 0x20));
      osEventFlagsClear(*(undefined4 *)(iVar2 + 0x38),0x80);
      *(undefined1 *)(iVar3 + 0x15) = 1;
      aging_indicator_apply();
      *(undefined1 *)(iVar3 + 0x10) = 0;
      *(undefined1 *)(iVar3 + 0x11) = 0;
    }
    if (*(char *)(iVar2 + 5) != '\0') {
      osEventFlagsSet(*(undefined4 *)(iVar2 + 0x38),0x20);
      puVar4 = _DAT_08007144;
      *_DAT_08007144 = 0x24;
      puVar4[1] = 0;
      puVar4[2] = 1;
      puVar4[3] = 0;
      puVar4[4] = 0xa7;
    }
    osDelay(1);
  } while( true );
}

