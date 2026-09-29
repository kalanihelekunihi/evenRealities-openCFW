
undefined8 FUN_004d93a4(int param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  undefined4 *puVar2;
  
  puVar2 = *(undefined4 **)(*param_2 + 8);
  if ((*(uint *)*puVar2 >> 8 & 0xc0) == 0x80) {
    bVar1 = FUN_004d9384(param_1,puVar2,param_2 + 1);
  }
  else {
    bVar1 = FUN_004d9384(param_1,puVar2,param_2[1]);
  }
  *(int **)(param_1 + 0x20) = param_2 + 3;
  return CONCAT44(param_4,(uint)bVar1);
}

