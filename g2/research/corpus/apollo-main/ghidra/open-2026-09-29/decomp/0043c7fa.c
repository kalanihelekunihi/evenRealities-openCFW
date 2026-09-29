
undefined8
compress_log_ring_read_locked(int param_1,ushort param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  int *piVar2;
  int *piVar3;
  uint uVar4;
  undefined4 uVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  
  piVar3 = DAT_0043d0e8;
  piVar2 = DAT_0043d0e0;
  iVar8 = *DAT_0043d0e8;
  uVar7 = DAT_0043d0e8[1];
  uVar4 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar4 = getCurrentExceptionNumber();
    uVar4 = uVar4 & 0x1ff;
  }
  if ((uVar4 == 0) && (*DAT_0043d0e0 != 0)) {
    iVar6 = FUN_00441750(*DAT_0043d0e0,500);
    if (iVar6 == 1) {
      uVar9 = piVar3[2];
      uVar4 = piVar3[3];
      if ((uVar7 < uVar9) || (uVar7 < uVar4)) {
        FUN_00441710(*piVar2);
        uVar5 = 0;
      }
      else {
        if (uVar9 < uVar4) {
          iVar6 = -uVar9;
        }
        else {
          iVar6 = uVar7 - uVar9;
        }
        if ((uint)param_2 < (uVar4 + iVar6) - 1) {
          uVar7 = uVar7 - uVar9;
          if (uVar7 < param_2) {
            FUN_00439be4(param_1,iVar8 + uVar9,uVar7);
            FUN_00439be4(param_1 + uVar7,iVar8,param_2 - uVar7);
          }
          else {
            FUN_00439be4(param_1,iVar8 + uVar9,param_2);
          }
          if (param_2 < uVar7) {
            iVar8 = uVar9 + param_2;
          }
          else {
            iVar8 = param_2 - uVar7;
          }
          piVar3[2] = iVar8;
          FUN_00441710(*piVar2);
          uVar5 = 1;
        }
        else {
          FUN_00441710(*piVar2);
          uVar5 = 0;
        }
      }
    }
    else {
      uVar5 = 0;
    }
  }
  else {
    uVar5 = 0;
  }
  return CONCAT44(param_4,uVar5);
}

