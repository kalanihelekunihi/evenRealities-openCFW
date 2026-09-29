
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_005011d0(undefined4 param_1,int *param_2)

{
  char *pcVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  
  if (param_2 == (int *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_dashboard_ext_00501d1c,PTR_s_D__01_workspace_s200_ap510b_iar__00501d18,
                   PTR_s_handle_send_pb_file_data_00501d14,0x20f,PTR_s_STEP4__data_NULL_00501d10);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__dashboard_ext_STEP4__data_NULL_00501d20);
    }
  }
  else {
    iVar6 = *param_2;
    uVar3 = param_2[1];
    iVar7 = param_2[2];
    iVar4 = param_2[3];
    iVar8 = param_2[4];
    uVar5 = (uint)*(ushort *)(param_2 + 5);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_dashboard_ext_00501d1c,PTR_s_D__01_workspace_s200_ap510b_iar__00501d18,
                   PTR_s_handle_send_pb_file_data_00501d14,0x21d,
                   PTR_s_STEP4__session__u_total__u_compr_00501d24,iVar6,uVar3,iVar7,iVar4,iVar8,
                   uVar5);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x11800000,PTR_s__dashboard_ext_STEP4__session__u_00501d28,
                          PTR_s__dashboard_ext_STEP4__session__u_00501d28,iVar6,uVar3,iVar7,iVar4,
                          iVar8,uVar5);
    }
    pcVar1 = _DAT_0050181c;
    if (uVar5 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_dashboard_ext_00501d1c,PTR_s_D__01_workspace_s200_ap510b_iar__00501d18,
                     PTR_s_handle_send_pb_file_data_00501d14,0x221,
                     PTR_s_STEP4__empty_fragment__ignore__f_00501d2c,iVar4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__dashboard_ext_STEP4__empty_frag_00501d30,
                            PTR_s__dashboard_ext_STEP4__empty_frag_00501d30,iVar4);
      }
      FUN_00500824();
      FUN_00501108(param_1,iVar6,uVar3,iVar7,iVar4,iVar8,1);
    }
    else if ((uVar3 == 0) || (0x5000 < uVar3)) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_dashboard_ext_00501d1c,PTR_s_D__01_workspace_s200_ap510b_iar__00501d18,
                     PTR_s_handle_send_pb_file_data_00501d14,0x22b,
                     PTR_s_STEP4__total_size__u_out_of_rang_00501d34,uVar3,0x5000);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4800000,PTR_s__dashboard_ext_STEP4__total_size_00501d38,
                            PTR_s__dashboard_ext_STEP4__total_size_00501d38,uVar3,0x5000);
      }
      FUN_00500824();
      FUN_00501108(param_1,iVar6,uVar3,iVar7,iVar4,iVar8,1);
    }
    else if (*_DAT_0050181c == '\0') {
      if (iVar4 == 0) {
        if (uVar3 < uVar5) {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(1,PTR_s_dashboard_ext_00501d1c,
                         PTR_s_D__01_workspace_s200_ap510b_iar__00501d18,
                         PTR_s_handle_send_pb_file_data_00501d14,0x23f,
                         PTR_s_STEP4__first_packet_raw__u_>_tot_00501d44,uVar5,uVar3);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x4800000,PTR_s__dashboard_ext_STEP4__first_pack_00501d48,
                                PTR_s__dashboard_ext_STEP4__first_pack_00501d48,uVar5,uVar3);
          }
          FUN_00500824();
          FUN_00501108(param_1,iVar6,uVar3,iVar7,0,iVar8,1);
        }
        else {
          FUN_00500824();
          *pcVar1 = '\x01';
          *(int *)(pcVar1 + 4) = iVar6;
          *(uint *)(pcVar1 + 8) = uVar3;
          *(int *)(pcVar1 + 0xc) = iVar7;
          pcVar1[0x10] = '\0';
          pcVar1[0x11] = '\0';
          pcVar1[0x12] = '\0';
          pcVar1[0x13] = '\0';
          pcVar1[0x18] = '\x01';
          pcVar1[0x19] = '\0';
          pcVar1[0x1a] = '\0';
          pcVar1[0x1b] = '\0';
          FUN_00439be4(pcVar1 + 0x1c,(int)param_2 + 0x16,uVar5);
          *(uint *)(pcVar1 + 0x14) = uVar5;
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(3,PTR_s_dashboard_ext_00501d1c,
                         PTR_s_D__01_workspace_s200_ap510b_iar__00501d18,
                         PTR_s_handle_send_pb_file_data_00501d14,0x253,
                         PTR_s_STEP4__session__u_start__first_f_00501d4c,iVar6,uVar5,uVar3);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0xcc00000,PTR_s__dashboard_ext_STEP4__session__u_00501d50,
                                PTR_s__dashboard_ext_STEP4__session__u_00501d50,iVar6,uVar5,uVar3);
          }
          FUN_00501108(param_1,iVar6,uVar3,iVar7,0,iVar8,0);
          FUN_00500f00();
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_dashboard_ext_00501d1c,
                       PTR_s_D__01_workspace_s200_ap510b_iar__00501d18,
                       PTR_s_handle_send_pb_file_data_00501d14,0x236,
                       PTR_s_STEP4__first_packet_but_frag_idx_00501d3c,iVar4);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__dashboard_ext_STEP4__first_pack_00501d40,
                              PTR_s__dashboard_ext_STEP4__first_pack_00501d40,iVar4);
        }
        FUN_00500824();
        FUN_00501108(param_1,iVar6,uVar3,iVar7,iVar4,iVar8,1);
      }
    }
    else if ((((*(int *)(_DAT_0050181c + 4) == iVar6) && (*(uint *)(_DAT_0050181c + 8) == uVar3)) &&
             (*(int *)(_DAT_0050181c + 0xc) == iVar7)) &&
            (*(int *)(_DAT_0050181c + 0x10) + 1 == iVar4)) {
      if (uVar3 < uVar5 + *(int *)(_DAT_0050181c + 0x14)) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_dashboard_ext_00501d1c,
                       PTR_s_D__01_workspace_s200_ap510b_iar__00501d18,
                       PTR_s_handle_send_pb_file_data_00501d14,0x276,
                       PTR_s_STEP4__bytes_overflow__acc__u___r_00502124,
                       *(undefined4 *)(pcVar1 + 0x14),uVar5,uVar3,0x5000);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x5000000,PTR_s__dashboard_ext_STEP4__bytes_over_00502128,
                              PTR_s__dashboard_ext_STEP4__bytes_over_00502128,
                              *(undefined4 *)(pcVar1 + 0x14),uVar5,uVar3,0x5000);
        }
        FUN_00500824();
        FUN_00501108(param_1,iVar6,uVar3,iVar7,iVar4,iVar8,1);
      }
      else {
        FUN_00439be4(_DAT_0050181c + *(int *)(_DAT_0050181c + 0x14) + 0x1c,(int)param_2 + 0x16,uVar5
                    );
        *(uint *)(pcVar1 + 0x14) = uVar5 + *(int *)(pcVar1 + 0x14);
        *(int *)(pcVar1 + 0x10) = iVar4;
        *(int *)(pcVar1 + 0x18) = *(int *)(pcVar1 + 0x18) + 1;
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_dashboard_ext_00501d1c,
                       PTR_s_D__01_workspace_s200_ap510b_iar__00501d18,
                       PTR_s_handle_send_pb_file_data_00501d14,0x289,
                       PTR_s_STEP4__session__u_frag_idx__u_OK_0050212c,*(undefined4 *)(pcVar1 + 4),
                       iVar4,*(undefined4 *)(pcVar1 + 0x14),*(undefined4 *)(pcVar1 + 8),
                       *(undefined4 *)(pcVar1 + 0x18));
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x11400000,PTR_s__dashboard_ext_STEP4__session__u_00502134,
                              PTR_s__dashboard_ext_STEP4__session__u_00502134,
                              *(undefined4 *)(pcVar1 + 4),iVar4,*(undefined4 *)(pcVar1 + 0x14),
                              *(undefined4 *)(pcVar1 + 8),*(undefined4 *)(pcVar1 + 0x18));
        }
        FUN_00501108(param_1,iVar6,uVar3,iVar7,iVar4,iVar8,0);
        FUN_00500f00();
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_dashboard_ext_00501d1c,PTR_s_D__01_workspace_s200_ap510b_iar__00501d18,
                     PTR_s_handle_send_pb_file_data_00501d14,0x262,
                     PTR_s_STEP4__session_order_mismatch__r_00501d54);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__dashboard_ext_STEP4__session_or_00501d58,
                            PTR_s__dashboard_ext_STEP4__session_or_00501d58);
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_dashboard_ext_00501d1c,PTR_s_D__01_workspace_s200_ap510b_iar__00501d18,
                     PTR_s_handle_send_pb_file_data_00501d14,0x267,_DAT_005020e8,
                     *(undefined4 *)(pcVar1 + 4),*(undefined4 *)(pcVar1 + 8),
                     *(undefined4 *)(pcVar1 + 0xc),*(undefined4 *)(pcVar1 + 0x10));
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x9000000,_DAT_00502104,_DAT_00502104,*(undefined4 *)(pcVar1 + 4),
                            *(undefined4 *)(pcVar1 + 8),*(undefined4 *)(pcVar1 + 0xc),
                            *(undefined4 *)(pcVar1 + 0x10));
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_dashboard_ext_00501d1c,PTR_s_D__01_workspace_s200_ap510b_iar__00501d18,
                     PTR_s_handle_send_pb_file_data_00501d14,0x26a,
                     PTR_s_incoming__sid__u_total__u_compre_0050211c,iVar6,uVar3,iVar7,iVar4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x9000000,PTR_s__dashboard_ext__incoming__sid__u_00502120,
                            PTR_s__dashboard_ext__incoming__sid__u_00502120,iVar6,uVar3,iVar7,iVar4)
        ;
      }
      FUN_00500824();
      FUN_00501108(param_1,iVar6,uVar3,iVar7,iVar4,iVar8,1);
    }
  }
  return;
}

