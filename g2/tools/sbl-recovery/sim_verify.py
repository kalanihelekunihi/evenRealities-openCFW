#!/usr/bin/env python3
"""End-to-end sim: OTAP-armed reset → HLE SBL → host stock reflash. No hardware."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # evenRealities-OpenCFW
EMU = Path("/Users/kalani/Repo/g2-firmware-emulator")
WEBFLASHER = Path("/Users/kalani/Repo/SybilSight-webflasher")
WORKDIR = ROOT / "build/em9305-nor-20261122"
STOCK_OTA = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
STOCK_OTA_SHA = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
STOCK_APP = WORKDIR / "stock.app.bin"
OPENCFW_APP = WORKDIR / "opencfw-otap-disarm.app.bin"
ITCM = WORKDIR / "itcm.bin"
NOR = WORKDIR / "nor-with-em9305.bin"
NOR_SHA = "69efc6d023779beec9dada757ec9fe852f9454b4b84bae6fe8421c703f35c9d1"
PLAT = WORKDIR / "platform.repl"
STOCK_RESET = 0x005E4233
STOCK_SP = 0x2007FB00

sys.path.insert(0, str(EMU / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(WEBFLASHER / "scripts"))

from g2emu.renode_console import RenodeConsole
from g2_sbl_recovery import RenodeSblTransport, run_update, STOCK_SHA256
from g2_sbl_wire import data_frame, hello_frame, ota_descriptor_frame, parse_ack, update_frame
from g2_sbl_protocol import find_status_frames


def scalar(output: str) -> str:
    matches = re.findall(r"(?m)^(0x[0-9A-Fa-f]+|True|False)\s*$", output.replace("\r", ""))
    if not matches:
        raise RuntimeError(f"no scalar in: {output[-400:]}")
    return matches[-1]


def setup_resc_commands() -> str:
    return f"""
