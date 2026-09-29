
void FUN_0050b744(int param_1,int param_2,int param_3)

{
  undefined4 *puVar1;
  short sVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  
  if (*DAT_0050c27c == 0) {
    iVar3 = FUN_0044ddea(*DAT_0050c300);
    puVar1 = DAT_0050c30c;
    if (iVar3 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0050c2fc,DAT_0050c2f8,DAT_0050c2f4,0x5c3,DAT_0050c304);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0050c308,DAT_0050c308);
      }
    }
    else {
      osMutexAcquire(*DAT_0050c30c,0xffffffff);
      sVar2 = FUN_0050b1ac();
      osMutexRelease(*puVar1);
      puVar1 = DAT_0050c310;
      if ((sVar2 != 0) && (iVar3 = FUN_0043e0e0(*DAT_0050c310,1), iVar3 == 0)) {
        FUN_0043ded4(*puVar1,1);
      }
      FUN_0050c868();
      iVar5 = 0;
      for (iVar3 = 0; iVar3 < 4; iVar3 = iVar3 + 1) {
        if (*(int *)(iVar3 * 0x30 + DAT_0050bf98 + 0x20) == 0) {
          iVar5 = DAT_0050bf98 + iVar3 * 0x30;
          break;
        }
      }
      if (iVar5 == 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0050c2fc,DAT_0050c2f8,DAT_0050c2f4,0x5e5,DAT_0050c3bc);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_0050c3e8,DAT_0050c3e8);
        }
      }
      else {
        FUN_0050b5f4(iVar5);
        if (param_1 < 1) {
          if ((*(char *)(iVar5 + 0x24) == '\0') || (*(char *)(iVar5 + 0x25) != '\0')) {
            FUN_0050bd1c();
          }
          else {
            iVar3 = FUN_0043e2ea(*(undefined4 *)(iVar5 + 4));
            if (iVar3 == 0) {
              iVar3 = FUN_0043d0ce();
              if (iVar3 << 0x1e < 0) {
                FUN_0043d574(2,DAT_0050c2fc,DAT_0050c2f8,DAT_0050c2f4,0x61a,DAT_0050c4a4);
              }
              iVar3 = FUN_0043d0ce();
              if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
                compress_log_output(0x8000000,DAT_0050c4a8,DAT_0050c4a8);
              }
            }
            else {
              FUN_0043f66c(*(undefined4 *)(iVar5 + 4));
              iVar3 = FUN_0044e498(*(undefined4 *)(iVar5 + 4));
              if (param_2 == 0) {
                param_2 = 1;
              }
              if (param_3 < 0x65) {
                if (0x31 < param_3) {
                  param_2 = param_2 << 1;
                }
              }
              else {
                param_2 = param_2 * 3;
              }
              uVar4 = FUN_0050c3f4(*(undefined4 *)(iVar5 + 4),iVar3 - param_2);
              FUN_0050a010(param_2,param_3);
              FUN_0050c1c0(*(undefined4 *)(iVar5 + 4),uVar4,0xfa);
              iVar5 = FUN_0043d0ce();
              if (iVar5 << 0x1e < 0) {
                FUN_0043d574(3,DAT_0050c2fc,DAT_0050c2f8,DAT_0050c2f4,0x634,DAT_0050c51c,iVar3,uVar4
                             ,0xfa);
              }
              iVar5 = FUN_0043d0ce();
              if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                compress_log_output(0xcc00000,DAT_0050c6b8,DAT_0050c6b8,iVar3,uVar4,0xfa);
              }
            }
          }
        }
        else if ((*(char *)(iVar5 + 0x24) == '\0') || (*(char *)(iVar5 + 0x26) != '\0')) {
          FUN_0050ba64();
        }
        else {
          iVar3 = FUN_0043e2ea(*(undefined4 *)(iVar5 + 4));
          if (iVar3 == 0) {
            iVar3 = FUN_0043d0ce();
            if (iVar3 << 0x1e < 0) {
              FUN_0043d574(2,DAT_0050c2fc,DAT_0050c2f8,DAT_0050c2f4,0x5f6,DAT_0050c3ec);
            }
            iVar3 = FUN_0043d0ce();
            if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
              compress_log_output(0x8000000,DAT_0050c3f0,DAT_0050c3f0);
            }
          }
          else {
            FUN_0043f66c(*(undefined4 *)(iVar5 + 4));
            iVar3 = FUN_0044e498(*(undefined4 *)(iVar5 + 4));
            if (param_2 == 0) {
              param_2 = 1;
            }
            if (param_3 < 0x65) {
              if (0x31 < param_3) {
                param_2 = param_2 << 1;
              }
            }
            else {
              param_2 = param_2 * 3;
            }
            uVar4 = FUN_0050c3f4(*(undefined4 *)(iVar5 + 4),param_2 + iVar3);
            FUN_0050a010(param_2,param_3);
            FUN_0050c1c0(*(undefined4 *)(iVar5 + 4),uVar4,0xfa);
          }
        }
      }
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0050c2fc,DAT_0050c2f8,DAT_0050c2f4,0x5bd,DAT_0050c280);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0050c284,DAT_0050c284);
    }
  }
  return;
}

