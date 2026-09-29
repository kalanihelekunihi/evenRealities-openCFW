
void gx8002_subdf3(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 local_58;
  undefined4 uStack_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined1 auStack_48 [20];
  undefined1 auStack_34 [4];
  uint uStack_30;
  undefined1 auStack_20 [20];
  
  local_58 = param_1;
  uStack_54 = param_2;
  uStack_50 = param_3;
  uStack_4c = param_4;
  gx8002_unpack_double(&local_58,auStack_48);
  gx8002_unpack_double(&uStack_50,auStack_34);
  uStack_30 = uStack_30 ^ 1;
  gx8002_fpadd_parts(auStack_48,auStack_34,auStack_20);
  gx8002_pack_double();
  return;
}

