
void FUN_005eabde(char *param_1)

{
  short sVar1;
  bool bVar2;
  int iVar3;
  undefined2 uVar4;
  int iVar5;
  int iVar6;
  
  iVar3 = DAT_005eb28c;
  bVar2 = false;
  if (*(int *)(DAT_005eb28c + 4) != 0) {
    iVar5 = td_ring_ptr();
    iVar6 = td_last_session_record();
    if (((iVar5 != 0) && (iVar6 != 0)) && (*(short *)(iVar5 + 0x8500) != 0)) {
      sVar1 = *(short *)(iVar5 + 0x8500);
      if (sVar1 == (short)(*(short *)(iVar3 + 0x1c4) + 1)) {
        uVar4 = FUN_005ea67a();
        *(undefined2 *)(iVar3 + (uint)(ushort)(sVar1 - 1U) * 2 + 0x3c) = uVar4;
        FUN_005ea6da(sVar1 - 1U);
        *(short *)(iVar3 + 0x1c4) = sVar1;
      }
      else {
        if ((sVar1 != 0x40) || (*(short *)(iVar3 + 0x1c4) != 0x40)) {
          FUN_005eaad4(param_1);
          return;
        }
        FUN_005eab8e();
        bVar2 = true;
      }
      *(undefined1 *)(iVar3 + 0x1c2) = 0;
      if ((param_1 == (char *)0x0) || (*param_1 == '\0')) {
        if (*(char *)(iVar3 + 0x28c) == '\0') {
          FUN_0044e498(*(undefined4 *)(iVar3 + 4));
          FUN_005ea926();
        }
        else {
          FUN_005ea992();
        }
      }
      else {
        FUN_005eaa96(param_1);
        if (bVar2) {
          FUN_0044e498(*(undefined4 *)(iVar3 + 4));
          FUN_005ea926();
        }
      }
    }
  }
  return;
}

