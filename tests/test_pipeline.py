def test_pipeline_1():
    import tempfile

    from corazon import run_pipeline

    tic_id = 383724012
    sector = 14
    out_dir = tempfile.NamedTemporaryFile().name
    run_pipeline.run_write_one(tic_id, sector, out_dir)

import json
import requests
import sys
import typing

from urllib.parse import urlencode, quote
def mast_query(tic_id: int) -> typing.Any:
    request = {
        'service': 'Mast.Catalogs.Filtered.Tic',
        'params': {
            'columns': '*',
            'filters': [{
                'paramName': 'ID',
                'values': [tic_id],
            }],
        },
        'format': 'json',
        'removenullcolumns': True
    }
    req_str = json.dumps(request)
    req_str = quote(req_str)
    req_payload = f'request={req_str}'

    url = 'https://mast.stsci.edu/api/v0/invoke'
    content = requests.post(url, data=req_payload, headers={
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/plain'
    }).json()
    if content['status'] not in ['COMPLETE']:
        raise NotImplementedError

    import pdb; pdb.set_trace()
    pass


import csv
import decimal
import slugify
import types
def parse_mast_csv(filepath: str) -> types.GeneratorType:
    with open(filepath, 'r') as stream:
        reader = csv.reader(stream)

        next(reader)
        next(reader)
        headers = [slugify.slugify(col.strip('#')) for col in next(reader)]
        field_types = [slugify.slugify(col.strip('#')) for col in next(reader)]
        next(reader)
        for row in reader:
            datum = {key: value for key, value in zip(headers, row)}
            for idx, field_type in enumerate(field_types):
                field_name = headers[idx]
                if field_type in ['string']:
                    if datum[field_name].lower() == 'false':
                        datum[field_name] = False

                    elif datum[field_name].lower() == 'true':
                        datum[field_name] = True

                    elif datum[field_name].strip() == '':
                        datum[field_name] = None

                    continue

                elif field_type in ['ra', 'dec']:
                    datum[field_name] = decimal.Decimal(datum[field_name])

                elif field_type in ['float']:
                    datum[field_name] = float(datum[field_name])

                elif field_type in ['int']:
                    datum[field_name] = int(datum[field_name])

                else:
                    raise NotImplementedError(field_type)

            yield datum

def test_concurrent_pipeline():
    import os
    import shutil
    import tempfile

    from corazon import run_pipeline

    from tess_stars2px import tess_stars2px_function_entry

    filepath = './tess-data/CTLv8_0_287_713310_43_634668.csv'
    base_out_dir = '/tmp/lightkurves'
    if os.path.exists(base_out_dir):
        shutil.rmtree(base_out_dir)

    for row in parse_mast_csv(filepath):
        outId, outEclipLong, outEclipLat, outSec, outCam, outCcd, outColPix, \
            outRowPix, scinfo = tess_stars2px_function_entry(row['tic-id'], float(row['ra']), float(row['dec']))
        for idx in range(0, len(outId)):
            tic_id = outId[idx]
            sector = outSec[idx]
            print(f'Testing TIC:{tic_id} - Sector: {sector}')
            tic_folder = os.path.join(base_out_dir, str(tic_id), str(sector))
            if not os.path.exists(tic_folder):
                os.makedirs(tic_folder)

            run_pipeline.run_write_one(tic_id, sector, tic_folder)
