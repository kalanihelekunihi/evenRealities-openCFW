
undefined8 compress_log_ring_write(int param_1,uint param_2,int param_3)

{
  bool bVar1;
  bool bVar2;
  int *piVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  uint local_30;
  int local_2c;
  
  piVar3 = DAT_0043d0e8;
  bVar2 = false;
  iVar6 = *DAT_0043d0e8;
  uVar7 = DAT_0043d0e8[1];
  uVar4 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar4 = getCurrentExceptionNumber();
    uVar4 = uVar4 & 0x1ff;
  }
  local_30 = param_2;
  local_2c = param_3;
  if (((uVar4 == 0) && (*DAT_0043d0e0 != 0)) &&
     (iVar5 = FUN_00441750(*DAT_0043d0e0,500), iVar5 == 1)) {
    uVar8 = piVar3[2];
    uVar4 = piVar3[3];
    if ((uVar8 <= uVar7) && (uVar4 <= uVar7)) {
      if (uVar4 < uVar8) {
        iVar5 = -uVar4;
      }
      else {
        iVar5 = uVar7 - uVar4;
      }
      uVar8 = (uVar8 + iVar5) - 1;
      if ((param_2 & 0xffff) < uVar8) {
        local_30 = uVar7 - uVar4;
        if (local_30 < (param_2 & 0xffff)) {
          local_2c = iVar6 + uVar4;
          FUN_00439be4(local_2c,param_1,local_30);
          FUN_00439be4(iVar6,param_1 + local_30,(param_2 & 0xffff) - local_30);
        }
        else {
          FUN_00439be4(iVar6 + uVar4,param_1,param_2 & 0xffff);
        }
        if ((param_2 & 0xffff) < local_30) {
          iVar6 = uVar4 + (param_2 & 0xffff);
        }
        else {
          iVar6 = (param_2 & 0xffff) - local_30;
        }
        piVar3[3] = iVar6;
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1d < 0) {
          if (0xeb < uVar7 - uVar8) {
            bVar2 = true;
          }
        }
        else {
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) && (0xfff < uVar7 - uVar8)) {
            bVar2 = true;
          }
        }
      }
      else {
        bVar2 = true;
      }
    }
    FUN_00441710(*DAT_0043d0e0);
    if (((bVar2) && (iVar6 = FUN_0043d0ce(), iVar6 << 0x1f < 0)) &&
       ((iVar6 = FUN_00443484(), iVar6 == 0 || (iVar6 = semantic_OtaTransferActive(), iVar6 == 0))))
    {
      FUN_00448f7c();
    }
  }
  return CONCAT44(local_2c,local_30);
}

