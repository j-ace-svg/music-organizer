{
  description = "Pygame development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    nixpkgs-python.url = "github:cachix/nixpkgs-python";
  };

  outputs = { self, nixpkgs, nixpkgs-python }: 
    let
      system = "x86_64-linux";

      pythonVersion = "3.12.2";

      pkgs = import nixpkgs { inherit system; };
      myPython = nixpkgs-python.packages.${system}.${pythonVersion};
      myPythonWithPackages = myPython.withPackages (ps: with ps; [
        yt-dlp
        appdirs
        toml
      ]);
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          myPythonWithPackages
        ];
        shellHook = ''
          python --version
        '';
      };
    };
}
