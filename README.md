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

## Tests

```bash
python -m unittest
```