
undefined8 FUN_004437e0(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  byte *pbVar2;
  int *piVar3;
  char *pcVar4;
  undefined4 *puVar5;
  undefined4 *puVar6;
  uint *puVar7;
  uint *puVar8;
  int iVar9;
  undefined4 uVar10;
  uint3 uVar11;
  
  iVar9 = FUN_0043d0ce();
  if (iVar9 << 0x1e < 0) {
    param_2 = 0x279;
    param_3 = DAT_004442bc;
    FUN_0043d574(3,DAT_004443ac,DAT_004443a8,DAT_004443a4,0x279,DAT_004442bc,param_4);
  }
  iVar9 = FUN_0043d0ce();
  if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_004442c0,DAT_004442c0);
  }
  FUN_004425a6();
  pbVar2 = DAT_004442c4;
  param_2 = param_2 & 0xffffff00;
  FUN_0043c0e4(DAT_004442c4,2,0);
  piVar3 = DAT_004442c8;
  if (*(char *)*DAT_004442c8 != '\x01') {
    iVar9 = FUN_0043d0ce();
    if (iVar9 << 0x1e < 0) {
      param_2 = 0x27e;
      param_3 = DAT_004442cc;
      FUN_0043d574(1,DAT_004443ac,DAT_004443a8,DAT_004443a4);
    }
    iVar9 = FUN_0043d0ce();
    if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004443b0,DAT_004443b0);
    }
    return CONCAT44(param_3,param_2);
  }
  FUN_0046d464();
  do {
    pcVar4 = DAT_004443bc;
    FUN_0043c0e4(DAT_004443bc,0xc,0);
    puVar5 = DAT_004443c0;
    param_2 = param_2 & 0xffffff00;
    iVar9 = osMessageQueueGet(*DAT_004443c4,pcVar4,0,*DAT_004443c0,param_2);
    uVar10 = DAT_004444a4;
    uVar11 = (uint3)(param_2 >> 8);
    if (iVar9 == 0) {
      param_2 = CONCAT31(uVar11,1);
      FUN_0043c0e4(DAT_004444a4,0x2800,0);
      puVar6 = DAT_004443c8;
      osMutexAcquire(*DAT_004443c8,0xffffffff);
      FUN_0046d9ac(DAT_004444a8,uVar10,*(undefined4 *)(pcVar4 + 8));
      osMutexRelease(*puVar6);
    }
    else {
      param_2 = (uint)uVar11 << 8;
    }
    task_vote_acquire_current();
    bVar1 = *pbVar2;
    if (bVar1 == 0) {
      if ((param_2 & 0xff) == 1) {
        param_2 = param_2 & 0xffffff00;
        if (*pcVar4 == '\x02') {
          slave_sync_connection_status_0046f32c();
          *pbVar2 = 1;
          FUN_0046f68a();
          SVC_Settings_AutoBrightnessOpen();
          (**(code **)(*piVar3 + 0xc))();
          (**(code **)(*piVar3 + 8))();
          puVar7 = DAT_0044458c;
          *DAT_0044458c = 0;
          *DAT_00444590 = 0;
          *DAT_00444594 = 0;
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            param_2 = 0x2a0;
            FUN_0043d574(3,DAT_004443ac,DAT_004443a8,DAT_004443a4,0x2a0,DAT_004444ac,
                         *(undefined4 *)(pcVar4 + 4));
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0xc400000,DAT_004444b0,DAT_004444b0,*(undefined4 *)(pcVar4 + 4));
          }
          FUN_0044227e();
          FUN_0044ff38();
          uVar10 = FUN_0045f15a();
          *DAT_00444598 = uVar10;
          FUN_00460090(DAT_004444b4);
          FUN_00471164();
          FUN_004600b4();
          FUN_0044228a(*(undefined4 *)(pcVar4 + 4),2,DAT_004444a4,*(undefined4 *)(pcVar4 + 8));
          *puVar7 = *(uint *)(pcVar4 + 4);
          FUN_00442456(2,*(undefined4 *)(pcVar4 + 4));
          *puVar5 = 0x10;
          FUN_00465d7c(*puVar7 & 0xffff);
          FUN_00471cd6(0);
          FUN_00464344();
          sync_info_fn_00471fa4();
          FUN_0047243a();
        }
        else if (*pcVar4 != '\x03') {
          if (*pcVar4 == '\x05') {
            iVar9 = FUN_0043d0ce();
            if (iVar9 << 0x1e < 0) {
              param_2 = 0x2b9;
              FUN_0043d574(4,DAT_004443ac,DAT_004443a8,DAT_004443a4,0x2b9,DAT_0044459c);
            }
            iVar9 = FUN_0043d0ce();
            if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
              compress_log_output(0x10000000,DAT_004445a0,DAT_004445a0);
            }
            FUN_0043c0e4(pbVar2,2,0);
            *DAT_0044458c = 0;
            *puVar5 = 0xffffffff;
          }
          else if (*pcVar4 == '\b') {
            iVar9 = FUN_0043d0ce();
            if (iVar9 << 0x1e < 0) {
              param_2 = 0x2c0;
              FUN_0043d574(4,DAT_004443ac,DAT_004443a8,DAT_004443a4,0x2c0,DAT_004446a8);
            }
            iVar9 = FUN_0043d0ce();
            if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
              compress_log_output(0x10000000,DAT_004446ac,DAT_004446ac);
            }
            FUN_0043c0e4(pbVar2,2,0);
            *DAT_0044458c = 0;
            *puVar5 = 0xffffffff;
          }
        }
      }
    }
    else {
      if (bVar1 == 2) goto LAB_00443dc0;
      if (bVar1 < 2) {
        if ((param_2 & 0xff) == 1) {
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            param_2 = 0x2ca;
            FUN_0043d574(4,DAT_004443ac,DAT_004443a8,DAT_004443a4,0x2ca,DAT_00444690);
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_004446b0,DAT_004446b0);
          }
          param_2 = param_2 & 0xffffff00;
          if (*pcVar4 == '\x05') {
            iVar9 = FUN_0043d0ce();
            if (iVar9 << 0x1e < 0) {
              param_2 = 0x2cd;
              FUN_0043d574(4,DAT_004443ac,DAT_004443a8,DAT_004443a4,0x2cd,DAT_00444700);
            }
            iVar9 = FUN_0043d0ce();
            if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
              compress_log_output(0x10000000,DAT_00444704,DAT_00444704);
            }
            puVar7 = DAT_00444594;
            if (((*DAT_00444594 == 0) || (*DAT_00444590 != 1)) ||
               ((*(uint *)(pcVar4 + 4) != *DAT_00444594 && (*(int *)(pcVar4 + 4) != 0)))) {
              if (((*DAT_00444594 == 0) || (*DAT_00444590 != 1)) ||
                 (*(uint *)(pcVar4 + 4) != *DAT_0044458c)) {
                iVar9 = FUN_0043d0ce();
                if (iVar9 << 0x1e < 0) {
                  param_2 = 0x2dd;
                  FUN_0043d574(4,DAT_004443ac,DAT_004443a8,DAT_004443a4,0x2dd,DAT_00444718);
                }
                iVar9 = FUN_0043d0ce();
                if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
                  compress_log_output(0x10000000,DAT_0044471c,DAT_0044471c);
                }
                if (((*(uint *)(pcVar4 + 4) == *puVar7) || (*(int *)(pcVar4 + 4) == 0)) &&
                   (*DAT_00444590 == 2)) {
                  FUN_0044228a(*puVar7,5,DAT_004444a4,*(undefined4 *)(pcVar4 + 8));
                  puVar6 = DAT_00444598;
                  FUN_0045faa8(*DAT_00444598,0,*puVar7);
                  for (iVar9 = 0; iVar9 < 0x18; iVar9 = iVar9 + 1) {
                    FUN_00464344();
                    FUN_00454b4c(0x10);
                  }
                  FUN_0045f7be(*puVar6);
                  *puVar6 = 0;
                  *pbVar2 = 2;
                  sync_info_fn_00471fa4();
                }
                else {
                  if (((*(uint *)(pcVar4 + 4) != *DAT_0044458c) && (*(int *)(pcVar4 + 4) != 0)) ||
                     ((*DAT_00444590 != 1 || (*puVar7 != 0)))) {
                    iVar9 = FUN_0043d0ce();
                    if (iVar9 << 0x1e < 0) {
                      param_2 = 0x2f1;
                      FUN_0043d574(2,DAT_004443ac,DAT_004443a8,DAT_004443a4,0x2f1,DAT_00444854,
                                   *(undefined4 *)(pcVar4 + 4));
                    }
                    iVar9 = FUN_0043d0ce();
                    if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
                      compress_log_output(0x8400000,DAT_00444858,DAT_00444858,
                                          *(undefined4 *)(pcVar4 + 4));
                    }
                    goto LAB_0044390a;
                  }
                  FUN_0044228a(*DAT_0044458c,5,DAT_004444a4,*(undefined4 *)(pcVar4 + 8));
                  FUN_00464344();
                  puVar6 = DAT_00444598;
                  FUN_0045f7be(*DAT_00444598);
                  *puVar6 = 0;
                  *pbVar2 = 2;
                  sync_info_fn_00471fa4();
                }
LAB_00443dc0:
                iVar9 = FUN_0043d0ce();
                if (iVar9 << 0x1e < 0) {
                  param_2 = 0x343;
                  FUN_0043d574(3,DAT_004443ac,DAT_004443a8,DAT_004443a4,0x343,DAT_0044484c);
                }
                iVar9 = FUN_0043d0ce();
                if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
                  compress_log_output(0xc000000,DAT_00444850,DAT_00444850);
                }
                SVC_Settings_AutoBrightnessClose();
                (**(code **)(*piVar3 + 4))();
                (**(code **)(*piVar3 + 0x10))();
                FUN_00465b10();
                *DAT_0044458c = 0;
                *DAT_00444590 = 0;
                *DAT_00444594 = 0;
                *puVar5 = 0xffffffff;
                FUN_00471d58(0);
                FUN_0043c0e4(pbVar2,2,0);
                FUN_0046f6a2();
                SVC_Settings_SaveSettingConfigToKVCheck();
                FUN_0047243a();
              }
              else {
                iVar9 = FUN_0043d0ce();
                if (iVar9 << 0x1e < 0) {
                  param_2 = 0x2da;
                  FUN_0043d574(3,DAT_004443ac,DAT_004443a8,DAT_004443a4,0x2da,DAT_00444710);
                }
                iVar9 = FUN_0043d0ce();
                if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
                  compress_log_output(0xc000000,DAT_00444714,DAT_00444714);
                }
              }
            }
            else {
              FUN_0044228a(*DAT_00444594,5,DAT_004444a4,*(undefined4 *)(pcVar4 + 8));
              FUN_0045faa8(*DAT_00444598,0,*puVar7);
              iVar9 = FUN_0043d0ce();
              if (iVar9 << 0x1e < 0) {
                param_2 = 0x2d1;
                FUN_0043d574(4,DAT_004443ac,DAT_004443a8,DAT_004443a4,0x2d1,DAT_00444708,*puVar7);
              }
              iVar9 = FUN_0043d0ce();
              if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
                compress_log_output(0x10400000,DAT_0044470c,DAT_0044470c,*puVar7);
              }
              *puVar7 = 0;
              for (iVar9 = 0; iVar9 < 0x18; iVar9 = iVar9 + 1) {
                FUN_00464344();
                FUN_00454b4c(0x10);
              }
              sync_info_fn_00471fa4();
            }
          }
          else if (*pcVar4 == '\x03') {
            if ((*(uint *)(pcVar4 + 4) == *DAT_0044458c) || (*(uint *)(pcVar4 + 4) == *DAT_00444594)
               ) {
              FUN_0044228a(*(undefined4 *)(pcVar4 + 4),3,DAT_004444a4,*(undefined4 *)(pcVar4 + 8),
                           param_2);
              FUN_00464344();
            }
          }
          else {
            if (*pcVar4 != '\x02') {
              if (*pcVar4 == '\a') {
                iVar9 = FUN_00442d86(DAT_004444a4,*(undefined4 *)(pcVar4 + 8));
                if (iVar9 != 1) {
                  FUN_00464344();
                  goto LAB_0044390a;
                }
                iVar9 = FUN_0043d0ce();
                if (iVar9 << 0x1e < 0) {
                  param_2 = 0x30f;
                  FUN_0043d574(3,DAT_004443ac,DAT_004443a8,DAT_004443a4,0x30f,DAT_00444864);
                }
                iVar9 = FUN_0043d0ce();
                if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
                  compress_log_output(0xc000000,DAT_00444868,DAT_00444868);
                }
                sync_info_fn_00471fa4();
                *pbVar2 = 2;
                puVar7 = DAT_00444594;
                FUN_0044228a(*DAT_00444594,5,0,0);
                puVar6 = DAT_00444598;
                FUN_0045faa8(*DAT_00444598,0,*puVar7);
                for (iVar9 = 0; iVar9 < 0x18; iVar9 = iVar9 + 1) {
                  FUN_00464344();
                  FUN_00454b4c(0x10);
                }
                FUN_0045f7be(*puVar6);
                *puVar6 = 0;
              }
              else if (*pcVar4 == '\b') {
                iVar9 = FUN_0043d0ce();
                if (iVar9 << 0x1e < 0) {
                  param_2 = 800;
                  FUN_0043d574(4,DAT_004443ac,DAT_004443a8,DAT_004443a4,800,DAT_004446a8);
                }
                iVar9 = FUN_0043d0ce();
                if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
                  compress_log_output(0x10000000,DAT_004446ac,DAT_004446ac);
                }
                puVar7 = DAT_00444594;
                if (*DAT_00444594 != 0) {
                  iVar9 = FUN_0043d0ce();
                  if (iVar9 << 0x1e < 0) {
                    param_2 = 0x322;
                    FUN_0043d574(4,DAT_004443ac,DAT_004443a8,DAT_004443a4,0x322,DAT_0044486c,*puVar7
                                );
                  }
                  iVar9 = FUN_0043d0ce();
                  if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
                    compress_log_output(0x10400000,DAT_00444870,DAT_00444870,*puVar7);
                  }
                  FUN_0044228a(*puVar7,5,0,0);
                  FUN_0045faa8(*DAT_00444598,0,*puVar7);
                  for (iVar9 = 0; iVar9 < 0x18; iVar9 = iVar9 + 1) {
                    FUN_00464344();
                    FUN_00454b4c(0x10);
                  }
                  *puVar7 = 0;
                }
                puVar8 = DAT_0044458c;
                if (((*DAT_0044458c != 0) && (*DAT_0044458c != *puVar7)) && (*DAT_00444590 == 1)) {
                  iVar9 = FUN_0043d0ce();
                  if (iVar9 << 0x1e < 0) {
                    param_2 = 0x32d;
                    FUN_0043d574(4,DAT_004443ac,DAT_004443a8,DAT_004443a4,0x32d,DAT_00444874,*puVar8
                                );
                  }
                  iVar9 = FUN_0043d0ce();
                  if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
                    compress_log_output(0x10400000,DAT_00444878,DAT_00444878,*puVar8);
                  }
                  FUN_0044228a(*puVar8,5,0,0);
                  *puVar8 = 0;
                }
                puVar6 = DAT_00444598;
                FUN_0045f7be(*DAT_00444598);
                *puVar6 = 0;
                sync_info_fn_00471fa4();
                *pbVar2 = 2;
              }
              goto LAB_00443dc0;
            }
            iVar9 = FUN_0043d0ce();
            if (iVar9 << 0x1e < 0) {
              param_2 = 0x2fe;
              FUN_0043d574(3,DAT_004443ac,DAT_004443a8,DAT_004443a4,0x2fe,DAT_0044485c);
            }
            iVar9 = FUN_0043d0ce();
            if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
              compress_log_output(0xc000000,DAT_00444860,DAT_00444860);
            }
            FUN_0044227e();
            iVar9 = FUN_0044264e(*(undefined4 *)(pcVar4 + 4),DAT_004444a4,
                                 *(undefined4 *)(pcVar4 + 8));
            sync_info_fn_00471fa4();
            if (iVar9 == 1) {
              for (iVar9 = 0; iVar9 < 0x18; iVar9 = iVar9 + 1) {
                FUN_00464344();
                FUN_00454b4c(0x10);
              }
            }
            else {
              FUN_00464344();
            }
          }
        }
        else {
          if (*DAT_00444594 == 0) {
            FUN_0044228a(*DAT_0044458c,4,0,0);
          }
          else {
            FUN_0044228a(*DAT_00444594,4,0,0);
          }
          FUN_00464344();
        }
      }
      else {
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          param_2 = 0x359;
          FUN_0043d574(2,DAT_004443ac,DAT_004443a8,DAT_004443a4,0x359,DAT_004443b4);
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_004443b8,DAT_004443b8);
        }
        (**(code **)(*piVar3 + 4))();
        (**(code **)(*piVar3 + 0x10))();
        SVC_Settings_AutoBrightnessClose();
        FUN_0043c0e4(pbVar2,2,0);
        *DAT_0044458c = 0;
        *puVar5 = 0xffffffff;
      }
    }
LAB_0044390a:
    task_vote_release_current();
  } while( true );
}

