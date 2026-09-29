
undefined4 FUN_005d843a(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 *puVar5;
  undefined4 uVar6;
  
  param_1 = param_1 + param_2 * 0xcc;
  iVar4 = *(int *)(param_1 + 4);
  uVar6 = *(undefined4 *)(param_1 + 200);
  if (iVar4 != 0) {
    uVar1 = FT_MulFix(*(undefined4 *)(param_1 + 8),uVar6);
    *(undefined4 *)(param_1 + 0xc) = uVar1;
    *(uint *)(param_1 + 0x10) = *(int *)(param_1 + 0xc) + 0x20U & 0xffffffc0;
    puVar5 = (undefined4 *)(param_1 + 0x14);
    while (iVar4 = iVar4 + -1, iVar4 != 0) {
      iVar2 = FT_MulFix(*puVar5,uVar6);
      iVar3 = iVar2 - *(int *)(param_1 + 0xc);
      if (iVar3 < 0) {
        iVar3 = -iVar3;
      }
      if (iVar3 < 0x80) {
        iVar2 = *(int *)(param_1 + 0xc);
      }
      puVar5[1] = iVar2;
      puVar5[2] = iVar2 + 0x20U & 0xffffffc0;
      puVar5 = puVar5 + 3;
    }
  }
  return param_4;
}

