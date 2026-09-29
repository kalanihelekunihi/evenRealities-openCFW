
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong semantic_postprocess_samples(void)

{
  int iVar1;
  undefined4 uVar2;
  uint in_r3;
  uint uVar3;
  uint in_fpscr;
  
  if (*DAT_004a5ee0 != '\x04') {
    uVar3 = 0;
    while( true ) {
      iVar1 = DAT_004a5698;
      if (*(uint *)(DAT_004a5698 + 8) <= uVar3) break;
      if ((*(byte *)(uVar3 * 0x70 + DAT_004a5698 + 0x10) & 0x3f) >> 5 != 0) {
        uVar2 = semantic_normalize_heading((int)*(float *)(uVar3 * 0x70 + DAT_004a5698 + 0x70));
        uVar2 = VectorSignedToFloat(uVar2,(byte)(in_fpscr >> 0x16) & 3);
        *(undefined4 *)(uVar3 * 0x70 + iVar1 + 0x74) = uVar2;
        semantic_set_heading(*(undefined4 *)(uVar3 * 0x70 + iVar1 + 0x6c));
        semantic_set_magnetic_vector(uVar3 * 0x70 + iVar1 + 0x68);
      }
      if ((*(byte *)(uVar3 * 0x70 + iVar1 + 0x10) & 0xf) >> 3 != 0) {
        semantic_transform_vector(uVar3 * 0x70 + iVar1 + 0x4c,DAT_004a60d0);
      }
      uVar2 = DAT_004a60d0;
      semantic_transform_vector(uVar3 * 0x70 + iVar1 + 0x34,DAT_004a60d0);
      semantic_transform_vector(iVar1 + uVar3 * 0x70 + 0x40,uVar2);
      uVar3 = uVar3 + 1;
    }
    DRV_IMUSaveRawDataToCSV();
    if (*_DAT_004a5b6c == 1) {
      DRV_IMUCheckHeadUpEvent();
    }
    if (*_DAT_004a60d8 == 1) {
      DRV_IMUCheckCompassEvent();
    }
    if (*_DAT_004a60dc == 1) {
      semantic_noop_sample_callback();
    }
    if (*_DAT_004a60e0 == 1) {
      semantic_forward_periodic_sample();
    }
  }
  return (ulonglong)in_r3 << 0x20;
}

