
undefined8 FUN_00584df4(void)

{
  int *piVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  undefined4 in_r3;
  
  piVar1 = DAT_00584e48;
  if (*DAT_00584e48 == 0) {
    uVar2 = 1;
  }
  else {
    *DAT_00584e4c = 0;
    uVar3 = FUN_00480f0c(2,*DAT_00584e8c);
    uVar4 = FUN_00480f0c(0,*DAT_00584e90);
    uVar2 = FUN_0058dbb8(*piVar1,2,1);
    uVar2 = uVar3 | uVar4 | uVar2;
  }
  return CONCAT44(in_r3,uVar2);
}

