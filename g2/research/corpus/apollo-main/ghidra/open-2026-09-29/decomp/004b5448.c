
void attcProcRsp(int *param_1,ushort param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  code *pcVar3;
  undefined2 local_28;
  byte local_26;
  char local_25;
  int local_24;
  short local_20;
  undefined2 local_1e;
  undefined1 local_1c;
  undefined4 uStack_18;
  
  if (*(char *)((int)param_1 + 6) != '\0') {
    uVar2 = (*(byte *)(param_3 + 8) & 0xfffffffe) / 2;
    local_26 = (byte)uVar2;
    if ((local_26 < 0x12) && ((local_26 == 0 || (uVar2 == *(byte *)((int)param_1 + 6))))) {
      uStack_18 = param_4;
      WsfTimerStop(param_1 + 6);
      local_24 = param_3 + 9;
      local_20 = param_2 - 1;
      local_1e = (undefined2)param_1[3];
      local_25 = '\0';
      pcVar3 = *(code **)(DAT_004b59a0 + (uint)local_26 * 4);
      if (pcVar3 != (code *)0x0) {
        if (param_2 < *(byte *)(DAT_004b59a4 + (uint)local_26)) {
          return;
        }
        (*pcVar3)(param_1,param_2,param_3,&local_28);
      }
      if ((*(char *)((int)param_1 + 7) == '\0') || (local_25 != '\0')) {
        *(undefined1 *)((int)param_1 + 6) = 0;
        attcFreePkt(param_1 + 1);
      }
      if ((local_26 != 1) && (*(int *)(DAT_004b599c + 0x58) != 0)) {
        local_1c = *(undefined1 *)((int)param_1 + 7);
        local_28 = (undefined2)param_1[1];
        (**(code **)(DAT_004b599c + 0x58))(&local_28);
      }
      iVar1 = DAT_004b59a8;
      if (-1 < (int)((uint)*(byte *)(*param_1 + (uint)*(byte *)(param_1 + 10) * 4 + 2) << 0x1e)) {
        if (param_1[2] == 0) {
          if (((char)param_1[10] == '\0') &&
             (*(char *)((uint)*(byte *)((int)param_1 + 0x29) * 0xc + DAT_004b59a8 + 0x182) != '\0'))
          {
            attcSetupReq(param_1,(uint)*(byte *)((int)param_1 + 0x29) * 0xc + DAT_004b59a8 + 0x180);
            *(undefined1 *)(iVar1 + (uint)*(byte *)((int)param_1 + 0x29) * 0xc + 0x182) = 0;
          }
        }
        else {
          attcSendReq(param_1);
        }
      }
    }
  }
  return;
}

