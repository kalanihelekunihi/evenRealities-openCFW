
undefined8
FUN_004918c2(int param_1,undefined2 *param_2,undefined4 param_3,undefined4 param_4,
            undefined2 param_5)

{
  int iVar1;
  undefined4 uVar2;
  byte bVar3;
  
  bVar3 = 0;
  do {
    if (0x7f < bVar3) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_3 = 0x14c;
        FUN_0043d574(1,DAT_00491ee8,DAT_00491ee4,DAT_00491f10,0x14c,DAT_00491f0c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__TinyFrame__TF___error_Failed_to_00491f14,
                            PTR_s__TinyFrame__TF___error_Failed_to_00491f14);
      }
      uVar2 = 0;
LAB_00491960:
      return CONCAT44(param_3,uVar2);
    }
    iVar1 = param_1 + (uint)bVar3 * 0x18;
    if (*(int *)(iVar1 + 0x6434) == 0) {
      *(undefined4 *)(iVar1 + 0x6434) = param_3;
      *(undefined4 *)(iVar1 + 0x6438) = param_4;
      *(undefined2 *)(iVar1 + 0x6430) = *param_2;
      *(undefined4 *)(iVar1 + 0x6440) = *(undefined4 *)(param_2 + 8);
      *(undefined4 *)(iVar1 + 0x6444) = *(undefined4 *)(param_2 + 10);
      *(undefined2 *)(iVar1 + 0x643c) = param_5;
      *(undefined2 *)(iVar1 + 0x643e) = *(undefined2 *)(iVar1 + 0x643c);
      if (*(byte *)(param_1 + 0x7158) <= bVar3) {
        *(byte *)(param_1 + 0x7158) = bVar3 + 1;
      }
      uVar2 = 1;
      goto LAB_00491960;
    }
    bVar3 = bVar3 + 1;
  } while( true );
}

