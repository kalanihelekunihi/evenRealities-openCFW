
undefined8 FUN_0048f7ca(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  if ((*(int *)(param_2 + 8) == 0) ||
     (iVar1 = FUN_0048f3be(param_2,0,*(undefined4 *)(param_2 + 8)), iVar1 != 0)) {
    *(undefined4 *)(param_1 + 4) = *(undefined4 *)(param_2 + 4);
    *(undefined4 *)(param_1 + 0xc) = *(undefined4 *)(param_2 + 0xc);
    uVar2 = 1;
  }
  else {
    uVar2 = 0;
  }
  return CONCAT44(param_4,uVar2);
}

