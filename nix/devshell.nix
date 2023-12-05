# SPDX-FileCopyrightText: 2023 Technology Innovation Institute (TII)
#
# SPDX-License-Identifier: Apache-2.0
{
  perSystem = {
    pkgs,
    inputs',
    ...
  }: {
    devShells.default = pkgs.mkShell {
      name = "ghafscan-dev-shell";

      packages =
        (with pkgs; [
          coreutils
          gnugrep
          grype
          nix
          reuse
          (
            python3.withPackages (ps:
              with ps; [
                colorlog
                gitpython
                pandas
                pytest
                tabulate
              ])
          )
        ])
        ++ [
          # bring in vulnxscan from sbomnix
          inputs'.sbomnix.packages.default
          # csvdiff
          inputs'.csvdiff.packages.default
        ]
        ++ [
          inputs'.nix-fast-build.packages.default
        ];
      shellHook = ''
        export PYTHONPATH="$PYTHONPATH:$(pwd)/src"
      '';
    };
  };
}
