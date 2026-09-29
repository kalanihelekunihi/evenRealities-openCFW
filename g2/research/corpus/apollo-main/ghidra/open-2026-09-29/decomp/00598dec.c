
/* WARNING: Instruction at (ram,0x00598e5a) overlaps instruction at (ram,0x00598e58)
    */

undefined1 * FUN_00598dec(int param_1,int param_2,int param_3,float *param_4)

{
  float *pfVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  uint in_fpscr;
  float fVar9;
  float fVar10;
  float local_24 [3];
  
  pfVar1 = local_24;
  iVar2 = *(int *)(DAT_00598efc + param_1 * 0x1c + param_2 * 4);
  piVar5 = *(int **)(param_1 * 0x1c + DAT_00598f00 + param_2 * 4);
  iVar4 = 0;
  local_24[0] = 0.0;
  local_24[1] = 0.0;
  iVar3 = *(int *)(&DAT_00598f04 + param_1 * 4);
  iVar6 = *piVar5;
  if (0 < iVar2) {
    do {
      piVar5 = piVar5 + 1;
      iVar8 = *piVar5;
      iVar7 = iVar8 - iVar6;
      fVar10 = *(float *)(param_3 + iVar6 * 4);
      iVar6 = iVar6 + 1;
      if (iVar6 < iVar8) {
        if ((iVar8 - iVar6 & 3U) != 0) {
          do {
            loopEnd();
          } while( true );
        }
        if ((uint)(iVar8 - iVar6) >> 2 != 0) {
          do {
            loopEnd();
          } while( true );
        }
      }
      fVar9 = (float)VectorSignedToFloat(iVar7,(byte)(in_fpscr >> 0x16) & 3);
      fVar9 = (fVar10 * fVar10) / fVar9;
      if (iVar4 < iVar2 - iVar3) {
        iVar7 = 0;
      }
      else {
        iVar7 = 4;
      }
      *(float *)((int)local_24 + iVar7) = *(float *)((int)local_24 + iVar7) + fVar9;
      *param_4 = fVar9;
      param_4 = param_4 + 1;
      iVar4 = iVar4 + 1;
    } while (iVar4 < iVar2);
  }
  iVar2 = (uint)(local_24[0] * 30.0 < local_24[1]) << 0x1f;
  if (iVar2 < 0) {
    pfVar1 = (float *)0x1;
  }
  if (-1 < iVar2) {
    pfVar1 = (float *)0x0;
  }
  return (undefined1 *)pfVar1;
}

