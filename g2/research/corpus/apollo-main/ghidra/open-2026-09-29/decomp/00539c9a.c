
undefined4 FUN_00539c9a(byte param_1,undefined1 *param_2)

{
  uint uVar1;
  
  if (param_1 == 0) {
    uVar1 = *DAT_00539dc4 & 3;
    if (uVar1 == 0) {
      *param_2 = 0;
    }
    else if (uVar1 == 2) {
      *param_2 = 2;
    }
    else if (uVar1 < 2) {
      *param_2 = 1;
    }
  }
  else if (param_1 == 2) {
    uVar1 = *DAT_00539dc4 >> 4 & 1;
    if (uVar1 == 0) {
      *param_2 = 6;
    }
    else if (uVar1 == 1) {
      *param_2 = 7;
    }
  }
  else if (param_1 < 2) {
    uVar1 = *DAT_00539dc4 >> 2 & 3;
    if (uVar1 == 0) {
      *param_2 = 3;
    }
    else if (uVar1 == 2) {
      *param_2 = 5;
    }
    else if (uVar1 < 2) {
      *param_2 = 4;
    }
  }
  else if (param_1 == 4) {
    uVar1 = *DAT_00539dc4 >> 7 & 3;
    if (uVar1 == 0) {
      *param_2 = 0xb;
    }
    else if (uVar1 == 2) {
      *param_2 = 0xd;
    }
    else if (uVar1 < 2) {
      *param_2 = 0xc;
    }
  }
  else if (param_1 < 4) {
    uVar1 = *DAT_00539dc4 >> 5 & 3;
    if (uVar1 == 0) {
      *param_2 = 8;
    }
    else if (uVar1 == 2) {
      *param_2 = 10;
    }
    else if (uVar1 < 2) {
      *param_2 = 9;
    }
  }
  else if (param_1 == 5) {
    return 6;
  }
  return 0;
}

