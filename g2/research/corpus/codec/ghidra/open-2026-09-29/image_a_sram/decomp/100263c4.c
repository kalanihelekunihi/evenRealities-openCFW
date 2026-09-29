
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void gx8002_tws_standby_loop(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = _gx8002_active_snpu_queue_pointer;
  if ((*(int *)(_gx8002_active_snpu_queue_pointer + 0x4c) == 2) &&
     (iVar2 = *(int *)(_gx8002_active_snpu_queue_pointer + 0x50) + -1,
     *(int *)(_gx8002_active_snpu_queue_pointer + 0x50) = iVar2, iVar2 == 0)) {
    *(undefined4 *)(iVar1 + 0x4c) = 4;
  }
  return;
}

