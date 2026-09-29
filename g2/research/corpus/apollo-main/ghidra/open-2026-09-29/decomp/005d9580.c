
undefined8 FUN_005d9580(byte *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  byte *pbVar4;
  byte *pbVar5;
  uint uVar6;
  
  if (((*param_1 == 0x75) && (param_1[1] == 0x6e)) && (param_1[2] == 0x69)) {
    uVar2 = 0;
    pbVar4 = param_1 + 3;
    for (iVar3 = 4; 0 < iVar3; iVar3 = iVar3 + -1) {
      bVar1 = *pbVar4;
      uVar6 = bVar1 - 0x30;
      if (9 < uVar6) {
        if (bVar1 - 0x41 < 6) {
          uVar6 = bVar1 - 0x37;
        }
        else {
          uVar6 = 0x10;
        }
      }
      if (0xf < uVar6) break;
      uVar2 = uVar6 + uVar2 * 0x10;
      pbVar4 = pbVar4 + 1;
    }
    if (iVar3 == 0) {
      if (*pbVar4 == 0) goto LAB_005d9670;
      if (*pbVar4 == 0x2e) {
        uVar2 = uVar2 | 0x80000000;
        goto LAB_005d9670;
      }
    }
  }
  if (*param_1 == 0x75) {
    uVar2 = 0;
    pbVar4 = param_1;
    for (iVar3 = 6; pbVar4 = pbVar4 + 1, 0 < iVar3; iVar3 = iVar3 + -1) {
      bVar1 = *pbVar4;
      uVar6 = bVar1 - 0x30;
      if (9 < uVar6) {
        if (bVar1 - 0x41 < 6) {
          uVar6 = bVar1 - 0x37;
        }
        else {
          uVar6 = 0x10;
        }
      }
      if (0xf < uVar6) break;
      uVar2 = uVar6 + uVar2 * 0x10;
    }
    if (iVar3 < 3) {
      if (*pbVar4 == 0) goto LAB_005d9670;
      if (*pbVar4 == 0x2e) {
        uVar2 = uVar2 | 0x80000000;
        goto LAB_005d9670;
      }
    }
  }
  for (pbVar4 = param_1;
      (pbVar5 = (byte *)0x0, *pbVar4 != 0 &&
      ((*pbVar4 != 0x2e || (pbVar5 = pbVar4, pbVar4 <= param_1)))); pbVar4 = pbVar4 + 1) {
  }
  if (pbVar5 == (byte *)0x0) {
    uVar2 = FUN_005d94c0();
  }
  else {
    uVar2 = FUN_005d94c0(param_1,pbVar5);
    uVar2 = uVar2 | 0x80000000;
  }
LAB_005d9670:
  return CONCAT44(param_4,uVar2);
}

