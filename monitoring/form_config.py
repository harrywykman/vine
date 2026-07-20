from monitoring.models import ObservationTarget

# Display config for the disease partial. Kept separate from ObservationTarget's
# enum values because those values were made unique across the whole enum
# (e.g. "Leaves (powdery)") to avoid Python enum aliasing — that's not what
# should be shown to the scout, so labels here are the clean, human label.
#
# heading = section subheading shown above the group (e.g. "Powdery Mildew")
# fields  = ordered list of {target, label} shown under that heading

DISEASE_SECTIONS: list[dict] = [
    {
        "heading": "Powdery Mildew",
        "fields": [
            {"target": ObservationTarget.POWDERY_FLAG_SHOOTS, "label": "Flag shoots"},
            {"target": ObservationTarget.POWDERY_LEAVES, "label": "Leaves"},
            {"target": ObservationTarget.POWDERY_BUNCHES, "label": "Bunches"},
            {"target": ObservationTarget.POWDERY_BERRIES, "label": "Berries"},
        ],
    },
    {
        "heading": "Downy Mildew",
        "fields": [
            {
                "target": ObservationTarget.DOWNY_OIL_SPOTS,
                "label": "Oil spots on leaves",
            },
            {"target": ObservationTarget.DOWNY_LEAVES, "label": "Down on leaves"},
            {"target": ObservationTarget.DOWNY_BUNCHES, "label": "Bunches"},
        ],
    },
    {
        "heading": "Botrytis / Other Bunch Rots",
        "fields": [
            {
                "target": ObservationTarget.BOTRYTIS_LEAF_LESIONS,
                "label": "Leaf lesions",
            },
            {
                "target": ObservationTarget.BOTRYTIS_SHOOT_LESIONS,
                "label": "Shoot lesions",
            },
            {
                "target": ObservationTarget.BOTRYTIS_BUNCH_DAMAGE,
                "label": "Bunch damage",
            },
        ],
    },
    {
        "heading": "Leaf Spot / Phomopsis",
        "fields": [
            {"target": ObservationTarget.PHOMOPSIS_LEAVES, "label": "Leaves"},
            {"target": ObservationTarget.PHOMOPSIS_SHOOTS, "label": "Shoots"},
            {"target": ObservationTarget.PHOMOPSIS_BUNCHES, "label": "Bunches"},
            {"target": ObservationTarget.PHOMOPSIS_CANES, "label": "Canes"},
        ],
    },
    {
        "heading": "Other Diseases",
        "fields": [
            {
                "target": ObservationTarget.DIAPORTHE_SYMPTOMS,
                "label": "Diaporthe symptoms",
            },
            {"target": ObservationTarget.LRV_SYMPTOMS, "label": "LRV symptoms"},
            {
                "target": ObservationTarget.TRUNK_DISEASE_SYMPTOMS,
                "label": "Trunk disease symptoms",
            },
            {
                "target": ObservationTarget.AUSTRALIAN_GRAPEVINE_YELLOWS,
                "label": "Australian Grapevine Yellows",
            },
            {
                "target": ObservationTarget.SCLEROTINIA_SYMPTOMS,
                "label": "Sclerotinia symptoms",
            },
        ],
    },
]

# Flat ordered list of target values, in the exact order they're rendered in
# the form. The POST handler zips submitted parallel lists against this to
# know which target each list position corresponds to.
DISEASE_TARGET_ORDER: list[ObservationTarget] = [
    field["target"] for section in DISEASE_SECTIONS for field in section["fields"]
]
