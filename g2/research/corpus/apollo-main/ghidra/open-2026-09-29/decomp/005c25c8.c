
ushort FUN_005c25c8(ushort param_1)

{
  ushort uVar1;
  
  uVar1 = param_1 & 0xf;
  if ((param_1 & 0xf) == 0) {
    uVar1 = 1;
  }
  return uVar1;
}

