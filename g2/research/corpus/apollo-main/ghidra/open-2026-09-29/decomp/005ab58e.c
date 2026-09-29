
int af_loader_compute_darkening(int param_1,int param_2,int param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  
  iVar12 = *(int *)(*(int *)(param_1 + 4) + 0x178);
  if ((int)((uint)*(ushort *)(*(int *)(param_2 + 0x58) + 0xc) * 0x10000) < 0x40000) {
    iVar5 = 0x40000;
  }
  else {
    iVar5 = (uint)*(ushort *)(*(int *)(param_2 + 0x58) + 0xc) << 0x10;
  }
  iVar1 = FT_DivFix(0x3e80000,(uint)*(ushort *)(param_2 + 0x44) << 0x10);
  if (iVar1 < 0x28f) {
    return 0;
  }
  iVar4 = *(int *)(iVar12 + 0x18);
  iVar6 = *(int *)(iVar12 + 0x1c);
  iVar7 = *(int *)(iVar12 + 0x20);
  iVar8 = *(int *)(iVar12 + 0x24);
  iVar9 = *(int *)(iVar12 + 0x28);
  iVar10 = *(int *)(iVar12 + 0x2c);
  iVar11 = *(int *)(iVar12 + 0x30);
  iVar12 = *(int *)(iVar12 + 0x34);
  if (param_3 < 1) {
    iVar13 = 0x4b0000;
  }
  else {
    iVar13 = FT_MulFix(param_3 << 0x10,iVar1);
  }
  iVar2 = FT_MSB(iVar13);
  iVar3 = FT_MSB(iVar5);
  if (iVar3 + iVar2 < 0x2e) {
    iVar2 = FT_MulFix(iVar13,iVar5);
  }
  else {
    iVar2 = iVar11 << 0x10;
  }
  if (iVar2 < iVar4 * 0x10000) {
    iVar12 = FT_DivFix(iVar6 << 0x10,iVar5);
    goto LAB_005ab6f0;
  }
  if (iVar2 < iVar7 * 0x10000) {
    iVar2 = FT_DivFix(iVar4 << 0x10,iVar5);
    if (iVar7 - iVar4 != 0) {
      iVar4 = FT_MulDiv(iVar13 - iVar2,iVar8 - iVar6,iVar7 - iVar4);
      iVar12 = FT_DivFix(iVar6 << 0x10,iVar5);
      iVar12 = iVar12 + iVar4;
      goto LAB_005ab6f0;
    }
LAB_005ab68a:
    iVar4 = FT_DivFix(iVar7 << 0x10,iVar5);
    if (iVar9 - iVar7 != 0) {
      iVar4 = FT_MulDiv(iVar13 - iVar4,iVar10 - iVar8,iVar9 - iVar7);
      iVar12 = FT_DivFix(iVar8 << 0x10,iVar5);
      iVar12 = iVar12 + iVar4;
      goto LAB_005ab6f0;
    }
LAB_005ab6c4:
    iVar4 = FT_DivFix(iVar9 << 0x10,iVar5);
    if (iVar11 - iVar9 != 0) {
      iVar4 = FT_MulDiv(iVar13 - iVar4,iVar12 - iVar10,iVar11 - iVar9);
      iVar12 = FT_DivFix(iVar10 << 0x10,iVar5);
      iVar12 = iVar12 + iVar4;
      goto LAB_005ab6f0;
    }
  }
  else {
    if (iVar2 < iVar9 * 0x10000) goto LAB_005ab68a;
    if (iVar2 < iVar11 * 0x10000) goto LAB_005ab6c4;
  }
  iVar12 = FT_DivFix(iVar12 << 0x10,iVar5);
LAB_005ab6f0:
  iVar12 = FT_DivFix(iVar12,iVar1);
  return (int)(short)((uint)(iVar12 + 0x8000) >> 0x10);
}

