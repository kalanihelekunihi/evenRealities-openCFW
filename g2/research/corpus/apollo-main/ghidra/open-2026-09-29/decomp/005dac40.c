
undefined8 FUN_005dac40(int param_1,uint param_2,undefined4 *param_3)

{
  ushort uVar1;
  undefined4 uVar2;
  ushort *puVar3;
  undefined4 uVar4;
  uint uVar5;
  code *pcVar6;
  undefined4 uVar7;
  uint uVar8;
  ushort uVar9;
  uint uVar10;
  uint uVar11;
  bool bVar12;
  int local_28;
  
  uVar4 = *(undefined4 *)(param_1 + 100);
  local_28 = 0;
  uVar2 = 0;
  uVar11 = 0xffffffff;
  uVar8 = 0xffffffff;
  uVar5 = 0xffffffff;
  uVar10 = 0xffffffff;
  bVar12 = false;
  puVar3 = *(ushort **)(param_1 + 0x164);
  for (uVar9 = 0; uVar9 < *(ushort *)(param_1 + 0x154); uVar9 = uVar9 + 1) {
    if (((uint)puVar3[3] == (param_2 & 0xffff)) && (puVar3[4] != 0)) {
      uVar1 = *puVar3;
      if ((uVar1 == 0) || (uVar1 == 2)) {
        uVar11 = (uint)uVar9;
      }
      else if (uVar1 < 2) {
        if (puVar3[2] == 0) {
          uVar5 = (uint)uVar9;
        }
        else if (puVar3[1] == 0) {
          uVar8 = (uint)uVar9;
        }
      }
      else if (((uVar1 == 3) && ((uVar10 == 0xffffffff || ((puVar3[2] & 0x3ff) == 9)))) &&
              ((puVar3[1] < 2 || (puVar3[1] == 10)))) {
        bVar12 = (puVar3[2] & 0x3ff) == 9;
        uVar10 = (uint)uVar9;
      }
    }
    puVar3 = puVar3 + 10;
  }
  if (-1 < (int)uVar5) {
    uVar8 = uVar5;
  }
  pcVar6 = DAT_005db92c;
  if (((int)uVar10 < 0) || ((-1 < (int)uVar8 && (!bVar12)))) {
    if ((int)uVar8 < 0) {
      pcVar6 = (code *)0x0;
      if (-1 < (int)uVar11) {
        puVar3 = (ushort *)(*(int *)(param_1 + 0x164) + uVar11 * 0x14);
        pcVar6 = DAT_005db92c;
      }
    }
    else {
      puVar3 = (ushort *)(*(int *)(param_1 + 0x164) + uVar8 * 0x14);
      pcVar6 = DAT_005db930;
    }
  }
  else {
    puVar3 = (ushort *)(*(int *)(param_1 + 0x164) + uVar10 * 0x14);
    if ((1 < puVar3[1]) && (puVar3[1] != 10)) {
      pcVar6 = (code *)0x0;
    }
  }
  if ((puVar3 != (ushort *)0x0) && (pcVar6 != (code *)0x0)) {
    if (*(int *)(puVar3 + 8) == 0) {
      uVar7 = *(undefined4 *)(param_1 + 0x170);
      param_2 = 0;
      uVar2 = ft_mem_realloc(uVar4,1,0,puVar3[4],0,&local_28);
      *(undefined4 *)(puVar3 + 8) = uVar2;
      if (((local_28 == 0) &&
          (local_28 = FT_Stream_Seek(uVar7,*(undefined4 *)(puVar3 + 6)), local_28 == 0)) &&
         (local_28 = FT_Stream_Read(uVar7,*(undefined4 *)(puVar3 + 8),puVar3[4]), local_28 == 0)) {
        bVar12 = false;
      }
      else {
        bVar12 = true;
      }
      if (bVar12) {
        ft_mem_free(uVar4,*(undefined4 *)(puVar3 + 8));
        puVar3[8] = 0;
        puVar3[9] = 0;
        puVar3[4] = 0;
        uVar2 = 0;
        goto LAB_005dade6;
      }
    }
    uVar2 = (*pcVar6)(puVar3,uVar4);
  }
LAB_005dade6:
  *param_3 = uVar2;
  return CONCAT44(param_2,local_28);
}

