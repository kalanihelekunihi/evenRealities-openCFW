
undefined4 FUN_004b45b0(ushort *param_1)

{
  char cVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  iVar2 = 0;
  if (((((char)param_1[1] != '?') && (*param_1 != 0)) && (*param_1 != 0)) && (*param_1 < 4)) {
    iVar2 = DAT_004b46f0 + (uint)*param_1 * 0x30 + -0x30;
  }
  cVar1 = (char)param_1[1];
  if (cVar1 == '\'') {
    if (iVar2 != 0) {
      FUN_004b3944();
    }
  }
  else if (cVar1 == '(') {
    if (iVar2 != 0) {
      FUN_004b39de();
    }
  }
  else if (cVar1 == '*') {
    if (iVar2 != 0) {
      FUN_004b3aa8();
    }
  }
  else if (cVar1 == '+') {
    if (iVar2 != 0) {
      FUN_004b3aea();
    }
  }
  else if (cVar1 == ',') {
    if (iVar2 != 0) {
      FUN_004b3aec();
    }
  }
  else if (cVar1 != '-') {
    if (cVar1 == '/') {
      if (iVar2 != 0) {
        FUN_004b3a86();
      }
    }
    else if (cVar1 == '0') {
      if (iVar2 != 0) {
        FUN_004b3b4c();
      }
    }
    else if (cVar1 == '1') {
      if (iVar2 != 0) {
        FUN_004b39f6();
      }
    }
    else if (cVar1 == ':') {
      if (iVar2 != 0) {
        FUN_004b3bb4();
      }
    }
    else if (cVar1 == ';') {
      if (iVar2 != 0) {
        FUN_004b3bd2();
      }
    }
    else if (cVar1 == '?') {
      FUN_004b3ba0();
    }
  }
  return unaff_r7;
}

