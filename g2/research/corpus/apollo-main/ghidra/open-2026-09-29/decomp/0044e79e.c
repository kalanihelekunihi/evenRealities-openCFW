
void FUN_0044e79e(undefined4 param_1,int param_2,int param_3,undefined1 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  if (param_3 != 0 || param_2 != 0) {
    FUN_0043f66c(param_1);
    iVar1 = FUN_0044e486(param_1);
    param_2 = param_2 - iVar1;
    iVar2 = FUN_0044e2a4(param_1,0);
    if (iVar2 == 1) {
      if (param_2 < 0) {
        param_2 = 0;
      }
      if (0 < param_2) {
        iVar2 = FUN_0044e586(param_1);
        iVar3 = FUN_0044e67a(param_1);
        iVar3 = iVar3 + iVar2;
        if (iVar3 < 0) {
          iVar3 = 0;
        }
        if (iVar3 < param_2) {
          param_2 = iVar3;
        }
      }
    }
    else {
      if (0 < param_2) {
        param_2 = 0;
      }
      if (param_2 < 0) {
        iVar2 = FUN_0044e586(param_1);
        iVar3 = FUN_0044e67a(param_1);
        iVar3 = iVar3 + iVar2;
        if (iVar3 < 0) {
          iVar3 = 0;
        }
        if (param_2 + iVar3 < 0 != SCARRY4(param_2,iVar3)) {
          param_2 = -iVar3;
        }
      }
    }
    iVar2 = FUN_0044e498(param_1);
    param_3 = param_3 - iVar2;
    if (0 < param_3) {
      param_3 = 0;
    }
    if (param_3 < 0) {
      iVar3 = FUN_0044e4aa(param_1);
      iVar4 = FUN_0044e4bc(param_1);
      iVar4 = iVar4 + iVar3;
      if (iVar4 < 0) {
        iVar4 = 0;
      }
      if (param_3 + iVar4 < 0 != SCARRY4(param_3,iVar4)) {
        param_3 = -iVar4;
      }
    }
    if (param_3 + iVar2 != 0 || param_2 + iVar1 != 0) {
      FUN_0044e884(param_1,param_2 + iVar1,param_3 + iVar2,param_4);
    }
  }
  return;
}

