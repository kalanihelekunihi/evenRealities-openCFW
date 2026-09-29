
char FUN_0054449a(undefined4 param_1,undefined4 param_2,int param_3)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  
  uVar2 = FUN_0044a43c(param_2);
  iVar3 = FUN_00543e28(param_1,param_2,uVar2,param_3 + 0x50);
  if (iVar3 == 0) {
    cVar1 = FUN_0054447a(param_1,param_2,param_3);
    if (cVar1 != '\0') {
      FUN_00543d1c(param_1,param_2,uVar2,*(undefined4 *)(param_3 + 0x50));
    }
  }
  else {
    FUN_00544000(param_1,param_3);
    cVar1 = '\x01';
  }
  return cVar1;
}

