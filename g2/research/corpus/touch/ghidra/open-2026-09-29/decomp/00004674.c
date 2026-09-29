
uint reset_startup_handler(void)

{
  undefined4 uVar1;
  int iVar2;
  int *piVar3;
  int *piVar4;
  uint uVar5;
  undefined4 in_cr14;
  
  touch_leaf_1370_passthrough();
  touch_runtime_141c_handoff();
  uVar1 = uRam000046dc;
  memcpy(uRam000046dc,uRam000046e0,0xc0);
  *(undefined4 *)(iRam000046e4 + 8) = uVar1;
  DataSynchronizationBarrier(0xf);
  for (piVar4 = piRam000046e8; piVar3 = piRam000046f0, piVar4 < piRam000046ec; piVar4 = piVar4 + 3)
  {
    for (uVar5 = 0; uVar5 < (uint)piVar4[2]; uVar5 = uVar5 + 1) {
      *(undefined4 *)(piVar4[1] + uVar5 * 4) = *(undefined4 *)(*piVar4 + uVar5 * 4);
    }
  }
  for (; piVar3 < piRam000046f4; piVar3 = piVar3 + 2) {
    for (uVar5 = 0; uVar5 < (uint)piVar3[1]; uVar5 = uVar5 + 1) {
      *(undefined4 *)(*piVar3 + uVar5 * 4) = 0;
    }
  }
  touch_runtime_0164_reset_entry();
  coprocessor_store(0,in_cr14,0);
  uVar5 = *(uint *)(DAT_00004714 + 0x28) >> 6 & 3;
  iVar2 = Cy_SysClk_ClkHfGetFrequency(0);
  return iVar2 + ((uint)(1 << uVar5) >> 1) >> uVar5;
}

