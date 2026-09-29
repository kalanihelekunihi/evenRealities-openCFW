
int FUN_005da73a(int param_1)

{
  int iVar1;
  uint uVar2;
  undefined1 *puVar3;
  int iVar4;
  uint *puVar5;
  byte *pbVar6;
  uint uVar7;
  uint uVar8;
  undefined4 uVar9;
  int iVar10;
  byte *pbVar11;
  byte *local_48;
  int local_44;
  int *local_40;
  int local_3c;
  int local_38;
  int local_34;
  int local_30;
  uint local_2c;
  undefined1 auStack_28 [12];
  uint local_1c;
  
  uVar9 = *(undefined4 *)(param_1 + 100);
  iVar10 = *(int *)(param_1 + 0x224);
  if (*(int *)(param_1 + 0x2c4) == 0) {
    iVar1 = FUN_005da5d6(param_1,0x19,&local_44,&local_38);
    if (iVar1 == 0) {
      iVar1 = FUN_005da5d6(param_1,0x10,&local_44,&local_38);
    }
    if (iVar1 == 0) {
      iVar1 = FUN_005da5d6(param_1,1,&local_44,&local_38);
    }
    if (iVar1 == 0) {
      return 0;
    }
    if (local_44 == -1) {
      local_48 = (byte *)0x0;
      iVar1 = FUN_005da518(*(undefined4 *)(param_1 + 100),*(undefined4 *)(param_1 + 0x170),
                           local_38 * 0x14 + *(int *)(param_1 + 0x164),DAT_005db3e0);
    }
    else {
      local_48 = (byte *)0x0;
      iVar1 = FUN_005da446(*(undefined4 *)(param_1 + 100),*(undefined4 *)(param_1 + 0x170),
                           local_44 * 0x14 + *(int *)(param_1 + 0x164),DAT_005db3e0);
    }
    uVar2 = FUN_0044a43c(iVar1);
    if (0x5b < uVar2) {
      uVar2 = 0x5b;
      *(undefined1 *)(iVar1 + 0x5b) = 0;
    }
    *(int *)(param_1 + 0x2c4) = iVar1;
    *(uint *)(param_1 + 0x2c8) = uVar2;
  }
  local_48 = (byte *)&local_34;
  (**(code **)(iVar10 + 0x20))(param_1,&local_2c,&local_40,0);
  if (((*(uint *)(param_1 + 4) & DAT_005db3e4) != 0) && (-1 < *(int *)(param_1 + 8) << 0x10)) {
    iVar10 = *(int *)(param_1 + 0x21c);
    iVar1 = ((*(uint *)(param_1 + 4) & 0x7fffffff) >> 0x10) - 1;
    uVar2 = *(uint *)(*(int *)(local_34 + 0x10) + iVar1 * 0xc + 8);
    local_3c = 0;
    if ((uVar2 == 6) || (uVar2 - 0x100 < 0x7f00)) {
      (**(code **)(iVar10 + 0x74))(param_1,uVar2 & 0xffff,&local_3c);
    }
    iVar4 = local_3c;
    if (local_3c != 0) {
      iVar10 = FUN_0044a43c(local_3c);
      pbVar11 = (byte *)(iVar10 + iVar4 + 1);
      goto LAB_005da858;
    }
    (**(code **)(iVar10 + 0x74))
              (param_1,*(uint *)(*(int *)(local_34 + 0x10) + iVar1 * 0xc + 4) & 0xffff,&local_48);
    if (local_48 != (byte *)0x0) {
      iVar10 = FUN_0044a43c(local_48);
      iVar4 = ft_mem_alloc(uVar9,iVar10 + *(int *)(param_1 + 0x2c8) + 2,&local_30);
      if (local_30 != 0) {
        return 0;
      }
      FUN_0048d540(iVar4,*(undefined4 *)(param_1 + 0x2c4));
      puVar3 = (undefined1 *)(*(int *)(param_1 + 0x2c8) + iVar4);
      *puVar3 = 0x2d;
      pbVar11 = puVar3 + 1;
      for (pbVar6 = local_48; *pbVar6 != 0; pbVar6 = pbVar6 + 1) {
        if (((*pbVar6 - 0x30 < 10) || (*pbVar6 - 0x41 < 0x1a)) || (*pbVar6 - 0x61 < 0x1a)) {
          *pbVar11 = *pbVar6;
          pbVar11 = pbVar11 + 1;
        }
      }
      *pbVar11 = 0;
      pbVar11 = pbVar11 + 1;
      ft_mem_free(uVar9,local_48);
      local_48 = (byte *)0x0;
      goto LAB_005da858;
    }
  }
  iVar10 = *(int *)(local_34 + 0xc);
  iVar4 = ft_mem_alloc(uVar9,local_2c * 0x11 + *(int *)(param_1 + 0x2c8) + 1,&local_30);
  if (local_30 != 0) {
    return 0;
  }
  FUN_0048d540(iVar4,*(undefined4 *)(param_1 + 0x2c4));
  pbVar11 = (byte *)(iVar4 + *(int *)(param_1 + 0x2c8));
  for (uVar2 = 0; uVar2 < local_2c; uVar2 = uVar2 + 1) {
    if (*local_40 != *(int *)(iVar10 + 8)) {
      *pbVar11 = 0x5f;
      pbVar11 = (byte *)FUN_005da656(*local_40,pbVar11 + 1);
      uVar7 = *(uint *)(iVar10 + 0x10);
      if ((uVar7 >> 0x18 != 0x20) &&
         ((((uVar7 >> 0x18) - 0x30 < 10 || ((uVar7 >> 0x18) - 0x41 < 0x1a)) ||
          ((uVar7 >> 0x18) - 0x61 < 0x1a)))) {
        *pbVar11 = (byte)(uVar7 >> 0x18);
        pbVar11 = pbVar11 + 1;
      }
      uVar7 = *(uint *)(iVar10 + 0x10);
      if (((uVar7 >> 0x10 & 0xff) != 0x20) &&
         ((((uVar7 >> 0x10 & 0xff) - 0x30 < 10 || ((uVar7 >> 0x10 & 0xff) - 0x41 < 0x1a)) ||
          ((uVar7 >> 0x10 & 0xff) - 0x61 < 0x1a)))) {
        *pbVar11 = (byte)(uVar7 >> 0x10);
        pbVar11 = pbVar11 + 1;
      }
      uVar7 = *(uint *)(iVar10 + 0x10);
      if (((uVar7 >> 8 & 0xff) != 0x20) &&
         ((((uVar7 >> 8 & 0xff) - 0x30 < 10 || ((uVar7 >> 8 & 0xff) - 0x41 < 0x1a)) ||
          ((uVar7 >> 8 & 0xff) - 0x61 < 0x1a)))) {
        *pbVar11 = (byte)(uVar7 >> 8);
        pbVar11 = pbVar11 + 1;
      }
      uVar7 = *(uint *)(iVar10 + 0x10);
      if (((uVar7 & 0xff) != 0x20) &&
         ((((uVar7 & 0xff) - 0x30 < 10 || ((uVar7 & 0xff) - 0x41 < 0x1a)) ||
          ((uVar7 & 0xff) - 0x61 < 0x1a)))) {
        *pbVar11 = (byte)uVar7;
        pbVar11 = pbVar11 + 1;
      }
    }
    local_40 = local_40 + 1;
    iVar10 = iVar10 + 0x18;
  }
LAB_005da858:
  if (0x7f < (int)pbVar11 - iVar4) {
    FUN_005da202(iVar4,(int)pbVar11 - iVar4,DAT_005db3e8,auStack_28);
    puVar3 = (undefined1 *)(*(int *)(param_1 + 0x2c8) + iVar4);
    *puVar3 = 0x2d;
    puVar5 = &local_1c;
    puVar3[0x24] = 0;
    puVar3[0x23] = 0x2e;
    puVar3[0x22] = 0x2e;
    puVar3[0x21] = 0x2e;
    puVar3 = puVar3 + 0x20;
    for (uVar2 = 0; uVar2 < 4; uVar2 = uVar2 + 1) {
      uVar8 = *puVar5;
      for (uVar7 = 0; uVar7 < 8; uVar7 = uVar7 + 1) {
        *puVar3 = *(undefined1 *)(DAT_005db564 + (uVar8 & 0xf));
        puVar3 = puVar3 + -1;
        uVar8 = uVar8 >> 4;
      }
      puVar5 = puVar5 + -1;
    }
  }
  return iVar4;
}

