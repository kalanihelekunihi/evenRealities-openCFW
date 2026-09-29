
undefined4 FUN_005e1f44(int param_1)

{
  undefined4 uVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  int *piVar9;
  int *piVar10;
  int iVar11;
  int local_40a4;
  undefined4 local_40a0;
  undefined1 auStack_4024 [16384];
  
  iVar11 = *(int *)(param_1 + 0x90);
  iVar6 = *(int *)(param_1 + 0x94);
  uVar1 = *(undefined4 *)(param_1 + 0x88);
  iVar7 = *(int *)(param_1 + 0x8c);
  uVar8 = iVar6 - iVar11;
  if (0x80 < uVar8) {
    uVar2 = (uVar8 + 0x7f) / 0x80;
    uVar8 = ((uVar2 + uVar8) - 1) / uVar2;
  }
  uVar2 = uVar8 * 4 + 0xf >> 4;
  *(undefined1 **)(param_1 + 0xa8) = auStack_4024 + uVar2 * 0x10;
  *(uint *)(param_1 + 0xac) = 0x400 - uVar2;
  *(undefined1 **)(param_1 + 0xa4) = auStack_4024;
  do {
    if (iVar6 <= iVar11) {
      return 0;
    }
    *(int *)(param_1 + 0x90) = iVar11;
    iVar11 = uVar8 + iVar11;
    iVar3 = iVar6;
    if (iVar11 < iVar6) {
      iVar3 = iVar11;
    }
    *(int *)(param_1 + 0x94) = iVar3;
    local_40a0 = uVar1;
    local_40a4 = iVar7;
    piVar9 = &local_40a4;
    do {
      iVar5 = *piVar9;
      iVar3 = piVar9[1];
      FUN_0043c0e4(*(undefined4 *)(param_1 + 0xa4),uVar8 << 2,0);
      *(undefined4 *)(param_1 + 0xb0) = 0;
      *(undefined4 *)(param_1 + 0xa0) = 1;
      *(int *)(param_1 + 0x88) = piVar9[1];
      *(int *)(param_1 + 0x8c) = *piVar9;
      iVar4 = FUN_005e1f0a(param_1);
      if (iVar4 == 0) {
        FUN_005e1e7e(param_1);
        piVar10 = piVar9 + -1;
      }
      else {
        if (iVar4 != 0x40) {
          return 1;
        }
        iVar3 = iVar5 - iVar3 >> 1;
        if (iVar3 == 0) {
          return 1;
        }
        piVar10 = piVar9 + 1;
        piVar9[2] = *piVar10;
        *piVar10 = iVar3 + *piVar10;
      }
      piVar9 = piVar10;
    } while (&local_40a4 <= piVar10);
  } while( true );
}

