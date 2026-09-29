
undefined4 FUN_004b064e(char param_1)

{
  undefined4 uVar1;
  
  if (param_1 == '\x06') {
    uVar1 = 9;
  }
  else if (param_1 == '\v') {
    uVar1 = 0xb;
  }
  else if (param_1 == '\f') {
    uVar1 = 0x31;
  }
  else if (param_1 == '\r') {
    uVar1 = 0x35;
  }
  else if (param_1 == '\x0e') {
    uVar1 = 9;
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
  else if (param_1 == '\x15') {
    uVar1 = 0x44;
  }
  else {
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

