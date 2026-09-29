
int FUN_00511990(float *param_1,float *param_2,float *param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint in_fpscr;
  float fVar7;
  undefined4 local_44;
  undefined4 local_40;
  undefined4 local_2c;
  
  uVar2 = DAT_00512384;
  uVar1 = FUN_0055f4f2(DAT_00512384,0);
  uVar2 = FUN_0055eff0(uVar2,0);
  iVar5 = DAT_00512388;
  iVar4 = DAT_00512388;
  iVar3 = FUN_0055f654(uVar1,&local_44);
  if (iVar3 == iVar5) {
    fVar7 = (float)VectorSignedToFloat(local_2c,(byte)(in_fpscr >> 0x16) & 3);
    *param_2 = fVar7 / DAT_00511bc0;
    fVar7 = (float)VectorSignedToFloat(local_40,(byte)(in_fpscr >> 0x16) & 3);
    *param_3 = fVar7 / DAT_00511bc0;
    fVar7 = (float)VectorSignedToFloat(local_44,(byte)(in_fpscr >> 0x16) & 3);
    *param_1 = fVar7 / DAT_00511bc0;
    iVar6 = FUN_0055f294(uVar2,param_4);
    iVar3 = iVar4;
    if (iVar6 != iVar5) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00512408,DAT_00512404,DAT_00512400,0x262,DAT_00512474,iVar6);
      }
      iVar5 = FUN_0043d0ce();
      if ((-1 < iVar5 << 0x1f) && (iVar5 = FUN_0043d0ce(), -1 < iVar5 << 0x1d)) {
        return iVar6;
      }
      compress_log_output(0x4400000,DAT_00512478,DAT_00512478,iVar6);
      return iVar6;
    }
  }
  else {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00512408,DAT_00512404,DAT_00512400,0x251,DAT_005123fc,iVar3);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_0051240c,DAT_0051240c,iVar3);
    }
  }
  iVar4 = FUN_0055f544(uVar1,0);
  if (iVar4 == iVar5) {
    iVar6 = FUN_0055f544(uVar1,1);
    iVar4 = iVar3;
    if (iVar6 != iVar5) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00512408,DAT_00512404,DAT_00512400,0x270,DAT_00512018,iVar6);
      }
      iVar5 = FUN_0043d0ce();
      iVar4 = iVar6;
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00512370,DAT_00512370,iVar6);
      }
    }
  }
  else {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00512408,DAT_00512404,DAT_00512400,0x26a,DAT_00512018,iVar4);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00512370,DAT_00512370,iVar4);
    }
  }
  return iVar4;
}

