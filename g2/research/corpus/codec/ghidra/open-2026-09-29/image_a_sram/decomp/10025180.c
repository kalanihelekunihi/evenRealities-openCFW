
uint gx8002_clock_gate_query_fixed(uint param_1)

{
  int iVar1;
  uint uVar2;
  int aiStack_20 [3];
  uint *puStack_14;
  
  iVar1 = __module_get_info(param_1,aiStack_20);
  if ((iVar1 == 0) && ((int)*(char *)(aiStack_20[0] + 5) != 0)) {
    if ((param_1 < 0x17) && ((1 << (param_1 & 0x3f) & 0x490000U) != 0)) {
      uVar2 = *puStack_14 >> ((int)*(char *)((param_1 + 1) * 0x10 + iRam100251e8 + 5) & 0x3fU) &
              *puStack_14 >> ((int)*(char *)((param_1 + 2) * 0x10 + iRam100251e8 + 5) & 0x3fU);
    }
    else {
      uVar2 = (int)*puStack_14 >> ((int)*(char *)(aiStack_20[0] + 5) & 0x3fU);
    }
    uVar2 = ~uVar2 & 1;
  }
  else {
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

