# NASA Earthdata Explorer

A small web app for requesting NASA Earth science data through NASA's
[Harmony service](https://harmony.earthdata.nasa.gov/) with the official
[harmony-py client](https://github.com/nasa/harmony-py). Enter a CMR collection
ID and optionally constrain the request by a longitude/latitude bounding box and
date range. The app submits the request and shows direct download links for the
results.

## Run locally

Requires Python 3.11 or newer and NASA Earthdata Login credentials:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export EDL_USERNAME="your-earthdata-username"
export EDL_PASSWORD="your-earthdata-password"
streamlit run app.py
```

Alternatively, configure Earthdata Login in `~/.netrc` as documented by
[NASA harmony-py](https://github.com/nasa/harmony-py#using-harmony-py). Credentials
are read by harmony-py on the server and are not requested or stored by the app.

The app limits each request to at most 100 granules (10 by default). Collection
IDs can be found through NASA's [Common Metadata Repository](https://cmr.earthdata.nasa.gov/search/site/).

This Python app cannot run on GitHub Pages, which only serves static files. Run it
locally or deploy it to a Python-capable host. Do not expose a deployment that
uses shared Earthdata credentials publicly without adding appropriate access
controls.

## Static site (GitHub Pages)

The site is static: it only displays files that were prepared offline.
[index.html](index.html) is a map of Galveston Bay (panning/zoom limited to the
Galveston–Houston area) with a layer picker and a slider to step through 6-month snapshots.

Layers are listed in [data/manifest.json](data/manifest.json). Two are included:

- **Benzene detection** (`type: "status"`). Two views: *Status* (red = detected,
  white = not detected, grey = no coverage) and *Recency*, which colors each cell by how
  recently benzene was last detected, as of the selected snapshot (red = now, fading to
  pale yellow = long ago, white = never).
- **Turbidity** (`type: "numeric"`), shaded on a color scale. Use the same approach for
  sediment or any other measured value.

### Data format

One GeoJSON file per snapshot, in EPSG:4326 (plain longitude/latitude). Coordinates are
`[longitude, latitude]` and polygon rings must be closed.

| Layer type | Required polygon property | Values |
|---|---|---|
| `status` | `status` | `detected`, `not_detected`, `no_coverage` |
| `numeric` | the name in the layer's `property` (e.g. `value`) | a number, or `null` for no data |

Recency matches cells across snapshots, so every snapshot of a layer should use the same
grid. Give each polygon a `cell_id` property to make that explicit (otherwise identical
geometry is used as the id).

### Adding a layer (e.g. sediment)

1. Put the files in `data/<layer>/` (e.g. `data/sediment/2024-H1.geojson`).
2. Add an entry to `layers` in [data/manifest.json](data/manifest.json):

```json
{
  "id": "sediment",
  "name": "Suspended sediment",
  "type": "numeric",
  "property": "value",
  "unit": "mg/L",
  "min": 0,
  "max": 100,
  "palette": ["#f7f4e9", "#c9a66b", "#6b4226"],
  "description": "Shown under the map.",
  "snapshots": [{ "label": "2024 Jan–Jun", "file": "data/sediment/2024-H1.geojson" }]
}
```

Each layer has its own snapshot list (oldest first), so layers need not share dates.
No code changes are needed.

### Data workflow

1. Download and aggregate the data locally (e.g. in QGIS) per period.
2. Grid the study area, classify or measure each cell, and export one GeoJSON per period.
3. Optional: export the Galveston shapefile as GeoJSON (reproject to EPSG:4326, simplify)
   to `data/galveston-boundary.geojson`. It is drawn as an outline when present, and is
   also useful for clipping polygons to water.

The files currently in `data/` are **randomly generated sample data** and must be replaced.
Check which instrument/product actually measures benzene (or whether a proxy such as
formaldehyde is used) and say so on the map.

### Deploy

Set Settings → Pages → Source to "GitHub Actions". Each push to `main` publishes
`index.html` and `data/` via [.github/workflows/pages.yml](.github/workflows/pages.yml).
Everything pushed is public. Preview locally with `python -m http.server` and open
http://localhost:8000 (opening the file directly will not work).

## Tests

```bash
python -m unittest
```