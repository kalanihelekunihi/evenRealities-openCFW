
undefined4 gx8002_clock_module_source_fixed(uint param_1,uint param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  int aiStack_2c [2];
  uint *puStack_24;
  uint *puStack_20;
  int *piStack_1c;
  int *piStack_18;
  
  if (0x19 < param_1) {
    return 0xffffffff;
  }
  if (param_2 == 2) {
    if (9 < param_1) {
      return 0xffffffff;
    }
    uVar3 = 1;
    if ((1 << (param_1 & 0x3f) & 0x247U) == 0) {
      return 0xffffffff;
    }
  }
  else {
    if (2 < (int)param_2) {
      if (param_1 != 7) {
        if (param_1 != 8) {
          return 0xffffffff;
        }
        param_2 = param_2 - 5;
        uVar3 = 3;
        goto LAB_10024c0c;
      }
      param_2 = (int)param_2 >> 2;
    }
    uVar3 = 1;
  }
LAB_10024c0c:
  iVar1 = __module_get_info(param_1,aiStack_2c);
  if (iVar1 == 0) {
    uVar2 = (uint)*(char *)(aiStack_2c[0] + 6);
    if (uVar2 != 0xffffffff) {
      if ((param_2 == 2) && (param_1 != 8)) {
        uVar2 = (uint)(char)(*(char *)(aiStack_2c[0] + 6) + '\x01');
        param_2 = 1;
      }
      if ((*puStack_24 >> (uVar2 & 0x3f) & uVar3) == param_2) {
        return 0;
      }
      if (param_1 < 0x17) {
        uVar3 = ~(0x490000U >> (param_1 & 0x3f));
      }
      else {
        uVar3 = 1;
      }
      if ((uVar3 & 1) == 0) {
        uVar3 = *puStack_20 >> ((int)*(char *)(iRam10024d6c + (param_1 + 1) * 0x10 + 5) & 0x3fU) &
                *puStack_20 >> ((int)*(char *)(iRam10024d6c + (param_1 + 2) * 0x10 + 5) & 0x3fU);
      }
      else {
        uVar3 = *puStack_20 >> ((int)*(char *)(aiStack_2c[0] + 5) & 0x3fU);
      }
      if ((~uVar3 & 1) != 0) {
        uVar3 = (uint)*(char *)(aiStack_2c[0] + 4);
        if (param_1 - 7 < 2) {
          __reg_set_val(puStack_24);
          iVar1 = 1 << (uVar3 & 0x3f);
          *piStack_1c = iVar1;
          uVar3 = *puStack_20;
          uVar2 = *puStack_24;
          if ((uVar2 >> ((int)*(char *)(iRam10024d6c + 0x26) & 0x3fU) & 1) == 0) {
            return 0;
          }
          if ((uVar3 >> ((int)*(char *)(iRam10024d6c + 0x25) & 0x3fU) & 1) != 0) {
            if ((((uVar2 >> ((int)*(char *)(iRam10024d6c + 0x86) & 0x3fU) & 3) != 0) ||
                ((uVar3 >> ((int)*(char *)(iRam10024d6c + 0x85) & 0x3fU) & 1) != 0)) &&
               (((uVar2 >> ((int)*(char *)(iRam10024d6c + 0x76) & 0x3fU) |
                 uVar3 >> ((int)*(char *)(iRam10024d6c + 0x75) & 0x3fU)) & 1) != 0)) {
              return 0;
            }
            *piStack_18 = iVar1;
            return 0;
          }
          return 0;
        }
        if (param_2 != 1) {
          __reg_set_val(puStack_24);
          *piStack_1c = 1 << (uVar3 & 0x3f);
          return 0;
        }
        *piStack_18 = 1 << (uVar3 & 0x3f);
      }
      __reg_set_val(puStack_24);
      return 0;
    }
  }
  return 0xffffffff;
}

