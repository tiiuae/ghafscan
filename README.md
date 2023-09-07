<!--
SPDX-FileCopyrightText: 2023 Technology Innovation Institute (TII)

SPDX-License-Identifier: CC-BY-SA-4.0
-->

# ghafscan

This repository automates vulnerability scans for the [Ghaf Framework](https://github.com/tiiuae/ghaf).
The Ghaf [vulnerability reports](./reports/) available on this repository are automatically updated on [daily basis](./.github/workflows/vulnerability-scan.yml#L12) for the selected Ghaf branches and targets as specified in the [Vulnerability Scan](./.github/workflows/vulnerability-scan.yml) GitHub action workflow. 

### Example Reports
- [Ghaf 'main' generic-x86_64-release](./reports/main/packages.x86_64-linux.generic-x86_64-release.md)
- [Ghaf 'main' riscv64-linux.microchip-icicle-kit-release](./reports/main/packages.riscv64-linux.microchip-icicle-kit-release.md)
- [Ghaf 'ghaf-23.06' generic-x86_64-release](./reports/ghaf-23.06/packages.x86_64-linux.generic-x86_64-release.md)

# Motivation

Key points demonstrated in this repository:
- Running automatic vulnerability scans for nix flake projects, using [Ghaf Framework](https://github.com/tiiuae/ghaf) as an example.
- Using [vulnxscan](https://github.com/tiiuae/sbomnix/tree/main/scripts/vulnxscan) as the main vulnerability scanning tool for a nix flake project.
- Using nix flake updates to derive potentially missing security fixes for a nix flake project.
- Incorporating [manual analysis](manual_analysis.csv) results to the automated vulnerability scans.

# Running Locally
`ghafscan` requires common [Nix](https://nixos.org/download.html) tools and assumes [nix flakes](https://nixos.wiki/wiki/Flakes#Enable_flakes) is enabled. Nix tools such as `nix` are expected to be in `$PATH`.

### Running as Nix Flake
`ghafscan` can be run as a [Nix flake](https://nixos.wiki/wiki/Flakes) from the `tiiuae/ghafscan` repository:
```bash
# '--' signifies the end of argument list for `nix`.
# '--help' is the first argument to `ghafscan`
$ nix run github:tiiuae/ghafscan#ghafscan -- --help
```

or from a local repository:
```bash
$ git clone https://github.com/tiiuae/ghafscan
$ cd ghafscan
$ nix run .#ghafscan -- --help
```
See the full list of supported flake targets by running `nix flake show`.

### Running from Nix Development Shell

To start a local development shell, run:
```bash
$ git clone https://github.com/tiiuae/ghafscan
$ cd ghafscan 
$ nix develop
```

From the development shell, run `ghafscan` as follows:
```bash
$ ghafscan --help
```

To deactivate the Nix development shell, run `exit` in your shell.

# Contribute
All pull requests, suggestions, and error reports are welcome.
To start development, we recommend using Nix flakes [development shell](./README.md#running-from-nix-development-shell).

Run `make help` in the development shell to see the list of supported make targets.
Prior to sending any pull requests, make sure at least the `make pre-push` runs without failures.

# License

This project is licensed under the Apache-2.0 license - see the [Apache-2.0.txt](LICENSES/Apache-2.0.txt) file for details.
