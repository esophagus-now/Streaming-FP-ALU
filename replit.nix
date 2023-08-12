{ pkgs }: {
    deps = [
        pkgs.verilog
        pkgs.replitPackages.stderred
        pkgs.python310Full
    ];
    env = {
        STDERREDBIN = "${pkgs.replitPackages.stderred}/bin/stderred";
        PYTHONHOME = "${pkgs.python310Full}";
        PYTHONBIN = "${pkgs.python310Full}/bin/python3.10";
    };
}