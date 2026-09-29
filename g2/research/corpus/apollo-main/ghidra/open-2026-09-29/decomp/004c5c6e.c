
void FUN_004c5c6e(ushort param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint local_2c;
  uint local_28;
  uint local_24;
  undefined4 uStack_20;
  
  uStack_20 = param_4;
  iVar3 = FUN_004c5c4c(param_1);
  iVar2 = DAT_004c61d4;
  iVar1 = DAT_004c61d0;
  if (-1 < iVar3) {
    if (param_2 == 0xd) {
      if (*(int *)(DAT_004c61d0 + iVar3 * 4) == 0) {
        *(int *)(DAT_004c61d0 + iVar3 * 4) = param_3;
      }
      else if ((*(int *)(DAT_004c61d4 + iVar3 * 4) != 0) &&
              (5000 < (uint)(param_3 - *(int *)(DAT_004c61d4 + iVar3 * 4)))) {
        uVar5 = (*(int *)(DAT_004c61d4 + iVar3 * 4) + 5000) - *(int *)(DAT_004c61d0 + iVar3 * 4);
        if (param_1 == 4) {
          local_2c = uVar5;
          FUN_0048eb32(DAT_004c61d8,1,&local_2c);
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(3,DAT_004c6184,DAT_004c6180,DAT_004c61e0,0xfe,DAT_004c61dc,uVar5);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0xc400000,DAT_004c61e4,DAT_004c61e4,uVar5);
          }
        }
        else {
          local_24 = (uint)param_1;
          local_28 = uVar5;
          FUN_0048eb32(DAT_004c61e8,2,&local_28);
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            local_2c = (uint)param_1;
            FUN_0043d574(3,DAT_004c6184,DAT_004c6180,DAT_004c61e0,0x104,DAT_004c61ec,uVar5);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0xc800000,DAT_004c61f0,DAT_004c61f0,uVar5,param_1);
          }
        }
        *(int *)(iVar1 + iVar3 * 4) = param_3;
        *(undefined4 *)(iVar2 + iVar3 * 4) = 0;
      }
    }
    else if (param_2 == 0xe) {
      *(int *)(DAT_004c61d4 + iVar3 * 4) = param_3;
    }
  }
  return;
}

