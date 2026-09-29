
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void gx8002_tws_set_standby(int param_1)

{
  int iVar1;
  
  iVar1 = _gx8002_active_snpu_queue_pointer;
  *(int *)(_gx8002_active_snpu_queue_pointer + 0x4c) = param_1;
  if (param_1 == 2) {
    *(undefined4 *)(iVar1 + 0x50) = 0x32;
  }
  return;
}

