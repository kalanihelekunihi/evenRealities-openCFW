
void gx8002_system_initialize(void)

{
  int iVar1;
  uint in_r3;
  
  gx8002_clock_init_pointer(0,uRam100235e4,1,in_r3 & 0xfc0 | 0x3f);
  iVar1 = gx8002_start_mode();
  if (iVar1 == 0) {
    gx8002_clear_bss();
  }
  gx8002_board_initialize();
  iVar1 = iRam100235ec;
  *(undefined4 *)(iRam100235ec + 0xb10) = 0xff;
  *(undefined4 *)(iVar1 + 0x200) = 0;
  *(undefined4 *)(iVar1 + 0x180) = 0xffffffff;
  *(undefined4 *)(iVar1 + 0x204) = 0;
  *(undefined4 *)(iVar1 + 0x184) = 0xffffffff;
  *(undefined4 *)(iVar1 + 0x208) = 0;
  *(undefined4 *)(iVar1 + 0x188) = 0xffffffff;
  *(undefined4 *)(iVar1 + 0x20c) = 0;
  *(undefined4 *)(iVar1 + 0x18c) = 0xffffffff;
  return;
}

