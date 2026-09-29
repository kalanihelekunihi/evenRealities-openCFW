
undefined4 ui_onboarding_main_sub_004A8DB6(int param_1)

{
  char cVar1;
  
  cVar1 = DAT_004a9114[1];
  if (*DAT_004a9114 == '\x02') {
    if (cVar1 == '\0') {
      if (param_1 == 0x48) {
        return 1;
      }
    }
    else if (cVar1 == '\x02') {
      if (param_1 == 0x44) {
        return 1;
      }
    }
    else if (cVar1 == '\x04') {
      if (param_1 == 10) {
        return 1;
      }
    }
    else if (cVar1 == '\x06') {
      if (param_1 == 0x48) {
        return 1;
      }
    }
    else if (cVar1 == '\b') {
      if (param_1 == 8) {
        return 1;
      }
    }
    else if (cVar1 == '\v') {
      if (param_1 == 0x48) {
        return 1;
      }
    }
    else {
      if (cVar1 != '\r') {
        return 0;
      }
      if (param_1 == 0x48) {
        return 1;
      }
    }
  }
  else if (*DAT_004a9114 == '\x03') {
    if (param_1 == 0x4b) {
      if (*DAT_004a9154 == '\x01') {
        return 0;
      }
      return 1;
    }
    if (param_1 == 0x49) {
      return 1;
    }
  }
  return 0;
}

