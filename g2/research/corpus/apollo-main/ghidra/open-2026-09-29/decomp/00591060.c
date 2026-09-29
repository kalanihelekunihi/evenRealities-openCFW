
void FUN_00591060(byte *param_1,undefined4 *param_2,int param_3)

{
  uint *puVar1;
  uint *puVar2;
  byte *pbVar3;
  undefined4 uVar4;
  uint uVar5;
  uint in_fpscr;
  uint local_10;
  
  uVar5 = (*param_1 + 1) * *(int *)(DAT_005915b8 + (uint)param_1[2] * 4);
  if (0 < (int)uVar5) {
    pbVar3 = param_1 + *(int *)(param_1 + 0x4a0) * 2 + 0x4ac;
    puVar1 = (uint *)(param_1 + *(int *)(param_1 + 0x4a4) * 4 + 0x4ac);
    puVar2 = puVar1;
    if ((int)(uVar5 * -0x80000000) < 0) {
      uVar4 = *param_2;
      *(short *)pbVar3 = (short)((uint)uVar4 >> 8);
      local_10 = VectorSignedToFloat(uVar4,(byte)(in_fpscr >> 0x16) & 3);
      if ((local_10 & 0x7f800000) != 0) {
        local_10 = local_10 + 0xfc000000;
      }
      param_2 = param_2 + param_3;
      pbVar3 = pbVar3 + 2;
      puVar2 = puVar1 + 1;
      *puVar1 = local_10;
    }
    if (uVar5 >> 1 != 0) {
      do {
        uVar4 = *param_2;
        *(short *)pbVar3 = (short)((uint)uVar4 >> 8);
        local_10 = VectorSignedToFloat(uVar4,(byte)(in_fpscr >> 0x16) & 3);
        if ((local_10 & 0x7f800000) != 0) {
          local_10 = local_10 + 0xfc000000;
        }
        *puVar2 = local_10;
        uVar4 = param_2[param_3];
        *(short *)(pbVar3 + 2) = (short)((uint)uVar4 >> 8);
        local_10 = VectorSignedToFloat(uVar4,(byte)(in_fpscr >> 0x16) & 3);
        if ((local_10 & 0x7f800000) != 0) {
          local_10 = local_10 + 0xfc000000;
        }
        param_2 = param_2 + param_3 + param_3;
        pbVar3 = pbVar3 + 4;
        puVar2[1] = local_10;
        puVar2 = puVar2 + 2;
        loopEnd();
      } while( true );
    }
  }
  return;
}

