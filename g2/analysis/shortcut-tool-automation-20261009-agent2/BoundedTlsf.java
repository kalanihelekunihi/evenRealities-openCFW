import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import java.nio.file.*;

public class BoundedTlsf extends GhidraScript {
    public void run() throws Exception {
        Path output=Paths.get(getScriptArgs()[0]);
        long[][] ranges={{0x4d0524L,0x4d0554L},{0x4cffc2L,0x4d003aL},{0x4cfd18L,0x4cfd56L},{0x4cfd56L,0x4cfd66L}};
        for(long[] pair:ranges){
            Address a=toAddr(pair[0]);
            if(getFunctionAt(a)==null){
                currentProgram.getProgramContext().setValue(currentProgram.getRegister("TMode"),a,toAddr(pair[1]-1),java.math.BigInteger.ONE);
                AddressSet scope=new AddressSet(a,toAddr(pair[1]-1));
                new DisassembleCommand(a,scope,true).applyTo(currentProgram,monitor);
                createFunction(a,"bounded_"+Long.toHexString(pair[0]));
            }
        }
        DecompInterface decompiler=new DecompInterface();
        decompiler.openProgram(currentProgram);
        for(int n=0;n<2;n++){
            long[] pair=ranges[n];Address a=toAddr(pair[0]);Function f=getFunctionAt(a);
            if(!f.getBody().equals(new AddressSet(a,toAddr(pair[1]-1))))throw new Exception("Bounded body extent mismatch "+a);
            DecompileResults result=decompiler.decompileFunction(f,45,monitor);
            if(!result.decompileCompleted())throw new Exception(result.getErrorMessage());
            String header="// Private authenticated original-byte program; raw decompiler output.\n// "+currentProgram.getLanguageID()+" "+currentProgram.getCompilerSpec().getCompilerSpecID()+"\n// Body "+f.getBody()+"\n";
            Files.writeString(output.resolve(Long.toHexString(pair[0])+"-ghidra-raw.c"),header+result.getDecompiledFunction().getC());
            println("BOUNDED_BODY "+a+" "+f.getBody()+" SUCCESS");
        }
        decompiler.dispose();
    }
}
