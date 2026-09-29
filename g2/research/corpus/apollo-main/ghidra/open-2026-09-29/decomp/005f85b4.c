
undefined4 tt_get_sfnt_checksum(int param_1,ushort param_2)

{
  undefined4 uVar1;
  int iVar2;
  
  if (*(int *)(param_1 + 0x204) == 0) {
    uVar1 = 0;
  }
  else {
    iVar2 = (**(code **)(param_1 + 0x204))
                      (param_1,*(undefined4 *)(*(int *)(param_1 + 0x9c) + (uint)param_2 * 0x10),
                       *(undefined4 *)(param_1 + 0x68),0);
    if (iVar2 == 0) {
      uVar1 = tt_synth_sfnt_checksum
                        (*(undefined4 *)(param_1 + 0x68),
                         *(undefined4 *)(*(int *)(param_1 + 0x9c) + (uint)param_2 * 0x10 + 0xc));
    }
    else {
      uVar1 = 0;
    }
  }
  return uVar1;
}

