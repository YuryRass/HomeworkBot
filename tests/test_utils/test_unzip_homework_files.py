import os
import pytest

from utils.unzip_test_files import save_test_files

pytestmark = pytest.mark.usefixtures("delete_all_files")


@pytest.mark.asyncio
async def test_save_test_files(out_dir, zip_file):
    # сырое представление архива in.zip
    with open(zip_file, 'rb') as myzip:
        downloaded_file = myzip.read()

    # помещаем в папку out распакованный архив
    await save_test_files(out_dir, downloaded_file)

    assert os.listdir(out_dir) == \
        ['archive.zip'] + [f'file_{i}.py' for i in range(5)]
