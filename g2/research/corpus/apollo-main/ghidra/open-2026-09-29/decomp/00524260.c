
float FUN_00524260(float param_1)

{
  float fVar1;
  
  if ((-1.0 <= param_1) && ((int)((uint)(param_1 < DAT_005242e4) << 0x1f) < 0)) {
    return (param_1 * DAT_005242ec) / (param_1 * DAT_005242e8 * param_1 + 1.0);
  }
  fVar1 = (param_1 * DAT_005242ec) / (DAT_005242e8 + param_1 * param_1);
  if (DAT_005242e4 <= param_1) {
    return DAT_005242f0 - fVar1;
  }
  return -(fVar1 + DAT_005242f0);
}

