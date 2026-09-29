
void FUN_0054cfd0(byte param_1)

{
  int *piVar1;
  int *piVar2;
  char *pcVar3;
  int *piVar4;
  int *piVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  int iVar9;
  
  piVar5 = DAT_0054dc10;
  piVar4 = DAT_0054dabc;
  pcVar3 = DAT_0054d938;
  piVar2 = DAT_0054d934;
  piVar1 = DAT_0054d930;
  if ((*DAT_0054d3b8 == 0) || (*DAT_0054d930 == 0)) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0054d98c,DAT_0054d988,DAT_0054d984,0xcbf,DAT_0054d980);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0054d990,DAT_0054d990);
    }
  }
  else if (*DAT_0054d938 == '\0') {
    iVar6 = *DAT_0054dabc;
    if (iVar6 < 1) {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0054d98c,DAT_0054d988,DAT_0054d984,0xccb,DAT_0054d99c);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0054d9a0,DAT_0054d9a0);
      }
    }
    else if (iVar6 < 5) {
      if (param_1 == 0) {
        if (*DAT_0054d934 < 1) {
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            FUN_0043d574(4,DAT_0054d98c,DAT_0054d988,DAT_0054d984,0xcda,DAT_0054dac8);
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_0054dacc,DAT_0054dacc);
          }
          FUN_0054c844(1);
        }
        else {
          FUN_0054d948();
          *piVar2 = *piVar2 + -1;
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            FUN_0043d574(4,DAT_0054d98c,DAT_0054d988,DAT_0054d984,0xcd6,DAT_0054dac0,*piVar2);
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_0054dac4,DAT_0054dac4,*piVar2);
          }
          FUN_0054d9a4();
          FUN_0054cbaa();
        }
      }
      else if (param_1 == 2) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0054d98c,DAT_0054d988,DAT_0054d984,0xcef,DAT_0054db28,
                       (int)piVar4 + *DAT_0054d934 * 0x40 + 6,*DAT_0054d934);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_0054dbfc,DAT_0054dbfc,
                              (int)piVar4 + *DAT_0054d934 * 0x40 + 6,*DAT_0054d934);
        }
        uVar8 = DAT_0054dc00;
        FUN_0043c0e4(DAT_0054dc00,0x40,0);
        piVar1 = DAT_0054d934;
        FUN_0044b5a0(uVar8,(int)piVar4 + *DAT_0054d934 * 0x40 + 6,0x3f);
        piVar2 = DAT_0054dc04;
        *DAT_0054dc04 = *piVar1;
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0054d98c,DAT_0054d988,DAT_0054d984,0xcf3,DAT_0054db2c,uVar8,*piVar2);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_0054dc08,DAT_0054dc08,uVar8,*piVar2);
        }
      }
      else if (param_1 < 2) {
        if (*DAT_0054d934 < iVar6 + -1) {
          FUN_0054d948();
          *piVar2 = *piVar2 + 1;
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            FUN_0043d574(4,DAT_0054d98c,DAT_0054d988,DAT_0054d984,0xce3,DAT_0054dad0,*piVar2);
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_0054dad4,DAT_0054dad4,*piVar2);
          }
          FUN_0054d9a4();
          FUN_0054cbaa();
        }
        else {
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            FUN_0043d574(4,DAT_0054d98c,DAT_0054d988,DAT_0054d984,0xce7,DAT_0054db20);
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_0054db24,DAT_0054db24);
          }
          FUN_0054c844(0);
        }
      }
      else if (param_1 == 3) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0054d98c,DAT_0054d988,DAT_0054d984,0xcf7,DAT_0054dc0c);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_0054dd80,DAT_0054dd80);
        }
      }
    }
    else {
      iVar9 = *DAT_0054d934 - *DAT_0054dc10;
      if (param_1 == 0) {
        if (*DAT_0054d934 < 1) {
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            FUN_0043d574(4,DAT_0054d98c,DAT_0054d988,DAT_0054d984,0xd2c,DAT_0054dac8);
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_0054dacc,DAT_0054dacc);
          }
          FUN_0054c844(1);
        }
        else {
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            FUN_0043d574(4,DAT_0054d98c,DAT_0054d988,DAT_0054d984,0xd05,DAT_0054dc14,*piVar2,iVar9,
                         *piVar5);
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x10c00000,DAT_0054dc18,DAT_0054dc18,*piVar2,iVar9,*piVar5);
          }
          if (iVar9 < 3) {
            if (iVar9 == 1) {
              if (*piVar5 < 1) {
                FUN_0054d948();
                *piVar2 = *piVar2 + -1;
                iVar6 = FUN_0043d0ce();
                if (iVar6 << 0x1e < 0) {
                  FUN_0043d574(4,DAT_0054d98c,DAT_0054d988,DAT_0054d984,0xd1e,DAT_0054dd8c,*piVar2);
                }
                iVar6 = FUN_0043d0ce();
                if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                  compress_log_output(0x10400000,DAT_0054dd90,DAT_0054dd90,*piVar2);
                }
                FUN_0054d9a4();
                FUN_0054cbaa();
              }
              else {
                FUN_0054d948();
                *piVar5 = *piVar5 + -1;
                *piVar2 = *piVar2 + -1;
                uVar8 = FUN_0054cc00(*piVar2);
                iVar6 = FUN_0043d0ce();
                if (iVar6 << 0x1e < 0) {
                  FUN_0043d574(4,DAT_0054d98c,DAT_0054d988,DAT_0054d984,0xd18,DAT_0054dd84,*piVar2,
                               *piVar5,uVar8);
                }
                iVar6 = FUN_0043d0ce();
                if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                  compress_log_output(0x10c00000,DAT_0054dd88,DAT_0054dd88,*piVar2,*piVar5,uVar8);
                }
                FUN_0054cece(*piVar1,uVar8,200);
              }
            }
            else {
              FUN_0054d948();
              *piVar2 = *piVar2 + -1;
              iVar6 = FUN_0043d0ce();
              if (iVar6 << 0x1e < 0) {
                FUN_0043d574(4,DAT_0054d98c,DAT_0054d988,DAT_0054d984,0xd26,DAT_0054dc1c,*piVar2);
              }
              iVar6 = FUN_0043d0ce();
              if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                compress_log_output(0x10400000,DAT_0054dc20,DAT_0054dc20,*piVar2);
              }
              FUN_0054d9a4();
              FUN_0054cbaa();
            }
          }
          else {
            FUN_0054d948();
            *piVar2 = *piVar2 + -1;
            iVar6 = FUN_0043d0ce();
            if (iVar6 << 0x1e < 0) {
              FUN_0043d574(4,DAT_0054d98c,DAT_0054d988,DAT_0054d984,0xd0b,DAT_0054dc1c,*piVar2);
            }
            iVar6 = FUN_0043d0ce();
            if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
              compress_log_output(0x10400000,DAT_0054dc20,DAT_0054dc20,*piVar2);
            }
            FUN_0054d9a4();
            FUN_0054cbaa();
          }
        }
      }
      else if (param_1 == 2) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0054d98c,DAT_0054d988,DAT_0054d984,0xd67,DAT_0054db28,
                       (int)piVar4 + *piVar2 * 0x40 + 6,*piVar2);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_0054dbfc,DAT_0054dbfc,(int)piVar4 + *piVar2 * 0x40 + 6,
                              *piVar2);
        }
        uVar8 = DAT_0054dc00;
        FUN_0043c0e4(DAT_0054dc00,0x40,0);
        FUN_0044b5a0(uVar8,(int)piVar4 + *piVar2 * 0x40 + 6,0x3f);
        *DAT_0054dc04 = *piVar2;
      }
      else if (param_1 < 2) {
        if (*DAT_0054d934 < iVar6 + -1) {
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            FUN_0043d574(4,DAT_0054d98c,DAT_0054d988,DAT_0054d984,0xd35,DAT_0054dd94,*piVar2,iVar9,
                         *piVar5);
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            compress_log_output(0x10c00000,DAT_0054dd98,DAT_0054dd98,*piVar2,iVar9,*piVar5);
          }
          if (iVar9 < 3) {
            FUN_0054d948();
            *piVar2 = *piVar2 + 1;
            iVar6 = FUN_0043d0ce();
            if (iVar6 << 0x1e < 0) {
              FUN_0043d574(4,DAT_0054d98c,DAT_0054d988,DAT_0054d984,0xd3b,DAT_0054dc1c,*piVar2);
            }
            iVar6 = FUN_0043d0ce();
            if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
              compress_log_output(0x10400000,DAT_0054dc20,DAT_0054dc20,*piVar2);
            }
            FUN_0054d9a4();
            FUN_0054cbaa();
          }
          else if (iVar9 == 3) {
            iVar6 = iVar6 + -5;
            if (iVar6 < 0) {
              iVar6 = 0;
            }
            if (*piVar5 < iVar6) {
              FUN_0054d948();
              *piVar5 = *piVar5 + 1;
              *piVar2 = *piVar2 + 1;
              *pcVar3 = '\x01';
              uVar8 = FUN_0054cc00(*piVar2);
              iVar6 = FUN_0043d0ce();
              if (iVar6 << 0x1e < 0) {
                FUN_0043d574(4,DAT_0054d98c,DAT_0054d988,DAT_0054d984,0xd4b,DAT_0054dd84,*piVar2,
                             *piVar5,uVar8);
              }
              iVar6 = FUN_0043d0ce();
              if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                compress_log_output(0x10c00000,DAT_0054dd88,DAT_0054dd88,*piVar2,*piVar5,uVar8);
              }
              FUN_0054cece(*piVar1,uVar8,200);
            }
            else {
              FUN_0054d948();
              *piVar2 = *piVar2 + 1;
              iVar6 = FUN_0043d0ce();
              if (iVar6 << 0x1e < 0) {
                FUN_0043d574(4,DAT_0054d98c,DAT_0054d988,DAT_0054d984,0xd51,DAT_0054dfac,*piVar2);
              }
              iVar6 = FUN_0043d0ce();
              if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                compress_log_output(0x10400000,DAT_0054dfb0,DAT_0054dfb0,*piVar2);
              }
              FUN_0054d9a4();
              FUN_0054cbaa();
            }
          }
          else {
            FUN_0054d948();
            *piVar2 = *piVar2 + 1;
            iVar6 = FUN_0043d0ce();
            if (iVar6 << 0x1e < 0) {
              FUN_0043d574(4,DAT_0054d98c,DAT_0054d988,DAT_0054d984,0xd59,DAT_0054dc1c,*piVar2);
            }
            iVar6 = FUN_0043d0ce();
            if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
              compress_log_output(0x10400000,DAT_0054dc20,DAT_0054dc20,*piVar2);
            }
            FUN_0054d9a4();
            FUN_0054cbaa();
          }
        }
        else {
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            FUN_0043d574(4,DAT_0054d98c,DAT_0054d988,DAT_0054d984,0xd5f,DAT_0054db20);
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_0054db24,DAT_0054db24);
          }
          FUN_0054c844(0);
        }
      }
      else if (param_1 == 3) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0054d98c,DAT_0054d988,DAT_0054d984,0xd70,DAT_0054dc0c);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_0054dd80,DAT_0054dd80);
        }
      }
    }
  }
  else {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0054d98c,DAT_0054d988,DAT_0054d984,0xcc5,DAT_0054d994);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0054d998);
    }
  }
  return;
}

