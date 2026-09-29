
void gx8002_dw_spi_probe(void)

{
  int iVar1;
  undefined4 uVar2;
  uint *puVar3;
  int iVar4;
  int iVar5;
  
  iVar1 = iRam10206570;
  iVar5 = iRam10206570 + 0x34;
  iVar4 = iRam10206570 + 0x10;
  *(undefined4 *)(iRam10206570 + 0x38) = 0xa3000000;
  *(int *)(iVar1 + 0x34) = iVar4;
  *(int *)(iVar1 + 0x28) = iVar5;
  *(undefined4 *)(iVar1 + 0x10) = 0;
  *(undefined4 *)(iVar1 + 0x14) = 1;
  *(undefined **)(iVar1 + 0x20) = PTR_gx8002_dw_spi_cleanup_10206574;
  *(undefined **)(iVar1 + 0x18) = PTR_gx8002_dw_spi_setup_10206578;
  *(undefined **)(iVar1 + 0x1c) = PTR_gx8002_dw_spi_quick_transfer_1020657c;
  func_0x10025080(0xe);
  *(undefined4 *)(*(int *)(iVar1 + 0x38) + 8) = 0;
  *(undefined4 *)(*(int *)(iVar1 + 0x38) + 0x2c) = 0x4e;
  if (*(int *)(iVar1 + 0x3c) == 0) {
    iVar5 = 2;
    iVar4 = 0x100;
    do {
      *(int *)(*(int *)(iVar1 + 0x38) + 0x18) = iVar5;
      if (*(int *)(*(int *)(iVar1 + 0x38) + 0x18) != iVar5) {
        if (iVar5 == 0x101) {
          iVar5 = 0;
        }
        break;
      }
      iVar5 = iVar5 + 1;
      iVar4 = iVar4 + -1;
    } while (iVar4 != 0);
    *(int *)(iVar1 + 0x3c) = iVar5;
    *(undefined4 *)(*(int *)(iVar1 + 0x38) + 0x18) = 0;
  }
  if (*(int *)(iVar1 + 0x40) == 0) {
    iVar5 = 2;
    iVar4 = 0x100;
    do {
      *(int *)(*(int *)(iVar1 + 0x38) + 0x1c) = iVar5;
      if (*(int *)(*(int *)(iVar1 + 0x38) + 0x1c) != iVar5) {
        if (iVar5 == 0x101) {
          iVar5 = 0;
        }
        break;
      }
      iVar5 = iVar5 + 1;
      iVar4 = iVar4 + -1;
    } while (iVar4 != 0);
    *(int *)(iVar1 + 0x40) = iVar5;
    *(undefined4 *)(*(int *)(iVar1 + 0x38) + 0x1c) = 0;
  }
  uRam0000008c = 3;
  *(undefined4 *)(*(int *)(iVar1 + 0x38) + 8) = 1;
  puVar3 = (uint *)(*(int *)(iVar1 + 0x38) + 0x28);
  do {
  } while ((*puVar3 & 8) != 0);
  do {
  } while ((*puVar3 & 1) != 0);
  func_0x10025080(0xe,0);
  uVar2 = uRam10206580;
  *(undefined4 *)(iVar1 + 0x44) = 0;
  *(undefined4 *)(iVar1 + 0x48) = 0;
  gx8002_spi_register_master(uVar2);
  func_0x1002553c(0x10,uRam10206588,uRam10206584);
  return;
}

