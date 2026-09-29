
undefined4 FUN_0044c9dc(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  undefined4 uVar3;
  
  uVar1 = FUN_0044ddea(param_1);
  for (uVar2 = 0; uVar2 < uVar1; uVar2 = uVar2 + 1) {
    uVar3 = *(undefined4 *)(**(int **)(param_1 + 8) + uVar2 * 4);
    FUN_00440656(uVar3);
    FUN_00451670(uVar3,0x32,0);
    FUN_00440656(uVar3);
    FUN_0044c9dc(uVar3);
  }
  return param_4;
}

