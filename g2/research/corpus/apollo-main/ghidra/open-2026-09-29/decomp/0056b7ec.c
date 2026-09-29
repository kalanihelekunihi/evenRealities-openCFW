
uint attcUuidCmp(undefined4 *param_1,undefined4 param_2,byte param_3)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  
  if ((*(byte *)(param_1 + 1) & 1) == param_3) {
    if (param_3 == 0) {
      uVar3 = 2;
    }
    else {
      uVar3 = 0x10;
    }
    iVar1 = FUN_004751c8(*param_1,param_2,uVar3);
    uVar2 = (uint)(iVar1 == 0);
  }
  else if ((param_3 == 1) && (-1 < (int)((uint)*(byte *)(param_1 + 1) << 0x1f))) {
    uVar2 = attUuidCmp16to128(*param_1);
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

