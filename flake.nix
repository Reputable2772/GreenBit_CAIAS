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
      ];
    in
    {
      devShells.x86_64-linux.default = pkgs.mkShell {
        nativeBuildInputs =
          with pkgs;
          [
            python315
            python315Packages.venvShellHook
            nixfmt
          ]
          ++ runtimeLibs;

        shellHook = ''
          export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath runtimeLibs}:$LD_LIBRARY_PATH"          echo "Python environment loaded. libstdc++ is now in LD_LIBRARY_PATH."

          # Optional: Automatically enter your venv if it exists
          if [ -d ".venv" ]; then
            source .venv/bin/activate
          fi
        '';
      };
    };
}
