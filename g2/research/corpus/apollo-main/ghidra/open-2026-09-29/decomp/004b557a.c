
undefined8 attcProcInd(int *param_1,uint param_2,int param_3,uint param_4)

{
  short sVar1;
  int iVar2;
  ushort local_18;
  char local_16;
  undefined1 local_15;
  uint local_14;
  short local_10;
  short local_e;
  uint local_c;
  
  local_18 = (ushort)param_1;
  local_16 = (char)((uint)param_1 >> 0x10);
  local_15 = (undefined1)((uint)param_1 >> 0x18);
  local_14 = param_2;
  if (2 < (param_2 & 0xffff)) {
    local_16 = (char)((*(byte *)(param_3 + 8) & 0xfffffffe) / 2);
    sVar1 = (ushort)*(byte *)(param_3 + 10) * 0x100 + (ushort)*(byte *)(param_3 + 9);
    local_14 = param_3 + 0xb;
    _local_10 = CONCAT22(sVar1,(short)param_2 + -3);
    local_18 = (ushort)*(byte *)(*param_1 + 0xe);
    local_15 = 0;
    local_c = param_4 & 0xffffff00;
    if ((sVar1 != 0) && (*(int *)(DAT_004b599c + 0x58) != 0)) {
      (**(code **)(DAT_004b599c + 0x58))(&local_18);
    }
    if ((*(char *)(DAT_004b59a8 + 0x1b4) == '\0') || (local_16 != '\x0e')) {
      *(byte *)(*param_1 + (uint)*(byte *)(param_1 + 10) * 4 + 2) =
           *(byte *)(*param_1 + (uint)*(byte *)(param_1 + 10) * 4 + 2) | 0x10;
    }
    else if ((-1 < (int)((uint)*(byte *)(*param_1 + (uint)*(byte *)(param_1 + 10) * 4 + 2) << 0x1e))
            && (iVar2 = attMsgAlloc(9), iVar2 != 0)) {
      *(undefined1 *)(iVar2 + 8) = 0x1e;
      L2cDataReq(4,*(undefined2 *)(*param_1 + 0xc),1);
    }
  }
  return CONCAT44(local_14,CONCAT13(local_15,CONCAT12(local_16,local_18)));
}

