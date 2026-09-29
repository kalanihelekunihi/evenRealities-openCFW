
uint gx8002_start_mode(void)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = gx_pmu_get_wakeup_source();
  if (iVar1 - 2U < 4) {
    uVar2 = uRam00000058 & 1;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

