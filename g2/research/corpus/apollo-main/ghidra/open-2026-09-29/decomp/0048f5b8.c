
undefined8 FUN_0048f5b8(int param_1,uint *param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  undefined8 uVar6;
  uint local_20;
  undefined4 uStack_1c;
  
  uVar5 = 0;
  uVar3 = 0;
  uVar4 = 0;
  local_20 = param_3;
  uStack_1c = param_4;
  while( true ) {
    iVar1 = FUN_0048f454(param_1,&local_20);
    if (iVar1 == 0) {
      uVar2 = 0;
      goto LAB_0048f624;
    }
    if ((0x3e < uVar5) && ((local_20 & 0xfe) != 0)) break;
    uVar6 = FUN_004d914c(local_20 & 0x7f,0,uVar5);
    uVar3 = uVar3 | (uint)uVar6;
    uVar4 = uVar4 | (uint)((ulonglong)uVar6 >> 0x20);
    uVar5 = uVar5 + 7;
    if (-1 < (int)(local_20 << 0x18)) {
      *param_2 = uVar3;
      param_2[1] = uVar4;
      uVar2 = 1;
LAB_0048f624:
      return CONCAT44(local_20,uVar2);
    }
  }
  uVar2 = DAT_00490114;
  if (*(int *)(param_1 + 0xc) != 0) {
    uVar2 = *(undefined4 *)(param_1 + 0xc);
  }
  *(undefined4 *)(param_1 + 0xc) = uVar2;
  uVar2 = 0;
  goto LAB_0048f624;
}

