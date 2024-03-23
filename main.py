from dataclasses import dataclass
import fiona
import csv
from shapely.geometry import Polygon, shape

PDR_FILE = "shapefiles/PDR 20231208.zip"
LEGACY_FILE = "shapefiles/Legacy_Forests.zip"
OUTPUT_FILE = "timber_sales.csv"
LOG_EVERY = 100

legacy_shapes: list[Polygon] = []

with fiona.open(f"zip://{LEGACY_FILE}") as legacy:
    for feature in legacy:
        props = feature["properties"]
        legacy_shapes.append(shape(feature["geometry"]))


@dataclass
class TimberSale:
    region: str
    district: str
    admin: str
    name: str
    sale_date: str
    technique: str
    sale_acreage: float | None
    unit_acreage: float | None
    acres_of_legacy: float
    # stand_ages: list[str]
    # trust_beneficiaries: list[str]


count = 0

with (
    fiona.open(f"zip://{PDR_FILE}") as pdr,
    open(OUTPUT_FILE, "w", newline="") as f,
):
    writer = csv.writer(f)
    writer.writerow(TimberSale.__annotations__.keys())
    for feature in pdr:
        count += 1
        props = feature["properties"]
        geom = shape(feature["geometry"])

        ts = TimberSale(
            region=props["REGION_NM"],
            district=props["DISTRICT_N"],
            admin=props["ADMIN_NM"],
            name=props["TS_NM"],
            sale_date=props["TS_AUCTION"].split(" ")[0],
            technique=props["TECHNIQUE_"],
            sale_acreage=round(props["TS_ACRES"], 2) if props["TS_ACRES"] else None,
            unit_acreage=round(props["ACRES_TREA"], 2) if props["ACRES_TREA"] else None,
            acres_of_legacy=sum(
                geom.intersection(legacy_shape).area for legacy_shape in legacy_shapes
            ),
            # stand_ages=[],
            # trust_beneficiaries=[],
        )
        writer.writerow(ts.__dict__.values())

        if count % LOG_EVERY == 0:
            print(f"Processed {count} timber sales...")
