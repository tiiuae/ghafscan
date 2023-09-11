<!--
SPDX-FileCopyrightText: 2023 Technology Innovation Institute (TII)

SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Vulnerability Report

This vulnerability report is generated for Ghaf target `TARGET_NAME` revision  https://github.com/tiiuae/ghaf/commit/GHAF_HEAD. The tables on this page include known vulnerabilities impacting buildtime or runtime dependencies of the given target.

This report is automatically generated as specified on the [Vulnerability Scan](../.github/workflows/vulnerability-scan.yml) GitHub action workflow. It uses the tooling from [sbomnix](https://github.com/tiiuae/sbomnix) repository, such as [vulnxscan](https://github.com/tiiuae/sbomnix/tree/main/scripts/vulnxscan), as well as the manual analysis results maintained in the [manual_analysis.csv](../manual_analysis.csv) file.

See section [Theory of Operation](https://github.com/tiiuae/ghafscan#theory-of-operation) in the [ghafscan README.md](https://github.com/tiiuae/ghafscan/blob/main/README.md) for details of how the data on this report is generated.

Reports
=================

* [Vulnerabilities Fixed in Ghaf nixpkgs Upstream](#vulnerabilities-fixed-in-ghaf-nixpkgs-upstream)
* [Vulnerabilities Fixed in nix-unstable](#vulnerabilities-fixed-in-nix-unstable)
* [New Vulnerabilities Since Last Run](#new-vulnerabilities-since-last-run)
* [All Vulnerabilities Impacting Ghaf](#all-vulnerabilities-impacting-ghaf)
* [Whitelisted Vulnerabilities](#whitelisted-vulnerabilities)

## Vulnerabilities Fixed in Ghaf nixpkgs Upstream 

Following table lists vulnerabilities that have been fixed in the nixpkgs channel the Ghaf target is currently pinned to, but the fixes have not been included in Ghaf.

Update the target Ghaf [flake.lock](https://github.com/tiiuae/ghaf/blob/main/flake.lock) file to mitigate the following issues:

FIXED_IN_NIXPKGS

## Vulnerabilities Fixed in nix-unstable

Following table lists vulnerabilities that have been fixed in nixpkgs nix-unstable channel, but the fixes have not been backported to the channel the Ghaf target is currently pinned to.

Following issues potentially require backporting the fix from nixpkgs-unstable to the correct nixpkgs release branch.

Consider [whitelisting](../../manual_analysis.csv) possible false positives based on manual analysis, or - if determined valid - help nixpkgs community backport the fix to the correct nixpkgs branch:

FIXED_IN_NIX_UNSTABLE


## New Vulnerabilities Since Last Run

Following table lists vulnerabilities currently impacting the Ghaf target that have emerged since the last time this vulnerability report was generated.

Consider [whitelisting](../../manual_analysis.csv) possible false positives based on manual analysis, or - if determined valid - help nixpkgs community fix the following issues in nixpkgs:

NEW_SINCE_LAST_RUN


## All Vulnerabilities Impacting Ghaf

Following table lists all vulnerabilities currently impacting the Ghaf target.

Consider [whitelisting](../../manual_analysis.csv) possible false positives based on manual analysis, or - if determined valid - help nixpkgs community fix the following issues in nixpkgs:

CURRENT_VULNS


## Whitelisted Vulnerabilities

Following table lists vulnerabilities that would otherwise have been included to the report, but were left out due to whitelisting.

<details>
<summary>Whitelisted vulnerabilities</summary>
<br>
ONLY_WHITELISTED
</details>
