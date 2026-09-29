
/* WARNING: Instruction at (ram,0x005989a6) overlaps instruction at (ram,0x005989a4)
    */

void FUN_00598994(float param_1,float *param_2,float param_3,float param_4)

{
  float unaff_r5;
  float unaff_r6;
  
  if (((uint)param_3 & 3) != 0) {
    do {
      *param_2 = *param_2 * param_1;
      param_2[1] = param_2[1] * param_1;
      param_2[2] = param_2[2] * param_1;
      param_2[3] = param_2[3] * param_1;
      loopEnd();
      param_2 = (float *)((uint)(param_2 + 4) >> 8);
    } while( true );
  }
  if ((uint)param_3 >> 2 != 0) {
    do {
      *param_2 = *param_2 * param_1;
      param_2[1] = param_2[1] * param_1;
      param_2[2] = param_2[2] * param_1;
      param_2[3] = param_2[3] * param_1;
      param_2[4] = param_2[4] * param_1;
      param_2[5] = param_2[5] * param_1;
      param_2[6] = param_2[6] * param_1;
      param_2[7] = param_2[7] * param_1;
      param_2[8] = param_2[8] * param_1;
      param_2[9] = param_2[9] * param_1;
      param_2[10] = param_2[10] * param_1;
      param_2[0xb] = param_2[0xb] * param_1;
      param_2[0xc] = param_2[0xc] * param_1;
      param_2[0xd] = param_2[0xd] * param_1;
      param_2[0xe] = param_2[0xe] * param_1;
      param_2[0xf] = param_2[0xf] * param_1;
      param_2 = param_2 + 0x10;
      loopEnd();
    } while( true );
  }
  *param_2 = (float)param_2;
  param_2[1] = param_3;
  param_2[2] = param_4;
  param_2[3] = unaff_r5;
  param_2[4] = unaff_r6;
  return;
}

