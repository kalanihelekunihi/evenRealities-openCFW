
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 _atTpTest(uint param_1,uint param_2)

{
  undefined *puVar1;
  ushort uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uStack_38;
  undefined *puStack_34;
  uint uStack_30;
  uint uStack_2c;
  uint uStack_28;
  uint uStack_24;
  uint uStack_20;
  ushort uStack_1c;
  ushort uStack_1a;
  ushort uStack_18;
  ushort uStack_16;
  ushort uStack_14;
  
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    puStack_34 = PTR_s_para1___s_005a5d18;
    uStack_38 = 0x1d;
    uStack_30 = param_1;
    FUN_0043d574(3,_DAT_005a5d24,PTR_s_D__01_workspace_s200_ap510b_iar__005a5d20,
                 PTR_s__atTpTest_005a5d1c);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__at_tp_para1___s_005a5d28,PTR_s__at_tp_para1___s_005a5d28,
                        param_1);
  }
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    puStack_34 = PTR_s_para2___s_005a5d2c;
    uStack_38 = 0x1e;
    uStack_30 = param_2;
    FUN_0043d574(3,_DAT_005a5d24,PTR_s_D__01_workspace_s200_ap510b_iar__005a5d20,
                 PTR_s__atTpTest_005a5d1c);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__at_tp_para2___s_005a5d30,PTR_s__at_tp_para2___s_005a5d30,
                        param_2);
  }
  uVar4 = FUN_0044a43c(0x5a5d08);
  iVar3 = FUN_0044b610(param_1,0x5a5d08,uVar4);
  if (iVar3 == 0) {
    FUN_0043bb00(&uStack_1c,0,10);
    FUN_0055b6a8(&uStack_1c);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      uStack_20 = (uint)uStack_14;
      uStack_24 = (uint)uStack_16;
      uStack_28 = (uint)uStack_18;
      uStack_2c = (uint)uStack_1a;
      uStack_30 = (uint)uStack_1c;
      puStack_34 = PTR_s_diff___u___u___u___u___u_005a5d34;
      uStack_38 = 0x23;
      FUN_0043d574(3,_DAT_005a5d24,PTR_s_D__01_workspace_s200_ap510b_iar__005a5d20,
                   PTR_s__atTpTest_005a5d1c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      uStack_2c = (uint)uStack_14;
      uStack_30 = (uint)uStack_16;
      puStack_34 = (undefined *)(uint)uStack_18;
      uStack_38 = (uint)uStack_1a;
      compress_log_output(0xd400000,PTR_s__at_tp_diff___u___u___u___u___u_005a5d38,
                          PTR_s__at_tp_diff___u___u___u___u___u_005a5d38,uStack_1c);
    }
    puStack_34 = (undefined *)(uint)uStack_14;
    uStack_38 = (uint)uStack_16;
    at_core_output(PTR_s_diff___u___u___u___u___u_005a5d3c,uStack_1c,uStack_1a,uStack_18);
  }
  else {
    uVar4 = FUN_0044a43c(0x5a5d0c);
    iVar3 = FUN_0044b610(param_1,0x5a5d0c,uVar4);
    uVar4 = _DAT_005a5d40;
    if (iVar3 == 0) {
      FUN_0055b64a();
    }
    else {
      uVar5 = FUN_0044a43c(_DAT_005a5d40);
      iVar3 = FUN_0044b610(param_1,uVar4,uVar5);
      uVar4 = _DAT_005a5d48;
      if (iVar3 == 0) {
        *_DAT_005a5d44 = 1;
      }
      else {
        uVar5 = FUN_0044a43c(_DAT_005a5d48);
        iVar3 = FUN_0044b610(param_1,uVar4,uVar5);
        puVar1 = PTR_s_bsln_read_005a5d4c;
        if (iVar3 == 0) {
          *_DAT_005a5d44 = 0;
        }
        else {
          uVar4 = FUN_0044a43c(PTR_s_bsln_read_005a5d4c);
          iVar3 = FUN_0044b610(param_1,puVar1,uVar4);
          puVar1 = PTR_s_bsln_set_005a5d5c;
          if (iVar3 == 0) {
            uVar2 = FUN_0055b78a();
            iVar3 = FUN_0043d0ce();
            if (iVar3 << 0x1e < 0) {
              uStack_30 = (uint)uVar2;
              puStack_34 = PTR_s_Proximity_baseline___u_005a5d50;
              uStack_38 = 0x35;
              FUN_0043d574(3,_DAT_005a5d24,PTR_s_D__01_workspace_s200_ap510b_iar__005a5d20,
                           PTR_s__atTpTest_005a5d1c);
            }
            iVar3 = FUN_0043d0ce();
            if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
              compress_log_output(0xc400000,PTR_s__at_tp_Proximity_baseline___u_005a5d54,
                                  PTR_s__at_tp_Proximity_baseline___u_005a5d54,uVar2);
            }
            at_core_output(PTR_s_Proximity_baseline___u_005a5d58,uVar2);
          }
          else {
            uVar4 = FUN_0044a43c(PTR_s_bsln_set_005a5d5c);
            iVar3 = FUN_0044b610(param_1,puVar1,uVar4);
            puVar1 = PTR_s_gesture_cfg_read_005a5d6c;
            if (iVar3 == 0) {
              FUN_0055b64a();
              uStack_2c = 0;
              FUN_0055b6dc(&uStack_2c);
              FUN_0055b730();
              iVar3 = FUN_0043d0ce();
              if (iVar3 << 0x1e < 0) {
                puStack_34 = PTR_s_Proximity_baseline_save_command_s_005a5d60;
                uStack_38 = 0x3e;
                FUN_0043d574(3,_DAT_005a5d24,PTR_s_D__01_workspace_s200_ap510b_iar__005a5d20,
                             PTR_s__atTpTest_005a5d1c);
              }
              iVar3 = FUN_0043d0ce();
              if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
                compress_log_output(0xc000000,PTR_s__at_tp_Proximity_baseline_save_c_005a5d64,
                                    PTR_s__at_tp_Proximity_baseline_save_c_005a5d64);
              }
              at_core_output(PTR_s_Proximity_baseline_save_command_s_005a5d68);
            }
            else {
              uVar4 = FUN_0044a43c(PTR_s_gesture_cfg_read_005a5d6c);
              iVar3 = FUN_0044b610(param_1,puVar1,uVar4);
              puVar1 = PTR_s_gesture_cfg_set_005a5d74;
              if (iVar3 == 0) {
                FUN_0043bb00(&puStack_34,0,2);
                iVar3 = FUN_0055b92a(&puStack_34);
                if (iVar3 != 0) {
                  at_core_output(PTR_s_Gesture_cfg_read_failed__005a5d70);
                  return 0;
                }
                atTpPrintGestureCfg(&puStack_34);
              }
              else {
                uVar4 = FUN_0044a43c(PTR_s_gesture_cfg_set_005a5d74);
                iVar3 = FUN_0044b610(param_1,puVar1,uVar4);
                if (iVar3 == 0) {
                  FUN_0043bb00((int)&uStack_38 + 2,0,2);
                  FUN_0043bb00(&uStack_38,0,2);
                  uStack_30 = 0;
                  if (param_2 == 0) {
                    at_core_output(PTR_s_Usage__AT_TP_gesture_cfg_set_<th_005a5d78);
                    return 0;
                  }
                  iVar3 = FUN_00475fc0(param_2,0x5a5d10,&uStack_30);
                  if (((iVar3 != 1) || (uStack_30 == 0)) || (0xffff < uStack_30)) {
                    at_core_output(PTR_s_Invalid_gesture_cfg__Usage__AT_T_005a5d7c);
                    return 0;
                  }
                  uStack_38 = CONCAT22((short)uStack_30,(undefined2)uStack_38);
                  iVar3 = FUN_0055b840((int)&uStack_38 + 2);
                  if (iVar3 != 0) {
                    at_core_output(PTR_s_Gesture_cfg_write_failed__005a5d80);
                    return 0;
                  }
                  osDelay(100);
                  iVar3 = FUN_0055b92a(&uStack_38);
                  if (iVar3 != 0) {
                    at_core_output(PTR_s_Gesture_cfg_write_success__but_r_005a5d84);
                    return 0;
                  }
                  if ((uStack_38 & 0xffff) != (uint)uStack_38._2_2_) {
                    at_core_output(PTR_s_Gesture_cfg_write_mismatch__wrot_005a5d88,uStack_38._2_2_,
                                   uStack_38 & 0xffff);
                    return 0;
                  }
                  at_core_output(PTR_s_Gesture_cfg_updated_and_verified_005a5d8c);
                  atTpPrintGestureCfg(&uStack_38);
                }
              }
            }
          }
        }
      }
    }
  }
  at_core_output(PTR_s_AT_TP_OK_005a5d90);
  return 1;
}

