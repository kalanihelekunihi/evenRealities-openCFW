
undefined8 INP_MessageProcesser(uint *param_1,undefined4 param_2,undefined4 param_3)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  uVar1 = 0;
  uVar4 = *param_1;
  uVar3 = 0;
  do {
    if (4 < uVar3) {
      if (uVar3 == 5) {
        iVar2 = FUN_0043d0ce(uVar1);
        if (iVar2 << 0x1e < 0) {
          param_2 = 0xc6;
          param_3 = DAT_00513510;
          FUN_0043d574(1,PTR_s_thread_input_005134c8,DAT_005134c4,DAT_00513514,0xc6,DAT_00513510,
                       uVar4 & 0xffff);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_00513518,DAT_00513518,uVar4 & 0xffff);
        }
      }
LAB_0051301a:
      return CONCAT44(param_3,param_2);
    }
    uVar1 = uVar4 & 0xffff;
    if ((uVar1 == *(ushort *)(DAT_0051350c + uVar3 * 8)) &&
       (uVar1 = 0, *(int *)(DAT_0051350c + uVar3 * 8 + 4) != 0)) {
      (**(code **)(DAT_0051350c + uVar3 * 8 + 4))(param_1);
      goto LAB_0051301a;
    }
    uVar3 = uVar3 + 1;
  } while( true );
}

