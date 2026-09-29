
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_004efa78(void)

{
  ushort *puVar1;
  uint *puVar2;
  char cVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  undefined4 in_r3;
  uint uVar7;
  undefined4 uStack_28;
  uint uStack_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  
  puVar2 = _DAT_004eff24;
  uVar6 = *_DAT_004eff24;
  *_DAT_004eff24 = uVar6 + 1;
  if (0xe10 < uVar6) {
    *puVar2 = 0;
    uStack_1c = in_r3;
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004eff18,DAT_004eff14,PTR_s_Calendar_expire_check_004eff2c,0x4fd,
                   PTR_s_Calendar_expire_check__check_cal_004eff28);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__dashborad_calendar_Calendar_exp_004eff30,
                          PTR_s__dashborad_calendar_Calendar_exp_004eff30);
    }
    puVar1 = DAT_004efc9c;
    if (*DAT_004efc9c != 0) {
      uVar6 = 0;
      for (uVar7 = 0; (int)uVar7 < (int)(uint)*puVar1; uVar7 = uVar7 + 1) {
        uVar5 = service_time_rtc_refresh();
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          uStack_28 = uVar5;
          FUN_0043d574(4,DAT_004eff18,DAT_004eff14,PTR_s_Calendar_expire_check_004eff2c,0x509,
                       PTR_s_current_timestamp____d_004eff34);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10400000,PTR_s__dashborad_calendar_current_time_004eff38,
                              PTR_s__dashborad_calendar_current_time_004eff38,uVar5);
        }
        if (*(uint *)(puVar1 + uVar7 * 0x108 + 0x108) < uVar5) {
          if (900 < uVar5 - *(int *)(puVar1 + uVar7 * 0x108 + 0x108)) {
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              uStack_20 = *(undefined4 *)(puVar1 + uVar7 * 0x108 + 0x108);
              uStack_28 = uVar7;
              uStack_24 = uVar5;
              FUN_0043d574(4,DAT_004eff18,DAT_004eff14,PTR_s_Calendar_expire_check_004eff2c,0x50b,
                           PTR_s_Calendar_expire_check__calendar___004eff3c);
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              compress_log_output(0x10c00000,PTR_s__dashborad_calendar_Calendar_exp_004eff40,
                                  PTR_s__dashborad_calendar_Calendar_exp_004eff40,uVar7,uVar5,
                                  *(undefined4 *)(puVar1 + uVar7 * 0x108 + 0x108));
            }
            uVar6 = uVar6 | 1 << (uVar7 & 0xff);
          }
        }
      }
      cVar3 = FUN_0045a570();
      if ((uVar6 != 0) && (cVar3 == '\x01')) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          uStack_28 = uVar6;
          FUN_0043d574(4,DAT_004eff18,DAT_004eff14,PTR_s_Calendar_expire_check_004eff2c,0x512,
                       PTR_s_Calendar_expire_check__calendar_e_004eff44);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10400000,PTR_s__dashborad_calendar_Calendar_exp_004eff48,
                              PTR_s__dashborad_calendar_Calendar_exp_004eff48,uVar6);
        }
        FUN_0043c0e4(&uStack_28,5,0);
        uStack_28 = CONCAT13((char)(uVar6 >> 0x10),
                             CONCAT12((char)(uVar6 >> 8),CONCAT11((char)uVar6,10)));
        uStack_24 = CONCAT31(uStack_24._1_3_,(char)(uVar6 >> 0x18));
        FUN_00464bb2(1,&uStack_28,5,0);
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004eff18,DAT_004eff14,PTR_s_Calendar_expire_check_004eff2c,0x51a,
                       PTR_s_Calendar_expire_check__send_cale_004eff4c);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__dashborad_calendar_Calendar_exp_004eff50,
                              PTR_s__dashborad_calendar_Calendar_exp_004eff50);
        }
      }
    }
  }
  return;
}

