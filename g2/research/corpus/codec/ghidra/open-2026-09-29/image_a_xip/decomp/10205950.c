
void gx8002_npu_regs_init(void)

{
  int iVar1;
  
  iVar1 = DAT_10205998;
  gx8002_npu_set_clock_gate(*(undefined4 *)(DAT_10205998 + 0x5c4),1);
  gx8002_npu_set_idle_cycle(*(undefined4 *)(iVar1 + 0x5c4),2000);
  gx8002_npu_set_idle_mode(*(undefined4 *)(iVar1 + 0x5c4),0);
  gx8002_npu_clr_interrupt(*(undefined4 *)(iVar1 + 0x5c4),0x6f);
  gx8002_npu_en_interrupt(*(undefined4 *)(iVar1 + 0x5c4),0x6d);
  gx8002_npu_set_overtime_thr(*(undefined4 *)(iVar1 + 0x5c4),0x100000);
  return;
}

