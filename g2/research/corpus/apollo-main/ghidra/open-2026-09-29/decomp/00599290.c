
/* WARNING: Instruction at (ram,0x005992de) overlaps instruction at (ram,0x005992dc)
    */

void FUN_00599290(int param_1,int param_2,uint *param_3,undefined1 *param_4)

{
  undefined *puVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint *puVar6;
  int iVar7;
  int iVar8;
  
  iVar8 = 0;
  puVar6 = (uint *)(param_1 + param_2 * 4);
  while( true ) {
    puVar6 = puVar6 + -1;
    uVar2 = *puVar6;
    if (uVar2 != 0) break;
    if (0xe < iVar8) goto LAB_005992b6;
    iVar8 = iVar8 + 1;
  }
  if ((int)uVar2 < 0) {
    uVar4 = 1;
    uVar2 = -uVar2;
  }
  else {
LAB_005992b6:
    uVar4 = 0;
  }
  uVar5 = 0;
  iVar8 = iVar8 + 1;
  if (iVar8 < param_2) {
    do {
      puVar1 = PTR_LAB_005996e8;
      *param_3 = uVar5;
      puVar6 = puVar6 + -1;
      uVar3 = *puVar6;
      if (uVar3 != 0) {
        uVar5 = uVar4 | uVar5 << 1;
        uVar4 = uVar3 >> 0x1f;
      }
      if (uVar2 < 10) {
        iVar7 = uVar2 << 2;
      }
      else {
        iVar7 = 0x28;
      }
      *param_3 = uVar5;
      uVar5 = uVar5 + *(int *)(puVar1 + iVar7 + iVar8 * 0x2c);
      if ((int)uVar3 < 0) {
        uVar3 = -uVar3;
      }
      iVar8 = (param_2 - iVar8) + -1;
      loopEnd();
      param_3 = (uint *)(uVar3 >> 0x14);
      uVar2 = uVar3;
    } while( true );
  }
  *param_4 = (char)uVar4;
  *param_3 = 0;
  return;
}

