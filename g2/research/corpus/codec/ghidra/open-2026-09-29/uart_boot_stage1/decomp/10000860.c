
undefined4 gx8002_uart_stage1_raila(uint param_1,uint param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  int aiStack_24 [2];
  uint *puStack_1c;
  uint *puStack_18;
  int *piStack_14;
  int *piStack_10;
  
  if (param_1 < 0x1a) {
    if (param_2 == 2) {
      if (9 < param_1) {
        return 0xffffffff;
      }
      if ((1 << (param_1 & 0x3f) & 0x247U) == 0) {
        return 0xffffffff;
      }
    }
    else if (2 < (int)param_2) {
      if (param_1 == 7) {
        param_2 = (int)param_2 >> 2;
      }
      else {
        if (param_1 != 8) {
          return 0xffffffff;
        }
        param_2 = (int)param_2 / 6;
      }
    }
    iVar1 = gx8002_uart_stage1_pmu_fill_desc(param_1,aiStack_24);
    if (iVar1 == 0) {
      uVar2 = (uint)*(char *)(aiStack_24[0] + 6);
      if (uVar2 != 0xffffffff) {
        if (param_2 == 2) {
          uVar2 = (uint)(char)(*(char *)(aiStack_24[0] + 6) + '\x01');
          param_2 = 1;
        }
        if ((*puStack_1c >> (uVar2 & 0x3f) & 1) != param_2) {
          if ((param_1 < 0x17) && ((0U >> (param_1 & 0x3f) & 1) != 0)) {
            uVar3 = *puStack_18 >> ((int)*(char *)(iRam10000a2c + (param_1 + 1) * 0x10 + 5) & 0x3fU)
                    & *puStack_18 >>
                      ((int)*(char *)(iRam10000a2c + (param_1 + 2) * 0x10 + 5) & 0x3fU);
          }
          else {
            uVar3 = *puStack_18 >> ((int)*(char *)(aiStack_24[0] + 5) & 0x3fU);
          }
          if ((~uVar3 & 1) == 0) {
            *puStack_1c = (-2 << (uVar2 & 0x3f) | 0xfffffffeU >> 0x20 - (uVar2 & 0x3f)) &
                          *puStack_1c | param_2 << (uVar2 & 0x3f);
            return 0;
          }
          uVar3 = (uint)*(char *)(aiStack_24[0] + 4);
          if (param_1 - 7 < 2) {
            *puStack_1c = param_2 << (uVar2 & 0x3f) | *puStack_1c & ~(1 << (uVar2 & 0x3f));
            iVar1 = 1 << (uVar3 & 0x3f);
            *piStack_14 = iVar1;
            uVar3 = *puStack_18;
            uVar2 = *puStack_1c;
            if ((((uVar2 >> ((int)*(char *)(iRam10000a2c + 0x26) & 0x3fU) & 1) != 0) &&
                ((uVar3 >> ((int)*(char *)(iRam10000a2c + 0x25) & 0x3fU) & 1) != 0)) &&
               ((((uVar2 >> ((int)*(char *)(iRam10000a2c + 0x86) & 0x3fU) |
                  uVar3 >> ((int)*(char *)(iRam10000a2c + 0x85) & 0x3fU)) & 1) == 0 ||
                (((uVar2 >> ((int)*(char *)(iRam10000a2c + 0x76) & 0x3fU) |
                  uVar3 >> ((int)*(char *)(iRam10000a2c + 0x75) & 0x3fU)) & 1) == 0)))) {
              *piStack_10 = iVar1;
            }
          }
          else if (param_2 == 1) {
            *piStack_10 = 1 << (uVar3 & 0x3f);
            uVar2 = 1 << (uVar2 & 0x3f);
            *puStack_1c = uVar2 | *puStack_1c & ~uVar2;
          }
          else {
            *puStack_1c = param_2 << (uVar2 & 0x3f) | *puStack_1c & ~(1 << (uVar2 & 0x3f));
            *piStack_14 = 1 << (uVar3 & 0x3f);
          }
        }
        return 0;
      }
    }
  }
  return 0xffffffff;
}

