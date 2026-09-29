
undefined8 FUN_005d01de(undefined4 *param_1,byte *param_2,int param_3)

{
  byte bVar1;
  bool bVar2;
  bool bVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  bool bVar8;
  byte *local_30;
  byte *local_2c;
  undefined4 *local_28;
  
  local_30 = (byte *)*param_1;
  iVar5 = 0;
  iVar6 = 0;
  iVar7 = 1;
  bVar8 = false;
  bVar2 = false;
  bVar3 = false;
  if (local_30 < param_2) {
    if ((*local_30 == 0x2d) || (*local_30 == 0x2b)) {
      bVar8 = *local_30 == 0x2d;
      local_30 = local_30 + 1;
      if (local_30 == param_2) goto LAB_005d0206;
      if ((*local_30 == 0x2d) || (*local_30 == 0x2b)) {
        iVar5 = 0;
        goto LAB_005d0398;
      }
    }
    local_28 = param_1;
    if (*local_30 != 0x2e) {
      local_2c = local_30;
      iVar5 = FUN_005d018a(&local_30,param_2);
      if (local_30 == local_2c) {
        iVar5 = 0;
        goto LAB_005d0398;
      }
      if (iVar5 < 0x8000) {
        iVar5 = iVar5 << 0x10;
      }
      else {
        bVar2 = true;
      }
    }
    if ((local_30 < param_2) && (*local_30 == 0x2e)) {
      while ((((local_30 = local_30 + 1, local_30 < param_2 &&
               ((((*local_30 != 0x20 && (*local_30 != 0xd)) && (*local_30 != 10)) &&
                ((*local_30 != 9 && (*local_30 != 0xc)))))) && (*local_30 != 0)) &&
             ((*local_30 < 0x80 &&
              (bVar1 = *(byte *)(DAT_005d070c + (*local_30 & 0x7f)), bVar1 < 10))))) {
        if ((iVar7 < DAT_005d0710) && (iVar6 < DAT_005d0710)) {
          iVar6 = iVar6 * 10 + (int)(char)bVar1;
          if ((iVar5 == 0) && (0 < param_3)) {
            param_3 = param_3 + -1;
          }
          else {
            iVar7 = iVar7 * 10;
          }
        }
      }
    }
    if ((local_30 + 1 < param_2) && ((*local_30 == 0x65 || (*local_30 == 0x45)))) {
      local_30 = local_30 + 1;
      local_2c = local_30;
      iVar4 = FUN_005d018a(&local_30,param_2);
      if (local_2c == local_30) {
        iVar5 = 0;
        goto LAB_005d0398;
      }
      if (iVar4 < 0x3e9) {
        if (iVar4 < -1000) {
          bVar3 = true;
        }
        else {
          param_3 = iVar4 + param_3;
        }
      }
      else {
        bVar2 = true;
      }
    }
    *local_28 = local_30;
    if (iVar6 == 0 && iVar5 == 0) {
      iVar5 = 0;
    }
    else {
      if (bVar2) {
LAB_005d0386:
        iVar5 = 0x7fffffff;
      }
      else {
        if (bVar3) {
LAB_005d0396:
          iVar5 = 0;
          goto LAB_005d0398;
        }
        for (; 0 < param_3; param_3 = param_3 + -1) {
          if (DAT_005d0710 <= iVar5) goto LAB_005d0386;
          iVar5 = iVar5 * 10;
          if (iVar6 < DAT_005d0710) {
            iVar6 = iVar6 * 10;
          }
          else {
            if (iVar7 == 1) goto LAB_005d0386;
            iVar7 = iVar7 / 10;
          }
        }
        for (; param_3 < 0; param_3 = param_3 + 1) {
          iVar5 = iVar5 / 10;
          if (iVar7 < DAT_005d0710) {
            iVar7 = iVar7 * 10;
          }
          else {
            iVar6 = iVar6 / 10;
          }
          if (iVar6 == 0 && iVar5 == 0) goto LAB_005d0396;
        }
        if (iVar6 != 0) {
          iVar6 = FT_DivFix(iVar6,iVar7);
          iVar5 = iVar6 + iVar5;
        }
      }
      if (bVar8) {
        iVar5 = -iVar5;
      }
    }
  }
  else {
LAB_005d0206:
    iVar5 = 0;
  }
LAB_005d0398:
  return CONCAT44(local_30,iVar5);
}

