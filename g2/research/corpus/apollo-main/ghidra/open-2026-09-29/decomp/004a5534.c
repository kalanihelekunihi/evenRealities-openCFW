
void semantic_fixed_vector_to_float(int param_1,int param_2,uint param_3,byte param_4)

{
  int iVar1;
  uint in_fpscr;
  float fVar2;
  float fVar3;
  
  fVar2 = (float)VectorSignedToFloat(1 << (param_3 & 0xff),(byte)(in_fpscr >> 0x16) & 3);
  for (iVar1 = 0; iVar1 < (int)(uint)param_4; iVar1 = iVar1 + 1) {
    fVar3 = (float)VectorSignedToFloat(*(undefined4 *)(param_1 + iVar1 * 4),
                                       (byte)(in_fpscr >> 0x16) & 3);
    *(float *)(param_2 + iVar1 * 4) = fVar3 * (1.0 / fVar2);
  }
  return;
}

