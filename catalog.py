"""Static catalog of Le Mans Ultimate cars and tracks.

Car detection works off the vehicle folder name found in the //VEH= line of
every .svm file, so this maps those folder names to human-readable names and
classes. Unknown folders (future DLC cars) still work — they are shown under
the "Other" class with the raw folder name, so the bot never breaks on a game
update; you just add one line here to make it pretty.
"""

# vehicle_folder -> (display_name, car_class)
CARS: dict[str, tuple[str, str]] = {
    # Hypercar
    "Alpine_A424_2024": ("Alpine A424", "Hypercar"),
    "Aston_Martin_Valkyrie_2025": ("Aston Martin Valkyrie", "Hypercar"),
    "BMW_M_Hybrid_V8_2023": ("BMW M Hybrid V8", "Hypercar"),
    "Cadillac_V-lmdh_2023": ("Cadillac V-Series.R", "Hypercar"),
    "Ferrari_499P_2023": ("Ferrari 499P", "Hypercar"),
    "Genesis_GMR001_2026": ("Genesis GMR-001", "Hypercar"),
    "Isotta_Tipo6_2024": ("Isotta Fraschini Tipo 6-C", "Hypercar"),
    "Lamborghini_SC63_2024": ("Lamborghini SC63", "Hypercar"),
    "Peugeot_9x8_2023": ("Peugeot 9X8 (2023)", "Hypercar"),
    "Peugeot_9x8_2024": ("Peugeot 9X8 Evo", "Hypercar"),
    "Porsche_963_2023": ("Porsche 963", "Hypercar"),
    "SGC_007_2023": ("Glickenhaus SCG 007", "Hypercar"),
    "Toyota_GR10_2023": ("Toyota GR010 Hybrid", "Hypercar"),
    "Vandervell_680_2023": ("Vanwall Vandervell 680", "Hypercar"),
    # LMP2
    "Oreca_07_ELMS_2023": ("Oreca 07 (ELMS)", "LMP2"),
    "Oreca_07_LM_2023": ("Oreca 07 (Le Mans)", "LMP2"),
    # LMP3
    "ADESS_AD25_2026": ("ADESS AD25", "LMP3"),
    "Duqueine_D09LMP3_2026": ("Duqueine D-09", "LMP3"),
    "Ginetta_G61Evo_2025": ("Ginetta G61-LT-P3 Evo", "LMP3"),
    "Ligier_JSP325_2025": ("Ligier JS P325", "LMP3"),
    # LMGT3
    "911GT3R_2024": ("Porsche 911 GT3 R (992)", "LMGT3"),
    "BMW_M4_LMGT3_2023": ("BMW M4 GT3", "LMGT3"),
    "Corvette_Z06GT3R_2023": ("Corvette Z06 GT3.R", "LMGT3"),
    "Ferrari_296GT3_2023": ("Ferrari 296 GT3", "LMGT3"),
    "Ford_Mustang_GT3_2024": ("Ford Mustang GT3", "LMGT3"),
    "Lamborghini_Huracan_GT3_2024": ("Lamborghini Huracán GT3 Evo2", "LMGT3"),
    "LexusRCF_GT3_2024": ("Lexus RC F GT3", "LMGT3"),
    "McLaren_720sGT3Evo_2023": ("McLaren 720S GT3 Evo", "LMGT3"),
    "Mercedes_AMGGT3Evo_2025": ("Mercedes-AMG GT3 Evo", "LMGT3"),
    "Vantage_AMR_GT3Evo_2024": ("Aston Martin Vantage GT3 Evo", "LMGT3"),
    # GTE
    "Aston_Martin_Vantage_AMR_2023": ("Aston Martin Vantage AMR (GTE)", "GTE"),
    "Chevrolet_C8R_LM_2023": ("Corvette C8.R (GTE)", "GTE"),
    "Ferrari_488GTE_LM_2023": ("Ferrari 488 GTE Evo", "GTE"),
    "Porsche_911RSR-19_2023": ("Porsche 911 RSR-19", "GTE"),
    # Cup / one-make
    "992S_PC_2023": ("Porsche 911 Cup (992)", "Cup"),
    "McLaren_720sGChallenge_2026": ("McLaren 720S Challenge", "Cup"),
}

# Order in which classes are shown in the menu
CLASS_ORDER = ["Hypercar", "LMP2", "LMP3", "LMGT3", "GTE", "Cup", "Other"]

CLASS_EMOJI = {
    "Hypercar": "🚀",
    "LMP2": "🏎",
    "LMP3": "🛞",
    "LMGT3": "🏁",
    "GTE": "🔥",
    "Cup": "🏆",
    "Other": "❓",
}

# track_folder (as used by the game in UserData\player\Settings) -> display name.
# Always shown in original English, regardless of the bot's interface language —
# these are the real track/folder names players need to match against the game.
TRACKS: dict[str, str] = {
    "Bahrain": "Bahrain",
    "Circuit De Barcelona": "Barcelona",
    "Circuit Of The Americas": "COTA (Austin)",
    "Daytonarc": "Daytona",
    "Fuji": "Fuji",
    "Imola": "Imola",
    "Interlagos": "Interlagos",
    "Lagunaseca": "Laguna Seca",
    "Lemans": "Le Mans",
    "Monza": "Monza",
    "Paulricard": "Paul Ricard",
    "Portimao": "Portimão",
    "Qatar": "Lusail (Qatar)",
    "Sebring": "Sebring",
    "Silverstone": "Silverstone",
    "Silverstonewec": "Silverstone (WEC)",
    "Silverstone_International": "Silverstone Int.",
    "Silverstone_National": "Silverstone Nat.",
    "Spa": "Spa-Francorchamps",
}


def car_name(folder: str) -> str:
    return CARS.get(folder, (folder.replace("_", " "), "Other"))[0]


def car_class(folder: str) -> str:
    return CARS.get(folder, ("", "Other"))[1]


def track_name(folder: str) -> str:
    return TRACKS.get(folder, folder.replace("_", " "))
