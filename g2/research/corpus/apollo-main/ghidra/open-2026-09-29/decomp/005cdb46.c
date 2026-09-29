
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4
FUN_005cdb46(undefined4 param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  cVar1 = FUN_004516f8(_DAT_005cdb80,param_2);
  if (cVar1 == '\x01') {
    iVar2 = FUN_00450286(param_2);
    uVar3 = *param_2;
    if (iVar2 == 0x31) {
      uVar4 = FUN_005cda66(uVar3);
      FUN_005cd7cc(uVar3,uVar4,0);
    }
  }
  return param_4;
}

