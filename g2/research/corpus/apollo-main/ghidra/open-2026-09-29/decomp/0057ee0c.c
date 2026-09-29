
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0057ee0c(undefined4 param_1,undefined4 param_2,char *param_3)

{
  undefined4 uVar1;
  undefined1 *puVar2;
  char *pcVar3;
  char *pcVar4;
  char *pcVar5;
  int iVar6;
  int iVar7;
  undefined1 auStack_924 [256];
  char acStack_824 [264];
  undefined1 auStack_71c [264];
  undefined1 auStack_614 [256];
  undefined1 auStack_514 [256];
  undefined1 auStack_414 [256];
  undefined1 auStack_314 [256];
  char acStack_214 [256];
  char acStack_114 [256];
  
  if (*_DAT_0057f270 == 1) {
    for (; (*param_3 != '\0' && (*param_3 != ' ')); param_3 = param_3 + 1) {
    }
    for (; (*param_3 != '\0' && (*param_3 == ' ')); param_3 = param_3 + 1) {
    }
    pcVar3 = param_3;
    if (*param_3 == '\0') {
      FUN_004733ee(_DAT_0057f8b8);
    }
    else {
      for (; (pcVar4 = pcVar3, *pcVar3 != '\0' && (*pcVar3 != ' ')); pcVar3 = pcVar3 + 1) {
      }
      for (; (*pcVar4 != '\0' && (*pcVar4 == ' ')); pcVar4 = pcVar4 + 1) {
      }
      pcVar5 = pcVar4;
      if (*pcVar4 == '\0') {
        FUN_004733ee(_DAT_0057f8b8);
      }
      else {
        for (; (*pcVar5 != '\0' && (*pcVar5 != ' ')); pcVar5 = pcVar5 + 1) {
        }
        iVar7 = (int)pcVar3 - (int)param_3;
        iVar6 = (int)pcVar5 - (int)pcVar4;
        if ((iVar7 < 0xff) && (iVar6 < 0xff)) {
          FUN_0044b5a0(acStack_114,param_3,iVar7);
          acStack_114[iVar7] = '\0';
          FUN_0044b5a0(acStack_214,pcVar4,iVar6);
          acStack_214[iVar6] = '\0';
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_prvCommand_filesystem_0057f954,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0057f950,
                         PTR_s_prvCommand_mv_0057f94c,0x26d,PTR_s_param1___s_0057f948,acStack_114);
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x10400000,PTR_s__prvCommand_filesystem_param1____0057f958,
                                PTR_s__prvCommand_filesystem_param1____0057f958,acStack_114);
          }
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_prvCommand_filesystem_0057f954,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0057f950,
                         PTR_s_prvCommand_mv_0057f94c,0x26e,PTR_s_param2___s_0057f95c,acStack_214);
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x10400000,PTR_s__prvCommand_filesystem_param2____0057f960,
                                PTR_s__prvCommand_filesystem_param2____0057f960,acStack_214);
          }
          FUN_0043c0e4(auStack_314,0xff,0);
          iVar6 = _DAT_0057f3c4;
          if (acStack_114[0] == '/') {
            FUN_0044b5a0(auStack_314,acStack_114,0xfe);
          }
          else {
            FUN_0048d540(auStack_314,_DAT_0057f3c4);
            iVar7 = FUN_0044a43c(iVar6);
            if ((*(char *)(iVar7 + iVar6 + -1) != '/') && (acStack_114[0] != '/')) {
              FUN_00567c80(auStack_314,0x57f26c);
            }
            FUN_00567c80(auStack_314,acStack_114);
          }
          FUN_0043c0e4(auStack_414,0xff,0);
          iVar6 = _DAT_0057f3c4;
          if (acStack_214[0] == '/') {
            FUN_0044b5a0(auStack_414,acStack_214,0xfe);
          }
          else {
            FUN_0048d540(auStack_414,_DAT_0057f3c4);
            iVar7 = FUN_0044a43c(iVar6);
            if ((*(char *)(iVar7 + iVar6 + -1) != '/') && (acStack_214[0] != '/')) {
              FUN_00567c80(auStack_414,0x57f26c);
            }
            FUN_00567c80(auStack_414,acStack_214);
          }
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_prvCommand_filesystem_0057f954,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0057f950,
                         PTR_s_prvCommand_mv_0057f94c,0x28e,PTR_s_src_path___s_0057f964,auStack_314)
            ;
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x10400000,PTR_s__prvCommand_filesystem_src_path__0057f968,
                                PTR_s__prvCommand_filesystem_src_path__0057f968,auStack_314);
          }
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_prvCommand_filesystem_0057f954,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0057f950,
                         PTR_s_prvCommand_mv_0057f94c,0x28f,PTR_s_dst_path___s_0057f96c,auStack_414)
            ;
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x10400000,PTR_s__prvCommand_filesystem_dst_path__0057f970,
                                PTR_s__prvCommand_filesystem_dst_path__0057f970,auStack_414);
          }
          iVar6 = FUN_0057eaa8(auStack_514,auStack_314);
          if (iVar6 == 0) {
            iVar6 = FUN_0057eaa8(auStack_614,auStack_414);
            uVar1 = _DAT_0057f3c0;
            if (iVar6 == 0) {
              iVar6 = FUN_004cfa8a(_DAT_0057f3c0,auStack_514,auStack_71c);
              if (iVar6 == 0) {
                iVar6 = FUN_004cfa8a(uVar1,auStack_614,acStack_824);
                FUN_0043c0e4(auStack_924,0xff,0);
                if (iVar6 == 0) {
                  if (acStack_824[0] != '\x02') {
                    FUN_004733ee(PTR_s_mv__destination_file_already_exi_0057fc5c);
                    return 0;
                  }
                  FUN_0048d540(auStack_924,auStack_614);
                  iVar6 = FUN_0044a43c();
                  if (auStack_924[iVar6 + -1] != '/') {
                    FUN_00567c80(auStack_924,0x57f26c);
                  }
                  iVar6 = FUN_00567c64(auStack_514,0x2f);
                  if (iVar6 == 0) {
                    puVar2 = auStack_514;
                  }
                  else {
                    puVar2 = (undefined1 *)(iVar6 + 1);
                  }
                  FUN_00567c80(auStack_924,puVar2);
                }
                else {
                  FUN_0048d540(auStack_924,auStack_614);
                }
                iVar6 = FUN_0043d0ce();
                if (iVar6 << 0x1e < 0) {
                  FUN_0043d574(4,PTR_s_prvCommand_filesystem_0057f954,
                               PTR_s_D__01_workspace_s200_ap510b_iar__0057f950,
                               PTR_s_prvCommand_mv_0057f94c,0x2c9,PTR_s_final_dst_path___s_0057fc60,
                               auStack_924);
                }
                iVar6 = FUN_0043d0ce();
                if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                  compress_log_output(0x10400000,PTR_s__prvCommand_filesystem_final_dst_0057fc64,
                                      PTR_s__prvCommand_filesystem_final_dst_0057fc64,auStack_924);
                }
                iVar6 = FUN_004cfa8a(uVar1,auStack_924,acStack_824);
                if (iVar6 == 0) {
                  FUN_004733ee(PTR_s_mv__destination_already_exists_0057fc68);
                }
                else {
                  iVar6 = FUN_004cfa80(uVar1,auStack_514,auStack_924);
                  if (iVar6 != 0) {
                    FUN_004733ee(PTR_s_mv__move_rename_failed_0057ff10);
                  }
                }
              }
              else {
                FUN_004733ee(PTR_s_mv__source_file_directory_not_fo_0057f97c);
              }
            }
            else {
              FUN_004733ee(PTR_s_mv__invalid_destination_path_0057f978);
            }
          }
          else {
            FUN_004733ee(PTR_s_mv__invalid_source_path_0057f974);
          }
        }
        else {
          FUN_004733ee(PTR_s_mv__parameter_too_long_0057f944);
        }
      }
    }
  }
  return 0;
}

