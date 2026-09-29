
void Cy_SysClk_IloStopMeasurement(void)

{
  if (*DAT_00009e00 == '\0') {
    *DAT_00009e04 = 0;
    *(uint *)(DAT_00009e08 + 0x34) = *(uint *)(DAT_00009e08 + 0x34) & DAT_00009e0c;
    *DAT_00009e10 = *DAT_00009e10 & DAT_00009e14;
  }
  return;
}

