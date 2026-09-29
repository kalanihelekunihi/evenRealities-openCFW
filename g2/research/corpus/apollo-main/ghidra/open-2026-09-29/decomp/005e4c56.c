
undefined8 FUN_005e4c56(int param_1,int param_2,undefined4 *param_3)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  if (((param_1 == 0) || (*(int *)(param_1 + 0x214) == 0)) || (param_3 == (undefined4 *)0x0)) {
    uVar1 = 0;
  }
  else {
    if (param_2 == 0x44) {
      iVar2 = -param_3[1];
    }
    else {
      iVar2 = param_3[1];
    }
    uVar1 = FUN_005e4b68(*(undefined4 *)(param_1 + 0x214),iVar2,*param_3);
  }
  return CONCAT44(unaff_r7,uVar1);
}

