
undefined4 FUN_004c32b4(uint param_1,char param_2)

{
  undefined4 unaff_r7;
  
  if (param_1 == 0) {
    if (param_2 == '\0') goto LAB_004c33c4;
    if (param_2 == '\x01') {
      return unaff_r7;
    }
    if (param_2 != '\x04') {
      if (param_2 == '\x05') {
        return unaff_r7;
      }
      if (param_2 != '\x06') {
        if (param_2 == '\a') {
          return unaff_r7;
        }
        if (param_2 != '\b') {
          if (param_2 == '\t') {
            return unaff_r7;
          }
          if (param_2 != '\n') {
            if (param_2 == '\v') {
              return unaff_r7;
            }
            if (param_2 != '\x10') {
              if (param_2 == '\x11') {
                return unaff_r7;
              }
              if (param_2 != '\x12') {
                return unaff_r7;
              }
            }
            goto LAB_004c33ac;
          }
          FUN_00480f0c(0x25,*DAT_004c3700);
          FUN_00480f0c(0x26,*DAT_004c3704);
          FUN_00480f0c(0x27,*DAT_004c3708);
          FUN_00480f0c(0x28,*DAT_004c370c);
          FUN_00480f0c(0x29,*DAT_004c3710);
          FUN_00480f0c(0x2a,*DAT_004c3714);
          FUN_00480f0c(0x2b,*DAT_004c3718);
          FUN_00480f0c(0x2c,*DAT_004c371c);
          FUN_00480f0c(0x2d,*DAT_004c3720);
        }
      }
      FUN_00480f0c(0x44,*DAT_004c3724);
      FUN_00480f0c(0x45,*DAT_004c3728);
      FUN_00480f0c(0x46,*DAT_004c372c);
      FUN_00480f0c(0x47,*DAT_004c3730);
    }
LAB_004c33ac:
    FUN_00480f0c(0x42,*DAT_004c36d8);
    FUN_00480f0c(0x43,*DAT_004c36d4);
LAB_004c33c4:
    FUN_00480f0c(199,*DAT_004c36e4);
    FUN_00480f0c(0x40,*DAT_004c36e0);
    FUN_00480f0c(0x41,*DAT_004c36dc);
    FUN_00480f0c(0x48,*DAT_004c3734);
    return unaff_r7;
  }
  if (param_1 == 2) {
    return unaff_r7;
  }
  if (1 < param_1) {
    return unaff_r7;
  }
  if (param_2 == '\0') goto LAB_004c3486;
  if (param_2 == '\x01') {
    return unaff_r7;
  }
  if (param_2 == '\x04') goto LAB_004c346e;
  if (param_2 == '\x05') {
    return unaff_r7;
  }
  if (param_2 == '\x06') {
LAB_004c343e:
    FUN_00480f0c(99,*DAT_004c3738);
    FUN_00480f0c(100,*DAT_004c373c);
    FUN_00480f0c(0x65,*DAT_004c3740);
    FUN_00480f0c(0x66,*DAT_004c3744);
  }
  else {
    if (param_2 == '\a') {
      return unaff_r7;
    }
    if (param_2 == '\b') goto LAB_004c343e;
    if (param_2 == '\t') {
      return unaff_r7;
    }
    if (param_2 != '\x10') {
      if (param_2 == '\x11') {
        return unaff_r7;
      }
      if (param_2 != '\x12') {
        if (param_2 == '\x13') {
          return unaff_r7;
        }
        if (param_2 != '\x16') {
          if (param_2 == '\x17') {
            return unaff_r7;
          }
          if (param_2 != '\x18') {
            return unaff_r7;
          }
        }
        goto LAB_004c343e;
      }
    }
  }
LAB_004c346e:
  FUN_00480f0c(0x61,*DAT_004c36ec);
  FUN_00480f0c(0x62,*DAT_004c36e8);
LAB_004c3486:
  FUN_00480f0c(0x31,*DAT_004c36f8);
  FUN_00480f0c(0x5f,*DAT_004c36f4);
  FUN_00480f0c(0x60,*DAT_004c36f0);
  FUN_00480f0c(0x67,*DAT_004c3748);
  FUN_00480f0c(0x68,*DAT_004c374c);
  return unaff_r7;
}

