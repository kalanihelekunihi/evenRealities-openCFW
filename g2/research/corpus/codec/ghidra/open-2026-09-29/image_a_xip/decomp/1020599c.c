
undefined4 gx8002_snpu_resume_internal(void)

{
  undefined4 *puVar1;
  int iVar2;
  
  puVar1 = puRam102059e4;
  *puRam102059e4 = 0;
  puVar1[0x170] = 0;
  puVar1[0x174] = 0;
  func_0x100251ec(1);
  iVar2 = gx8002_npu_is_enabled(puVar1[0x171]);
  if (iVar2 != 0) {
    gx8002_npu_disable(puVar1[0x171]);
    do {
      iVar2 = gx8002_npu_all_idle(puVar1[0x171]);
    } while (iVar2 == 0);
  }
  gx8002_npu_reset(puVar1[0x172]);
  gx8002_npu_regs_init();
  return 0;
}

