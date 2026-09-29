
uint gx8002_clock_module_query(uint param_1)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  int aiStack_20 [2];
  uint *puStack_18;
  
  iVar1 = __module_get_info(param_1,aiStack_20);
  uVar3 = 0xffffffff;
  if (iVar1 == 0) {
    uVar3 = (uint)*(char *)(aiStack_20[0] + 6);
    if (uVar3 == 0xffffffff) {
      uVar3 = 0xffffffff;
    }
    else {
      uVar2 = 0;
      if ((param_1 < 10) && ((1 << (param_1 & 0x3f) & 0x243U) != 0)) {
        uVar2 = uVar3 + 1;
      }
      if ((uVar2 == 0) || ((*puStack_18 >> (uVar2 & 0x3f) & 1) == 0)) {
        uVar3 = *puStack_18 >> (uVar3 & 0x3f) & 1;
        if (param_1 == 7) {
          uVar3 = (uVar3 != 0) + 3;
        }
        else if (param_1 == 8) {
          uVar3 = (uVar3 != 0) + 5;
        }
      }
      else if (param_1 == 7) {
        uVar3 = 4;
      }
      else {
        uVar3 = 6;
        if (param_1 != 8) {
          uVar3 = 2;
        }
      }
    }
  }
  return uVar3;
}

