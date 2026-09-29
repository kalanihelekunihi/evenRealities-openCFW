
undefined8 semantic_transform_vector(float *param_1,int param_2)

{
  uint uVar1;
  float local_14 [3];
  
  local_14[0] = 0.0;
  local_14[1] = 0.0;
  local_14[2] = 0.0;
  for (uVar1 = 0; uVar1 < 3; uVar1 = uVar1 + 1) {
    local_14[uVar1] = *param_1 * *(float *)(uVar1 * 0xc + param_2);
    local_14[uVar1] = local_14[uVar1] + param_1[1] * *(float *)(param_2 + uVar1 * 0xc + 4);
    local_14[uVar1] = local_14[uVar1] + param_1[2] * *(float *)(param_2 + uVar1 * 0xc + 8);
  }
  *param_1 = local_14[0];
  param_1[1] = local_14[1];
  param_1[2] = local_14[2];
  return CONCAT44(local_14[1],local_14[0]);
}

