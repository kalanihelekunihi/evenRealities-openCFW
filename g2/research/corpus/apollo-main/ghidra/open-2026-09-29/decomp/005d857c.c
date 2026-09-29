
undefined8
FUN_005d857c(uint *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
            undefined4 param_5,int param_6,int param_7)

{
  uint uVar1;
  uint uVar2;
  uint *puVar3;
  uint *puVar4;
  uint *puVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  uint *puVar9;
  uint *puVar10;
  
  if (param_7 == 0) {
    puVar3 = param_1 + 0x81;
    puVar4 = param_1;
  }
  else {
    puVar3 = param_1 + 0x183;
    puVar4 = param_1 + 0x102;
  }
  *puVar4 = 0;
  *puVar3 = 0;
  FUN_005d849a(param_1,0,param_2,param_3,puVar4,puVar3);
  puVar9 = puVar4;
  puVar10 = puVar3;
  FUN_005d849a(param_1,1,param_4,param_5);
  uVar1 = *puVar4;
  uVar2 = *puVar3;
  if (uVar1 != 0) {
    puVar5 = puVar4 + 1;
    for (uVar7 = uVar1; uVar7 != 0; uVar7 = uVar7 - 1) {
      if ((1 < uVar7) && ((int)(puVar5[8] - *puVar5) < (int)puVar5[1])) {
        puVar5[1] = puVar5[8] - *puVar5;
      }
      puVar5[3] = *puVar5;
      puVar5[2] = *puVar5 + puVar5[1];
      puVar5 = puVar5 + 8;
    }
  }
  if (uVar2 != 0) {
    puVar5 = puVar3 + 1;
    for (uVar7 = uVar2; uVar7 != 0; uVar7 = uVar7 - 1) {
      if ((1 < uVar7) && ((int)puVar5[1] < (int)(*puVar5 - puVar5[8]))) {
        puVar5[1] = *puVar5 - puVar5[8];
      }
      puVar5[2] = *puVar5;
      puVar5[3] = *puVar5 + puVar5[1];
      puVar5 = puVar5 + 8;
    }
  }
  for (iVar6 = 1; -1 < iVar6; iVar6 = iVar6 + -1) {
    if (uVar1 != 0) {
      puVar4[4] = puVar4[4] - param_6;
      uVar7 = puVar4[3];
      puVar4 = puVar4 + 1;
      while (uVar1 = uVar1 - 1, uVar1 != 0) {
        iVar8 = puVar4[0xb] - uVar7;
        if (iVar8 / 2 < param_6) {
          puVar4[0xb] = iVar8 / 2 + uVar7;
          puVar4[2] = puVar4[0xb];
        }
        else {
          puVar4[2] = param_6 + uVar7;
          puVar4[0xb] = puVar4[0xb] - param_6;
        }
        uVar7 = puVar4[10];
        puVar4 = puVar4 + 8;
      }
      puVar4[2] = param_6 + uVar7;
    }
    uVar1 = uVar2;
    puVar4 = puVar3;
  }
  return CONCAT44(puVar10,puVar9);
}

