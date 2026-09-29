
void FT_Request_Metrics(int param_1,byte *param_2)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  undefined2 *puVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  
  iVar2 = *(int *)(param_1 + 0x58);
  puVar4 = (undefined2 *)(iVar2 + 0xc);
  if (-1 < (int)((uint)*(byte *)(param_1 + 8) << 0x1f)) {
    FUN_0043c0e4(puVar4,0x1c,0);
    *(undefined4 *)(iVar2 + 0x10) = 0x10000;
    *(undefined4 *)(iVar2 + 0x14) = 0x10000;
    return;
  }
  uVar5 = 0;
  uVar6 = 0;
  iVar7 = 0;
  iVar8 = 0;
  bVar1 = *param_2;
  if (bVar1 == 0) {
    uVar5 = (uint)*(ushort *)(param_1 + 0x44);
    uVar6 = uVar5;
  }
  else if (bVar1 == 2) {
    uVar5 = *(int *)(param_1 + 0x3c) - *(int *)(param_1 + 0x34);
    uVar6 = *(int *)(param_1 + 0x40) - *(int *)(param_1 + 0x38);
  }
  else if (bVar1 < 2) {
    uVar5 = (int)*(short *)(param_1 + 0x46) - (int)*(short *)(param_1 + 0x48);
    uVar6 = uVar5;
  }
  else {
    if (bVar1 == 4) {
      *(undefined4 *)(iVar2 + 0x10) = *(undefined4 *)(param_2 + 4);
      *(undefined4 *)(iVar2 + 0x14) = *(undefined4 *)(param_2 + 8);
      if (*(int *)(iVar2 + 0x10) == 0) {
        *(undefined4 *)(iVar2 + 0x10) = *(undefined4 *)(iVar2 + 0x14);
      }
      else if (*(int *)(iVar2 + 0x14) == 0) {
        *(undefined4 *)(iVar2 + 0x14) = *(undefined4 *)(iVar2 + 0x10);
      }
      goto LAB_00526c4e;
    }
    if (bVar1 < 4) {
      uVar5 = (uint)*(short *)(param_1 + 0x4c);
      uVar6 = (int)*(short *)(param_1 + 0x46) - (int)*(short *)(param_1 + 0x48);
    }
  }
  if ((int)uVar5 < 0) {
    uVar5 = -uVar5;
  }
  if ((int)uVar6 < 0) {
    uVar6 = -uVar6;
  }
  if (*(int *)(param_2 + 0xc) == 0) {
    iVar7 = *(int *)(param_2 + 4);
  }
  else {
    iVar7 = (*(int *)(param_2 + 0xc) * *(int *)(param_2 + 4) + 0x24) / 0x48;
  }
  if (*(int *)(param_2 + 0x10) == 0) {
    iVar8 = *(int *)(param_2 + 8);
  }
  else {
    iVar8 = (*(int *)(param_2 + 0x10) * *(int *)(param_2 + 8) + 0x24) / 0x48;
  }
  if (*(int *)(param_2 + 4) == 0) {
    uVar3 = FT_DivFix(iVar8,uVar6);
    *(undefined4 *)(iVar2 + 0x14) = uVar3;
    *(undefined4 *)(iVar2 + 0x10) = uVar3;
    iVar7 = FT_MulDiv(iVar8,uVar5,uVar6);
  }
  else {
    uVar3 = FT_DivFix(iVar7,uVar5);
    *(undefined4 *)(iVar2 + 0x10) = uVar3;
    if (*(int *)(param_2 + 8) == 0) {
      *(undefined4 *)(iVar2 + 0x14) = *(undefined4 *)(iVar2 + 0x10);
      iVar8 = FT_MulDiv(iVar7,uVar6,uVar5);
    }
    else {
      uVar3 = FT_DivFix(iVar8,uVar6);
      *(undefined4 *)(iVar2 + 0x14) = uVar3;
      if (*param_2 == 3) {
        if (*(int *)(iVar2 + 0x10) < *(int *)(iVar2 + 0x14)) {
          *(undefined4 *)(iVar2 + 0x14) = *(undefined4 *)(iVar2 + 0x10);
        }
        else {
          *(undefined4 *)(iVar2 + 0x10) = *(undefined4 *)(iVar2 + 0x14);
        }
      }
    }
  }
LAB_00526c4e:
  if (*param_2 != 0) {
    iVar7 = FT_MulFix(*(undefined2 *)(param_1 + 0x44),*(undefined4 *)(iVar2 + 0x10));
    iVar8 = FT_MulFix(*(undefined2 *)(param_1 + 0x44),*(undefined4 *)(iVar2 + 0x14));
  }
  *puVar4 = (short)(iVar7 + 0x20 >> 6);
  *(short *)(iVar2 + 0xe) = (short)(iVar8 + 0x20 >> 6);
  ft_recompute_scaled_metrics(param_1,puVar4);
  return;
}

