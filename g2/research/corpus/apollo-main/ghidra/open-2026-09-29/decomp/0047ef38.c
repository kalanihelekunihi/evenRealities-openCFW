
undefined8 FUN_0047ef38(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  
  piVar1 = DAT_0047f948;
  if ((*DAT_0047f948 == -1) &&
     ((iVar2 = FUN_004d3f3c(1,0x244,1,DAT_0047f948), *piVar1 == 0 || (iVar2 != 0)))) {
    *piVar1 = 0;
  }
  if (param_1 == (int *)0x0) {
    uVar3 = 6;
  }
  else {
    *param_1 = *piVar1;
    uVar3 = 0;
  }
  return CONCAT44(param_4,uVar3);
}

