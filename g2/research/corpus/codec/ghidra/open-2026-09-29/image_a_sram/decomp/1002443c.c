
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 flash_interface_initialize(void)

{
  int iVar1;
  byte bVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  bool bVar6;
  byte bStack_19;
  undefined4 uStack_18;
  
  uStack_18 = 0;
  gx8002_platform_config(9,&uStack_18);
  gx8002_platform_gate(0xd,1);
  wait_bus_ready();
  uRam00000090 = 1;
  _DAT_a200002c = 0x4e;
  _DAT_a20000f0 = 1;
  _DAT_a2000014 = 4;
  _DAT_a200001c = 0x1f;
  _DAT_a2000008 = 1;
  gx8002_request_irq(0xf,PTR_flash_spi_irq_handler_10024598,0);
  gx8002_flash_wait_ready();
  iVar3 = gx8002_flash_discover();
  iVar1 = DAT_1002459c;
  if (iVar3 != 0) {
    return 0;
  }
  gx8002_flash_protection_initialize();
  _DAT_a2000014 = 2;
  iVar5 = *(int *)(*(int *)(iVar1 + 0xc) + 4);
  _DAT_a2000008 = iVar3;
  if (DAT_100245a0 < iVar5) {
    if (iVar5 != DAT_100245c4) {
      if (DAT_100245c4 < iVar5) {
        if (iVar5 != DAT_100245d8) {
          iVar3 = DAT_100245e0;
          iVar4 = DAT_100245dc;
          if (DAT_100245d8 < iVar5) goto LAB_10024514;
LAB_100244cc:
          bVar6 = 1 < (uint)(iVar4 + iVar5);
          goto LAB_100244d0;
        }
      }
      else if (iVar5 != DAT_100245c8) {
        iVar3 = DAT_100245cc;
        if ((DAT_100245c8 < iVar5) && (iVar3 = DAT_100245d4, iVar5 == DAT_100245d0)) {
          bVar2 = gx8002_flash_read_status();
          if ((bVar2 & 0x40) == 0) {
            bStack_19 = bVar2 | 0x40;
            gx8002_flash_wait_ready();
            gx8002_flash_write_enable();
            gx8002_flash_command_write(1,&bStack_19,1);
            gx8002_flash_wait_ready();
          }
          goto LAB_1002453c;
        }
LAB_10024514:
        bVar6 = iVar5 != iVar3;
LAB_100244d0:
        if (bVar6) goto LAB_100244f8;
      }
    }
LAB_100244d2:
    gx8002_flash_quad_enable_pair();
  }
  else {
    if (DAT_100245a4 <= iVar5) goto LAB_100244d2;
    if (DAT_100245a8 < iVar5) {
      if (iVar5 == DAT_100245b8) {
        gx8002_flash_quad_enable();
        gx8002_flash_quad_enable_pair();
        goto LAB_1002453c;
      }
      if (iVar5 == DAT_100245bc) goto LAB_100244d2;
      if (iVar5 != DAT_100245c0) goto LAB_100244f8;
    }
    else if (iVar5 < DAT_100245ac) {
      if (iVar5 == DAT_100245b0) goto LAB_100244d2;
      iVar4 = DAT_100245b4;
      if (DAT_100245b0 <= iVar5) goto LAB_100244cc;
LAB_100244f8:
      gx8002_flash_quad_enable();
    }
  }
  if (iVar5 == 0x204016) {
    gx8002_flash_device_config();
  }
LAB_1002453c:
  *(undefined **)(iVar1 + 0x18) = PTR_gx8002_flash_word_program_100245e4;
  *(undefined **)(iVar1 + 0x1c) = PTR_gx8002_flash_word_read_100245e8;
  gx_xip_init(0xeb,8,1,0x18,4,0,1,4,4);
  return DAT_100245ec;
}

