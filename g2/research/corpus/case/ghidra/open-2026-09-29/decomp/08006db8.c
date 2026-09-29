
undefined4 case_prepare_controller_wait(int param_1)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar1 = DAT_08006e04;
  uVar3 = 0;
  *(uint *)(DAT_08006e04 + 0xc) = *(uint *)(DAT_08006e04 + 0xc) & 0xffffff7f;
  if (*(int *)(iVar1 + 0x18) * 0x4000000 < 0) {
    *(uint *)(iVar1 + 0x18) = *(uint *)(iVar1 + 0x18) & 0xffffffdf;
    iVar2 = case_wait_status_bit5();
    if (iVar2 != 0) {
      *(undefined1 *)(param_1 + 0x29) = 3;
      uVar3 = 3;
    }
    *(uint *)(iVar1 + 0x18) = *(uint *)(iVar1 + 0x18) | 0x20;
  }
  else {
    iVar1 = case_wait_status_bit5();
    if (iVar1 != 0) {
      *(undefined1 *)(param_1 + 0x29) = 3;
      uVar3 = 3;
    }
  }
  return uVar3;
}

