
undefined8
FUN_0053a590(undefined4 param_1,undefined1 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int local_10;
  undefined4 uStack_c;
  
  local_10 = 0;
  uStack_c = param_4;
  iVar1 = FUN_00480f8a(param_1,0,&local_10);
  if (iVar1 == 0) {
    if (local_10 == 1) {
      *param_2 = 1;
    }
    else {
      *param_2 = 0;
    }
    uVar2 = 0;
  }
  else {
    uVar2 = 0xffffffff;
  }
  return CONCAT44(local_10,uVar2);
}

