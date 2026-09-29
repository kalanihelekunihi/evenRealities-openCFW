
undefined8 FUN_005e4d10(int param_1,int param_2,char param_3,int param_4)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  
  if ((param_1 == 0) || (*(int *)(param_1 + 0x214) == 0)) {
    uVar2 = 0;
  }
  else if ((param_2 == 0x44) &&
          (((*(char *)(param_1 + 0x27c) == '\0' && (*(char *)(param_1 + 0x279) == '\0')) &&
           (param_3 != '\0')))) {
    iVar3 = FUN_0044e498(*(undefined4 *)(param_1 + 0x214));
    if ((iVar3 < 1) || (iVar3 <= param_4)) {
      uVar2 = 0;
    }
    else {
      iVar3 = FUN_005eb576(2,param_4);
      if ((iVar3 == 0) ||
         (iVar3 = FUN_005eb47a(*(undefined1 *)(param_1 + 0x279),param_4), iVar3 == 0)) {
        bVar1 = 1;
      }
      else {
        bVar1 = 0;
      }
      uVar2 = (uint)bVar1;
    }
  }
  else {
    uVar2 = 0;
  }
  return CONCAT44(param_4,uVar2);
}

