# Official Goodix carrier and independent TDK revision review

## Goodix: finite carrier check closes without a new matching source

Useful candidate was specifically components/libraries/app_error/app_error.c, matching the existing OpenCFW copied utils/assert utility lineage. Official public goodix-ble/GR551x.SDK master pinned by commit API to ac263ce938c28fd8a3a8217b4477b9e60ad20964. Public path-history API returned two entries: c3c8afe433bcc39de4d5115d4203a81b213bb0be (“Update SDK to v2.1.0”) and575cedb33858d03f54049ae1d130b6253649a388 (“official SDKv2.0.2”). Retained only two useful source variants plus metadata, all under this audit directory. Goodix BSD3Clause license is embedded and preserved in each source. Full URLs, SHA256, sizes, Gitblob identities and metadata hashes are GOODIX-CARRIER-PROVENANCE.json.

Both official variants declare and contain46 error rows. Current Gitblob0ddea24a182f72b30714fa9945408ccef702e747 and2.0.2blob639f5cf10c5c293c899c76af83a9404b847d1090 differ from historical known1.7.0blobd5027735dd01b0948a7315d9c595356fcb91f59b/43rowfingerprint. This independently authenticates a negative official-carrier comparator, consistent with OpenCFW's existing exclusion of2.0.1+; it does not independently reauthenticate the unavailable historical43-row firmware receipt. No1.7.0app_error version appears in this finite ordinarypathhistory. Branches, renamedpaths or vendorarchives are not universally excluded.

The SDK root carrier was newly cross-checked relative to inspectedregistry, but theutilityfamily andofficialMicroPythonlineage are alreadyregistered. Noexactnewlibrary/header/document resolving a currentG2gap was found. WholeSDK/middleware acquisition would duplicate known families without a newstockdiscriminator. Goodixutilitycopy or sharedmiddleware does not imply G2usesGR551xchip orBLEstack; Apollo/EM hardware evidence remains separate. Target1.7.0officialvendorarchive would add provenance only unless a newaddress-bound gap needs it. Stop this finitecarrierlead rather than downloadgenericGR551xsource.

Initial restrictednetwork DNS failed; approved publiccurl escalation fetched these exact official inputs. No rejectedreview, credentialuse, licensedbinarydownload, tags-page restrictionbypass or codeexecution occurred.

## TDK: independent receipt/source checks pass

TDK-REVISION-INDEPENDENT-VERIFICATION.json authenticates four discovery receiptfiles and an independently downloaded old registeredpin inv_imu_edmp.c; oldbytes exactly equal discovery'soldfile. Three diffhunks cover twochangedregions: addedunequalODRconditionalpatch installation and mountingwrapper/helperrefactor. Vectorinitialization does notchange.

Newsource inv_imu_edmp_set_gaf_parameters tests acc_odr_us!=gyr_odr_us, copieskey from calibrationimage offset0, writes EDMPpatchpoint0x50. Headerconstants independently confirmbothvalues. Bothversions convertnineint8entries toQ14; newversion delegateswrite toaddedset_s16q14helper. Compilerinlining can removehelperboundary; itsabsence cannot selectoldrevision. EDMPvectorsremainROMbase/base+4/base+8; noROMimplementation supplied. Arduino package1.1.8 is distinct from internaldriver2.0.0-rc1 versionstring.

Discovery TDK-EDMP-REVISION-COMPARISON.md correctly leaves stockrevision unassigned because no currentauthenticatedaddress-bound selectedroutine was found. The nextusefulfinitevalidation is originalG2callsite/extentbinding for unequalODRbranch andextraSRAM0x50write, then exactcalibrationimagecomparison; not a submoduleupdate or assumptionnewermeansmatching. Partialhostsource still cannot implementprivateEDMP/GAF2/4 computation.

No emulator, firmware, indexes, canonicalledgers, devices or tests changed. Downloadedfiles were not executed. New-versus-known classification: Goodixnewprimarycarrier/knownnegativeversionfamily; TDKnewlocallyauthenticatedcomparisoninput/knownhistoricalSDKfamily, producingrevisionunresolved.
