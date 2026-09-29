
undefined4 FUN_0048297c(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uStack_18;
  undefined4 local_14;
  undefined4 local_10;
  undefined4 uStack_c;
  
  uStack_18 = param_1;
  local_14 = param_2;
  local_10 = param_3;
  uStack_c = param_4;
  FUN_0043bb00(&uStack_18,0,3);
  local_10 = *DAT_00482ad8;
  param_1 = param_1 & 0xff;
  if ((param_1 == 5) || (param_1 == 7)) {
    return *DAT_00482af0;
  }
  if (param_1 == 0x1c) {
    FUN_00439be4(&local_14,&local_10,3);
    return local_14;
  }
  if (param_1 == 0x22) {
    return *DAT_00482ae4;
  }
  if (param_1 == 0x23) {
LAB_00482a20:
    FUN_00439be4(&local_14,&uStack_18,3);
  }
  else {
    if (((param_1 != 0x24) && (param_1 != 0x25)) && (param_1 != 0x29)) {
      if (param_1 == 0x31) goto LAB_00482a20;
      if (param_1 != 0x32) {
        if (param_1 == 0x34) {
          return *DAT_00482ae8;
        }
        if (param_1 == 0x39) goto LAB_00482a20;
        if (param_1 != 0x3a) {
          if (param_1 == 0x3d) goto LAB_00482a20;
          if ((param_1 != 0x3e) && (param_1 != 0x44)) {
            if ((param_1 == 0x45) || (param_1 == 0x4c)) goto LAB_00482a20;
            if (param_1 != 0x4d) {
              if (param_1 == 0x52) goto LAB_00482a20;
              if (param_1 != 0x53) {
                if (param_1 == 0x58) goto LAB_00482a20;
                if (param_1 != 0x59) {
                  if (param_1 == 0x5a) {
                    return *DAT_00482aec;
                  }
                  if ((param_1 != 0x62) && (param_1 != 99)) {
                    if ((param_1 == 0x6e) || (param_1 == 0x6f)) {
                      return *DAT_00482adc;
                    }
                    if (param_1 == 0x76) {
                      return *DAT_00482af4;
                    }
                    if (param_1 != 0x78) {
                      return *DAT_00482af8;
                    }
                    goto LAB_00482a20;
                  }
                }
              }
            }
          }
        }
      }
    }
    local_14 = *DAT_00482ae0;
  }
  return local_14;
}

