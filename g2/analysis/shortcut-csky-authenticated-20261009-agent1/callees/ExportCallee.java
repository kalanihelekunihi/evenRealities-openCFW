import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.pcode.*;
import ghidra.program.model.symbol.*;
public class ExportCallee extends GhidraScript {
 public void run() throws Exception {
  String[] a=getScriptArgs(); Address start=toAddr(Long.decode(a[0]));
  disassemble(start); Function f=createFunction(start,"callee_"+a[0].substring(2));
  if(f==null){println("FAILED_FUNCTION");return;}
  println("BODY "+f.getBody());
  for(Instruction i:currentProgram.getListing().getInstructions(f.getBody(),true)) {
   println("INSN "+i.getAddress()+" "+i);
   for(Reference r:i.getReferencesFrom()) println("REF "+i.getAddress()+" "+r.getReferenceType()+" "+r.getToAddress());
   for(PcodeOp p:i.getPcode()) println("PCODE "+p);
  }
  DecompInterface d=new DecompInterface();d.openProgram(currentProgram);
  DecompileResults r=d.decompileFunction(f,60,monitor);
  println("DECOMPILE_COMPLETE "+r.decompileCompleted()+" ERROR "+r.getErrorMessage());
  if(r.getDecompiledFunction()!=null)println(r.getDecompiledFunction().getC()); d.dispose();
 }
}
