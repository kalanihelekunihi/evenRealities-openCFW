
uint FUN_004cda36(int param_1,int param_2,undefined4 param_3,int param_4,undefined4 param_5)

{
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uVar5;
  uint local_38 [2];
  uint local_30;
  undefined4 local_2c;
  uint local_28;
  undefined4 local_20;
  
  local_20 = param_3;
  if ((param_4 << 0x1e < 0) && (uVar1 = FUN_004cf9e0(param_1), uVar1 != 0)) {
    return uVar1;
  }
  *(undefined4 *)(param_2 + 0x50) = param_5;
  *(int *)(param_2 + 0x30) = param_4;
  *(undefined4 *)(param_2 + 0x34) = 0;
  *(undefined4 *)(param_2 + 0x3c) = 0;
  *(undefined4 *)(param_2 + 0x4c) = 0;
  uVar1 = FUN_004cc04a(param_1,param_2 + 8,&local_20,param_2 + 4);
  if (((int)uVar1 < 0) && ((uVar1 != 0xfffffffe || (iVar2 = FUN_004cad80(local_20), iVar2 == 0))))
  goto LAB_004cda8a;
  *(undefined1 *)(param_2 + 6) = 1;
  lfs_mlist_append(param_1,param_2);
  if (uVar1 == 0xfffffffe) {
    if (-1 < param_4 << 0x17) {
      uVar1 = 0xfffffffe;
      goto LAB_004cda8a;
    }
    iVar2 = FUN_004cadac(local_20);
    if (iVar2 != 0) {
      uVar1 = 0xffffffec;
      goto LAB_004cda8a;
    }
    uVar1 = FUN_004cad76(local_20);
    if (*(uint *)(param_1 + 0x70) < uVar1) {
      uVar1 = 0xffffffdc;
      goto LAB_004cda8a;
    }
    FUN_0048949c(local_38,0x18);
    uVar4 = DAT_004ce604;
    local_38[0] = DAT_004cdf6c | (uint)*(ushort *)(param_2 + 4) << 10;
    local_30 = uVar1 | (uint)*(ushort *)(param_2 + 4) << 10 | 0x100000;
    local_2c = local_20;
    local_28 = DAT_004ce604 | (uint)*(ushort *)(param_2 + 4) << 10;
    uVar1 = FUN_004cd388(param_1,param_2 + 8,local_38,3);
    if (uVar1 == 0xffffffe4) {
      uVar1 = 0xffffffdc;
    }
    if (uVar1 != 0) goto LAB_004cda8a;
  }
  else {
    if (param_4 << 0x16 < 0) {
      uVar1 = 0xffffffef;
      goto LAB_004cda8a;
    }
    iVar2 = FUN_004cae98(uVar1);
    if (iVar2 != 1) {
      uVar1 = 0xffffffeb;
      goto LAB_004cda8a;
    }
    if (param_4 << 0x15 < 0) {
      uVar4 = DAT_004ce604 | (uint)*(ushort *)(param_2 + 4) << 10;
      *(uint *)(param_2 + 0x30) = *(uint *)(param_2 + 0x30) | 0x10000;
    }
    else {
      local_38[0] = param_2 + 0x28;
      uVar1 = FUN_004cb3c8(param_1,param_2 + 8,DAT_004ce19c,
                           DAT_004cdf70 | (uint)*(ushort *)(param_2 + 4) << 10);
      if ((int)uVar1 < 0) goto LAB_004cda8a;
      FUN_004cafea(param_2 + 0x28);
      uVar4 = uVar1;
    }
  }
  for (uVar5 = 0; uVar5 < *(uint *)(*(int *)(param_2 + 0x50) + 8); uVar5 = uVar5 + 1) {
    if ((int)((uint)*(byte *)(param_2 + 0x30) << 0x1f) < 0) {
      local_38[0] = *(uint *)(*(int *)(*(int *)(param_2 + 0x50) + 4) + uVar5 * 0xc + 4);
      uVar1 = FUN_004cb3c8(param_1,param_2 + 8,DAT_004ce608,
                           (uint)*(ushort *)(param_2 + 4) << 10 |
                           (*(byte *)(*(int *)(*(int *)(param_2 + 0x50) + 4) + uVar5 * 0xc) + 0x300)
                           * 0x100000 |
                           *(uint *)(uVar5 * 0xc + *(int *)(*(int *)(param_2 + 0x50) + 4) + 8));
      if (((int)uVar1 < 0) && (uVar1 != 0xfffffffe)) goto LAB_004cda8a;
    }
    if ((int)((uint)*(byte *)(param_2 + 0x30) << 0x1e) < 0) {
      if (*(uint *)(param_1 + 0x78) <
          *(uint *)(*(int *)(*(int *)(param_2 + 0x50) + 4) + uVar5 * 0xc + 8)) {
        uVar1 = 0xffffffe4;
        goto LAB_004cda8a;
      }
      *(uint *)(param_2 + 0x30) = *(uint *)(param_2 + 0x30) | 0x10000;
    }
  }
  if (**(int **)(param_2 + 0x50) == 0) {
    uVar3 = FUN_004ca80a(*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x28));
    *(undefined4 *)(param_2 + 0x4c) = uVar3;
    if (*(int *)(param_2 + 0x4c) == 0) {
      uVar1 = 0xfffffff4;
      goto LAB_004cda8a;
    }
  }
  else {
    *(undefined4 *)(param_2 + 0x4c) = **(undefined4 **)(param_2 + 0x50);
  }
  FUN_004ca822(param_1,param_2 + 0x40);
  iVar2 = FUN_004cae98(uVar4);
  if (iVar2 == 0x201) {
    *(undefined4 *)(param_2 + 0x28) = 0xfffffffe;
    uVar3 = FUN_004caeb8(uVar4);
    *(undefined4 *)(param_2 + 0x2c) = uVar3;
    *(uint *)(param_2 + 0x30) = *(uint *)(param_2 + 0x30) | 0x100000;
    *(undefined4 *)(param_2 + 0x40) = *(undefined4 *)(param_2 + 0x28);
    *(undefined4 *)(param_2 + 0x44) = 0;
    *(undefined4 *)(param_2 + 0x48) = *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x28);
    if (*(int *)(param_2 + 0x2c) != 0) {
      uVar1 = lfs_min(*(undefined4 *)(param_2 + 0x48),0x3fe);
      local_38[0] = *(uint *)(param_2 + 0x4c);
      uVar1 = FUN_004cb3c8(param_1,param_2 + 8,DAT_004ce19c,
                           uVar1 | (uint)*(ushort *)(param_2 + 4) << 10 | 0x20000000);
      if ((int)uVar1 < 0) {
LAB_004cda8a:
        *(uint *)(param_2 + 0x30) = *(uint *)(param_2 + 0x30) | 0x80000;
        FUN_004cdce4(param_1,param_2);
        return uVar1;
      }
    }
  }
  return 0;
}

