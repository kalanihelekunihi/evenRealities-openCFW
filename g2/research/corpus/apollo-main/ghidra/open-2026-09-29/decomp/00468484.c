
undefined4 Onboarding_common_data_handler(int param_1,byte *param_2,uint param_3)

{
  byte bVar1;
  char cVar2;
  int iVar3;
  byte *pbVar4;
  byte bVar5;
  byte bVar6;
  undefined4 local_28;
  uint local_24;
  uint local_20;
  uint local_1c;
  uint local_18;
  
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    local_24 = DAT_00468f04;
    local_28 = 0xf3;
    local_20 = param_3;
    FUN_0043d574(4,DAT_00468a3c,DAT_00468a38,DAT_00468f08);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00468f0c,DAT_00468f0c,param_3);
  }
  onboarding_process_mutex_init();
  cVar2 = FUN_0045a568();
  if ((param_2 != (byte *)0x0) && (param_3 != 0)) {
    if (param_1 == 0) {
      iVar3 = APP_PbRxOnboardingFrameDataProcess(param_2,param_3 & 0xffff);
      pbVar4 = DAT_00468c24;
      if (iVar3 == 0) {
        if (DAT_00468c24[2] == 2) {
          if (*DAT_00468c24 == 4) {
            onboarding_flag_update(0);
            if (((cVar2 == '\x01') && (iVar3 = FUN_00443484(), iVar3 == 1)) &&
               (iVar3 = FUN_004434d0(0x10), iVar3 == 1)) {
              FUN_00464c36(0x10,0,0,0);
            }
          }
          else {
            iVar3 = FUN_00443484();
            if ((iVar3 == 0) || (iVar3 = FUN_004434d0(0x10), iVar3 != 1)) {
              iVar3 = FUN_0043d0ce();
              if (iVar3 << 0x1e < 0) {
                local_20 = (uint)*pbVar4;
                local_24 = DAT_00468f10;
                local_28 = 0x108;
                FUN_0043d574(3,DAT_00468a3c,DAT_00468a38,DAT_00468f08);
              }
              iVar3 = FUN_0043d0ce();
              if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
                compress_log_output(0xc400000,DAT_00468f14,DAT_00468f14,*pbVar4);
              }
              if (cVar2 == '\x01') {
                FUN_00464b2e(0x10,0,0,0);
              }
            }
            else if (((cVar2 == '\x01') && (iVar3 = FUN_00443484(), iVar3 == 1)) &&
                    (iVar3 = FUN_004434d0(0x10), iVar3 == 1)) {
              local_28._0_2_ = CONCAT11(*DAT_00468f18,(undefined1)local_28);
              FUN_00464bb2(0x10,(int)&local_28 + 1,1,0);
            }
          }
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          local_24 = DAT_00468f1c;
          local_28 = 0x116;
          FUN_0043d574(1,DAT_00468a3c,DAT_00468a38,DAT_00468f08);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_0046908c,DAT_0046908c);
        }
      }
    }
    else if (param_1 == 5) {
      if (param_3 == 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          local_24 = DAT_00469090;
          local_28 = 0x11e;
          FUN_0043d574(2,DAT_00468a3c,DAT_00468a38,DAT_00468f08);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_00469094,DAT_00469094);
        }
      }
      else {
        bVar1 = *param_2;
        if (bVar1 == 9) {
          if (2 < param_3) {
            bVar1 = param_2[1];
            bVar5 = param_2[2];
            iVar3 = FUN_0043d0ce();
            if (iVar3 << 0x1e < 0) {
              local_1c = (uint)bVar5;
              local_20 = (uint)bVar1;
              local_24 = DAT_00469098;
              local_28 = 0x129;
              FUN_0043d574(3,DAT_00468a3c,DAT_00468a38,DAT_00468f08);
            }
            iVar3 = FUN_0043d0ce();
            if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
              local_28 = (uint)bVar5;
              compress_log_output(0xc800000,DAT_0046909c,DAT_0046909c,bVar1);
            }
            pbVar4 = DAT_00468c24;
            *DAT_00468c24 = bVar1;
            pbVar4[1] = bVar5;
            if (cVar2 == '\x01') {
              local_28 = CONCAT31(local_28._1_3_,*DAT_004690a0);
              FUN_00464bb2(0x10,&local_28,1,0);
            }
          }
        }
        else if (bVar1 == 0xd) {
          if (1 < param_3) {
            bVar1 = param_2[1];
            pbVar4 = (byte *)kvdbOnboardingConfigPointer(0);
            if (pbVar4 == (byte *)0x0) {
              bVar5 = 0;
            }
            else {
              bVar5 = *pbVar4;
            }
            if ((bVar1 == 1) && (bVar5 == 1)) {
              bVar6 = 1;
            }
            else {
              bVar6 = 0;
            }
            iVar3 = FUN_0043d0ce();
            if (iVar3 << 0x1e < 0) {
              local_18 = (uint)bVar6;
              local_1c = (uint)bVar5;
              local_20 = (uint)bVar1;
              local_24 = DAT_004690a4;
              local_28 = 0x140;
              FUN_0043d574(4,DAT_00468a3c,DAT_00468a38,DAT_00468f08);
            }
            iVar3 = FUN_0043d0ce();
            if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
              local_24 = (uint)bVar6;
              local_28 = (uint)bVar5;
              compress_log_output(0x10c00000,DAT_004690a8,DAT_004690a8,bVar1);
            }
            if ((pbVar4 != (byte *)0x0) && (*pbVar4 != bVar6)) {
              onboarding_flag_update(bVar6);
              iVar3 = FUN_0043d0ce();
              if (iVar3 << 0x1e < 0) {
                local_1c = (uint)bVar6;
                local_20 = (uint)*pbVar4;
                local_24 = DAT_004690ac;
                local_28 = 0x145;
                FUN_0043d574(3,DAT_00468a3c,DAT_00468a38,DAT_00468f08);
              }
              iVar3 = FUN_0043d0ce();
              if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
                local_28 = (uint)bVar6;
                compress_log_output(0xc800000,DAT_004690b0,DAT_004690b0,*pbVar4);
              }
            }
            RPC_OnboardingFlagReplyToPeer(bVar5);
            onboarding_check_start_disp(0);
          }
        }
        else if (bVar1 == 0xe) {
          if (1 < param_3) {
            bVar1 = param_2[1];
            pbVar4 = (byte *)kvdbOnboardingConfigPointer(0);
            if (pbVar4 == (byte *)0x0) {
              bVar5 = 0;
            }
            else {
              bVar5 = *pbVar4;
            }
            if ((bVar1 == 1) && (bVar5 == 1)) {
              bVar6 = 1;
            }
            else {
              bVar6 = 0;
            }
            iVar3 = FUN_0043d0ce();
            if (iVar3 << 0x1e < 0) {
              local_18 = (uint)bVar6;
              local_1c = (uint)bVar5;
              local_20 = (uint)bVar1;
              local_24 = DAT_004690a4;
              local_28 = 0x15b;
              FUN_0043d574(3,DAT_00468a3c,DAT_00468a38,DAT_00468f08);
            }
            iVar3 = FUN_0043d0ce();
            if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
              local_24 = (uint)bVar6;
              local_28 = (uint)bVar5;
              compress_log_output(0xcc00000,DAT_004690a8,DAT_004690a8,bVar1);
            }
            if ((pbVar4 != (byte *)0x0) && (*pbVar4 != bVar6)) {
              onboarding_flag_update(bVar6);
              iVar3 = FUN_0043d0ce();
              if (iVar3 << 0x1e < 0) {
                local_1c = (uint)bVar6;
                local_20 = (uint)*pbVar4;
                local_24 = DAT_004690ac;
                local_28 = 0x160;
                FUN_0043d574(3,DAT_00468a3c,DAT_00468a38,DAT_00468f08);
              }
              iVar3 = FUN_0043d0ce();
              if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
                local_28 = (uint)bVar6;
                compress_log_output(0xc800000,DAT_004690b0,DAT_004690b0,*pbVar4);
              }
            }
          }
        }
        else if (bVar1 == 0xf) {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            local_24 = DAT_004690b4;
            local_28 = 0x169;
            FUN_0043d574(3,DAT_00468a3c,DAT_00468a38,DAT_00468f08);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0xc000000,DAT_004690b8,DAT_004690b8);
          }
          if (cVar2 == '\x01') {
            local_24 = CONCAT22(local_24._2_2_,*DAT_004690bc);
            FUN_00464bb2(0x10,&local_24,2,0);
          }
        }
        else if (bVar1 == 0x10) {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            local_24 = DAT_004690c0;
            local_28 = 0x176;
            FUN_0043d574(3,DAT_00468a3c,DAT_00468a38,DAT_00468f08);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0xc000000,DAT_004690c4,DAT_004690c4);
          }
          if (cVar2 == '\x01') {
            local_28 = CONCAT22(*DAT_004690c8,(undefined2)local_28);
            FUN_00464bb2(0x10,(int)&local_28 + 2,2,0);
          }
        }
        else {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            local_20 = (uint)bVar1;
            local_24 = DAT_004690cc;
            local_28 = 0x181;
            FUN_0043d574(2,DAT_00468a3c,DAT_00468a38,DAT_00468f08);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x8400000,PTR_s__onboarding_Onboarding__unknown_p_004690d0,
                                PTR_s__onboarding_Onboarding__unknown_p_004690d0,bVar1);
          }
        }
      }
    }
  }
  return 0;
}

