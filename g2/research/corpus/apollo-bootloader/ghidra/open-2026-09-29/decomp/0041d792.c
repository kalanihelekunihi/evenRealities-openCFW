
undefined8 FUN_0041d792(char param_1,undefined1 *param_2)

{
  uint *puVar1;
  undefined4 uVar2;
  uint uVar3;
  undefined4 unaff_r7;
  
  puVar1 = DAT_0041d8a4;
  if (param_2 == (undefined1 *)0x0) {
    uVar2 = 6;
  }
  else {
    if (param_1 == '\0') {
      uVar3 = *DAT_0041d8a4 & 3;
      if (uVar3 == 0) {
        param_2[1] = 0;
        *param_2 = 0;
        param_2[2] = 0;
      }
      else if (uVar3 == 2) {
        param_2[1] = 1;
        *param_2 = 1;
        param_2[2] = 1;
      }
      else if (uVar3 < 2) {
        param_2[1] = 0;
        *param_2 = 0;
        param_2[2] = 1;
      }
      else if (uVar3 == 3) {
        param_2[1] = 1;
        *param_2 = 1;
        param_2[2] = 2;
      }
      param_2[3] = (byte)((*puVar1 << 0x1c) >> 0x1e);
      param_2[4] = (*puVar1 & 0x7f) >> 6 != 0;
      param_2[5] = (*puVar1 & 0xff) >> 7 != 0;
      param_2[6] = (*puVar1 & 0x1ff) >> 8 != 0;
      param_2[7] = (*puVar1 & 0x3ff) >> 9 != 0;
      param_2[8] = (*puVar1 & 0x7ff) >> 10 != 0;
      param_2[9] = (*puVar1 & 0xfffff) >> 0x13 != 0;
      param_2[10] = (byte)(*puVar1 >> 0x14) & 3;
      FUN_0041d69c(param_2);
    }
    else {
      if (param_1 != '\x01') {
        uVar2 = 6;
        goto LAB_0041d87e;
      }
      FUN_0041d294(param_2);
    }
    uVar2 = 0;
  }
LAB_0041d87e:
  return CONCAT44(unaff_r7,uVar2);
}

