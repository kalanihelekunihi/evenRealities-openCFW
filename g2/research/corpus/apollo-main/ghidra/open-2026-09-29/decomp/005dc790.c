
int FUN_005dc790(int param_1,uint param_2)

{
  undefined1 *puVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  if (param_2 < 0x10000) {
    iVar2 = param_1 + 0x206;
    if (param_2 >> 8 == 0) {
      puVar1 = (undefined1 *)(param_1 + 6 + (param_2 & 0xff) * 2);
      iVar3 = iVar2;
      if (CONCAT11(*puVar1,puVar1[1]) != 0) {
        return 0;
      }
    }
    else {
      puVar1 = (undefined1 *)(param_1 + 6 + (param_2 >> 8) * 2);
      iVar3 = iVar2 + (CONCAT11(*puVar1,puVar1[1]) & 0xfffffff8);
      if (iVar3 == iVar2) {
        return 0;
      }
    }
  }
  return iVar3;
}

