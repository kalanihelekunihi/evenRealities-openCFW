
undefined4 FUN_004502e0(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  
  uVar1 = FUN_0044ffcc(param_1);
  iVar5 = 0;
  for (uVar6 = 0; uVar6 < uVar1; uVar6 = uVar6 + 1) {
    puVar2 = (undefined4 *)FUN_00488578(param_1,uVar6);
    puVar3 = (undefined4 *)FUN_00488578(param_1,iVar5);
    iVar4 = FUN_0045037e(*puVar2);
    if (iVar4 == 0) {
      *puVar3 = *puVar2;
      iVar5 = iVar5 + 1;
    }
    else {
      FUN_0044f758(*puVar2);
    }
  }
  if (iVar5 == 0) {
    FUN_00488478(param_1);
  }
  else {
    FUN_0048849c(param_1,iVar5);
  }
  return param_4;
}

