
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void g2_thread_entry_2(void)

{
  byte bVar1;
  byte bVar2;
  byte bVar3;
  byte bVar4;
  undefined1 uVar5;
  undefined1 uVar6;
  int iVar7;
  int iVar8;
  undefined4 uVar9;
  int iVar10;
  int extraout_r1;
  byte bVar11;
  byte bVar12;
  uint uStack_40;
  int iStack_3c;
  uint uStack_38;
  uint uStack_34;
  uint uStack_30;
  uint uStack_2c;
  uint uStack_28;
  uint uStack_24;
  undefined4 auStack_20 [4];
  uint uStack_10;
  int iStack_c;
  int iStack_8;
  int iStack_4;
  
  iVar8 = DAT_08008198;
  iVar7 = DAT_08008194;
  bVar12 = 0;
  iStack_4 = DAT_08008198 + 0x20;
  iStack_8 = DAT_08008198 + 0x40;
  do {
    pmic_boost_status_check();
    __aeabi_uidiv(*(undefined4 *)(iVar8 + 8),5);
    if (extraout_r1 == 0) {
      uStack_10 = 0;
      sensor_default_value_read(&uStack_10);
      iStack_c = 0;
      calibrated_sensor_value_convert(&iStack_c);
      auStack_20[0] = 0;
      scaled_sensor_value_read(auStack_20);
      if (iStack_c == DAT_0800819c) {
        peripheral_init_retry();
        left_channel_transaction_guard(10,0x40);
        left_channel_transaction_guard(0xb,0xff);
        bounded_percentage_convert(&uStack_40);
        *(char *)(iVar8 + 1) = (char)uStack_40;
      }
      if ((*(char *)(iVar8 + 1) == 'c') && (*(char *)(iVar8 + 3) != '\0')) {
        bVar11 = bVar12 + 1;
        if (0x3c < bVar12) {
          bVar11 = 0;
          if (*(char *)(iVar7 + 7) == '\0') {
            g2_log_printf(s_Bat_change_stucked___99__>_100_080081a0);
            g2_log_printf(&DAT_080081c0);
          }
          *(char *)(iVar8 + 1) = *(char *)(iVar8 + 1) + '\x01';
        }
      }
      else {
        bVar11 = 0;
      }
      if (*(byte *)(iVar8 + 0x19) == 0) {
        if (*(char *)(iVar8 + 0x15) == '\0') {
          if (*(char *)(iVar7 + 7) == '\0') {
            bVar12 = *(byte *)(iVar8 + 0x16);
            bVar1 = *(byte *)(DAT_08008194 + 0x3d);
            bVar2 = *(byte *)(iVar8 + 0x11);
            bVar3 = *(byte *)(iVar8 + 0x10);
            bVar4 = *(byte *)(iVar8 + 3);
            uVar5 = *(undefined1 *)(iVar8 + 4);
            uVar6 = *(undefined1 *)(iVar8 + 1);
            uVar9 = DAT_080081c8;
            goto LAB_0800802a;
          }
        }
        else if (*(char *)(iVar7 + 7) == '\0') {
          bVar12 = *(byte *)(iVar8 + 0x16);
          bVar1 = *(byte *)(DAT_08008194 + 0x3d);
          bVar2 = *(byte *)(iVar8 + 0x11);
          bVar3 = *(byte *)(iVar8 + 0x10);
          bVar4 = *(byte *)(iVar8 + 3);
          uVar5 = *(undefined1 *)(iVar8 + 4);
          uVar6 = *(undefined1 *)(iVar8 + 1);
          uVar9 = DAT_080081c4;
LAB_0800802a:
          uStack_28 = (uint)bVar1;
          uStack_2c = (uint)bVar12;
          uStack_34 = (uint)bVar2;
          uStack_38 = (uint)bVar3;
          uStack_40 = (uint)bVar4;
          uStack_30 = uStack_10;
          iStack_3c = iStack_c;
          uStack_24 = (uint)*(byte *)(iVar8 + 0x19);
          g2_log_printf(uVar9,auStack_20[0],uVar6,uVar5);
          g2_log_printf(&DAT_080081c0);
        }
      }
      if ((uStack_10 < 0x1c3) || (*(char *)(iVar8 + 0x16) == '\0')) {
        if ((uStack_10 - 1 < 399) && (*(char *)(iVar8 + 0x16) == '\0')) {
          if (*(char *)(iVar7 + 7) == '\0') {
            g2_log_printf(s_Temperature_back_to_normal__Star_080081f4);
            g2_log_printf(&DAT_080081c0);
          }
          right_channel_transaction_guard(0x16,0);
          *(undefined1 *)(iVar8 + 0x16) = 1;
        }
      }
      else {
        if (*(char *)(iVar7 + 7) == '\0') {
          g2_log_printf(s_Over_temperature____Stop_pmic_ch_080081cc);
          g2_log_printf(&DAT_080081c0);
        }
        right_channel_transaction_guard(0x16,0x10);
        *(undefined1 *)(iVar8 + 0x16) = 0;
      }
      if ((*(char *)(iVar8 + 1) == '\0') && (*(char *)(iVar8 + 3) == '\0')) {
        uStack_40 = 0;
        scaled_sensor_value_read(&uStack_40);
        if (uStack_40 < DAT_08008228) {
          if (*(char *)(iVar7 + 7) == '\0') {
            g2_log_printf(s_Standby__reason__low_bat__0800822c);
            g2_log_printf(&DAT_080081c0);
          }
          peripheral_transaction_guard(0x10,&iStack_3c,1);
          peripheral_transaction_guard(0x11,&iStack_3c,1);
          glasses_channel_command_pack(0);
          peripheral_mode_write_retry(0);
          HAL_PWR_DisableWakeUpPin(0x2b);
          HAL_PWR_EnableWakeUpPin(DAT_08008248);
          *(undefined4 *)(_DAT_08008250 + 0x18) = DAT_0800824c;
          HAL_PWR_EnterSTANDBYMode();
        }
      }
      bVar12 = bVar11;
      if ((*(char *)(DAT_08008194 + 0x3c) != '\0') && (*(char *)(DAT_08008194 + 0x3d) == '\0')) {
        if (*(char *)(iVar8 + 2) != '\x04') {
          aging_led_status_clear();
          case_gpio_pa6_write(1);
          *(undefined1 *)(iVar8 + 2) = 4;
          if (*(char *)(iVar7 + 7) == '\0') {
            g2_log_printf(s___AGING_PRE___Start_aging_led_08008253 + 1);
            g2_log_printf(&DAT_080081c0);
          }
        }
        bVar11 = *(byte *)(iStack_4 + 0x12);
        if ((bVar11 < 100) || (*(byte *)(iStack_8 + 0xe) < 100)) {
          if (*(uint *)(DAT_08008194 + 0x44) < 0x1c20) {
            iVar10 = *(uint *)(DAT_08008194 + 0x44) + 5;
            *(int *)(DAT_08008194 + 0x44) = iVar10;
            if (*(char *)(iVar7 + 7) == '\0') {
              uStack_40 = (uint)*(byte *)(iStack_8 + 0xe);
              iStack_3c = iVar10;
              g2_log_printf(s__AGING_PRE___GLS_not_ready__L__d_080082b4,
                            *(undefined2 *)(iVar8 + 0x36),bVar11,*(undefined2 *)(iStack_8 + 0x12));
              g2_log_printf(&DAT_080081c0);
            }
            goto LAB_0800818a;
          }
          if (*(char *)(iVar7 + 7) == '\0') {
            g2_log_printf(s__AGING_PRE___GLS_not_ready_after_08008274);
            g2_log_printf(&DAT_080081c0);
          }
        }
        aging_sequence_start();
      }
    }
LAB_0800818a:
    osDelay(1000);
  } while( true );
}

