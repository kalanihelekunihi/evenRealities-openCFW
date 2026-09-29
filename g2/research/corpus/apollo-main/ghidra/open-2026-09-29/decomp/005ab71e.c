
undefined8 af_property_get_face_globals(int param_1,int *param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  int local_10;
  
  iVar1 = 0;
  if (param_1 == 0) {
    iVar1 = 0x23;
    local_10 = param_4;
  }
  else {
    local_10 = *(int *)(param_1 + 0x74);
    if ((local_10 == 0) && (iVar1 = af_face_globals_new(param_1,&local_10), iVar1 == 0)) {
      *(int *)(param_1 + 0x74) = local_10;
      *(undefined4 *)(param_1 + 0x78) = DAT_005abc2c;
    }
    if (iVar1 == 0) {
      *param_2 = local_10;
    }
  }
  return CONCAT44(local_10,iVar1);
}

