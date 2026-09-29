
undefined4 FUN_0041fadc(uint param_1,char param_2)

{
  undefined4 unaff_r7;
  
  if (param_1 == 0) {
    if (param_2 == '\0') goto LAB_0041fbec;
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
            goto LAB_0041fbd4;
          }
          FUN_0041d92c(0x25,*DAT_0041fd20);
          FUN_0041d92c(0x26,*DAT_0041fd24);
          FUN_0041d92c(0x27,*DAT_0041fd28);
          FUN_0041d92c(0x28,*DAT_0041fd2c);
          FUN_0041d92c(0x29,*DAT_0041fd30);
          FUN_0041d92c(0x2a,*DAT_0041fd34);
          FUN_0041d92c(0x2b,*DAT_0041fd38);
          FUN_0041d92c(0x2c,*DAT_0041fd3c);
          FUN_0041d92c(0x2d,*DAT_0041fd40);
        }
      }
      FUN_0041d92c(0x44,*DAT_0041fd44);
      FUN_0041d92c(0x45,*DAT_0041fd48);
      FUN_0041d92c(0x46,*DAT_0041fd4c);
      FUN_0041d92c(0x47,*DAT_0041fd50);
    }
LAB_0041fbd4:
    FUN_0041d92c(0x42,*DAT_0041fcfc);
    FUN_0041d92c(0x43,*DAT_0041fcf8);
LAB_0041fbec:
    FUN_0041d92c(199,*DAT_0041fd08);
    FUN_0041d92c(0x40,*DAT_0041fd04);
    FUN_0041d92c(0x41,*DAT_0041fd00);
    FUN_0041d92c(0x48,*DAT_0041fd54);
    return unaff_r7;
  }
  if (param_1 == 2) {
    return unaff_r7;
  }
  if (1 < param_1) {
    return unaff_r7;
  }
  if (param_2 == '\0') goto LAB_0041fcae;
  if (param_2 == '\x01') {
    return unaff_r7;
  }
  if (param_2 == '\x04') goto LAB_0041fc96;
  if (param_2 == '\x05') {
    return unaff_r7;
  }
  if (param_2 == '\x06') {
LAB_0041fc66:
    FUN_0041d92c(99,*DAT_0041fd58);
    FUN_0041d92c(100,*DAT_0041fd5c);
    FUN_0041d92c(0x65,*DAT_0041fd60);
    FUN_0041d92c(0x66,*DAT_0041fd64);
  }
  else {
    if (param_2 == '\a') {
      return unaff_r7;
    }
    if (param_2 == '\b') goto LAB_0041fc66;
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
        goto LAB_0041fc66;
      }
    }
  }
LAB_0041fc96:
  FUN_0041d92c(0x61,*DAT_0041fd10);
  FUN_0041d92c(0x62,*DAT_0041fd0c);
LAB_0041fcae:
  FUN_0041d92c(0x31,*DAT_0041fd1c);
  FUN_0041d92c(0x5f,*DAT_0041fd18);
  FUN_0041d92c(0x60,*DAT_0041fd14);
  FUN_0041d92c(0x67,*DAT_0041fd68);
  FUN_0041d92c(0x68,*DAT_0041fd6c);
  return unaff_r7;
}

