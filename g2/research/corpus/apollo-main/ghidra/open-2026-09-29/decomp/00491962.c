
undefined8 FUN_00491962(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  byte bVar3;
  
  bVar3 = 0;
  do {
    if (0x1f < bVar3) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_2 = 0x162;
        FUN_0043d574(1,DAT_00491ee8,DAT_00491ee4,PTR_s_TF_AddTypeListener_00491f1c,0x162,
                     PTR_s__TF___error_Failed_to_add_type_l_00491f18,param_4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__TinyFrame__TF___error_Failed_to_00491f20,
                            PTR_s__TinyFrame__TF___error_Failed_to_00491f20);
      }
      uVar1 = 0;
LAB_004919e6:
      return CONCAT44(param_2,uVar1);
    }
    iVar2 = param_1 + (uint)bVar3 * 8;
    if (*(int *)(iVar2 + 0x7034) == 0) {
      *(undefined4 *)(iVar2 + 0x7034) = param_3;
      *(short *)(iVar2 + 0x7030) = (short)param_2;
      if (*(byte *)(param_1 + 0x7159) <= bVar3) {
        *(byte *)(param_1 + 0x7159) = bVar3 + 1;
      }
      uVar1 = 1;
      goto LAB_004919e6;
    }
    bVar3 = bVar3 + 1;
  } while( true );
}

