
undefined4
_atBuzzerTest(undefined *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined *puVar2;
  undefined *puVar3;
  uint uVar4;
  uint uStack_38;
  int iStack_34;
  uint uStack_30;
  uint uStack_2c;
  uint uStack_28;
  undefined1 auStack_24 [16];
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    puVar3 = PTR_DAT_005a53c8;
    if (param_1 != (undefined *)0x0) {
      puVar3 = param_1;
    }
    FUN_0043d574(3,PTR_s_at_buzzer_005a53d8,PTR_s_D__01_workspace_s200_ap510b_iar__005a53d4,
                 PTR_s__atBuzzerTest_005a53d0,0x25,PTR_s_AT_BUZZER__para1__s_005a53cc,puVar3);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    puVar3 = PTR_DAT_005a53c8;
    if (param_1 != (undefined *)0x0) {
      puVar3 = param_1;
    }
    compress_log_output(0xc400000,PTR_s__at_buzzer_AT_BUZZER__para1__s_005a53dc,
                        PTR_s__at_buzzer_AT_BUZZER__para1__s_005a53dc,puVar3);
  }
  if (param_1 == (undefined *)0x0) {
    at_core_output(PTR_s_AT_BUZZER__Missing_parameters_005a53e0);
    at_core_output(PTR_s_Usage__005a53e4);
    at_core_output(PTR_s_AT_BUZZER_note_<note>_<tone>_<be_005a53e8);
    at_core_output(PTR_s_AT_BUZZER_play_<type>_005a53ec);
    at_core_output(PTR_s_AT_BUZZER_start_<freq>_<duty>_005a53f0);
    at_core_output(PTR_s_AT_BUZZER_stop_005a53f4);
    return 0;
  }
  iVar1 = FUN_00481818(param_1,0x2c);
  FUN_0043c0e4(auStack_24,0x10,0);
  if (iVar1 == 0) {
    FUN_0044b5a0(auStack_24,param_1,0xf);
    puVar3 = (undefined *)0x0;
  }
  else {
    uVar4 = iVar1 - (int)param_1;
    if (0xf < uVar4) {
      uVar4 = 0xf;
    }
    FUN_0044b5a0(auStack_24,param_1,uVar4);
    auStack_24[uVar4] = 0;
    puVar3 = (undefined *)(iVar1 + 1);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    puVar2 = PTR_DAT_005a53c8;
    if (puVar3 != (undefined *)0x0) {
      puVar2 = puVar3;
    }
    FUN_0043d574(4,PTR_s_at_buzzer_005a53d8,PTR_s_D__01_workspace_s200_ap510b_iar__005a53d4,
                 PTR_s__atBuzzerTest_005a53d0,0x4a,PTR_s_subcmd__s__params__s_005a53f8,auStack_24,
                 puVar2);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    puVar2 = PTR_DAT_005a53c8;
    if (puVar3 != (undefined *)0x0) {
      puVar2 = puVar3;
    }
    compress_log_output(0x10800000,PTR_s__at_buzzer_subcmd__s__params__s_005a53fc,
                        PTR_s__at_buzzer_subcmd__s__params__s_005a53fc,auStack_24,puVar2);
  }
  iVar1 = FUN_0044b610(auStack_24,PTR_DAT_005a5400,4);
  if (iVar1 == 0) {
    if (puVar3 == (undefined *)0x0) {
      at_core_output(PTR_s_AT_BUZZER_note__Missing_paramete_005a5404);
      at_core_output(PTR_s_Usage__AT_BUZZER_note_<note>_<to_005a5408);
      return 0;
    }
    uStack_28 = 0;
    uStack_2c = 0;
    uStack_30 = 0;
    iVar1 = FUN_00475fc0(puVar3,PTR_s__d__d__d_005a540c,&uStack_28,&uStack_2c,&uStack_30);
    if (iVar1 != 3) {
      at_core_output(PTR_s_AT_BUZZER_note__Invalid_paramete_005a5410,iVar1);
      at_core_output(PTR_s_Usage__AT_BUZZER_note_<note>_<to_005a5408);
      return 0;
    }
    if (((7 < uStack_28) || (3 < uStack_2c)) || (99 < uStack_30 - 1)) {
      at_core_output(PTR_s_AT_BUZZER_note__Parameters_out_o_005a5424);
      at_core_output(PTR_s_note__0_7__tone__0_3__beat__1_10_005a5428);
      return 0;
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uStack_38 = uStack_30;
      FUN_0043d574(3,PTR_s_at_buzzer_005a53d8,PTR_s_D__01_workspace_s200_ap510b_iar__005a53d4,
                   PTR_s__atBuzzerTest_005a53d0,99,PTR_s_Buzzer_note__note__d__tone__d__b_005a5414,
                   uStack_28,uStack_2c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xcc00000,PTR_s__at_buzzer_Buzzer_note__note__d__005a5418,
                          PTR_s__at_buzzer_Buzzer_note__note__d__005a5418,uStack_28,uStack_2c,
                          uStack_30);
    }
    at_core_output(PTR_s_Buzzer_note___d__tone___d__beat__005a541c,uStack_28,uStack_2c,uStack_30);
    DRV_BuzzerPlayNote(uStack_28 & 0xff,uStack_2c & 0xff,uStack_30 & 0xff);
    at_core_output(PTR_s_AT_BUZZER_OK_005a5420);
  }
  else {
    iVar1 = FUN_0044b610(auStack_24,PTR_DAT_005a542c,4);
    if (iVar1 == 0) {
      if (puVar3 == (undefined *)0x0) {
        at_core_output(PTR_s_AT_BUZZER_play__Missing_paramete_005a5430);
        at_core_output(PTR_s_Usage__AT_BUZZER_play_<type>_005a5434);
        return 0;
      }
      uVar4 = thunk_FUN_0048d86c(puVar3);
      if (10 < uVar4) {
        at_core_output(PTR_s_AT_BUZZER_play__Type_out_of_rang_005a5438);
        return 0;
      }
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_at_buzzer_005a53d8,PTR_s_D__01_workspace_s200_ap510b_iar__005a53d4,
                     PTR_s__atBuzzerTest_005a53d0,0x83,PTR_s_Buzzer_play_type___d_005a543c,uVar4);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__at_buzzer_Buzzer_play_type___d_005a5440,
                            PTR_s__at_buzzer_Buzzer_play_type___d_005a5440,uVar4);
      }
      at_core_output(PTR_s_Buzzer_play_type___d_005a5444,uVar4);
      DRV_BuzzerPlay(uVar4);
      at_core_output(PTR_s_AT_BUZZER_OK_005a5420);
    }
    else {
      iVar1 = FUN_0044b610(auStack_24,PTR_s_start_005a5448,5);
      if (iVar1 == 0) {
        if (puVar3 == (undefined *)0x0) {
          at_core_output(PTR_s_AT_BUZZER_start__Missing_paramet_005a544c);
          at_core_output(PTR_s_Usage__AT_BUZZER_start_<freq>_<d_005a5450);
          return 0;
        }
        iStack_34 = 0;
        uStack_38 = 0;
        iVar1 = FUN_00475fc0(puVar3,PTR_s__d__d_005a5454,&iStack_34,&uStack_38);
        if (iVar1 != 2) {
          at_core_output(PTR_s_AT_BUZZER_start__Invalid_paramet_005a5458,iVar1);
          at_core_output(PTR_s_Usage__AT_BUZZER_start_<freq>_<d_005a5450);
          return 0;
        }
        if ((19999 < iStack_34 - 1U) || (100 < uStack_38)) {
          at_core_output(PTR_s_AT_BUZZER_start__Parameters_out_o_005a545c);
          at_core_output(PTR_s_freq__1_20000__duty__0_100_005a5460);
          return 0;
        }
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_at_buzzer_005a53d8,PTR_s_D__01_workspace_s200_ap510b_iar__005a53d4,
                       PTR_s__atBuzzerTest_005a53d0,0xa5,
                       PTR_s_Buzzer_start__freq__d__duty__d_005a5464,iStack_34,uStack_38);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0xc800000,PTR_s__at_buzzer_Buzzer_start__freq__d_005a5468,
                              PTR_s__at_buzzer_Buzzer_start__freq__d_005a5468,iStack_34,uStack_38);
        }
        at_core_output(PTR_s_Buzzer_start__freq__d__duty__d_005a546c,iStack_34,uStack_38);
        DRV_BuzzerStart(iStack_34,uStack_38 & 0xff);
        at_core_output(PTR_s_AT_BUZZER_OK_005a5420);
      }
      else {
        iVar1 = FUN_0044b610(auStack_24,PTR_DAT_005a5470,4);
        if (iVar1 != 0) {
          at_core_output(PTR_s_AT_BUZZER__Unknown_subcommand____005a5480,auStack_24);
          at_core_output(PTR_s_Use__note__play__start__stop_005a5484);
          return 0;
        }
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_at_buzzer_005a53d8,PTR_s_D__01_workspace_s200_ap510b_iar__005a53d4,
                       PTR_s__atBuzzerTest_005a53d0,0xae,PTR_s_Buzzer_stop_005a5474);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0xc000000,PTR_s__at_buzzer_Buzzer_stop_005a5478,
                              PTR_s__at_buzzer_Buzzer_stop_005a5478);
        }
        at_core_output(PTR_s_Buzzer_stop_005a547c);
        DRV_BuzzerStop();
        at_core_output(PTR_s_AT_BUZZER_OK_005a5420);
      }
    }
  }
  return 1;
}

