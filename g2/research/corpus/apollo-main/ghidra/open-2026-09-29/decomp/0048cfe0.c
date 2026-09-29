
void FUN_0048cfe0(int param_1,int *param_2,int param_3)

{
  byte bVar1;
  byte bVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  uint uVar9;
  uint uVar10;
  int iVar11;
  int local_3c;
  int local_38;
  undefined1 auStack_34 [16];
  
  iVar3 = FUN_0043e11c(param_1,DAT_0048d3bc);
  if (iVar3 != 0) {
    return;
  }
  iVar3 = FUN_0048c9a4(param_1);
  iVar4 = FUN_0048c9ae(param_1);
  if (iVar4 == 0) {
    return;
  }
  if (iVar3 == 0) {
    return;
  }
  iVar5 = FUN_0048c990(param_1);
  iVar6 = FUN_0048c99a(param_1);
  bVar1 = FUN_0048c9b8(param_1);
  bVar2 = FUN_0048c9c2(param_1);
  iVar11 = (*(int *)(param_2[2] + (iVar3 + iVar5) * 4 + -4) +
           *(int *)(*param_2 + (iVar3 + iVar5) * 4 + -4)) - *(int *)(*param_2 + iVar5 * 4);
  iVar4 = (*(int *)(param_2[3] + (iVar4 + iVar6) * 4 + -4) +
          *(int *)(param_2[1] + (iVar4 + iVar6) * 4 + -4)) - *(int *)(param_2[1] + iVar6 * 4);
  iVar3 = FUN_0048c8a8(param_1,0);
  if (iVar3 == 1) {
    if (bVar1 == 0) {
      bVar1 = 2;
    }
    else if (bVar1 == 2) {
      bVar1 = 0;
    }
  }
  local_38 = FUN_00451598(param_1 + 0x14);
  local_3c = FUN_004515a4(param_1 + 0x14);
  if (bVar1 == 1) {
    iVar3 = FUN_0048c87e(param_1,0);
    iVar7 = FUN_0048c888(param_1,0);
    iVar3 = (iVar3 - iVar7) / 2 + (iVar11 - local_38) / 2 + *(int *)(*param_2 + iVar5 * 4);
    *(ushort *)(param_1 + 0x2a) = *(ushort *)(param_1 + 0x2a) & 0xf7ff;
  }
  else if (bVar1 == 0) {
LAB_0048d0de:
    iVar3 = FUN_0048c87e(param_1,0);
    iVar3 = iVar3 + *(int *)(*param_2 + iVar5 * 4);
    *(ushort *)(param_1 + 0x2a) = *(ushort *)(param_1 + 0x2a) & 0xf7ff;
  }
  else if (bVar1 == 3) {
    iVar3 = FUN_0048c87e(param_1,0);
    iVar3 = iVar3 + *(int *)(*param_2 + iVar5 * 4);
    local_38 = FUN_0048c9e0(param_1);
    local_38 = iVar11 - local_38;
    *(ushort *)(param_1 + 0x2a) = *(ushort *)(param_1 + 0x2a) | 0x800;
  }
  else {
    if (2 < bVar1) goto LAB_0048d0de;
    iVar7 = FUN_0043fd9e(param_1);
    iVar3 = FUN_0048c888(param_1,0);
    iVar3 = ((iVar11 + *(int *)(*param_2 + iVar5 * 4)) - iVar7) - iVar3;
    *(ushort *)(param_1 + 0x2a) = *(ushort *)(param_1 + 0x2a) & 0xf7ff;
  }
  if (bVar2 == 1) {
    iVar5 = FUN_0048c86a(param_1,0);
    iVar11 = FUN_0048c874(param_1,0);
    iVar5 = (iVar5 - iVar11) / 2 + (iVar4 - local_3c) / 2 + *(int *)(param_2[1] + iVar6 * 4);
    *(ushort *)(param_1 + 0x2a) = *(ushort *)(param_1 + 0x2a) & 0xfbff;
    goto LAB_0048d256;
  }
  if (bVar2 != 0) {
    if (bVar2 == 3) {
      iVar5 = FUN_0048c86a(param_1,0);
      iVar5 = iVar5 + *(int *)(param_2[1] + iVar6 * 4);
      local_3c = FUN_0048c9fc(param_1);
      local_3c = iVar4 - local_3c;
      *(ushort *)(param_1 + 0x2a) = *(ushort *)(param_1 + 0x2a) | 0x400;
      goto LAB_0048d256;
    }
    if (bVar2 < 3) {
      iVar11 = FUN_0043fdda(param_1);
      iVar5 = FUN_0048c874(param_1,0);
      iVar5 = ((iVar4 + *(int *)(param_2[1] + iVar6 * 4)) - iVar11) - iVar5;
      *(ushort *)(param_1 + 0x2a) = *(ushort *)(param_1 + 0x2a) & 0xfbff;
      goto LAB_0048d256;
    }
  }
  iVar5 = FUN_0048c86a(param_1,0);
  iVar5 = iVar5 + *(int *)(param_2[1] + iVar6 * 4);
  *(ushort *)(param_1 + 0x2a) = *(ushort *)(param_1 + 0x2a) & 0xfbff;
LAB_0048d256:
  iVar4 = FUN_0043fd9e(param_1);
  if ((iVar4 != local_38) || (iVar4 = FUN_0043fdda(param_1), iVar4 != local_3c)) {
    FUN_0048c7fc(auStack_34,param_1 + 0x14);
    FUN_00440656(param_1);
    FUN_00450b6c(param_1 + 0x14,local_38);
    FUN_00450b76(param_1 + 0x14,local_3c);
    FUN_00440656(param_1);
    FUN_00451670(param_1,0x31,auStack_34);
    uVar8 = FUN_0044dca2(param_1);
    FUN_00451670(uVar8,0x2a,param_1);
  }
  uVar9 = FUN_0048c82e(param_1,0);
  uVar10 = FUN_0048c838(param_1,0);
  iVar4 = FUN_0043fd9e(param_1);
  iVar6 = FUN_0043fdda(param_1);
  if (((uVar9 & 0x60000000) == 0x20000000) && ((int)(uVar9 & 0x9fffffff) < 0x1fffffff)) {
    if ((int)(uVar9 & 0x9fffffff) < 0x10000000) {
      uVar9 = uVar9 & 0x9fffffff;
    }
    else {
      uVar9 = 0xfffffff - (uVar9 & 0x9fffffff);
    }
    uVar9 = (int)(uVar9 * iVar4) / 100;
  }
  if (((uVar10 & 0x60000000) == 0x20000000) && ((int)(uVar10 & 0x9fffffff) < 0x1fffffff)) {
    if ((int)(uVar10 & 0x9fffffff) < 0x10000000) {
      uVar10 = uVar10 & 0x9fffffff;
    }
    else {
      uVar10 = 0xfffffff - (uVar10 & 0x9fffffff);
    }
    uVar10 = (int)(uVar10 * iVar6) / 100;
  }
  iVar3 = (uVar9 + iVar3 + *(int *)(param_3 + 8)) - *(int *)(param_1 + 0x14);
  iVar4 = (uVar10 + iVar5 + *(int *)(param_3 + 0xc)) - *(int *)(param_1 + 0x18);
  if (iVar4 != 0 || iVar3 != 0) {
    FUN_00440656(param_1);
    *(int *)(param_1 + 0x14) = iVar3 + *(int *)(param_1 + 0x14);
    *(int *)(param_1 + 0x1c) = iVar3 + *(int *)(param_1 + 0x1c);
    *(int *)(param_1 + 0x18) = iVar4 + *(int *)(param_1 + 0x18);
    *(int *)(param_1 + 0x20) = iVar4 + *(int *)(param_1 + 0x20);
    FUN_00440656(param_1);
    FUN_0044035e(param_1,iVar3,iVar4,0);
  }
  return;
}

