
void FUN_005155e4(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                 undefined4 param_5,undefined4 param_6)

{
  undefined4 *puVar1;
  uint in_fpscr;
  undefined4 uVar2;
  
  puVar1 = DAT_005156b4;
  DAT_005156b4[4] = param_1;
  uVar2 = VectorSignedToFloat(param_1,(byte)(in_fpscr >> 0x16) & 3);
  puVar1[9] = uVar2;
  puVar1[0xb] = uVar2;
  uVar2 = VectorSignedToFloat(param_2,(byte)(in_fpscr >> 0x16) & 3);
  *puVar1 = param_3;
  puVar1[1] = param_4;
  puVar1[2] = param_5;
  puVar1[3] = param_6;
  puVar1[5] = param_2;
  puVar1[7] = 0;
  puVar1[8] = 0;
  puVar1[10] = 0;
  puVar1[0xc] = uVar2;
  puVar1[0xd] = 0;
  puVar1[0xe] = uVar2;
  return;
}

