# SPDX-FileCopyrightText: 2023 Technology Innovation Institute (TII)
#
# SPDX-License-Identifier: Apache-2.0
{
  description = "Flakes file for ghafscan";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    # Allows structuring the flake with the NixOS module system
    flake-parts = {
      url = "github:hercules-ci/flake-parts";
      inputs.nixpkgs-lib.follows = "nixpkgs";
    };
    # flake-parts module for finding the project root directory
    flake-root.url = "github:srid/flake-root";
    # Format all the things
    treefmt-nix = {
      url = "github:numtide/treefmt-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    # For preserving compatibility with non-Flake users
    flake-compat = {
      url = "github:nix-community/flake-compat";
      flake = false;
    };
    nix-fast-build = {
      url = "github:Mic92/nix-fast-build";
      # re-use some existing inputs
      inputs = {
        flake-parts.follows = "flake-parts";
        treefmt-nix.follows = "treefmt-nix";
      };
    };
    ci-public = {
      url = "github:tiiuae/ci-public";
      flake = false;
    };
    sbomnix = {
      url = "github:tiiuae/sbomnix";
      inputs = {
        # reduce duplicate inputs
        nixpkgs.follows = "nixpkgs";
        flake-root.follows = "flake-root";
        flake-parts.follows = "flake-parts";
        treefmt-nix.follows = "treefmt-nix";
        nix-fast-build.follows = "nix-fast-build";
      };
    };
  };

  outputs = inputs @ {flake-parts, ...}:
    flake-parts.lib.mkFlake
    {
      inherit inputs;
    } {
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      imports = [
        ./nix
      ];
    };
}
