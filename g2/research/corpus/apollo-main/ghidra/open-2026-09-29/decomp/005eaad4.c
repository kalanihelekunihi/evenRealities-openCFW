
undefined8 FUN_005eaad4(char *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined2 uVar2;
  int iVar3;
  ushort uVar4;
  ushort uVar5;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 uStack_18;
  
  iVar1 = DAT_005eb28c;
  local_20 = param_2;
  local_1c = param_3;
  if (*(int *)(DAT_005eb28c + 4) != 0) {
    uStack_18 = param_4;
    FUN_005eaa54(param_1,&local_1c,&local_20);
    FUN_005ea9f6();
    *(undefined1 *)(iVar1 + 0x28c) = (undefined1)local_20;
    iVar3 = td_ring_ptr();
    if (iVar3 == 0) {
      uVar4 = 0;
    }
    else {
      uVar4 = *(ushort *)(iVar3 + 0x8500);
    }
    if (uVar4 != 0) {
      for (uVar5 = 0; uVar5 < uVar4; uVar5 = uVar5 + 1) {
        iVar3 = td_session_record_at(uVar5);
        if (iVar3 == 0) {
          *(undefined2 *)(iVar1 + (uint)uVar5 * 2 + 0x3c) = 0x1c;
        }
        else {
          uVar2 = FUN_005ea67a();
          *(undefined2 *)(iVar1 + (uint)uVar5 * 2 + 0x3c) = uVar2;
        }
      }
      FUN_005ea6da(0);
      *(ushort *)(iVar1 + 0x1c4) = uVar4;
      *(undefined1 *)(iVar1 + 0x1c2) = 0;
      if ((param_1 == (char *)0x0) || (*param_1 == '\0')) {
        if (*(char *)(iVar1 + 0x28c) == '\0') {
          FUN_0044ea04(*(undefined4 *)(iVar1 + 4),local_1c,0);
          FUN_005ea926(local_1c);
        }
        else {
          FUN_005ea992();
        }
      }
      else {
        FUN_005eaa96(param_1);
      }
    }
  }
  return CONCAT44(local_1c,local_20);
}

