
void FUN_0059112e(byte *param_1,byte *param_2,int param_3)

{
  uint *puVar1;
  byte *pbVar2;
  uint uVar3;
  uint in_fpscr;
  uint local_14;
  
  if ((int)((*param_1 + 1) * *(int *)(DAT_005915bc + (uint)param_1[2] * 4)) < 1) {
    return;
  }
  pbVar2 = param_1 + *(int *)(param_1 + 0x4a0) * 2 + 0x4ac;
  puVar1 = (uint *)(param_1 + *(int *)(param_1 + 0x4a4) * 4 + 0x4ac);
  do {
    uVar3 = (uint)param_2[1] << 0x10 | (uint)*param_2 << 8 | (uint)param_2[2] << 0x18;
    *(short *)pbVar2 = (short)(uVar3 >> 0x10);
    local_14 = VectorSignedToFloat(uVar3,(byte)(in_fpscr >> 0x16) & 3);
    if ((local_14 & 0x7f800000) != 0) {
      local_14 = local_14 + 0xf8000000;
    }
    param_2 = param_2 + param_3 * 3;
    pbVar2 = pbVar2 + 2;
    *puVar1 = local_14;
    loopEnd();
    puVar1 = puVar1 + 1;
  } while( true );
}

