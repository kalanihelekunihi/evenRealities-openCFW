
undefined8
TT_Process_Simple_Glyph(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int *piVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined4 *puVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  
  iVar7 = param_1[3];
  iVar5 = 0;
  iVar6 = (int)*(short *)(iVar7 + 0x3a);
  iVar2 = param_1[0x12];
  piVar3 = (int *)(*(int *)(iVar7 + 0x3c) + iVar6 * 8);
  *piVar3 = param_1[0x11];
  piVar3[1] = iVar2;
  iVar4 = *(int *)(iVar7 + 0x3c) + iVar6 * 8;
  iVar2 = param_1[0x14];
  *(int *)(iVar4 + 8) = param_1[0x13];
  *(int *)(iVar4 + 0xc) = iVar2;
  iVar4 = *(int *)(iVar7 + 0x3c) + iVar6 * 8;
  iVar2 = param_1[0x2e];
  *(int *)(iVar4 + 0x10) = param_1[0x2d];
  *(int *)(iVar4 + 0x14) = iVar2;
  iVar4 = *(int *)(iVar7 + 0x3c) + iVar6 * 8;
  iVar2 = param_1[0x30];
  *(int *)(iVar4 + 0x18) = param_1[0x2f];
  *(int *)(iVar4 + 0x1c) = iVar2;
  *(undefined1 *)(*(int *)(iVar7 + 0x40) + iVar6) = 0;
  *(undefined1 *)(*(int *)(iVar7 + 0x40) + iVar6 + 1) = 0;
  *(undefined1 *)(*(int *)(iVar7 + 0x40) + iVar6 + 2) = 0;
  *(undefined1 *)(*(int *)(iVar7 + 0x40) + iVar6 + 3) = 0;
  iVar6 = iVar6 + 4;
  if (((*(uint *)(*param_1 + 4) & DAT_005f0b24) != 0) || (*(int *)(*param_1 + 8) << 0x10 < 0)) {
    iVar5 = TT_Vary_Apply_Glyph_Deltas(*param_1,param_1[5],iVar7 + 0x38,iVar6);
    if (-1 < (int)((uint)*(byte *)(*param_1 + 0x2c0) << 0x1e)) {
      param_1[0xf] = *(int *)(*(int *)(iVar7 + 0x3c) + iVar6 * 8 + -0x18) -
                     *(int *)(*(int *)(iVar7 + 0x3c) + iVar6 * 8 + -0x20);
    }
    if (-1 < (int)((uint)*(byte *)(*param_1 + 0x2c0) << 0x1b)) {
      param_1[0x2c] =
           *(int *)(*(int *)(iVar7 + 0x3c) + iVar6 * 8 + -8) -
           *(int *)(*(int *)(iVar7 + 0x3c) + iVar6 * 8 + -0x10);
    }
    if (iVar5 != 0) goto LAB_005eff2c;
  }
  if (-1 < (int)((uint)*(byte *)(param_1 + 4) << 0x1e)) {
    tt_prepare_zone(param_1 + 0x1e,iVar7 + 0x38,0,0);
    FUN_00439be4(param_1[0x23],param_1[0x22],(*(ushort *)(param_1 + 0x20) + 4) * 8);
  }
  puVar8 = *(undefined4 **)(iVar7 + 0x3c);
  iVar2 = *(int *)(iVar7 + 0x3c);
  if (-1 < (int)((uint)*(byte *)(param_1 + 4) << 0x1f)) {
    uVar9 = *(undefined4 *)(*(int *)(param_1[1] + 0x2c) + 4);
    uVar10 = *(undefined4 *)(*(int *)(param_1[1] + 0x2c) + 8);
    for (; puVar8 < (undefined4 *)(iVar2 + iVar6 * 8); puVar8 = puVar8 + 2) {
      uVar1 = FT_MulFix(*puVar8,uVar9);
      *puVar8 = uVar1;
      uVar1 = FT_MulFix(puVar8[1],uVar10);
      puVar8[1] = uVar1;
    }
  }
  if ((-1 < (int)((uint)*(byte *)(*param_1 + 0x2c0) << 0x1e)) ||
     ((int)((uint)*(byte *)(param_1 + 4) << 0x1e) < 0)) {
    iVar2 = *(int *)(iVar7 + 0x3c) + iVar6 * 8;
    iVar4 = *(int *)(iVar2 + -0x1c);
    param_1[0x11] = *(int *)(iVar2 + -0x20);
    param_1[0x12] = iVar4;
    iVar2 = *(int *)(iVar7 + 0x3c) + iVar6 * 8;
    iVar4 = *(int *)(iVar2 + -0x14);
    param_1[0x13] = *(int *)(iVar2 + -0x18);
    param_1[0x14] = iVar4;
  }
  if ((-1 < (int)((uint)*(byte *)(*param_1 + 0x2c0) << 0x1b)) ||
     ((int)((uint)*(byte *)(param_1 + 4) << 0x1e) < 0)) {
    iVar2 = *(int *)(iVar7 + 0x3c) + iVar6 * 8;
    iVar4 = *(int *)(iVar2 + -0xc);
    param_1[0x2d] = *(int *)(iVar2 + -0x10);
    param_1[0x2e] = iVar4;
    iVar2 = *(int *)(iVar7 + 0x3c) + iVar6 * 8;
    iVar4 = *(int *)(iVar2 + -4);
    param_1[0x2f] = *(int *)(iVar2 + -8);
    param_1[0x30] = iVar4;
  }
  if (-1 < (int)((uint)*(byte *)(param_1 + 4) << 0x1e)) {
    *(short *)(param_1 + 0x20) = (short)param_1[0x20] + 4;
    iVar5 = TT_Hint_Glyph(param_1,0);
  }
LAB_005eff2c:
  return CONCAT44(param_4,iVar5);
}

