
void FUN_0048bae4(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  int iVar6;
  undefined4 uVar7;
  int iVar8;
  int *piVar9;
  char cVar10;
  int iVar11;
  undefined1 local_7c;
  undefined1 local_7b;
  char local_7a;
  byte local_79;
  byte local_78;
  int local_74;
  int local_70;
  int local_6c;
  int local_68;
  int local_64;
  int local_60 [4];
  undefined4 local_50;
  uint local_48;
  int local_44 [6];
  uint local_2c;
  undefined4 uStack_28;
  
  uStack_28 = param_4;
  uVar2 = FUN_0048b9cc(param_1,0);
  local_79 = local_79 & 0xf8 | (byte)uVar2 & 1 ^ 1 | (byte)(((uVar2 & 0xff) >> 2 & 1) << 1) |
             (byte)(((uVar2 & 0xff) >> 3 & 1) << 2);
  local_7c = FUN_0048b9d8(param_1,0);
  local_7b = FUN_0048b9e4(param_1,0);
  local_7a = FUN_0048b9f0(param_1,0);
  iVar3 = FUN_0048b9c0(param_1,0);
  local_78 = iVar3 == 1;
  if ((int)((uint)local_79 << 0x1f) < 0) {
    iVar3 = FUN_0048b96e(param_1,0);
  }
  else {
    iVar3 = FUN_0048b978(param_1,0);
  }
  if ((int)((uint)local_79 << 0x1f) < 0) {
    uVar4 = FUN_0048b978(param_1,0);
  }
  else {
    uVar4 = FUN_0048b96e(param_1,0);
  }
  if ((int)((uint)local_79 << 0x1f) < 0) {
    uVar5 = FUN_0043fe16(param_1);
  }
  else {
    uVar5 = FUN_0043fe70(param_1);
  }
  iVar6 = FUN_0048ba36(param_1,0);
  local_6c = FUN_0044e498(param_1);
  local_6c = (iVar6 + *(int *)(param_1 + 0x18)) - local_6c;
  iVar6 = FUN_0048ba08(param_1,0);
  local_70 = FUN_0044e486(param_1);
  cVar10 = local_7a;
  local_70 = (iVar6 + *(int *)(param_1 + 0x14)) - local_70;
  if ((int)((uint)local_79 << 0x1f) < 0) {
    puVar1 = &stack0xfffffffc;
  }
  else {
    puVar1 = &stack0xfffffff8;
  }
  piVar9 = (int *)(puVar1 + -0x68);
  local_64 = FUN_0048b90a(param_1,0);
  local_68 = FUN_0048b928(param_1,0);
  if (((((int)((uint)local_79 << 0x1f) < 0) && (local_68 == 0x3fffffff)) &&
      ((*(ushort *)(param_1 + 0x2a) & 0x7ff) >> 10 == 0)) ||
     (((-1 < (int)((uint)local_79 << 0x1f) && (local_64 == 0x3fffffff)) &&
      ((*(ushort *)(param_1 + 0x2a) & 0xfff) >> 0xb == 0)))) {
    cVar10 = '\0';
  }
  if ((local_78 & (local_79 & 1 ^ 1)) != 0) {
    if (cVar10 == '\0') {
      cVar10 = '\x01';
    }
    else if (cVar10 == '\x01') {
      cVar10 = '\0';
    }
  }
  iVar11 = 0;
  local_74 = 0;
  iVar6 = 0;
  if (cVar10 != '\0') {
    if ((local_79 & 7) >> 2 == 0) {
      iVar8 = 0;
    }
    else {
      iVar8 = *(ushort *)(*(int *)(param_1 + 8) + 0x30) - 1;
    }
    while ((iVar8 < (int)(uint)*(ushort *)(*(int *)(param_1 + 8) + 0x30) && (-1 < iVar8))) {
      local_2c = local_2c & 0xfffffffe;
      iVar8 = FUN_0048be22(param_1,&local_7c,iVar8,uVar5,uVar4,local_44);
      iVar11 = iVar3 + local_44[0] + iVar11;
      iVar6 = iVar6 + 1;
    }
    if (iVar6 != 0) {
      iVar11 = iVar11 - iVar3;
    }
    if ((int)((uint)local_79 << 0x1f) < 0) {
      uVar7 = FUN_0043fe70(param_1);
    }
    else {
      uVar7 = FUN_0043fe16(param_1);
    }
    FUN_0048c6d8(cVar10,uVar7,iVar11,iVar6,piVar9,&local_74);
  }
  if ((local_79 & 7) >> 2 == 0) {
    iVar6 = 0;
  }
  else {
    iVar6 = *(ushort *)(*(int *)(param_1 + 8) + 0x30) - 1;
  }
  if ((local_78 & (local_79 & 1 ^ 1)) != 0) {
    *piVar9 = iVar11 + *piVar9;
  }
  while ((iVar6 < (int)(uint)*(ushort *)(*(int *)(param_1 + 8) + 0x30) && (-1 < iVar6))) {
    local_48 = local_48 | 1;
    iVar11 = FUN_0048be22(param_1,&local_7c,iVar6,uVar5,uVar4,local_60);
    if ((local_78 & (local_79 & 1 ^ 1)) != 0) {
      *piVar9 = *piVar9 - local_60[0];
    }
    FUN_0048c14e(param_1,&local_7c,iVar6,iVar11,local_70,local_6c,uVar5,uVar4,local_60);
    FUN_0044f758(local_50);
    local_50 = 0;
    iVar6 = iVar11;
    if ((local_78 & (local_79 & 1 ^ 1)) == 0) {
      *piVar9 = iVar3 + local_74 + local_60[0] + *piVar9;
    }
    else {
      *piVar9 = (*piVar9 - local_74) - iVar3;
    }
  }
  if ((local_64 == 0x3fffffff) || (local_68 == 0x3fffffff)) {
    FUN_0043f1a4(param_1);
  }
  FUN_00451670(param_1,0x33,0);
  return;
}

