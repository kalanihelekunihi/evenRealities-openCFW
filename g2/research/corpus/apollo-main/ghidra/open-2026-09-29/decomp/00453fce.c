
undefined4 FUN_00453fce(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  
  if (param_2 == 0) {
    param_2 = FUN_0044fc62(*(undefined4 *)(DAT_00454168 + 0x10));
  }
  if (param_2 != 0) {
    iVar2 = FUN_0044dca2(param_2);
    if (iVar2 != 0) {
      uVar3 = FUN_0044c582(iVar2,0);
      *(undefined4 *)(param_1 + 0x39) = uVar3;
    }
    FUN_004541b6(param_1,param_2);
    while (iVar5 = iVar2, iVar5 != 0) {
      bVar1 = false;
      uVar4 = FUN_0044ddea(iVar5);
      for (uVar6 = 0; uVar6 < uVar4; uVar6 = uVar6 + 1) {
        if (bVar1) {
          FUN_004541b6(param_1);
        }
        else if (*(int *)(**(int **)(iVar5 + 8) + uVar6 * 4) == param_2) {
          bVar1 = true;
        }
      }
      FUN_00451670(iVar5,0x1f,param_1);
      FUN_00451670(iVar5,0x20,param_1);
      FUN_00451670(iVar5,0x21,param_1);
      iVar2 = FUN_0044dca2(iVar5);
      param_2 = iVar5;
    }
  }
  return param_4;
}