include @renode/peripherals/G2Apollo510_GPIO.cs
include @renode/peripherals/G2Apollo510_Timer.cs
include @renode/peripherals/G2Apollo510_UART.cs
include @renode/peripherals/G2Apollo510_IOMaster.cs
include @renode/peripherals/G2Apollo510_SystemTimer.cs
include @renode/peripherals/G2Apollo510_RTC.cs
include @renode/peripherals/G2Apollo510_Watchdog.cs
include @renode/peripherals/G2Apollo510_SblWired.cs
include @renode/peripherals/G2Apollo510_ADC.cs
include @renode/peripherals/G2Apollo510_PowerController.cs
include @renode/peripherals/G2Apollo510_PDM.cs
include @renode/peripherals/G2Apollo510_I2S.cs
include @renode/peripherals/G2Apollo510_CoreControl.cs
include @renode/peripherals/G2Apollo510_CryptoOtp.cs
include @renode/peripherals/G2Apollo510_CustomerOtp.cs
include @renode/peripherals/G2CY8C4046FNI.cs
include @renode/peripherals/G2ICM45608.cs
include @renode/peripherals/G2OPT3001.cs
include @renode/peripherals/G2NPM1300.cs
include @renode/peripherals/G2NemaGpu.cs
include @renode/peripherals/G2Apollo510_MSPI.cs
include @renode/peripherals/G2MX25U25643G.cs
mach create "g2"
machine LoadPlatformDescription @{PLAT}
machine LoadPlatformDescriptionFromString "sblwired: G2.G2Apollo510_SblWired @ sysbus 0x50001000"
include @renode/g2-reset.resc
otp_customer_bank LoadFixture @fixtures/otp/synthetic-right.hex "synthetic-right" "unlocked"
include @renode/controller-peripherals.resc
include @renode/display-peripherals.resc
sysbus LoadBinary @{OPENCFW_APP} 0x00438000
sysbus LoadBinary @{ITCM} 0x00000040
cpu VectorTableOffset 0x00438000
cpu Reset
cpu SP 0x2007FB00
cpu PC 0x0059427d
mspi1.nor LoadFixture @{NOR} 0 "{NOR_SHA}" "Stock 2.2.6.10 + em9305"
sysbus WriteDoubleWord 0x4002000C 0x22
""".strip()


def main() -> int:
    out = WORKDIR / "sbl-recovery-sim"
    if out.exists():
        # allow reuse of empty-ish dir only if we create uniquely? require fresh-ish
        # overwrite logs in place for campaign workdir
        pass
    out.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": 1,
        "date": "2026-11-22",
        "timezone": "America/Chicago",
        "title": "Host SBL recovery tool sim-verified against HLE wired-load SBL",
        "physicalDevicesOpened": False,
        "protectedSblRomExecuted": False,
        "hardwareHookupDocumented": True,
        "cases": [],
        "passed": False,
    }
    image = STOCK_OTA.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != STOCK_OTA_SHA:
        raise SystemExit(f"stock OTA hash {digest} differs")
    report["stockImageSha256"] = digest
    report["stockImageBytes"] = len(image)
    report["stockAppSha256"] = hashlib.sha256(STOCK_APP.read_bytes()).hexdigest()

    console = RenodeConsole(EMU, out / "renode-session",
                            configuration=EMU / "renode/ota-automation.config")
    try:
        console.command(setup_resc_commands(), timeout=120)
        # Arm via the application early-arm, then unexpected reset into SBL.
        console.command('emulation RunFor "0.01"')
        otap = scalar(console.command("sysbus ReadDoubleWord 0x40020264"))
        if otap.lower() != "0xafd1363a":
            raise RuntimeError(f"did not arm: {otap}")
        console.command("machine Reset")
        wired = scalar(console.command("sblwired WiredLoadActive"))
        halted = scalar(console.command("cpu IsHalted"))
        report["cases"].append({
            "case": "unexpected-reset-enters-hle-wired-load",
            "otap": otap,
            "wiredLoadActive": wired,
            "cpuHalted": halted,
            "passed": wired.lower() in {"0x1", "0x00000001", "true"} and halted.lower() == "true",
        })
        if not report["cases"][-1]["passed"]:
            raise RuntimeError(f"wired-load not entered: wired={wired} halted={halted}")

        transport = RenodeSblTransport(console, out / "frames")

        # HELLO → STATUS
        status = transport.transact(hello_frame(), label="HELLO-probe")
        frames = find_status_frames(status)
        report["cases"].append({
            "case": "hello-returns-status",
            "statusBytes": len(status),
            "maxStorage": frames[0]["maxStorage"] if frames else None,
            "passed": len(frames) == 1 and len(status) == 96,
        })
        if not report["cases"][-1]["passed"]:
            raise RuntimeError("HELLO STATUS failed")

        # Bad CRC rejected
        bad = bytearray(hello_frame()); bad[-1] ^= 1
        # After a bad hello we still need a valid parse_ack or raw status? model returns ACK type 0 status 3
        nack = transport.transact(bytes(bad), label="HELLO-badcrc")
        parsed = parse_ack(nack, expected_message_type=0)
        report["cases"].append({
            "case": "bad-crc-rejected",
            "statusName": parsed["statusName"],
            "passed": (not parsed["accepted"]) and parsed["statusName"] == "crc",
        })
        if not report["cases"][-1]["passed"]:
            raise RuntimeError("bad CRC was not rejected")

        # DATA before descriptor/update is a sequence/invalid error
        early = transport.transact(data_frame(0, b"\x00" * 16), label="DATA-early")
        early_ack = parse_ack(early, expected_message_type=8, expected_sequence=0)
        report["cases"].append({
            "case": "data-before-update-rejected",
            "statusName": early_ack["statusName"],
            "passed": not early_ack["accepted"],
        })
        if not report["cases"][-1]["passed"]:
            raise RuntimeError("early DATA was accepted")

        # Fresh session for the real stock update (state may be dirty).
        console.command("sblwired EnterWiredLoad")
        audit = run_update(
            transport, image, digest=STOCK_SHA256, chunk=8180, route="right",
        )
        (out / "update-audit.json").write_text(json.dumps(audit, indent=2) + "\n")
        programmed = console.command(f"sblwired VerifyProgrammed @{STOCK_OTA}", timeout=120)
        # extract sha from output (property-like print or return)
        sha_hits = re.findall(r"[0-9a-f]{64}", programmed.lower())
        otap_after = scalar(console.command("sysbus ReadDoubleWord 0x40020264"))
        halted_after = scalar(console.command("cpu IsHalted"))
        pc_after = int(scalar(console.command("cpu PC")), 16)
        sp_after = int(scalar(console.command("cpu SP")), 16)
        ok = (
            audit["outcome"] == "reset-acknowledged-postflight-required"
            and audit["resetAcknowledged"]
            and audit["firmwareImageBytesAcknowledged"] == len(image)
            and otap_after.lower() in {"0x0", "0x00000000"}
            and halted_after.lower() == "false"
            and (pc_after & ~1) == (STOCK_RESET & ~1)
            and sp_after == STOCK_SP
            and report["stockAppSha256"] in sha_hits + [audit.get("qualification", {})]
        )
        # VerifyProgrammed returns the payload sha, which is stock.app.bin
        if report["stockAppSha256"] not in sha_hits:
            # still accept if VerifyProgrammed did not throw and property matches
            prop = re.findall(r"[0-9a-f]{64}", console.command("sblwired ProgrammedSha256").lower())
            ok = ok or (report["stockAppSha256"] in prop)
            sha_hits += prop
        report["cases"].append({
            "case": "full-stock-update-uart-chunks",
            "dataFramesAcknowledged": audit["dataFramesAcknowledged"],
            "commandsAcknowledged": audit["commandsAcknowledged"],
            "otapAfter": otap_after,
            "cpuHalted": halted_after,
            "pc": hex(pc_after),
            "sp": hex(sp_after),
            "programmedSha256": sha_hits[0] if sha_hits else None,
            "expectedAppSha256": report["stockAppSha256"],
            "passed": bool(sha_hits) and report["stockAppSha256"] in sha_hits
                and audit["resetAcknowledged"]
                and otap_after.lower() in {"0x0", "0x00000000"}
                and halted_after.lower() == "false"
                and (pc_after & ~1) == (STOCK_RESET & ~1)
                and sp_after == STOCK_SP,
        })
        if not report["cases"][-1]["passed"]:
            raise RuntimeError(f"full stock update postflight failed: {report['cases'][-1]}")

        # Short run to ensure the new vectors are live (no immediate halt).
        console.command('emulation RunFor "0.05"')
        pc_run = int(scalar(console.command("cpu PC")), 16)
        report["cases"].append({
            "case": "postflight-short-run",
            "pc": hex(pc_run),
            "passed": pc_run != 0,
        })
        report["passed"] = all(c["passed"] for c in report["cases"])
        report["updateAudit"] = audit
    finally:
        try:
            console.command("quit", timeout=15)
        except Exception:
            pass
        console.close()
        (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("passed", "cases") if k in report}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
