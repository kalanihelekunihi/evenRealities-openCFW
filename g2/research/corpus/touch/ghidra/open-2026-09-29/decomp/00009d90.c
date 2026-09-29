
void Cy_SysClk_IloStartMeasurement(void)

{
  if (*DAT_00009dc0 == '\0') {
    *DAT_00009dc4 = 1;
    *(uint *)(DAT_00009dc8 + 0x34) = *(uint *)(DAT_00009dc8 + 0x34) & DAT_00009dcc | 0x100;
    *DAT_00009dd0 = DAT_00009dd8 | *DAT_00009dd0 & DAT_00009dd4;
  }
  return;
}

