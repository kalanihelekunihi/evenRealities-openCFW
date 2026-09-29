
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 gx8002_flash_initialize(void)

{
  int iVar1;
  int iVar2;
  undefined4 uStack_c;
  
  uStack_c = 0;
  gx8002_platform_config(9,&uStack_c);
  gx8002_platform_gate(0xd,1);
  wait_bus_ready();
  uRam00000090 = 1;
  _DAT_a200002c = 0x4e;
  _DAT_a20000f0 = 1;
  _DAT_a2000014 = 2;
  _DAT_a200001c = 0x1f;
  _DAT_a2000008 = 1;
  gx8002_flash_wait_ready();
  iVar2 = gx8002_flash_discover();
  iVar1 = iRam100246a8;
  if (iVar2 != 0) {
    return 0;
  }
  iVar2 = *(int *)(*(int *)(iRam100246a8 + 0xc) + 4);
  if (iVar2 == iRam100246ac) {
LAB_10024664:
    gx8002_flash_quad_enable_pair();
  }
  else {
    if (iRam100246ac < iVar2) {
      if (iVar2 == iRam100246b4) goto LAB_10024664;
    }
    else if ((uint)(iVar2 + iRam100246b0) < 2) goto LAB_10024668;
    gx8002_flash_quad_enable();
  }
LAB_10024668:
  if (*(int *)(*(int *)(iVar1 + 0xc) + 4) == 0x204016) {
    gx8002_flash_device_config();
  }
  *(undefined **)(iVar1 + 0x18) = PTR_gx8002_flash_word_program_100246b8;
  *(undefined **)(iVar1 + 0x1c) = PTR_gx8002_flash_word_read_100246bc;
  gx_xip_init(0xeb,8,1,0x18,4,0,1,4,4);
  return _configuration_0;
}

