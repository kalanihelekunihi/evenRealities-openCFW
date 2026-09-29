
undefined8 FUN_0041b918(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  
  piVar1 = DAT_0041c314;
  if ((*DAT_0041c314 == -1) &&
     ((iVar2 = FUN_00421548(1,0x244,1,DAT_0041c314), *piVar1 == 0 || (iVar2 != 0)))) {
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

