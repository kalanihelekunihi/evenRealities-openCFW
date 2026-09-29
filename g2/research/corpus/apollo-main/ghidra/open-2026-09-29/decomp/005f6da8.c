
void Ins_ISECT(int param_1,uint *param_2)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  
  uVar10 = *param_2;
  uVar11 = param_2[1];
  uVar1 = param_2[2];
  uVar12 = param_2[3];
  uVar2 = param_2[4];
  if (((((uVar12 & 0xffff) < (uint)*(ushort *)(param_1 + 0x2c)) &&
       ((uVar2 & 0xffff) < (uint)*(ushort *)(param_1 + 0x2c))) &&
      ((uVar11 & 0xffff) < (uint)*(ushort *)(param_1 + 0x50))) &&
     (((uVar1 & 0xffff) < (uint)*(ushort *)(param_1 + 0x50) &&
      ((uVar10 & 0xffff) < (uint)*(ushort *)(param_1 + 0x74))))) {
    iVar13 = *(int *)(*(int *)(param_1 + 0x34) + (uVar2 & 0xffff) * 8) -
             *(int *)(*(int *)(param_1 + 0x34) + (uVar12 & 0xffff) * 8);
    iVar14 = *(int *)(*(int *)(param_1 + 0x34) + (uVar2 & 0xffff) * 8 + 4) -
             *(int *)(*(int *)(param_1 + 0x34) + (uVar12 & 0xffff) * 8 + 4);
    iVar15 = *(int *)(*(int *)(param_1 + 0x58) + (uVar1 & 0xffff) * 8) -
             *(int *)(*(int *)(param_1 + 0x58) + (uVar11 & 0xffff) * 8);
    iVar16 = *(int *)(*(int *)(param_1 + 0x58) + (uVar1 & 0xffff) * 8 + 4) -
             *(int *)(*(int *)(param_1 + 0x58) + (uVar11 & 0xffff) * 8 + 4);
    iVar8 = *(int *)(*(int *)(param_1 + 0x34) + (uVar12 & 0xffff) * 8);
    iVar3 = *(int *)(*(int *)(param_1 + 0x58) + (uVar11 & 0xffff) * 8);
    iVar9 = *(int *)(*(int *)(param_1 + 0x34) + (uVar12 & 0xffff) * 8 + 4);
    iVar4 = *(int *)(*(int *)(param_1 + 0x58) + (uVar11 & 0xffff) * 8 + 4);
    iVar5 = FT_MulDiv(iVar15,-iVar14,0x40);
    iVar6 = FT_MulDiv(iVar16,iVar13,0x40);
    iVar6 = iVar6 + iVar5;
    iVar7 = FT_MulDiv(iVar15,iVar13,0x40);
    iVar5 = FT_MulDiv(iVar16,iVar14,0x40);
    iVar5 = iVar5 + iVar7;
    if (iVar5 < 0) {
      iVar5 = -iVar5;
    }
    iVar7 = iVar6;
    if (iVar6 < 0) {
      iVar7 = -iVar6;
    }
    if (iVar5 < iVar7 * 0x13) {
      iVar5 = FT_MulDiv(iVar8 - iVar3,-iVar14,0x40);
      iVar3 = FT_MulDiv(iVar9 - iVar4,iVar13,0x40);
      iVar4 = FT_MulDiv(iVar3 + iVar5,iVar15,iVar6);
      iVar5 = FT_MulDiv(iVar3 + iVar5,iVar16,iVar6);
      *(int *)(*(int *)(param_1 + 0x7c) + (uVar10 & 0xffff) * 8) =
           iVar4 + *(int *)(*(int *)(param_1 + 0x58) + (uVar11 & 0xffff) * 8);
      *(int *)(*(int *)(param_1 + 0x7c) + (uVar10 & 0xffff) * 8 + 4) =
           iVar5 + *(int *)(*(int *)(param_1 + 0x58) + (uVar11 & 0xffff) * 8 + 4);
    }
    else {
      *(int *)(*(int *)(param_1 + 0x7c) + (uVar10 & 0xffff) * 8) =
           (*(int *)(*(int *)(param_1 + 0x34) + (uVar2 & 0xffff) * 8) +
           *(int *)(*(int *)(param_1 + 0x34) + (uVar12 & 0xffff) * 8) +
           *(int *)(*(int *)(param_1 + 0x58) + (uVar1 & 0xffff) * 8) +
           *(int *)(*(int *)(param_1 + 0x58) + (uVar11 & 0xffff) * 8)) / 4;
      *(int *)(*(int *)(param_1 + 0x7c) + (uVar10 & 0xffff) * 8 + 4) =
           (*(int *)(*(int *)(param_1 + 0x34) + (uVar2 & 0xffff) * 8 + 4) +
           *(int *)(*(int *)(param_1 + 0x34) + (uVar12 & 0xffff) * 8 + 4) +
           *(int *)(*(int *)(param_1 + 0x58) + (uVar1 & 0xffff) * 8 + 4) +
           *(int *)(*(int *)(param_1 + 0x58) + (uVar11 & 0xffff) * 8 + 4)) / 4;
    }
    *(byte *)(*(int *)(param_1 + 0x84) + (uVar10 & 0xffff)) =
         *(byte *)(*(int *)(param_1 + 0x84) + (uVar10 & 0xffff)) | 0x18;
  }
  else if (*(char *)(param_1 + 0x235) != '\0') {
    *(undefined4 *)(param_1 + 0xc) = 0x86;
  }
  return;
}

