
undefined8 FUN_0048f628(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int local_10;
  undefined4 uStack_c;
  
  local_10 = param_3;
  uStack_c = param_4;
  do {
    iVar1 = FUN_0048f3be(param_1,&local_10,1);
    if (iVar1 == 0) {
      uVar2 = 0;
      goto LAB_0048f64a;
    }
  } while (local_10 << 0x18 < 0);
  uVar2 = 1;
LAB_0048f64a:
  return CONCAT44(local_10,uVar2);
}

