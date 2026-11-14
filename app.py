import datetime as dt
import math

import streamlit as st
from harmony import BBox, Client, Collection, Request


def build_request(
    collection_id,
    west=None,
    south=None,
    east=None,
    north=None,
    start_date=None,
    end_date=None,
    max_results=10,
    output_format=None,
):
    collection_id = collection_id.strip()
    if not collection_id:
        raise ValueError('Enter a NASA CMR collection ID.')

    bounds = (west, south, east, north)
    if any(value not in (None, '') for value in bounds):
        if any(value in (None, '') for value in bounds):
            raise ValueError('Enter all four bounding-box coordinates, or leave them all blank.')
        try:
            west, south, east, north = (float(value) for value in bounds)
        except (TypeError, ValueError) as error:
            raise ValueError('Bounding-box coordinates must be numbers.') from error
        if not all(math.isfinite(value) for value in (west, south, east, north)):
            raise ValueError('Bounding-box coordinates must be finite numbers.')
        if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
            raise ValueError('Use bounds with -180 ≤ west < east ≤ 180 and -90 ≤ south < north ≤ 90.')
        spatial = BBox(west, south, east, north)
    else:
        spatial = None

    if (start_date is None) != (end_date is None):
        raise ValueError('Choose both a start and end date.')
    if start_date and end_date:
        if start_date > end_date:
            raise ValueError('The start date must be on or before the end date.')
        temporal = {
            'start': dt.datetime.combine(start_date, dt.time.min),
            'stop': dt.datetime.combine(end_date, dt.time.max),
        }
    else:
        temporal = None

    if not isinstance(max_results, int) or not 1 <= max_results <= 100:
        raise ValueError('Maximum results must be between 1 and 100.')

    options = {
        'collection': Collection(id=collection_id),
        'max_results': max_results,
    }
    if spatial is not None:
        options['spatial'] = spatial
    if temporal is not None:
        options['temporal'] = temporal
    if output_format and output_format.strip():
        options['format'] = output_format.strip()

    request = Request(**options)
    if not request.is_valid():
        raise ValueError('; '.join(request.error_messages()))
    return request


def main():
    st.set_page_config(page_title='NASA Earthdata Explorer', page_icon='🛰️')
    st.title('NASA Earthdata Explorer')
    st.write(
        'Request NASA Earth science data through Harmony. Enter a CMR collection ID, '
        'optionally narrow it by location or date, and get direct links to the results.'
    )
    st.caption(
        'This app uses NASA’s harmony-py client. Configure Earthdata Login credentials '
        'for the account running this app before submitting a request.'
    )

    with st.form('harmony-request'):
        collection_id = st.text_input('NASA CMR collection ID', placeholder='C1234567890-PROVIDER')
        st.subheader('Optional filters')
        west_col, south_col, east_col, north_col = st.columns(4)
        west = west_col.text_input('West longitude')
        south = south_col.text_input('South latitude')
        east = east_col.text_input('East longitude')
        north = north_col.text_input('North latitude')
        filter_by_date = st.checkbox('Filter by date')
        if filter_by_date:
            date_col1, date_col2 = st.columns(2)
            start_date = date_col1.date_input('Start date', value=dt.date(2020, 1, 1))
            end_date = date_col2.date_input('End date', value=dt.date.today())
        else:
            start_date = end_date = None
        output_format = st.text_input('Output format (optional)', placeholder='image/tiff')
        max_results = st.slider('Maximum granules', min_value=1, max_value=100, value=10)
        submitted = st.form_submit_button('Request data')

    if submitted:
        try:
            request = build_request(
                collection_id,
                west,
                south,
                east,
                north,
                start_date,
                end_date,
                max_results,
                output_format,
            )
        except ValueError as error:
            st.error(str(error))
            return

        try:
            client = Client()
            with st.spinner('Submitting request and waiting for NASA Harmony…'):
                job_id = client.submit(request)
                client.wait_for_processing(job_id, show_progress=False)
                result_urls = list(client.result_urls(job_id))
        except Exception as error:
            st.error(f'NASA Harmony could not complete the request: {error}')
            return

        st.success(f'Request complete. Harmony job ID: {job_id}')
        if result_urls:
            st.subheader('Data results')
            for index, url in enumerate(result_urls, start=1):
                st.link_button(f'Download result {index}', url)
        else:
            st.info('The request completed, but Harmony returned no downloadable results.')


if __name__ == '__main__':
    main()
