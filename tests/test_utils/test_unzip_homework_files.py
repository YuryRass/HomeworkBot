import os
import pytest

from utils.unzip_test_files import save_test_files
from conftest import CheckExistTestFolder


class TestCheckExistTestFolder(CheckExistTestFolder):
    pytestmark = pytest.mark.usefixtures("delete_all_files")

    @pytest.mark.asyncio
    async def test_save_test_files(self, out_dir, downloaded_file):
        # помещаем в папку out распакованный архив
        await save_test_files(out_dir, downloaded_file)

        assert os.listdir(out_dir) == \
            ['archive.zip'] + [f'file_{i}.py' for i in range(5)]
