
int ReadSimpleMode(int param_1,int param_2,uint param_3,int param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int extraout_r1;
  undefined4 uVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  
  uVar4 = *(undefined4 *)(param_4 + 4);
  __aeabi_uidivmod(param_1,uVar4);
  iVar2 = __aeabi_uidiv(extraout_r1 + param_3 + -1,uVar4);
  iVar6 = *(int *)(param_4 + 0x10) + (param_1 - extraout_r1);
  uVar7 = 0;
  iVar3 = extraout_r1;
  while( true ) {
    if (iVar2 + 1U <= uVar7) {
      return 0;
    }
    (*(code *)(*(undefined4 **)(param_4 + 0x1c))[5])
              (**(undefined4 **)(param_4 + 0x1c),iVar6,*(undefined4 *)(param_4 + 4),DAT_0000867c);
    iVar1 = DAT_0000867c;
    uVar5 = *(int *)(param_4 + 4) - iVar3;
    if (param_3 < uVar5) {
      uVar5 = param_3;
    }
    memcpy(iVar3 + DAT_0000867c,param_2,uVar5);
    iVar3 = em_eeprom_row_read_helper(iVar6,iVar1,param_4);
    if (iVar3 != 0) break;
    *(int *)(param_4 + 0x18) = iVar6;
    param_3 = param_3 - uVar5;
    param_2 = param_2 + uVar5;
    iVar6 = iVar6 + (*(uint *)(param_4 + 4) & 0xfffffffc);
    uVar7 = uVar7 + 1;
    iVar3 = 0;
  }
  return iVar3;
}

