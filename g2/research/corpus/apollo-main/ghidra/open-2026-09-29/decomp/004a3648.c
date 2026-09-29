
void semantic_filter_update(float param_1,double *param_2)

{
  float fVar1;
  float fVar2;
  float fVar3;
  
  fVar1 = *(float *)(param_2 + 5);
  fVar2 = *(float *)((int)param_2 + 0x2c);
  fVar3 = *(float *)((int)param_2 + 0x34);
  *(undefined4 *)((int)param_2 + 0x2c) = *(undefined4 *)(param_2 + 5);
  *(float *)(param_2 + 5) = param_1;
  *(undefined4 *)((int)param_2 + 0x34) = *(undefined4 *)(param_2 + 6);
  *(float *)(param_2 + 6) =
       (float)((((double)param_1 * *param_2 + (double)fVar1 * param_2[1] +
                (double)fVar2 * param_2[2]) - (double)*(float *)(param_2 + 6) * param_2[3]) -
              (double)fVar3 * param_2[4]);
  return;
}

