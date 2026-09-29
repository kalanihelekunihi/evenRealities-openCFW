
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0057eaa8(undefined1 *param_1,undefined4 param_2)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  undefined1 auStack_510 [254];
  undefined1 uStack_412;
  int aiStack_410 [255];
  
  iVar5 = 0;
  if (*_DAT_0057f270 == 1) {
    FUN_0044b5a0(auStack_510,param_2,0xff);
    uStack_412 = 0;
    iVar2 = func_0x00594884(auStack_510,0x57eb8c);
    while ((iVar2 != 0 && (iVar5 < 0xff))) {
      iVar3 = FUN_0044a43c(iVar2);
      if (iVar3 == 0) {
        iVar2 = func_0x00594884(0,0x57eb8c);
      }
      else {
        iVar3 = FUN_0046cacc(iVar2,0x57eb84);
        if (iVar3 != 0) {
          iVar3 = FUN_0046cacc(iVar2,0x57eb88);
          if (iVar3 == 0) {
            if (0 < iVar5) {
              iVar5 = iVar5 + -1;
            }
          }
          else {
            aiStack_410[iVar5] = iVar2;
            iVar5 = iVar5 + 1;
          }
        }
        iVar2 = func_0x00594884(0,0x57eb8c);
      }
    }
    *param_1 = 0;
    FUN_00567c80(param_1,0x57eb8c);
    for (iVar2 = 0; iVar2 < iVar5; iVar2 = iVar2 + 1) {
      FUN_00567c80(param_1,aiStack_410[iVar2]);
      if (iVar2 != iVar5 + -1) {
        FUN_00567c80(param_1,0x57eb8c);
      }
    }
    if (iVar5 == 0) {
      FUN_0048d540(param_1,0x57eb8c);
    }
    uVar4 = FUN_0044a43c(param_1);
    if (uVar4 < 0xff) {
      uVar1 = 0;
    }
    else {
      uVar1 = 0xffffffff;
    }
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

