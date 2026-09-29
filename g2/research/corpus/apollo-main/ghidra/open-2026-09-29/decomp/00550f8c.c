
void FUN_00550f8c(byte param_1)

{
  int iVar1;
  int iVar2;
  int local_68;
  undefined4 local_64;
  undefined4 local_48;
  undefined4 local_38;
  
  if (((param_1 < 10) && (iVar2 = *(int *)(DAT_00550ff4 + (uint)param_1 * 4 + 0x10), iVar2 != 0)) &&
     (iVar1 = FUN_0043e0e0(iVar2,1), iVar1 == 0)) {
    FUN_004503d6(&local_68);
    local_68 = iVar2;
    FUN_004506ce(&local_68,0xff,0);
    local_38 = 200;
    local_64 = DAT_00551808;
    local_48 = DAT_0055180c;
    FUN_00450408(&local_68);
  }
  return;
}

