
undefined4 FUN_0047a85c(void)

{
  int *piVar1;
  undefined4 in_r3;
  int iVar2;
  byte bVar3;
  
  piVar1 = DAT_0047b4b0;
  iVar2 = *DAT_0047b4b0;
  FUN_00475014(0,1);
  FUN_004795dc(*piVar1);
  FUN_00479418();
  for (bVar3 = 0; bVar3 < 10; bVar3 = bVar3 + 1) {
    FUN_004789b0(iVar2,bVar3);
    iVar2 = iVar2 + 200;
  }
  return in_r3;
}

