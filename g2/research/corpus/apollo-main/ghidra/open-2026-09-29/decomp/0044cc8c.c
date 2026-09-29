
void FUN_0044cc8c(undefined4 *param_1)

{
  undefined1 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 *puVar4;
  
  param_1 = (undefined4 *)*param_1;
  uVar2 = FUN_0044b860(param_1[2]);
  uVar3 = FUN_0044bdea(*param_1,uVar2,*(undefined1 *)(param_1 + 1));
  param_1[3] = uVar3;
  uVar1 = *(undefined1 *)(param_1 + 1);
  *(undefined1 *)(param_1 + 1) = 0;
  FUN_0044ca18(*param_1,uVar2,uVar1,param_1);
  *(undefined1 *)(param_1 + 1) = uVar1;
  puVar4 = (undefined4 *)FUN_0044c72c(*param_1,param_1[2]);
  FUN_00482868(*puVar4,*(undefined1 *)(param_1 + 1),param_1[3]);
  FUN_0044bc8c(*param_1,param_1[2],*(undefined1 *)(param_1 + 1));
  return;
}

