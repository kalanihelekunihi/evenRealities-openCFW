
void FUN_00522974(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                 undefined4 param_5,undefined4 param_6,undefined4 param_7,undefined4 param_8,
                 undefined4 param_9,undefined4 param_10,undefined4 param_11,undefined4 param_12)

{
  undefined4 *puVar1;
  
  puVar1 = (undefined4 *)FUN_00514aec(0xc);
  if (puVar1 != (undefined4 *)0x0) {
    *puVar1 = 0x1c0;
    puVar1[1] = param_1;
    puVar1[2] = 0x1c4;
    puVar1[7] = param_4;
    puVar1[3] = param_2;
    puVar1[6] = 0x1cc;
    puVar1[8] = 0x1a0;
    puVar1[4] = 0x1c8;
    puVar1[5] = param_3;
    puVar1[9] = param_5;
    puVar1[10] = 0x1a4;
    puVar1[0xb] = param_6;
    puVar1[0xc] = 0x1a8;
    puVar1[0xd] = param_7;
    puVar1[0xe] = 0x1ac;
    puVar1[0x13] = param_10;
    puVar1[0x15] = param_11;
    puVar1[0xf] = param_8;
    puVar1[0x10] = 0x1b0;
    puVar1[0x11] = param_9;
    puVar1[0x12] = 0x1b4;
    puVar1[0x14] = 0x1b8;
    puVar1[0x16] = 0x1bc;
    puVar1[0x17] = param_12;
  }
  return;
}

