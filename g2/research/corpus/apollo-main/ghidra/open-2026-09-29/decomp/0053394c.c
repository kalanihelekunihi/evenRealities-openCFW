
undefined4 attsIndNtfCallback(undefined1 param_1,int param_2,undefined1 param_3,undefined4 param_4)

{
  byte bVar1;
  
  if (*(short *)(param_2 + 0x28) != 0) {
    attsExecCallback(param_1,*(undefined2 *)(param_2 + 0x28),param_3);
    *(undefined2 *)(param_2 + 0x28) = 0;
  }
  for (bVar1 = 0; bVar1 < 10; bVar1 = bVar1 + 1) {
    if (*(short *)(param_2 + (uint)bVar1 * 2 + 0x2a) != 0) {
      attsExecCallback(param_1,*(undefined2 *)(param_2 + (uint)bVar1 * 2 + 0x2a),param_3);
      *(undefined2 *)(param_2 + (uint)bVar1 * 2 + 0x2a) = 0;
    }
  }
  return param_4;
}

