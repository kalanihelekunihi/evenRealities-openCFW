
uint FUN_00509024(byte param_1,char param_2,undefined4 param_3,uint param_4)

{
  bool bVar1;
  uint local_10;
  
  local_10 = param_4;
  if (param_1 == 1) {
    FUN_0053a5be(0x81,param_2 == '\x01');
  }
  else if (param_1 == 2) {
    FUN_0053a5be(9,param_2 == '\x01');
  }
  else if (param_1 == 3) {
    FUN_0053a5be(0x80,param_2 == '\x01');
  }
  else if (param_1 == 4) {
    FUN_0053a5be(0x8e,param_2 == '\x01');
  }
  else {
    if (param_1 != 6) {
      if (param_1 == 7) {
        FUN_0053a5be(0x8f,param_2 == '\x01');
        return param_4;
      }
      if (param_1 == 8) {
        FUN_0053a5be(0x92,param_2 == '\x01');
        return param_4;
      }
      if (param_1 != 9) {
        return param_4;
      }
    }
    local_10 = FUN_00473940();
    if (param_2 == '\x01') {
      *DAT_0050946c = 1 << (uint)param_1 | *DAT_0050946c;
    }
    else if (param_2 == '\0') {
      *DAT_0050946c = *DAT_0050946c & ~(1 << (uint)param_1);
    }
    if (*DAT_0050946c == 0) {
      FUN_0053a5be(0x86,0);
    }
    else {
      FUN_0053a5be(0x86,1);
    }
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_10 & 1) == 1);
    }
  }
  return local_10;
}

