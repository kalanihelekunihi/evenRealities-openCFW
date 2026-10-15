import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;

public class G2LabelCallbackDecompile extends GhidraScript {
    @Override
    public void run() throws Exception {
        Address addr = toAddr(0x53fcc4);
        Function f = getFunctionAt(addr);
        if (f == null) {
            disassemble(addr);
            f = createFunction(addr, "audio_uart_ambiq_label_pixel_53fcc4");
        }
        println("LABEL_CALLBACK_FUNCTION " + f);
        if (f == null) return;
        println("LABEL_CALLBACK_BODY " + f.getBody());
        DecompInterface iface = new DecompInterface();
        iface.openProgram(currentProgram);
        DecompileResults result = iface.decompileFunction(f, 120, monitor);
        println("LABEL_CALLBACK_DECOMPILE_SUCCESS " + result.decompileCompleted());
        if (result.decompileCompleted()) {
            println("LABEL_CALLBACK_PSEUDOCODE_START");
            println(result.getDecompiledFunction().getC());
            println("LABEL_CALLBACK_PSEUDOCODE_END");
        }
    }
}
