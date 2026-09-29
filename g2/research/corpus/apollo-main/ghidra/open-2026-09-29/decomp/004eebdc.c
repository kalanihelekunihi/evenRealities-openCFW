
undefined4 FUN_004eebdc(byte *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  uint uVar2;
  int *piVar3;
  int *piVar4;
  int *piVar5;
  int iVar6;
  undefined4 uVar7;
  int iVar8;
  
  piVar4 = DAT_004efa50;
  piVar3 = DAT_004eef74;
  if (*DAT_004eef74 == 0) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004ef990,DAT_004ef98c,DAT_004ef988,0x34a,DAT_004eef78);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004ef994);
    }
  }
  else if (param_2 == 0) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004ef990,DAT_004ef98c,DAT_004ef988,0x34e,DAT_004ef998);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004ef99c,DAT_004ef99c);
    }
  }
  else {
    bVar1 = *param_1;
    if (bVar1 == 0) {
      bVar1 = param_1[1];
      uVar2 = *(uint *)(param_1 + 2);
      if (bVar1 == 10) {
        if ((*DAT_004efa50 != 0) || (iVar6 = FUN_0043e2ea(*DAT_004efa50), iVar6 != 0)) {
          FUN_00450500(*piVar4,DAT_004efa58);
        }
        *DAT_004efa5c = 0;
        piVar4 = DAT_004efa60;
        iVar6 = FUN_0044ddea(*DAT_004efa60);
        while (piVar5 = DAT_004efa64, iVar6 = iVar6 + -1, -1 < iVar6) {
          iVar8 = FUN_0044dce2(*piVar4,iVar6);
          if (iVar8 != 0) {
            FUN_0044d7b8();
          }
        }
        if (*DAT_004efa64 != 0) {
          ui_common_api_fn_00509c96(*DAT_004efa64);
          *piVar5 = 0;
        }
        *piVar3 = 0;
        FUN_004e92f4();
        FUN_005000cc(*DAT_004efa68,3);
      }
      else if ((bVar1 == 0x44) || (bVar1 == 0x45)) {
        if ((*DAT_004efa50 == 0) || (iVar6 = FUN_0043e2ea(*DAT_004efa50), iVar6 == 0)) {
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            FUN_0043d574(2,DAT_004ef990,DAT_004ef98c,DAT_004ef988,0x35b,DAT_004ef9a0);
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x8000000,DAT_004efa54,DAT_004efa54);
          }
        }
        else {
          if (bVar1 == 0x44) {
            uVar7 = 1;
          }
          else {
            uVar7 = 0xffffffff;
          }
          FUN_004ed882(uVar7,uVar2 >> 0x10,uVar2 & 0xffff);
        }
      }
      else if (bVar1 != 0x46) {
        if (bVar1 == 0x47) {
          if ((*DAT_004efa50 == 0) || (iVar6 = FUN_0043e2ea(*DAT_004efa50), iVar6 == 0)) {
            iVar6 = FUN_0043d0ce();
            if (iVar6 << 0x1e < 0) {
              FUN_0043d574(2,DAT_004ef990,DAT_004ef98c,DAT_004ef988,0x3a0,DAT_004ef9a0);
            }
            iVar6 = FUN_0043d0ce();
            if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
              compress_log_output(0x8000000,DAT_004efa54,DAT_004efa54);
            }
          }
          else {
            FUN_00450500(*piVar4,DAT_004efa58);
            *DAT_004efa5c = 0;
            *DAT_004efa6c = 0;
            *DAT_004efa70 = 0;
            piVar4 = DAT_004efa60;
            if ((*piVar3 == 1) && (*DAT_004efa60 != 0)) {
              FUN_0044d878(*DAT_004efa60);
              FUN_004eef7c(*piVar4);
            }
          }
        }
        else if (bVar1 == 0x48) {
          if ((*DAT_004efa50 != 0) || (iVar6 = FUN_0043e2ea(*DAT_004efa50), iVar6 != 0)) {
            FUN_00450500(*piVar4,DAT_004efa58);
          }
          *DAT_004efa5c = 0;
          piVar4 = DAT_004efa60;
          iVar6 = FUN_0044ddea(*DAT_004efa60);
          while (piVar5 = DAT_004efa64, iVar6 = iVar6 + -1, -1 < iVar6) {
            iVar8 = FUN_0044dce2(*piVar4,iVar6);
            if (iVar8 != 0) {
              FUN_0044d7b8();
            }
          }
          if (*DAT_004efa64 != 0) {
            ui_common_api_fn_00509c96(*DAT_004efa64);
            *piVar5 = 0;
          }
          *piVar3 = 0;
          FUN_004e92f4();
          FUN_005000cc(*DAT_004efa68,3);
        }
        else {
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            FUN_0043d574(2,DAT_004ef990,DAT_004ef98c,DAT_004ef988,0x3b0,DAT_004efa74,bVar1);
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x8400000,DAT_004efc98,DAT_004efc98,bVar1);
          }
        }
      }
    }
    else if (bVar1 == 2) {
      FUN_004ed9b6(param_1 + 1,param_2 + -1,2,param_4,param_1,param_2,param_3,param_4);
    }
    else if (bVar1 < 2) {
      FUN_004e8970(param_1 + 1,param_2 + -1);
    }
  }
  return 0;
}

