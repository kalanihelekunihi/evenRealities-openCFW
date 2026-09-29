
void FUN_004919e8(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  byte bVar3;
  short *psVar4;
  int *piVar5;
  short local_2c;
  undefined1 local_2a;
  short local_28;
  int local_24;
  undefined2 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  FUN_004916b8(&local_2c);
  local_2c = *(short *)(param_1 + 0x14);
  local_2a = 0;
  local_28 = *(short *)(param_1 + 0x601e);
  local_24 = param_1 + 0x18;
  local_20 = *(undefined2 *)(param_1 + 0x16);
  for (bVar3 = 0; bVar3 < *(byte *)(param_1 + 0x7158); bVar3 = bVar3 + 1) {
    iVar2 = param_1 + (uint)bVar3 * 0x18;
    psVar4 = (short *)(iVar2 + 0x6430);
    if ((*(int *)(iVar2 + 0x6434) != 0) && (*psVar4 == local_2c)) {
      local_1c = *(undefined4 *)(iVar2 + 0x6440);
      local_18 = *(undefined4 *)(iVar2 + 0x6444);
      cVar1 = (**(code **)(iVar2 + 0x6434))(param_1,&local_2c);
      *(undefined4 *)(iVar2 + 0x6440) = local_1c;
      *(undefined4 *)(iVar2 + 0x6444) = local_18;
      if (cVar1 != '\0') {
        if (cVar1 == '\x02') {
          FUN_00491838(psVar4);
          return;
        }
        if (cVar1 != '\x03') {
          return;
        }
        *(undefined4 *)(iVar2 + 0x6440) = 0;
        *(undefined4 *)(iVar2 + 0x6444) = 0;
        FUN_0049183e(param_1,bVar3,psVar4);
        return;
      }
    }
  }
  local_1c = 0;
  local_18 = 0;
  for (bVar3 = 0; bVar3 < *(byte *)(param_1 + 0x7159); bVar3 = bVar3 + 1) {
    iVar2 = param_1 + (uint)bVar3 * 8;
    if (((*(int *)(iVar2 + 0x7034) != 0) && (*(short *)(iVar2 + 0x7030) == local_28)) &&
       (cVar1 = (**(code **)(iVar2 + 0x7034))(param_1,&local_2c), cVar1 != '\0')) {
      if (cVar1 != '\x03') {
        return;
      }
      FUN_0049188e(param_1,bVar3,(short *)(iVar2 + 0x7030));
      return;
    }
  }
  bVar3 = 0;
  while( true ) {
    if (*(byte *)(param_1 + 0x715a) <= bVar3) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00491ee8,DAT_00491ee4,PTR_s_TF_HandleReceivedMessage_00491f28,0x211,
                     PTR_s__TF___error_Unhandled_message__t_00491f24,local_28);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,PTR_s__TinyFrame__TF___error_Unhandled_00491f2c,
                            PTR_s__TinyFrame__TF___error_Unhandled_00491f2c,local_28);
      }
      return;
    }
    piVar5 = (int *)(param_1 + (uint)bVar3 * 4 + 0x7130);
    if ((*piVar5 != 0) && (cVar1 = (*(code *)*piVar5)(param_1,&local_2c), cVar1 != '\0')) break;
    bVar3 = bVar3 + 1;
  }
  if (cVar1 != '\x03') {
    return;
  }
  FUN_004918a8(param_1,bVar3,piVar5);
  return;
}

