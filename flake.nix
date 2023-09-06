# SPDX-FileCopyrightText: 2023 Technology Innovation Institute (TII)
#
# SPDX-License-Identifier: Apache-2.0
{
  description = "Flakes file for ghafscan";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = {
    self,
    nixpkgs,
  }: let
    pkgs = import nixpkgs {system = "x86_64-linux";};
    ghafscan = import ./default.nix {pkgs = pkgs;};
    ghafscan-shell = import ./shell.nix {pkgs = pkgs;};
  in rec {
    # nix package
    packages.x86_64-linux = {
      inherit ghafscan;
      default = ghafscan;
    };

    # nix run .#ghafscan
    apps.x86_64-linux.ghafscan = {
      type = "app";
      program = "${self.packages.x86_64-linux.ghafscan}/bin/ghafscan";
    };

    # nix develop
    devShells.x86_64-linux.default = ghafscan-shell;
  };
}
