
undefined8 FUN_005de6ac(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  byte *pbVar1;
  undefined4 uVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  
  pbVar1 = (byte *)FUN_005de652(*(int *)(param_1 + 0x10) + 6,param_4);
  if (pbVar1 == (byte *)0x0) {
    uVar2 = 0;
  }
  else {
    uVar3 = (uint)pbVar1[3] | (uint)pbVar1[1] << 0x10 | (uint)*pbVar1 << 0x18 | (uint)pbVar1[2] << 8
    ;
    uVar5 = (uint)pbVar1[7] |
            (uint)pbVar1[5] << 0x10 | (uint)pbVar1[4] << 0x18 | (uint)pbVar1[6] << 8;
    if ((uVar3 == 0) || (iVar4 = FUN_005de590(uVar3 + *(int *)(param_1 + 0x10),param_3), iVar4 == 0)
       ) {
      if (uVar5 == 0) {
        uVar2 = 0;
      }
      else {
        uVar2 = FUN_005de5ee(*(int *)(param_1 + 0x10) + uVar5,param_3);
      }
    }
    else {
      uVar2 = (**(code **)(*(int *)(param_2 + 0xc) + 0xc))(param_2,param_3);
    }
  }
  return CONCAT44(param_4,uVar2);
}

