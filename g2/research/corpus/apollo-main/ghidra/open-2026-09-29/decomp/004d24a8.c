
void DmSmpCbackExec(int param_1)

{
  if (((*(char *)(param_1 + 2) == '*') || (*(char *)(param_1 + 2) == ',')) &&
     (*(int *)(DAT_004d2534 + 0x90) != 0)) {
    (**(code **)(DAT_004d2534 + 0x90))(param_1);
  }
  (**(code **)(DAT_004d252c + 8))(param_1);
  return;
}

