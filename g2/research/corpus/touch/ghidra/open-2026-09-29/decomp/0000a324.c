
void Cy_SysLib_DelayUs(int param_1)

{
  Cy_SysLib_DelayCycles((uint)*DAT_0000a334 * param_1);
  return;
}

