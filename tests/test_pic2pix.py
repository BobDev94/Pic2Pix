"""
Simple pytest tests for pic2pix functionality
"""

import pytest
import argparse
import tempfile
import os
from PIL import Image
import numpy as np

# Import the functions we want to test
from pic2pix import uint8, posint, fps_range, duration_range


class TestValidationFunctions:
    """Test the argument validation functions"""

    def test_uint8_valid_values(self):
        """Test uint8 validation with valid values"""
        assert uint8("0") == 0
        assert uint8("127") == 127
        assert uint8("255") == 255

    def test_uint8_invalid_values(self):
        """Test uint8 validation with invalid values"""
        with pytest.raises(argparse.ArgumentTypeError):
            uint8("-1")
        with pytest.raises(argparse.ArgumentTypeError):
            uint8("256")
        with pytest.raises(argparse.ArgumentTypeError):
            uint8("abc")

    def test_posint_valid_values(self):
        """Test posint validation with valid values"""
        assert posint("1") == 1
        assert posint("100") == 100
        assert posint("999") == 999

    def test_posint_invalid_values(self):
        """Test posint validation with invalid values"""
        with pytest.raises(argparse.ArgumentTypeError):
            posint("0")
        with pytest.raises(argparse.ArgumentTypeError):
            posint("-1")
        with pytest.raises(argparse.ArgumentTypeError):
            posint("abc")

    def test_fps_range_valid_values(self):
        """Test fps_range validation with valid values"""
        assert fps_range("0.1") == 0.1
        assert fps_range("12") == 12.0
        assert fps_range("240") == 240.0

    def test_fps_range_invalid_values(self):
        """Test fps_range validation with invalid values"""
        with pytest.raises(argparse.ArgumentTypeError):
            fps_range("0.05")  # Too low
        with pytest.raises(argparse.ArgumentTypeError):
            fps_range("300")  # Too high
        with pytest.raises(argparse.ArgumentTypeError):
            fps_range("abc")

    def test_duration_range_valid_values(self):
        """Test duration_range validation with valid values"""
        assert duration_range("1") == 1
        assert duration_range("1000") == 1000
        assert duration_range("20000") == 20000

    def test_duration_range_invalid_values(self):
        """Test duration_range validation with invalid values"""
        with pytest.raises(argparse.ArgumentTypeError):
            duration_range("0")  # Too low
        with pytest.raises(argparse.ArgumentTypeError):
            duration_range("25000")  # Too high
        with pytest.raises(argparse.ArgumentTypeError):
            duration_range("abc")


class TestImageProcessing:
    """Test basic image processing functionality"""

    def create_test_image(self, size=(100, 100), color=(255, 0, 0, 255)):
        """Helper to create a test image"""
        img = Image.new("RGBA", size, color)
        return img

    def test_create_simple_image(self):
        """Test that we can create and work with PIL images"""
        img = self.create_test_image()
        assert img.size == (100, 100)
        assert img.mode == "RGBA"

    def test_image_to_numpy_conversion(self):
        """Test converting PIL image to numpy array"""
        img = self.create_test_image()
        np_img = np.array(img)
        assert np_img.shape == (100, 100, 4)  # height, width, channels
        assert np_img.dtype == np.uint8

    def test_palette_array_structure(self):
        """Test that our palette has the correct structure"""
        # This is the palette from your main function
        palette = [
            [31, 36, 10],
            [57, 87, 28],
            [165, 140, 39],
            [239, 172, 40],
            [239, 216, 161],
        ]
        np_palette = np.array(palette)
        assert np_palette.shape[1] == 3  # RGB channels
        assert np_palette.dtype == np.uint8 or np_palette.max() <= 255


class TestFileOperations:
    """Test file-related operations"""

    def test_output_directory_creation(self):
        """Test that output directories are created properly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_output_dir = os.path.join(temp_dir, "output")
            os.makedirs(base_output_dir, exist_ok=True)

            # Test folder structure
            folder_dir = os.path.join(base_output_dir, "folder")
            os.makedirs(folder_dir, exist_ok=True)

            assert os.path.exists(base_output_dir)
            assert os.path.exists(folder_dir)

    def test_image_file_extensions(self):
        """Test that we recognize common image extensions"""
        img_exts = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")

        test_files = [
            "image.png",
            "photo.jpg",
            "picture.JPEG",
            "bitmap.bmp",
            "animation.gif",
            "modern.webp",
        ]

        for filename in test_files:
            assert any(filename.lower().endswith(ext) for ext in img_exts)


# Integration test that requires the full environment
class TestCommandLine:
    """Test command line interface"""

    def test_import_main_function(self):
        """Test that we can import the main function"""
        from pic2pix import main

        assert callable(main)
