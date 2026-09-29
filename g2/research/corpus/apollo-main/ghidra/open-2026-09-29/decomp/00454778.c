
uint FUN_00454778(int param_1,undefined4 param_2,uint param_3)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = FUN_0044a43c(param_2);
  if (param_3 != 0) {
    uVar2 = uVar1;
    if (param_3 <= uVar1) {
      uVar2 = param_3 - 1;
    }
    FUN_00439be4(param_1,param_2,uVar2);
    *(undefined1 *)(param_1 + uVar2) = 0;
  }
  return uVar1;
}

