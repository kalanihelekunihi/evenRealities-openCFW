
undefined4 FUN_0044f316(undefined4 param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = FUN_0044e470(param_1);
  if (iVar1 == 0) {
    iVar1 = FUN_0044e4aa(param_1);
    iVar2 = FUN_0044e4bc(param_1);
    if ((iVar2 < 0) && (0 < iVar1)) {
      if (iVar1 + iVar2 < 0 == SCARRY4(iVar1,iVar2)) {
        iVar1 = -iVar2;
      }
      FUN_0044e884(param_1,0,iVar1,param_2);
    }
  }
  iVar1 = FUN_0044e45a(param_1);
  if (iVar1 == 0) {
    iVar1 = FUN_0044e586(param_1);
    iVar2 = FUN_0044e67a(param_1);
    iVar3 = FUN_0044e2a4(param_1,0);
    if (iVar3 == 1) {
      if ((iVar1 < 0) && (0 < iVar2)) {
        FUN_0044e884(param_1,iVar1,0,param_2);
      }
    }
    else if ((iVar2 < 0) && (0 < iVar1)) {
      if (iVar1 + iVar2 < 0 == SCARRY4(iVar1,iVar2)) {
        iVar1 = -iVar2;
      }
      FUN_0044e884(param_1,iVar1,0,param_2);
    }
  }
  return param_4;
}

