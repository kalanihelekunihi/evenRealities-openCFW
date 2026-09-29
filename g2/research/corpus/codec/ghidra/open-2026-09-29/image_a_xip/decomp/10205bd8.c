
int gx8002_snpu_process_status(void)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;
  int iVar7;
  undefined4 *puVar8;
  undefined4 uVar9;
  uint local_34;
  int iStack_30;
  
  puVar1 = DAT_10205cdc;
  gx8002_npu_get_interrupt(DAT_10205cdc[0x171],&local_34);
  gx8002_npu_clr_interrupt_without_overflow(puVar1[0x171],local_34);
  if ((local_34 & 1) == 0) {
    if (((local_34 & 8) == 0) && ((local_34 & 4) == 0)) {
      if ((local_34 & 0x20) == 0) {
        return (byte)~((local_34 & 0x40) != 0) + 1;
      }
      gx8002_npu_get_op_overflow_cmd_addr(puVar1[0x171],&iStack_30);
      gx8002_npu_clr_overflow_interrupt(puVar1[0x171],local_34);
    }
    else {
      gx8002_snpu_overtime_reset();
    }
  }
  else {
    gx8002_npu_get_over_cmd_addr(puVar1[0x171],&iStack_30);
    if (puVar1[0x174] != iStack_30) {
      puVar1[0x174] = iStack_30;
      uVar6 = 1;
      iVar7 = puVar1[0x16d];
      iVar3 = puVar1[0x16c];
      while( true ) {
        puVar8 = (undefined4 *)(iStack_30 + 0x20000000);
        uVar5 = puVar1[(iVar3 + 1) * 0x24];
        uVar9 = puVar1[iVar3 * 0x24 + 0x25];
        uVar2 = puVar1[iVar3 * 0x24 + 0x26];
        iVar4 = (iVar3 + 1) % 10;
        if (iVar7 == iVar4) {
          uVar6 = 2;
          gx8002_snpu_suspend();
        }
        if (puVar1 + iVar3 * 0x24 + 4 == puVar8) break;
        iVar3 = iVar4;
        if (uVar5 != 0) {
          (*(code *)(uVar5 & 0xfffffffe))(uVar9,uVar6,uVar2);
        }
      }
      *puVar1 = uVar6;
      puVar1[0x16c] = iVar4;
      if (uVar5 != 0) {
        (*(code *)(uVar5 & 0xfffffffe))(uVar9,uVar6);
      }
    }
  }
  return 0;
}

