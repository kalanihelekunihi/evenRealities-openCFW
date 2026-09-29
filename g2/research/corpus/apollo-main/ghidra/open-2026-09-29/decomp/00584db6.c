
uint FUN_00584db6(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  if (*DAT_00584e48 == 0) {
    uVar1 = 1;
  }
  else {
    uVar2 = FUN_0058dbb8(*DAT_00584e48,0,1);
    uVar3 = FUN_00480f0c(2,*DAT_00584e7c);
    uVar1 = FUN_00480f0c(0,*DAT_00584e78);
    uVar1 = uVar2 | uVar3 | uVar1;
    *DAT_00584e4c = 1;
  }
  return uVar1;
}

