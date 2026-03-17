{
  description = "NixOS flake for CAIAS Hackathon";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs, ... }@inputs:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      runtimeLibs = with pkgs; [
        stdenv.cc.cc.lib
        zlib
        glibc
        # openssl # Only if Pydantic needs HTTPS during build
      ];
    in
    {
      devShells.x86_64-linux.default = pkgs.mkShell {
        nativeBuildInputs = with pkgs; [
          python314
          python314Packages.venvShellHook
          nixfmt-rfc-style

          # Pydantic
          rustc
          cargo

          pkg-config
          gcc
          nodejs_25
        ];

        buildInputs = runtimeLibs;

        shellHook = ''
          export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath runtimeLibs}:$LD_LIBRARY_PATH"

          if [ -d ".venv" ]; then
            source .venv/bin/activate
          fi
        '';
      };
    };
}
