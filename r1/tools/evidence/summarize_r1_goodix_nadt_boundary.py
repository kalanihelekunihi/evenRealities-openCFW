#!/usr/bin/env python3
"""Pin the exact Goodix GH_NADT provider boundary in the recovered R1 image.

This is a static ownership gate.  It emits no NADT/liveness implementation and
does not treat recovered algorithm behavior as clean-room product logic.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"


def _function(
    entry: int,
    end_exclusive: int,
    size: int,
    role: str,
    sha256: str,
    callsites: tuple[int, ...],
    segments: tuple[tuple[int, int], ...] = (),
) -> dict[str, Any]:
    return {
        "entry": entry,
        "end_exclusive": end_exclusive,
        "size": size,
        "role": role,
        "sha256": sha256,
        "callsites": callsites,
        "segments": segments,
        "provider_family": "goodix_gh3x2x_candidate",
        "source_disposition": "vendor_source_required_not_redistributable",
    }


# Five compiler-scattered functions and the NADT initializer have explicit
# executable segments.  All other entries use their single entry/end extent.
GOODIX_NADT_FUNCTIONS = (
    _function(0x00028B18, 0x00028B8A, 114, "NADT scalar transform helper",
              "351584d1c836af77429fc6572a4d26b9328aec93a700691ffab7074be201958c",
              (0x00037436,)),
    _function(0x00028DE0, 0x00028DE6, 6, "NADT half-precision conversion helper",
              "a553fb9f262b5c1390230af3e0f3daef4be55f21ac13dcf301dc9ed5b3253b32",
              (0x000292B6, 0x0007660E)),
    _function(0x00028DEC, 0x00028E14, 40, "NADT vector conversion helper",
              "cd48cb31cef7c544d5bf43c2bceb84f5b1cbd6919d940274d3a46526b69a6d5e",
              (0x00029210,)),
    _function(0x00028E14, 0x00028E56, 66, "NADT input validity helper",
              "d201c01b74231826ec1dd38cff7d1c0746251f7ee15c866fcf5869901db04d57",
              (0x0006E080, 0x0006E08E, 0x0006E09C, 0x0006E0AA, 0x0006E0B8,
               0x0006E0C6)),
    _function(0x0002907C, 0x0002908E, 18,
              "NADT generated-model executor wrapper",
              "3c3c31d9c061a90349261e0352e9b15f92c2b76b1c5d26c2477b3359976d8e81",
              (0x00096980,)),
    _function(0x00029144, 0x0002934C, 520,
              "NADT dual-window feature/correlation extractor",
              "c981e359c84c06bd9782fd5a9230b1f446a78947b354b5d56fc23b4df0851661",
              (0x00095884,)),
    _function(0x0002F7DC, 0x0002F866, 138,
              "NADT generated-model tensor projection helper",
              "23ec560565c22d832ee2d81f687a2419268eea3ed1b98c7d99a8449bc1eb0adc",
              (0x000343AE,)),
    _function(0x00030B6C, 0x00030C98, 300, "NADT window filter helper",
              "5ca8634d0213ffc244eb6003ab604d66c7f5fc7b0197fdd9132a18ae3ccca129",
              (0x00047418,)),
    _function(0x00031624, 0x000316E4, 192, "NADT secondary classifier helper",
              "4bfcf0b880143a749d16c8bc40568aba3b42066cc183728a984adc6781bd7188",
              (0x0007DE06, 0x0007DE1A)),
    _function(0x00034194, 0x0003440A, 630,
              "NADT generated-model subgraph executor",
              "18b51a96c3f0c3d0c9c47727c5ec8f5a569e603ad2c882e74fef43f84588e285",
              (0x000378B0, 0x0003797C)),
    _function(0x0003497C, 0x00034A30, 180, "NADT peak-quality helper",
              "4fff585a98c999b99e8648b2f2e5e4b4d32e4f14a09bd8f668e6eef554779b4c",
              (0x00047550, 0x0007DEA0)),
    _function(0x000357A2, 0x000357CE, 44, "NADT sample statistic helper",
              "92695ea24e4775095465d9b6cf1f2bfe5a92c37047dd4869ea9de8be9cb0111a",
              (0x0004726E, 0x000472EE, 0x0004742A, 0x000475AE, 0x00047682)),
    _function(0x00035850, 0x00035D12, 1162,
              "NADT harmonic-candidate selector",
              "c9fbb161215e9026649909ed8ef04b628221d7d51cbd4affb3c04f0a4c6a6c7a",
              (0x0007685C,), ((0x00035850, 0x00035C40),
                              (0x00035C78, 0x00035D12))),
    _function(0x00035F70, 0x00036030, 192, "NADT signal normalization helper",
              "4be83d18b8a673cae179d45412ae6862963f2fb38b54c9b85c86721bd958e38e",
              (0x000474DC,)),
    _function(0x00036034, 0x000361C0, 394, "NADT sample preparation helper",
              "65e0dd17e48b9aae3df886e8536152a39787fbd105f7d8ce921ae5db2b12de90",
              (0x0006E0F6,), ((0x00036034, 0x000361AE),
                              (0x000361B0, 0x000361C0))),
    _function(0x000361D8, 0x00036230, 88, "NADT magnitude statistic helper",
              "c83b9450185f99169924fdb56041b5a3f2fd6898584cd5a892a559996193f2d4",
              (0x00047878, 0x00047882)),
    _function(0x0003623C, 0x00036282, 70, "NADT classifier subhelper A",
              "699902b763ce7bc0872645d66b9a0e8845a0e6731811e575ce68b2b2923286dc",
              (0x00037CB2, 0x00037CC0)),
    _function(0x00036394, 0x00036402, 110, "NADT classifier subhelper B",
              "40cce86499d48245088c14ffd4f0cdf05a7d262ae4587b55c5f33b4ef3de8467",
              (0x00037BEA,)),
    _function(0x00036734, 0x000367C0, 140, "NADT local-peak index extractor",
              "c9ea53c2c2ca97c05d07014d87178b42c3e9b11fceb7d68ac45257922c9756e2",
              (0x00029192, 0x00029238)),
    _function(0x00036F88, 0x00037270, 744, "NADT state/output selection helper",
              "1c454b3b53453c7d2e53dc9c04a6ed66c3d82d85b1e3dc7d389085d1cc59f3f3",
              (0x0006EA7A,)),
    _function(0x000373A4, 0x0003747C, 216, "NADT optical sample transform",
              "3642bc4cc3b4f100c5c26e8493a1cd1b132b9815e8b25f20953a0e72dabfa2a0",
              (0x0006E228,)),
    _function(0x00037890, 0x00037A84, 500,
              "NADT generated-model graph executor",
              "d2053f5c967d4772e40a406e8aa396de8df599a66d8b4cd292c886a3604fb944",
              (0x00029088,)),
    _function(0x00037A84, 0x00037B60, 220,
              "NADT peak dispersion/phase-quality estimator",
              "32b24dcc7f818f161743343f45a3bf3892c5123bf68a371163c7f7820a78ad3f",
              (0x000291D4, 0x0002927A)),
    _function(0x00037B80, 0x00037DAA, 554, "NADT auxiliary state classifier",
              "52f12f8d61f54c675abefbdb349899fbbcdec3f843aaaa65f9274e5ba5af601e",
              (0x0008586E,)),
    _function(0x0003E6C8, 0x0003E7A0, 216,
              "NADT Gaussian interval-probability helper",
              "a063b8c718e77e481b7bc5a761303479b9c7c0e18204e0ca0f47e765fd9e3991",
              (0x00095A9E,)),
    _function(0x00042BD0, 0x00042D0C, 316,
              "NADT periodic-peak rate estimator",
              "9f763ff5fb84407cc9c599184bf9e8e8c0443b6f824aa79a9a526df12d861e59",
              (0x000291E0, 0x00029286)),
    _function(0x00047240, 0x00047F0A, 3240, "NADT primary signal classifier",
              "01e21104d3d962a09b4c9087eb0e3a49b56b70ee7ebc1eb4d7aa09236f3ab1ac",
              (0x00085828,), ((0x00047240, 0x000476E6),
                              (0x000476F8, 0x00047B08),
                              (0x00047B18, 0x00047F0A))),
    _function(0x0005144C, 0x0005148E, 66, "NADT array statistic helper",
              "5dea1ab9017e7ce148b20881f54f1df4fd4e8774f7baa497a1cb7136b7e33262",
              (0x000361E2, 0x00047278, 0x000476D4, 0x000477E0)),
    _function(0x0005CED4, 0x0005CF72, 158, "NADT rolling-vector helper",
              "e1a375ba9640111f4ce4e873733f32f3411f0c0eb6cc65215a93befc58f6bedc",
              (0x0006E3CE,)),
    _function(0x00061F94, 0x00061FB2, 30, "NADT sample-mean wrapper",
              "afb84359ec9608fed220b8ea54caeee2f140b72a8dd488b129f92eb728c1f690",
              (0x00042BEC, 0x0009593C)),
    _function(0x00061FB4, 0x00061FD0, 28, "NADT sample-sum helper",
              "41fe15e61d06b99a07adda5e84d9263ed5dc13757cc2b3f8b87b9ddb77a9daa0",
              (0x00061F98,)),
    _function(0x00061FD4, 0x00061FEA, 22,
              "NADT sample-standard-deviation wrapper",
              "0108ae55e26b37172e49555f6def82ff948b69b6774a1d637242e434def31f01",
              (0x00095946,)),
    _function(0x00066394, 0x000663B0, 28,
              "NADT rolling-vector latest-value accessor",
              "4a12a31d354c3ebee0c1f7185f9eb4a61e51052fe5f6471ae532585d3e0fc789",
              (0x000959AC,)),
    _function(0x00066490, 0x00066494, 4,
              "NADT rolling-vector length accessor",
              "827073440d56fee43d2762e0c8127dd35fa36c1a3c56c522fd4cba28902bc348",
              (0x00095A58,)),
    _function(0x000666A4, 0x00066712, 110,
              "NADT normalized autocorrelation helper",
              "3b5860c5f12b9804745b33c979e182a0595ac7c2a6a1a8861bc06cf7d1c2d659",
              (0x00029170, 0x00029226)),
    _function(0x000668DC, 0x00066900, 36, "NADT minimum-index helper",
              "9e44622a1cd6d99a6abcc79a4898245259e18c5e90bff1e1973186e205b4cdb9",
              (0x00066A60,)),
    _function(0x00066900, 0x00066AB2, 434,
              "NADT local-maximum mask helper",
              "99ce8258e5fa0fb713084505092ddcb7954c3c5f675dbde87be9ad46a30e2272",
              (0x0003675C,)),
    _function(0x00066B30, 0x00066C0E, 222, "NADT filter kernel helper",
              "a21af69e0ba50a1dfe37d4cbfc855f92754c9a8e62ae617c8571f0dadd26a284",
              (0x00030C08,)),
    _function(0x0006E008, 0x0006E532, 1294, "GH_NADT streaming process",
              "1b8a57e2d23467bbcd143115751d867207f56b1f12de3bada3efb8439795b5ea",
              (0x0002CF0E,), ((0x0006E008, 0x0006E410),
                              (0x0006E42C, 0x0006E532))),
    _function(0x0006E540, 0x0006E544, 4, "GH_NADT result accessor",
              "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587",
              (0x000327AA,)),
    _function(0x0006E548, 0x0006E566, 30, "GH_NADT public-version copier",
              "50c67183d4674a285aad8b2b224729c77dfe9e5a44b2fcc017538b09d714976b",
              (0x000327CE,)),
    _function(0x0006E574, 0x0006E646, 210, "GH_NADT state reset",
              "f25f4599d9e827c0ab0e98e1c4ef973e00164b848b913159af5b4d75edb329e0",
              (0x0002CDBE,)),
    _function(0x0006E664, 0x00073FFA, 712, "GH_NADT initializer",
              "03e1b62f9bdbe3f5fdbbe119dafac8617c7ac13dc23928eb6e6c758e6e3b9af4",
              (0x000327D8,), ((0x0006E664, 0x0006E75E),
                              (0x00073E2C, 0x00073FFA))),
    _function(0x0006E788, 0x0006E806, 126, "GH_NADT version builder",
              "bf627bb8587f69473d9f39846a0e9979201e91e9d17cc6513ebba85a8e079c04",
              (0x0002A15C, 0x000327A6)),
    _function(0x0006E838, 0x0006EAE2, 682, "GH_NADT preprocessing core",
              "d0e8d34ddfaf97ba47f66e94aa6a104b3efac71452ecb02f4f5a25379f04f656",
              (0x0002D0DE,)),
    _function(0x0006F838, 0x0006F8F6, 190,
              "NADT generated-model tensor-combine helper",
              "e236c4688858947bbe12e6760b252a03553e1b077cf24f2c26f8004f2d63985e",
              (0x000342C6, 0x00034326)),
    _function(0x000766AC, 0x0007688A, 478,
              "NADT spectral peak-preparation pipeline",
              "adf8c54c2b2af59806f5a940cb1470aa71c010e3918ce4725559063151b25c33",
              (0x0006E8DA,)),
    _function(0x0007DCD8, 0x0007DD14, 60, "NADT sample-variance helper",
              "96becf1690650bfef08ec0b4db93a60418c5a010744c97b0966c73960dfe5344",
              (0x00061FDE,)),
    _function(0x0007DD58, 0x0007E0C2, 874, "NADT alternate-state classifier",
              "46240b4aebd8a3f9d4b26e2f109215ddb0793c7005de78f85826dc9ab7711775",
              (0x00085916, 0x00085932)),
    _function(0x000856EC, 0x00085B9A, 1154, "NADT window classifier",
              "29e04962b88b0993700f603717f98229bd217e959192d045ee3cd3fbda7f82e1",
              (0x0006E408,), ((0x000856EC, 0x00085AF0),
                              (0x00085B1C, 0x00085B9A))),
    _function(0x00087618, 0x000876C8, 176, "NADT turning-point extractor",
              "efa5cd3525bc72104652b5155d51b1dcfa895d43d65e960e20f8f96030accd00",
              (0x00047638,)),
    _function(0x000928E0, 0x000928FA, 26, "NADT sum-of-squares helper",
              "08b9196cd36eafbc4ffeb5728cc3cd5c77ec4f97c34002d54bed01607e75ac4b",
              (0x000291FE, 0x000292AA, 0x00037802, 0x0003780C)),
    _function(0x00092A04, 0x00092B54, 336,
              "NADT correlation/convolution helper",
              "ae749921a04229806a23b9284d99b91dffcbc3ab33d989bab3de109cb68bbf41",
              (0x000666C0,)),
    _function(0x00095750, 0x00095816, 198,
              "NADT inference-input normalization helper",
              "a5df7e4c911c672035a3c29116f11ff0079296f941a48732f76102804d16a350",
              (0x00096958,)),
    _function(0x00095828, 0x00095ACA, 674,
              "NADT signal-confidence/state tracker",
              "509a3440ed4c47ba3c10db0911eb66bff2fbe1bf804e294ad5fe024dad5b98eb",
              (0x0006EA88,)),
    _function(0x000968C4, 0x000969E6, 290,
              "NADT generated-model inference bridge",
              "7ae3d922f70779250287db9f7fdd8cb25d0a1057a3b4d663461bf3a497722c51",
              (0x0006E94E,)),
    _function(0x00097984, 0x000979DA, 86, "NADT bounded-history update",
              "459292601fb415f7b695142efb6c52590a341dec8d0c3ad41bf8c00f74610276",
              (0x000472D4, 0x00087664)),
    _function(0x00098E4C, 0x00098ECA, 126, "NADT feature-index extractor",
              "56596f096a26146060aa4f169f874a8f97baf5f2ec89eef8bacf48b0b1e75f04",
              (0x00037C4A, 0x00047516, 0x0007DE86)),
)


def _body(image: bytes, function: dict[str, Any]) -> bytes:
    segments = function["segments"] or ((function["entry"], function["end_exclusive"]),)
    return b"".join(
        image[int(start) - LOAD_BASE:int(end) - LOAD_BASE]
        for start, end in segments
    )


def summarize(image_path: Path) -> dict[str, object]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {digest}")

    functions = []
    for function in GOODIX_NADT_FUNCTIONS:
        body = _body(image, function)
        entry = int(function["entry"])
        calls = tuple(address for address, _ in direct_thumb_branches_to(
            image, LOAD_BASE, entry))
        if len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                calls != function["callsites"]:
            raise ValueError(f"Goodix GH_NADT boundary changed at 0x{entry:08x}")
        segments = function["segments"] or ((entry, int(function["end_exclusive"])),)
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{int(function['end_exclusive']):08x}",
            "callsites": [f"0x{address:08x}" for address in calls],
            "segments": [
                {"start": f"0x{start:08x}", "end_exclusive": f"0x{end:08x}"}
                for start, end in segments
            ],
        })

    marker = image[0x0006E808 - LOAD_BASE:0x0006E834 - LOAD_BASE]
    expected_marker = (
        b"GH_NADT_pre\0_pv\0_v1.0.2.0\0\0\0_\0\0\0" b"548d894d\0\0\0\0"
    )
    if marker != expected_marker:
        raise ValueError("Goodix GH_NADT version/hash marker changed")

    newly_routed = [item for item in functions if item["entry"] != "0x0006e788"]
    return {
        "analysis": "Goodix GH_NADT provider-boundary closure",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": len(functions),
        "function_bytes": sum(int(item["size"]) for item in functions),
        "newly_routed_function_count": len(newly_routed),
        "newly_routed_function_bytes": sum(int(item["size"]) for item in newly_routed),
        "functions": functions,
        "identity": {
            "component": "Goodix GH_NADT",
            "version": "v1.0.2.0",
            "component_hash": "548d894d",
            "marker_address": "0x0006e808",
            "streaming_period_samples": 25,
        },
        "boundary": {
            "provider_family": "goodix_gh3x2x_candidate",
            "source_disposition": "vendor_source_required_not_redistributable",
            "licensed_provider_required": True,
            "local_algorithm_reimplementation_authorized": False,
            "toolchain_runtime_and_sensor_heap_excluded": True,
        },
        "safety": {
            "static_parser_only": True,
            "algorithm_reimplementation_emitted": False,
            "live_sensor_access": False,
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))
