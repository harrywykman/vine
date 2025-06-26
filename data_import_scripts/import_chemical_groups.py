from sqlmodel import Session, select

from data.vineyard import ChemicalGroup, ChemicalGroupType
from database import engine

chemical_groups_data = [
    ChemicalGroup(
        code="1",
        name="MBC – fungicides (methyl benzimidazole carbamates)",
        type=ChemicalGroupType.FUNGICIDE,
        moa="benzimidazoles",
    ),
    ChemicalGroup(
        code="2",
        name="Dicarboximide",
        type=ChemicalGroupType.FUNGICIDE,
        moa="dicarboximides",
    ),
    ChemicalGroup(
        code="3",
        name="DMI – fungicides (demethylation inhibitors) (SB I: Class 1)",
        type=ChemicalGroupType.FUNGICIDE,
        moa="imidazoles, piperazines, triazoles",
    ),
    ChemicalGroup(
        code="4",
        name="PA – fungicides (phenylamides)",
        type=ChemicalGroupType.FUNGICIDE,
        moa="acylalanines, oxazolidinones",
    ),
    ChemicalGroup(
        code="5",
        name="Amines (“morpholines”) (SBI: Class II)",
        type=ChemicalGroupType.FUNGICIDE,
        moa="piperidines, spiroketal-amines",
    ),
    ChemicalGroup(
        code="7",
        name="SDHI – fungicides (succinate dehydrogenase inhibitors)",
        type=ChemicalGroupType.FUNGICIDE,
        moa="N-methoxy-(phenyl-ethyl)-pyrazole-carboxamides, oxathiin-carboxamides, phenyl-benzamides, pyridine-carboxamides, pyrazole-4-carboxamides, phenyl-oxo-ethyl thiophene amide, pyridinyl-ethyl-benzamides",
    ),
    ChemicalGroup(
        code="8",
        name="Hydroxy-(2-amino-) pyrimidine",
        type=ChemicalGroupType.FUNGICIDE,
        moa="hydroxy-(2-amino-) pyrimidines",
    ),
    ChemicalGroup(
        code="9",
        name="AP – fungicides (anilino-pyrimidines)",
        type=ChemicalGroupType.FUNGICIDE,
        moa="anilino-pyrimidines",
    ),
    ChemicalGroup(
        code="11",
        name="QoI – fungicides (quinone outside inhibitors)",
        type=ChemicalGroupType.FUNGICIDE,
        moa="methoxy-acrylates, oximino-acetates, methoxy-carbamates, methoxy-acetamides",
    ),
    ChemicalGroup(
        code="12",
        name="PP – fungicides (phenylpyrroles)",
        type=ChemicalGroupType.FUNGICIDE,
        moa="phenylpyrroles",
    ),
    ChemicalGroup(
        code="13",
        name="Aza-naphthalenes",
        type=ChemicalGroupType.FUNGICIDE,
        moa="aryloxyquinoline, quinazolinone",
    ),
    ChemicalGroup(
        code="14",
        name="AH – fungicides (aromatic hydrocarbons) (chlorophenyls, nitroanilines)",
        type=ChemicalGroupType.FUNGICIDE,
        moa="aromatic hydrocarbons, heteroaromatics (1,2,4-thiadiazoles)",
    ),
    ChemicalGroup(
        code="17",
        name="KRI – fungicides (keto reductase inhibitors) (SBI: Class III)",
        type=ChemicalGroupType.FUNGICIDE,
        moa="hydroxyanilides, amino-pyrazolinone",
    ),
    ChemicalGroup(
        code="19",
        name="Polyoxins",
        type=ChemicalGroupType.FUNGICIDE,
        moa="peptidyl pyrimidine nucleoside",
    ),
    ChemicalGroup(
        code="20",
        name="Phenylureas",
        type=ChemicalGroupType.FUNGICIDE,
        moa="phenylureas",
    ),
    ChemicalGroup(
        code="21",
        name="Qil – fungicides (quinone inside inhibitors)",
        type=ChemicalGroupType.FUNGICIDE,
        moa="cyano-imidazole, sulfamoyl-triazole, picolinamides",
    ),
    ChemicalGroup(
        code="28", name="Carbamates", type=ChemicalGroupType.FUNGICIDE, moa="carbamates"
    ),
    ChemicalGroup(
        code="29",
        name="Uncouplers of oxidative phosphorylation",
        type=ChemicalGroupType.FUNGICIDE,
        moa="2,6-dinitro-anilines",
    ),
    ChemicalGroup(
        code="40",
        name="CAA – fungicides (carboxylic acid amides)",
        type=ChemicalGroupType.FUNGICIDE,
        moa="cinnamic acid amides, mandelic acid amides",
    ),
    ChemicalGroup(
        code="43",
        name="Benzamides",
        type=ChemicalGroupType.FUNGICIDE,
        moa="pyridinylmethyl-benzamides",
    ),
    ChemicalGroup(
        code="45",
        name="QoSI – fungicides (quinone outside inhibitor, stigmatellin binding type)",
        type=ChemicalGroupType.FUNGICIDE,
        moa="triazolo-pyrimidylamine",
    ),
    ChemicalGroup(
        code="49",
        name="OSBPI-fungicides",
        type=ChemicalGroupType.FUNGICIDE,
        moa="oxysterol binding protein homologue inhibition (piperidinyl-thiazole-isoxazolines)",
    ),
    ChemicalGroup(
        code="50",
        name="Actin disruption aryl-phenyl-ketones",
        type=ChemicalGroupType.FUNGICIDE,
        moa="benzophenone, benzoylpyridine",
    ),
    ChemicalGroup(
        code="52",
        name="DHODHI-fungicides (dihydroorotate dehydrogenase inhibitor)",
        type=ChemicalGroupType.FUNGICIDE,
        moa="phenyl-propanol",
    ),
    ChemicalGroup(
        code="M",
        name="Multi-site activity inorganic",
        type=ChemicalGroupType.FUNGICIDE,
        moa="chlorine dioxide, hydrogen peroxide + peroxyacetic acid, iodine, mercury, sodium metabisulphite, hydroxyquinoline",
    ),
    ChemicalGroup(
        code="M1",
        name="Multi-site activity inorganic (electrophiles)",
        type=ChemicalGroupType.FUNGICIDE,
        moa="copper cuprous oxide, copper hydroxide, copper oxychloride, copper ammonium acetate, tribasic copper sulphate, copper octanoate",
    ),
    ChemicalGroup(
        code="M2",
        name="Multi-site activity inorganic (electrophiles)",
        type=ChemicalGroupType.FUNGICIDE,
        moa="sulphur, potassium bicarbonate, calcium polysulfide",
    ),
    ChemicalGroup(
        code="M3",
        name="Multi-site activity dithiocarbamate and relatives (electrophiles)",
        type=ChemicalGroupType.FUNGICIDE,
        moa="dithio-carbamates and relatives",
    ),
    ChemicalGroup(
        code="M4",
        name="Multi-site activity phthalimides (electrophiles)",
        type=ChemicalGroupType.FUNGICIDE,
        moa="phthalimides",
    ),
    ChemicalGroup(
        code="M5",
        name="Multi-site activity chloronitriles (phthalonitriles) (unspecified mechanism)",
        type=ChemicalGroupType.FUNGICIDE,
        moa="chloronitriles (phthalonitriles)",
    ),
    ChemicalGroup(
        code="M6",
        name="Multi-site activity sulfamides (electrophiles)",
        type=ChemicalGroupType.FUNGICIDE,
        moa="sulfamides",
    ),
    ChemicalGroup(
        code="M7",
        name="Multi-site activity bis-guanidine (membrane disruptors, detergents)",
        type=ChemicalGroupType.FUNGICIDE,
        moa="bis-guanidines",
    ),
    ChemicalGroup(
        code="M9",
        name="Multi-site activity quinones (anthraquinones) (electrophiles)",
        type=ChemicalGroupType.FUNGICIDE,
        moa="quinones (anthraquinones)",
    ),
    ChemicalGroup(
        code="BM01",
        name="Multi-site activity plant extract",
        type=ChemicalGroupType.FUNGICIDE,
        moa="polypeptide (lectin), terpene hydrocarbons, terpene alcohols and terpene phenols",
    ),
    ChemicalGroup(
        code="BM02",
        name="Multi-site activity microbial (living microbes or extract, metabolites)",
        type=ChemicalGroupType.FUNGICIDE,
        moa="Streptomyces sp., Bacillus spp., Trichoderma spp.",
    ),
    ChemicalGroup(
        code="P01",
        name="Benzothiadiazole",
        type=ChemicalGroupType.FUNGICIDE,
        moa="Benzothiadiazole",
    ),
    ChemicalGroup(
        code="P03",
        name="Host plant defence inducer via systemic acquired resistance",
        type=ChemicalGroupType.FUNGICIDE,
        moa="isotianil",
    ),
    ChemicalGroup(
        code="P07",
        name="Phosphonates",
        type=ChemicalGroupType.FUNGICIDE,
        moa="ethyl phosphonate, phosphorous acid and salts",
    ),
    ChemicalGroup(
        code="U1",
        name="Unknown",
        type=ChemicalGroupType.FUNGICIDE,
        moa="potassium salts of fatty acids",
    ),
    ChemicalGroup(
        code="U6",
        name="Unknown phenyl-acetamide",
        type=ChemicalGroupType.FUNGICIDE,
        moa="phenyl-acetamide",
    ),
    ChemicalGroup(
        code="U12",
        name="Cell membrane disruption (proposed) guanidines",
        type=ChemicalGroupType.FUNGICIDE,
        moa="guanidines",
    ),
]


def populate_chemical_groups():
    with Session(engine) as session:
        for group in chemical_groups_data:
            existing = session.exec(
                select(ChemicalGroup).where(ChemicalGroup.code == group.code)
            ).first()
            if existing:
                print(
                    f"Chemical group with code {group.code} already exists. Skipping."
                )
                continue

            session.add(group)

        session.commit()
        print("Chemical groups populated or already up-to-date.")


if __name__ == "__main__":
    populate_chemical_groups()
