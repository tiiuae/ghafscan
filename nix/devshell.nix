# SPDX-FileCopyrightText: 2023 Technology Innovation Institute (TII)
#
# SPDX-License-Identifier: Apache-2.0
{
  perSystem = {
    pkgs,
    inputs',
    self',
    ...
  }: {
    devShells.default = let
      pp = pkgs.python3Packages;
    in
      pkgs.mkShell rec {
        name = "ghafscan-dev-shell";

        buildInputs =
          (with pkgs; [
            coreutils
            curl
            gnugrep
            gnused
            graphviz
            grype
            gzip
            nix
            reuse
          ])
          ++ [
            self'.packages.csvdiff
            # bring in vulnxscan from sbomnix
            inputs'.sbomnix.packages.default
          ]
          ++ (with pp; [
            black
            colorlog
            gitpython
            pandas
            pycodestyle
            pylint
            pytest
            tabulate
            venvShellHook
          ])
          ++ [inputs'.nix-fast-build.packages.default];

        venvDir = "venv";
        postShellHook = ''
          export PYTHONPATH="$PWD/src:$PYTHONPATH"

          # https://github.com/NixOS/nix/issues/1009:
          export TMPDIR="/tmp"

          # Enter python development environment
          make install-dev
        '';
      };
  };
}
