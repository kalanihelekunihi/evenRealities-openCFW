
undefined4 DRV_IMUCheckHeadUpEvent(void)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  undefined4 in_r3;
  uint uVar4;
  uint in_fpscr;
  float fVar5;
  float fVar6;
  
  uVar4 = 0;
  do {
    iVar2 = DAT_004a5b70;
    iVar3 = DAT_004a5698;
    if (*(uint *)(DAT_004a5698 + 8) <= uVar4) {
      return 0;
    }
    fVar5 = (float)semantic_filter_update
                             (*(undefined4 *)(uVar4 * 0x70 + DAT_004a5698 + 0x3c),DAT_004a5b70);
    piVar1 = DAT_004a56cc;
    if ((*(byte *)(uVar4 * 0x70 + iVar3 + 0x10) & 0x3f) >> 5 == 0) {
LAB_004a4f08:
      if ((*(byte *)(uVar4 * 0x70 + iVar3 + 0x10) & 0x3f) >> 5 != 0) {
        fVar5 = (float)VectorSignedToFloat(*DAT_004a56cc + -0x14,(byte)(in_fpscr >> 0x16) & 3);
        in_fpscr = in_fpscr & 0xfffffff;
        if ((*(float *)(uVar4 * 0x70 + iVar3 + 0x6c) < fVar5) && (*DAT_004a5b78 == '\x01')) {
          *DAT_004a5b78 = '\0';
          *DAT_004a5b7c = '\x01';
          semantic_emit_imu_event(7,0);
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(2,DAT_004a5378,DAT_004a5374,DAT_004a5b84,0x43d,DAT_004a5b80,
                         (double)*(float *)(uVar4 * 0x70 + iVar3 + 0x6c));
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x8400000,DAT_004a5b88,DAT_004a5b88);
          }
        }
      }
    }
    else {
      fVar6 = (float)VectorSignedToFloat(*DAT_004a56cc,(byte)(in_fpscr >> 0x16) & 3);
      in_fpscr = in_fpscr & 0xfffffff;
      if (((*(float *)(uVar4 * 0x70 + iVar3 + 0x6c) <= fVar6) || (*(float *)(iVar2 + 0x38) <= fVar5)
          ) || (*DAT_004a5b7c != '\x01')) goto LAB_004a4f08;
      *DAT_004a5b7c = '\0';
      *DAT_004a5b78 = '\x01';
      semantic_emit_imu_event(6,0);
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,DAT_004a5378,DAT_004a5374,DAT_004a5b84,0x438,DAT_004a5b8c,
                     (double)*(float *)(uVar4 * 0x70 + iVar3 + 0x6c),*piVar1,in_r3);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8800000,DAT_004a5d00);
      }
    }
    uVar4 = uVar4 + 1;
  } while( true );
}

