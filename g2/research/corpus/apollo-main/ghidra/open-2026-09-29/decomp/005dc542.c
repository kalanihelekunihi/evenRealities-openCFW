
undefined4 FUN_005dc542(int param_1,int param_2)

{
  byte bVar1;
  uint uVar2;
  byte *pbVar3;
  
  if (*(uint *)(param_2 + 0x84) < param_1 + 4U) {
    ft_validator_run(param_2,8);
  }
  uVar2 = (uint)CONCAT11(*(undefined1 *)(param_1 + 2),*(undefined1 *)(param_1 + 3));
  if ((*(uint *)(param_2 + 0x84) < param_1 + uVar2) || (uVar2 < 0x106)) {
    ft_validator_run(param_2,8);
  }
  if (*(char *)(param_2 + 0x88) != '\0') {
    pbVar3 = (byte *)(param_1 + 6);
    for (uVar2 = 0; uVar2 < 0x100; uVar2 = uVar2 + 1) {
      bVar1 = *pbVar3;
      pbVar3 = pbVar3 + 1;
      if (*(uint *)(param_2 + 0x90) <= (uint)bVar1) {
        ft_validator_run(param_2,0x10);
      }
    }
  }
  return 0;
}

