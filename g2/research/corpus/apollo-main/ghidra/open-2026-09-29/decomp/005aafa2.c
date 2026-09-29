
undefined8 af_loader_reset(int *param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = 0;
  *param_1 = param_3;
  param_1[1] = *(int *)(param_3 + 0x74);
  if ((param_1[1] == 0) && (iVar1 = af_face_globals_new(param_3,param_1 + 1,param_2), iVar1 == 0)) {
    *(int *)(param_3 + 0x74) = param_1[1];
    *(undefined4 *)(param_3 + 0x78) = DAT_005abc2c;
  }
  return CONCAT44(param_4,iVar1);
}

