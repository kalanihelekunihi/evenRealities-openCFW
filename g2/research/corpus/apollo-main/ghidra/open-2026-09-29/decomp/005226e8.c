
void FUN_005226e8(float *param_1)

{
  undefined4 *puVar1;
  int iVar2;
  float fVar3;
  
  fVar3 = param_1[6];
  if ((((-1 < (int)((uint)(fVar3 < DAT_00522918) << 0x1f)) || (fVar3 < DAT_0052291c)) ||
      (-1 < (int)((uint)(param_1[7] < DAT_00522918) << 0x1f))) || (param_1[7] < DAT_0052291c)) {
    puVar1 = (undefined4 *)FUN_00514aec(9);
    if (puVar1 == (undefined4 *)0x0) {
      return;
    }
    *puVar1 = 0x174;
    fVar3 = param_1[5];
    puVar1[2] = 0x168;
    puVar1[1] = fVar3;
    fVar3 = param_1[2];
    puVar1[4] = 0x178;
    puVar1[3] = fVar3;
    fVar3 = param_1[6];
    puVar1[6] = 0x17c;
    puVar1[5] = fVar3;
    fVar3 = param_1[7];
    puVar1[8] = 0x180;
    puVar1[7] = fVar3;
    puVar1[9] = param_1[8];
    iVar2 = 10;
  }
  else {
    if ((-1 < (int)((uint)(fVar3 + -1.0 < DAT_00522918) << 0x1f)) || (fVar3 + -1.0 < DAT_0052291c))
    {
      *param_1 = *param_1 / param_1[8];
      param_1[1] = param_1[1] / param_1[8];
      param_1[2] = param_1[2] / param_1[8];
      param_1[3] = param_1[3] / param_1[8];
      param_1[4] = param_1[4] / param_1[8];
      param_1[5] = param_1[5] / param_1[8];
    }
    puVar1 = (undefined4 *)FUN_00514aec(6);
    if (puVar1 == (undefined4 *)0x0) {
      return;
    }
    *puVar1 = 0x174;
    fVar3 = param_1[5];
    puVar1[2] = 0x168;
    puVar1[1] = fVar3;
    puVar1[3] = param_1[2];
    iVar2 = 4;
  }
  puVar1[iVar2] = 0x160;
  puVar1[iVar2 + 1] = *param_1;
  puVar1[iVar2 + 2] = 0x164;
  puVar1[iVar2 + 3] = param_1[1];
  puVar1[iVar2 + 4] = 0x16c;
  puVar1[iVar2 + 5] = param_1[3];
  puVar1[iVar2 + 6] = 0x170;
  puVar1[iVar2 + 7] = param_1[4];
  return;
}

