
undefined4 FUN_005eaca0(ushort param_1,char *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  short sVar2;
  int iVar3;
  ushort uVar4;
  
  iVar1 = DAT_005eb28c;
  if (*(int *)(DAT_005eb28c + 4) != 0) {
    iVar3 = td_ring_ptr();
    if (iVar3 == 0) {
      uVar4 = 0;
    }
    else {
      uVar4 = *(ushort *)(iVar3 + 0x8500);
    }
    if (((uVar4 == 0) || (uVar4 <= param_1)) || (uVar4 != *(ushort *)(iVar1 + 0x1c4))) {
      FUN_005eaad4(param_2);
    }
    else {
      iVar3 = td_session_record_at(param_1);
      if (iVar3 == 0) {
        FUN_005eaad4(param_2);
      }
      else {
        sVar2 = FUN_005ea67a();
        if (sVar2 == *(short *)(iVar1 + (uint)param_1 * 2 + 0x3c)) {
          if (((*(char *)(iVar1 + 0x1c2) != '\0') && (*(ushort *)(iVar1 + 0x1c0) <= param_1)) &&
             (param_1 < (ushort)(*(short *)(iVar1 + 0x1c0) + 0xcU))) {
            FUN_005ea768((uint)param_1 - (uint)*(ushort *)(iVar1 + 0x1c0),param_1);
          }
          if ((param_2 != (char *)0x0) && (*param_2 != '\0')) {
            FUN_005eaa96(param_2);
          }
        }
        else {
          *(short *)(iVar1 + (uint)param_1 * 2 + 0x3c) = sVar2;
          FUN_005ea6da(param_1);
          *(undefined1 *)(iVar1 + 0x1c2) = 0;
          if ((param_2 == (char *)0x0) || (*param_2 == '\0')) {
            if ((*(char *)(iVar1 + 0x28c) == '\0') || (param_1 != (ushort)(uVar4 - 1))) {
              FUN_0044e498(*(undefined4 *)(iVar1 + 4));
              FUN_005ea926();
            }
            else {
              FUN_005ea992();
            }
          }
          else {
            FUN_005eaa96(param_2);
          }
        }
      }
    }
  }
  return param_4;
}

