
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 hub_calibration_success_display(void)

{
  int *piVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 in_r3;
  
  uVar3 = _DAT_004a7774;
  piVar1 = _DAT_004a7754;
  if (*_DAT_004a7754 != 0) {
    uVar2 = FUN_00460084(_DAT_004a7774);
    uVar3 = FUN_0045fffe(uVar3,uVar2);
    FUN_0049942e(*piVar1,uVar3);
  }
  uVar3 = _DAT_004a7778;
  piVar1 = _DAT_004a7760;
  if (*_DAT_004a7760 != 0) {
    uVar2 = FUN_00460084(_DAT_004a7778);
    uVar3 = FUN_0045fffe(uVar3,uVar2);
    FUN_0049942e(*piVar1,uVar3);
    FUN_0043f506(*piVar1,0x3fffffff);
    FUN_0043f66c(*piVar1);
    iVar4 = FUN_0043fd9e(*piVar1);
    FUN_0043f0e0(*piVar1,(0x240 - iVar4) / 2);
  }
  return in_r3;
}

