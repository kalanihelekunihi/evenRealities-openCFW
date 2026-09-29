
void _ringEnableCccd(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte *pbVar1;
  int iVar2;
  uint local_1c;
  undefined4 uStack_18;
  
  pbVar1 = DAT_004c4c68;
  uStack_18 = param_4;
  if (((((param_1 & 0xff) == 0) || ((param_1 & 0xff) != (uint)*DAT_004c4c68)) ||
      (param_1 >> 0x10 != (uint)*(ushort *)(DAT_004c4c68 + 8))) ||
     ((iVar2 = DmConnInUse(param_1 & 0xff), iVar2 == 0 ||
      (*(short *)(*(int *)(pbVar1 + 4) + 4) == 0)))) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_1c = (uint)*(ushort *)(DAT_004c4c68 + 8);
      FUN_0043d574(2,DAT_004c4c78,DAT_004c4c74,DAT_004c4c70,0x76,DAT_004c4c6c,param_1 & 0xff,
                   param_1 >> 0x10,*DAT_004c4c68);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x9000000,DAT_004c4c7c,DAT_004c4c7c,param_1 & 0xff,param_1 >> 0x10,
                          *DAT_004c4c68,*(undefined2 *)(DAT_004c4c68 + 8));
    }
  }
  else {
    local_1c = CONCAT22(local_1c._2_2_,*DAT_004c4c80);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004c4c78,DAT_004c4c74,DAT_004c4c70,0x7e,DAT_004c4c84,param_1 & 0xff,
                   *(undefined2 *)(*(int *)(pbVar1 + 4) + 4),param_1 >> 8 & 0xff);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xcc00000,DAT_004c4c88,DAT_004c4c88,param_1 & 0xff,
                          *(undefined2 *)(*(int *)(pbVar1 + 4) + 4),param_1 >> 8 & 0xff);
    }
    AttcWriteReq(param_1 & 0xff,*(undefined2 *)(*(int *)(pbVar1 + 4) + 4),2,&local_1c);
    if ((param_1 >> 8 & 0xff) == 1) {
      Thread_SendEvtToRingTask(4);
    }
  }
  return;
}

