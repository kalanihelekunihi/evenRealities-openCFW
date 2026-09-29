
void qsort_introsort_core(undefined1 *param_1,uint param_2,uint param_3,uint param_4,code *param_5)

{
  undefined1 uVar1;
  undefined1 *puVar2;
  undefined1 *puVar3;
  undefined1 *puVar4;
  int iVar5;
  uint uVar6;
  undefined1 *puVar7;
  undefined1 *puVar8;
  undefined1 *puVar9;
  undefined1 *puVar10;
  int iVar11;
  int iVar12;
  uint uVar13;
  undefined1 *local_b0 [33];
  undefined1 *local_2c;
  uint local_28;
  
  local_2c = param_1;
  local_28 = param_3;
  while ((puVar7 = local_2c, local_28 != 0 && (0x20 < param_2))) {
    puVar9 = local_2c + param_4 * param_2;
    puVar3 = local_2c + param_4 * (param_2 >> 1);
    iVar11 = (int)puVar9 + -param_4;
    uVar6 = (uint)(iVar11 - (int)local_2c) / param_4;
    puVar8 = puVar3 + param_4;
    local_b0[0] = puVar3;
    if (0x28 < uVar6) {
      iVar5 = param_4 * ((uVar6 >> 3) + 1);
      FUN_00423972(local_2c,local_2c + iVar5,local_2c + iVar5 * 2,param_4,param_5);
      FUN_00423972((int)puVar3 + -iVar5,puVar3,puVar3 + iVar5,param_4,param_5);
      iVar12 = -iVar5 + iVar11;
      FUN_00423972(iVar5 * -2 + iVar11,iVar12,iVar11,param_4,param_5);
      puVar7 = local_2c + iVar5;
      iVar11 = iVar12;
    }
    FUN_00423972(puVar7,puVar3,iVar11,param_4,param_5);
    puVar7 = local_b0[0];
    do {
      puVar3 = puVar7;
      if (puVar3 <= local_2c) break;
      iVar11 = (*param_5)(puVar3 + -param_4,puVar3);
      puVar7 = puVar3 + -param_4;
    } while (iVar11 == 0);
    while ((puVar7 = puVar8, puVar2 = puVar3, puVar8 < puVar9 &&
           (iVar11 = (*param_5)(puVar8,puVar3), iVar11 == 0))) {
      puVar8 = puVar8 + param_4;
    }
LAB_00423af8:
    for (; uVar6 = param_4, puVar8 < puVar9; puVar8 = puVar8 + param_4) {
      iVar11 = (*param_5)(puVar3,puVar8);
      if (-1 < iVar11) {
        if (0 < iVar11) break;
        FUN_00423864(puVar7,puVar8,param_4);
        puVar7 = puVar7 + param_4;
      }
LAB_00423b14:
    }
    while (param_4 = uVar6, puVar10 = puVar2, puVar4 = local_2c, local_2c < puVar10) {
      puVar2 = puVar10 + -param_4;
      iVar11 = (*param_5)(puVar2,puVar3);
      uVar6 = param_4;
      if (-1 < iVar11) {
        if (0 < iVar11) break;
        puVar3 = puVar3 + -param_4;
        puVar4 = puVar2;
        puVar10 = puVar3;
        if (param_4 < 0x40) {
          for (; param_4 != 0; param_4 = param_4 - 1) {
            uVar1 = *puVar10;
            *puVar10 = *puVar4;
            *puVar4 = uVar1;
            puVar4 = puVar4 + 1;
            puVar10 = puVar10 + 1;
          }
        }
        else {
          do {
            uVar13 = 0x80;
            if (param_4 < 0x81) {
              uVar13 = param_4;
            }
            FUN_0041568c(local_b0,puVar10,uVar13);
            FUN_0041568c(puVar10,puVar4,uVar13);
            FUN_0041568c(puVar4,local_b0,uVar13);
            param_4 = param_4 - uVar13;
            puVar4 = puVar4 + uVar13;
            puVar10 = puVar10 + uVar13;
          } while (param_4 != 0);
        }
      }
    }
    if (puVar10 != local_2c) {
      iVar11 = -param_4;
      puVar2 = puVar10 + iVar11;
      if (puVar8 != puVar9) {
        FUN_00423864(puVar8,puVar2,param_4);
        goto LAB_00423b14;
      }
      puVar3 = puVar3 + iVar11;
      puVar7 = puVar7 + iVar11;
      if (puVar2 == puVar3) {
        FUN_00423864(puVar3,puVar7,param_4);
      }
      else {
        FUN_004238ba(puVar2,puVar7,puVar3,param_4);
      }
      goto LAB_00423af8;
    }
    if (puVar8 != puVar9) {
      if (puVar7 == puVar8) {
        FUN_00423864(puVar8,puVar3,param_4);
      }
      else {
        FUN_004238ba(puVar8,puVar3,puVar7,param_4);
      }
      puVar8 = puVar8 + param_4;
      puVar3 = puVar3 + param_4;
      puVar7 = puVar7 + param_4;
      puVar2 = puVar10;
      goto LAB_00423af8;
    }
    local_28 = (local_28 >> 1) + (local_28 >> 2);
    param_2 = (uint)((int)puVar3 - (int)puVar4) / param_4;
    uVar6 = (uint)((int)puVar9 - (int)puVar7) / param_4;
    if (uVar6 < param_2) {
      qsort_introsort_core(puVar7,uVar6,local_28,param_4,param_5);
    }
    else {
      qsort_introsort_core(local_2c,param_2,local_28,param_4,param_5);
      param_2 = uVar6;
      local_2c = puVar7;
    }
  }
  if (param_2 < 0x21) {
    if (1 < param_2) {
      puVar3 = local_2c;
LAB_00423cd8:
      param_2 = param_2 - 1;
      if (param_2 != 0) {
        puVar3 = puVar3 + param_4;
        iVar11 = (*param_5)(puVar3,puVar7);
        puVar8 = puVar7;
        puVar9 = puVar3;
        if (-1 < iVar11) goto LAB_00423cf0;
        goto LAB_00423cd4;
      }
    }
  }
  else {
    uVar6 = param_2 >> 1;
    while (uVar6 != 0) {
      uVar6 = uVar6 - 1;
      FUN_004239c2(puVar7,uVar6,param_2,param_4,param_5);
    }
    puVar3 = puVar7 + param_4 * param_2;
    local_2c = puVar7;
    do {
      puVar3 = puVar3 + -param_4;
      FUN_00423864(puVar7,puVar3,param_4);
      param_2 = param_2 - 1;
      FUN_004239c2(puVar7,0,param_2,param_4,param_5);
    } while (1 < param_2);
  }
  return;
LAB_00423cf0:
  do {
    puVar8 = puVar9;
    iVar11 = (*param_5)(puVar3,puVar8 + -param_4);
    puVar9 = puVar8 + -param_4;
  } while (iVar11 < 0);
  if (puVar8 != puVar3) {
LAB_00423cd4:
    FUN_00423928(puVar8,puVar3,param_4);
  }
  goto LAB_00423cd8;
}

