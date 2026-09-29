
undefined8
FUN_005d849a(undefined4 param_1,undefined4 param_2,uint param_3,short *param_4,int *param_5,
            int *param_6)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int *piVar7;
  uint local_30;
  char local_2c;
  uint local_28;
  
  iVar3 = *param_5;
  iVar4 = *param_6;
  local_30 = CONCAT31((int3)((uint)param_1 >> 8),1);
  local_28 = param_3;
  do {
    if (local_28 < 2) {
      *param_5 = iVar3;
      *param_6 = iVar4;
      return CONCAT44(param_2,local_30);
    }
    bVar1 = false;
    if (((char)local_30 == '\0') && (local_2c = (char)param_2, local_2c == '\0')) {
      iVar5 = (int)*param_4;
      iVar6 = param_4[1] - iVar5;
      bVar1 = true;
      iVar2 = iVar3;
      piVar7 = param_5;
    }
    else {
      iVar5 = (int)param_4[1];
      iVar6 = *param_4 - iVar5;
      local_30 = local_30 & 0xffffff00;
      iVar2 = iVar4;
      piVar7 = param_6;
    }
    for (piVar7 = piVar7 + 1; (iVar2 != 0 && (*piVar7 <= iVar5)); piVar7 = piVar7 + 8) {
      if (iVar5 == *piVar7) {
        if (iVar6 < 0) {
          if (iVar6 < piVar7[1]) {
            piVar7[1] = iVar6;
          }
        }
        else if (piVar7[1] < iVar6) {
          piVar7[1] = iVar6;
        }
        goto LAB_005d84de;
      }
      iVar2 = iVar2 + -1;
    }
    for (; iVar2 != 0; iVar2 = iVar2 + -1) {
      FUN_00439c04(piVar7 + iVar2 * 8,piVar7 + iVar2 * 8 + -8,0x20);
    }
    *piVar7 = iVar5;
    piVar7[1] = iVar6;
    if (bVar1) {
      iVar3 = iVar3 + 1;
    }
    else {
      iVar4 = iVar4 + 1;
    }
LAB_005d84de:
    param_4 = param_4 + 2;
    local_28 = local_28 - 2;
  } while( true );
}

