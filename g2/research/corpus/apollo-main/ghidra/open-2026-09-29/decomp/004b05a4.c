
undefined4 FUN_004b05a4(char param_1)

{
  undefined4 uVar1;
  
  if (param_1 == '\x06') {
    uVar1 = 9;
  }
  else if (param_1 == '\a') {
    uVar1 = 0xb;
  }
  else if (param_1 == '\b') {
    uVar1 = 0x31;
  }
  else if (param_1 == '\t') {
    uVar1 = 0x35;
  }
  else if (param_1 == '\n') {
    uVar1 = 9;
  }
  else if (param_1 == '\v') {
    uVar1 = 0xc;
  }
  else if (param_1 == '\f') {
    uVar1 = 0x30;
  }
  else if (param_1 == '\r') {
    uVar1 = 0x34;
  }
  else if (param_1 == '\x0e') {
    uVar1 = 8;
  }
  else if (param_1 == '\x0f') {
    uVar1 = 0x39;
  }
  else if (param_1 == '\x10') {
    uVar1 = 0x10;
  }
  else if (param_1 == '\x11') {
    uVar1 = 0x11;
  }
  else if (param_1 == '\x12') {
    uVar1 = 4;
  }
  else if (param_1 == '\x14') {
    uVar1 = 4;
  }
  else if (param_1 == '\x15') {
    uVar1 = 0x44;
  }
  else if (param_1 == '0') {
    uVar1 = 0x12;
  }
  else if (param_1 == '1') {
    uVar1 = 0x16;
  }
  else if (param_1 == '2') {
    uVar1 = 0x17;
  }
  else if (param_1 == '4') {
    uVar1 = 0x4c;
  }
  else if (param_1 == '5') {
    uVar1 = 0x4d;
  }
  else {
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

