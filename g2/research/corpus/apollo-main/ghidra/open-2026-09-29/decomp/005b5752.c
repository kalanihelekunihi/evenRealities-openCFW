
undefined8 FUN_005b5752(int param_1,short *param_2)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  if (((*(int *)(param_1 + 0x84) == -1) || (param_2 == (short *)0x0)) || (*param_2 == 0)) {
    uVar1 = 0;
  }
  else {
    iVar2 = FUN_005897e0();
    if (iVar2 == 0) {
      uVar1 = 1;
    }
    else {
      uVar1 = 0;
    }
  }
  return CONCAT44(unaff_r7,uVar1);
}

