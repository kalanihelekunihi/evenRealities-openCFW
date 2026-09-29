
undefined8 FUN_00460050(undefined4 param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  ushort uVar2;
  uint uVar3;
  
  uVar2 = 0;
  do {
    if (param_3 <= (int)(uint)uVar2) {
      uVar3 = 0xffff;
LAB_00460082:
      return CONCAT44(param_4,uVar3);
    }
    iVar1 = FUN_0046cacc(*(undefined4 *)(param_2 + (uint)uVar2 * 4),param_1);
    if (iVar1 == 0) {
      uVar3 = (uint)uVar2;
      goto LAB_00460082;
    }
    uVar2 = uVar2 + 1;
  } while( true );
}

