
void FUN_00495e84(undefined4 *param_1,undefined4 *param_2)

{
  uint uVar1;
  
  if ((param_1 != (undefined4 *)0x0) && (param_2 != (undefined4 *)0x0)) {
    *param_2 = *param_1;
    param_2[1] = param_1[1];
    param_2[2] = param_1[2];
    param_2[3] = param_1[3];
    param_2[7] = param_1[7];
    param_2[4] = param_1[4];
    param_2[5] = param_1[5];
    param_2[6] = param_1[6];
    if (*(char *)(param_1 + 0xd) == '\0') {
      param_2[8] = 0;
      param_2[9] = 0;
      *(undefined1 *)(param_2 + 10) = 0;
    }
    else {
      param_2[8] = param_1[0xe];
      param_2[9] = param_1[0xf];
      *(bool *)(param_2 + 10) = param_1[0x10] != 0;
      for (uVar1 = 0;
          ((uVar1 < (uint)param_2[8] && ((int)uVar1 < 0x14)) &&
          ((int)uVar1 < (int)(uint)*(ushort *)(param_1 + 0x11))); uVar1 = uVar1 + 1) {
        FUN_0044b5a0((int)param_2 + uVar1 * 0x40 + 0x29,(int)param_1 + uVar1 * 0x40 + 0x46,0x3f);
        *(undefined1 *)(param_2 + uVar1 * 0x10 + 0x1a) = 0;
      }
    }
  }
  return;
}

