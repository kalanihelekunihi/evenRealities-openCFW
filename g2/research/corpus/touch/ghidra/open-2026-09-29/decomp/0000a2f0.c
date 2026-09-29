
void Cy_SysLib_Delay(uint param_1)

{
  for (; 0x8000 < param_1; param_1 = param_1 + DAT_0000a31c) {
    Cy_SysLib_DelayCycles(*DAT_0000a318);
  }
  Cy_SysLib_DelayCycles(param_1 * *DAT_0000a320);
  return;
}

