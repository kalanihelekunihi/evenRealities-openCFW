
void FUN_004c3500(uint param_1,char param_2)

{
  undefined4 *puVar1;
  
  puVar1 = DAT_004c36fc;
  if (param_1 == 0) {
    if (param_2 == '\0') goto LAB_004c35d6;
    if (param_2 == '\x01') {
      return;
    }
    if (param_2 != '\x04') {
      if (param_2 == '\x05') {
        return;
      }
      if (param_2 != '\x06') {
        if (param_2 == '\a') {
          return;
        }
        if (param_2 != '\b') {
          if (param_2 == '\t') {
            return;
          }
          if (param_2 != '\n') {
            if (param_2 == '\v') {
              return;
            }
            if (param_2 != '\x10') {
              if (param_2 == '\x11') {
                return;
              }
              if (param_2 != '\x12') {
                return;
              }
            }
            goto LAB_004c35c2;
          }
          FUN_00480f0c(0x25,*DAT_004c36fc);
          FUN_00480f0c(0x26,*puVar1);
          FUN_00480f0c(0x27,*puVar1);
          FUN_00480f0c(0x28,*puVar1);
          FUN_00480f0c(0x29,*puVar1);
          FUN_00480f0c(0x2a,*puVar1);
          FUN_00480f0c(0x2b,*puVar1);
          FUN_00480f0c(0x2c,*puVar1);
          FUN_00480f0c(0x2d,*puVar1);
        }
      }
      puVar1 = DAT_004c36fc;
      FUN_00480f0c(0x44,*DAT_004c36fc);
      FUN_00480f0c(0x45,*puVar1);
      FUN_00480f0c(0x46,*puVar1);
      FUN_00480f0c(0x47,*puVar1);
    }
LAB_004c35c2:
    puVar1 = DAT_004c36fc;
    FUN_00480f0c(0x42,*DAT_004c36fc);
    FUN_00480f0c(0x43,*puVar1);
LAB_004c35d6:
    puVar1 = DAT_004c36fc;
    FUN_00480f0c(199,*DAT_004c36fc);
    FUN_00480f0c(0x40,*puVar1);
    FUN_00480f0c(0x41,*puVar1);
    FUN_00480f0c(0x48,*puVar1);
    FUN_00480f0c(0x49,*puVar1);
    return;
  }
  if (param_1 == 2) {
    return;
  }
  if (1 < param_1) {
    return;
  }
  if (param_2 == '\0') goto LAB_004c366e;
  if (param_2 == '\x01') {
    return;
  }
  if (param_2 != '\x04') {
    if (param_2 == '\x05') {
      return;
    }
    if (param_2 != '\x06') {
      if (param_2 == '\a') {
        return;
      }
      if (param_2 != '\b') {
        if (param_2 == '\t') {
          return;
        }
        if (param_2 != '\x10') {
          if (param_2 == '\x11') {
            return;
          }
          if (param_2 != '\x12') {
            return;
          }
        }
        goto LAB_004c365c;
      }
    }
    FUN_00480f0c(99,*DAT_004c36fc);
    FUN_00480f0c(100,*puVar1);
    FUN_00480f0c(0x65,*puVar1);
    FUN_00480f0c(0x66,*puVar1);
  }
LAB_004c365c:
  puVar1 = DAT_004c36fc;
  FUN_00480f0c(0x61,*DAT_004c36fc);
  FUN_00480f0c(0x62,*puVar1);
LAB_004c366e:
  puVar1 = DAT_004c36fc;
  FUN_00480f0c(0x31,*DAT_004c36fc);
  FUN_00480f0c(0x5f,*puVar1);
  FUN_00480f0c(0x60,*puVar1);
  FUN_00480f0c(0x67,*puVar1);
  FUN_00480f0c(0x68,*puVar1);
  return;
}

