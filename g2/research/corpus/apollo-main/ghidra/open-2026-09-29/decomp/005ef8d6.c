
undefined8
TT_Load_Composite_Glyph(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint *puVar2;
  byte *pbVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  byte *pbVar8;
  undefined1 *puVar9;
  undefined1 *puVar10;
  int iVar11;
  int iVar12;
  uint uVar13;
  
  puVar9 = *(undefined1 **)(param_1 + 0xc4);
  pbVar8 = *(byte **)(param_1 + 200);
  iVar11 = *(int *)(param_1 + 0xc);
  iVar12 = 0;
  do {
    iVar1 = FT_GlyphLoader_CheckSubGlyphs(iVar11,iVar12 + 1);
    if (iVar1 != 0) goto LAB_005efaca;
    if (pbVar8 < puVar9 + 4) {
LAB_005ef94c:
      iVar1 = 0x15;
      goto LAB_005efaca;
    }
    puVar2 = (uint *)(*(int *)(iVar11 + 0x58) + iVar12 * 0x20);
    puVar2[3] = 0;
    puVar2[2] = puVar2[3];
    *(ushort *)(puVar2 + 1) = CONCAT11(*puVar9,puVar9[1]);
    pbVar3 = puVar9 + 4;
    *puVar2 = (uint)CONCAT11(puVar9[2],puVar9[3]);
    iVar5 = 2;
    if ((int)((uint)(byte)puVar2[1] << 0x1f) < 0) {
      iVar5 = 4;
    }
    if ((int)((uint)(byte)puVar2[1] << 0x1c) < 0) {
      iVar5 = iVar5 + 2;
    }
    else if ((int)((uint)(byte)puVar2[1] << 0x19) < 0) {
      iVar5 = iVar5 + 4;
    }
    else if ((int)((uint)(byte)puVar2[1] << 0x18) < 0) {
      iVar5 = iVar5 + 8;
    }
    if (pbVar8 < pbVar3 + iVar5) goto LAB_005ef94c;
    if ((int)((uint)(byte)puVar2[1] << 0x1e) < 0) {
      if ((int)((uint)(byte)puVar2[1] << 0x1f) < 0) {
        puVar2[2] = (int)CONCAT11(puVar9[4],puVar9[5]);
        puVar10 = puVar9 + 8;
        puVar2[3] = (int)CONCAT11(puVar9[6],puVar9[7]);
      }
      else {
        puVar2[2] = (int)(char)*pbVar3;
        puVar2[3] = (int)(char)puVar9[5];
        puVar10 = puVar9 + 6;
      }
    }
    else if ((int)((uint)(byte)puVar2[1] << 0x1f) < 0) {
      puVar2[2] = (uint)CONCAT11(puVar9[4],puVar9[5]);
      puVar10 = puVar9 + 8;
      puVar2[3] = (uint)CONCAT11(puVar9[6],puVar9[7]);
    }
    else {
      puVar2[2] = (uint)*pbVar3;
      puVar2[3] = (uint)(byte)puVar9[5];
      puVar10 = puVar9 + 6;
    }
    uVar13 = 0x10000;
    uVar4 = 0x10000;
    uVar6 = 0;
    uVar7 = 0;
    if ((int)((uint)(byte)puVar2[1] << 0x1c) < 0) {
      uVar4 = (int)CONCAT11(*puVar10,puVar10[1]) << 2;
      puVar9 = puVar10 + 2;
      uVar13 = uVar4;
    }
    else if ((int)((uint)(byte)puVar2[1] << 0x19) < 0) {
      uVar4 = (int)CONCAT11(*puVar10,puVar10[1]) << 2;
      uVar13 = (int)CONCAT11(puVar10[2],puVar10[3]) << 2;
      puVar9 = puVar10 + 4;
    }
    else {
      puVar9 = puVar10;
      if ((int)((uint)(byte)puVar2[1] << 0x18) < 0) {
        uVar4 = (int)CONCAT11(*puVar10,puVar10[1]) << 2;
        uVar6 = (int)CONCAT11(puVar10[2],puVar10[3]) << 2;
        uVar7 = (int)CONCAT11(puVar10[4],puVar10[5]) << 2;
        puVar9 = puVar10 + 8;
        uVar13 = (int)CONCAT11(puVar10[6],puVar10[7]) << 2;
      }
    }
    puVar2[4] = uVar4;
    puVar2[5] = uVar7;
    puVar2[6] = uVar6;
    puVar2[7] = uVar13;
    iVar12 = iVar12 + 1;
  } while ((int)((uint)(byte)puVar2[1] << 0x1a) < 0);
  *(int *)(iVar11 + 0x54) = iVar12;
  *(undefined1 **)(param_1 + 0xa4) = puVar9 + (*(int *)(*(int *)(param_1 + 0x18) + 8) - (int)pbVar8)
  ;
  *(undefined1 **)(param_1 + 0xc4) = puVar9;
LAB_005efaca:
  return CONCAT44(param_4,iVar1);
}

