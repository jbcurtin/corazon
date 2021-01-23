

def test_pipeline_1():
    import tempfile

    from corazon import run_pipeline

    tic_id = 383724012
    sector = 14
    out_dir = tempfile.NamedTemporaryFile().name
    run_pipeline.run_write_one(tic_id, sector, out_dir)
