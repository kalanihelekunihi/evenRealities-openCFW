
void gx8002_board_initialize(void)

{
  uint uVar1;
  
  uVar1 = gx_pmu_get_wakeup_source();
  if (1 < uVar1) {
    gx8002_flash_initialize();
  }
  func_0x10203c74();
  return;
}

