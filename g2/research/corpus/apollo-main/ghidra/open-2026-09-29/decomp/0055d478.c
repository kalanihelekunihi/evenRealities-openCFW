
uint FUN_0055d478(undefined4 param_1,byte *param_2,byte *param_3,undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  undefined4 local_18;
  undefined4 uStack_14;
  
  uVar2 = 0;
  local_18 = (uint)param_3 & 0xffff0000;
  if ((param_2 == (byte *)0x0) || (param_3 == (byte *)0x0)) {
    if (param_2 == (byte *)0x0) {
      if (param_3 == (byte *)0x0) {
        return 0xfffffff5;
      }
      if (4 < *param_3) {
        return 0xfffffff5;
      }
    }
    else if (4 < *param_2) {
      return 0xfffffff5;
    }
  }
  else if (4 < (uint)*param_3 + (uint)*param_2) {
    return 0xfffffff5;
  }
  uStack_14 = param_4;
  if (param_2 != (byte *)0x0) {
    uVar2 = FUN_0055d2c2(param_1,0,param_3 == (byte *)0x0,(int)&local_18 + 1,&local_18,param_2);
  }
  if (param_3 != (byte *)0x0) {
    uVar1 = FUN_0055d2c2(param_1,1,1,(int)&local_18 + 1,&local_18,param_3);
    uVar2 = uVar2 | uVar1;
  }
  return uVar2;
}

