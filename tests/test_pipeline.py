"""Unit tests for pipeline integration"""

import json
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.pipeline import PipelineScraper, scrape_products
from src.config import Config


class TestPipelineScraper:
    """Test cases for PipelineScraper class"""
    
    def test_pipeline_scraper_initialization(self):
        """Test PipelineScraper initialization"""
        pipeline = PipelineScraper()
        
        assert pipeline.config is not None
        assert pipeline.scraper is not None
        assert pipeline.logger is not None
    
    def test_pipeline_scraper_custom_config(self):
        """Test PipelineScraper with custom config"""
        config = Config(delay=5.0, limit=100)
        pipeline = PipelineScraper(config=config)
        
        assert pipeline.config["delay"] == 5.0
        assert pipeline.scraper.delay == 5.0
    
    def test_pipeline_scraper_custom_logger(self):
        """Test PipelineScraper with custom logger"""
        logger = Mock()
        pipeline = PipelineScraper(logger=logger)
        
        assert pipeline.logger == logger
    
    def test_pipeline_scraper_callbacks(self):
        """Test PipelineScraper with progress and batch callbacks"""
        on_progress = Mock()
        on_batch = Mock()
        
        pipeline = PipelineScraper(
            on_progress=on_progress,
            on_batch=on_batch
        )
        
        assert pipeline.on_progress == on_progress
        assert pipeline.on_batch == on_batch
    
    @patch('src.pipeline.Scraper')
    def test_pipeline_scrape_success(self, mock_scraper_class):
        """Test successful scrape operation"""
        mock_scraper = Mock()
        mock_scraper.scrape_and_save.return_value = True
        mock_scraper.stats = {
            "products_transformed": 100,
            "products_fetched": 100,
            "pages_fetched": 1
        }
        mock_scraper_class.return_value = mock_scraper
        
        pipeline = PipelineScraper()
        result = pipeline.scrape()
        
        assert result["success"] is True
        assert "timestamp" in result
        assert "duration_seconds" in result
        assert "statistics" in result
        assert result["statistics"]["products_transformed"] == 100
    
    @patch('src.pipeline.Scraper')
    def test_pipeline_scrape_failure(self, mock_scraper_class):
        """Test failed scrape operation"""
        mock_scraper = Mock()
        mock_scraper.scrape_and_save.return_value = False
        mock_scraper.stats = {}
        mock_scraper_class.return_value = mock_scraper
        
        pipeline = PipelineScraper()
        result = pipeline.scrape()
        
        assert result["success"] is False
    
    @patch('src.pipeline.Scraper')
    @patch('builtins.open', create=True)
    def test_pipeline_scrape_with_return_data(self, mock_open, mock_scraper_class):
        """Test scrape with return_data=True"""
        mock_scraper = Mock()
        mock_scraper.scrape_and_save.return_value = True
        mock_scraper.stats = {"products_transformed": 10}
        mock_scraper_class.return_value = mock_scraper
        
        test_data = {"items": [{"id": "1"}]}
        mock_file = Mock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=None)
        mock_file.read.return_value = json.dumps(test_data)
        mock_open.return_value = mock_file
        
        pipeline = PipelineScraper()
        result = pipeline.scrape(return_data=True)
        
        assert result["success"] is True
        assert "data" in result
        assert result["data"] == test_data
    
    @patch('src.pipeline.Scraper')
    @patch('builtins.open', create=True)
    def test_pipeline_scrape_with_metadata(self, mock_open, mock_scraper_class):
        """Test scrape_with_metadata method"""
        mock_scraper = Mock()
        mock_scraper.scrape_and_save.return_value = True
        mock_scraper.stats = {"products_transformed": 50}
        mock_scraper_class.return_value = mock_scraper
        
        test_data = {"items": [{"id": "1"}]}
        mock_file = Mock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=None)
        mock_file.read.return_value = json.dumps(test_data)
        mock_file.write = Mock()
        mock_open.return_value = mock_file
        
        pipeline = PipelineScraper()
        result = pipeline.scrape_with_metadata()
        
        assert result["success"] is True
        assert "metadata" in result
        # Metadata structure may be flat or nested
        metadata = result["metadata"]
        assert "timestamp" in metadata or "scraping_metadata" in metadata
        if "scraping_metadata" in metadata:
            assert "timestamp" in metadata["scraping_metadata"]
            assert "statistics" in metadata["scraping_metadata"]
        else:
            assert "statistics" in metadata
    
    @patch('src.pipeline.Scraper')
    def test_pipeline_scrape_with_metadata_failure(self, mock_scraper_class):
        """Test scrape_with_metadata when scraping fails"""
        mock_scraper = Mock()
        mock_scraper.scrape_and_save.return_value = False
        mock_scraper_class.return_value = mock_scraper
        
        pipeline = PipelineScraper()
        result = pipeline.scrape_with_metadata()
        
        assert result["success"] is False
        assert "error" in result
    
    @patch('src.pipeline.Scraper')
    def test_pipeline_get_status(self, mock_scraper_class):
        """Test get_status method"""
        mock_scraper = Mock()
        mock_scraper.stats = {"products_transformed": 100}
        mock_scraper_class.return_value = mock_scraper
        
        pipeline = PipelineScraper()
        status = pipeline.get_status()
        
        assert status["ready"] is True
        assert "config" in status
        assert "statistics" in status
        assert status["statistics"]["products_transformed"] == 100
    
    @patch('src.pipeline.Scraper')
    def test_pipeline_custom_output_file(self, mock_scraper_class):
        """Test scrape with custom output file"""
        mock_scraper = Mock()
        mock_scraper.scrape_and_save.return_value = True
        mock_scraper.stats = {}
        mock_scraper_class.return_value = mock_scraper
        
        pipeline = PipelineScraper()
        result = pipeline.scrape(output_file="custom_output.json")
        
        assert result["output_file"] == "custom_output.json"
        mock_scraper.scrape_and_save.assert_called_once_with("custom_output.json")


class TestScrapeProducts:
    """Test cases for scrape_products convenience function"""
    
    @patch('src.pipeline.PipelineScraper')
    def test_scrape_products_basic(self, mock_pipeline_class):
        """Test basic scrape_products usage"""
        mock_pipeline = Mock()
        mock_pipeline.scrape.return_value = {
            "success": True,
            "statistics": {"products_transformed": 50}
        }
        mock_pipeline_class.return_value = mock_pipeline
        
        result = scrape_products()
        
        assert result["success"] is True
        mock_pipeline.scrape.assert_called_once()
    
    @patch('src.pipeline.PipelineScraper')
    def test_scrape_products_with_kwargs(self, mock_pipeline_class):
        """Test scrape_products with custom parameters"""
        mock_pipeline = Mock()
        mock_pipeline.scrape.return_value = {"success": True, "statistics": {}}
        mock_pipeline_class.return_value = mock_pipeline
        
        result = scrape_products(
            output_file="custom.json",
            base_url="https://custom.com",
            delay=5.0
        )
        
        assert result["success"] is True
        # Verify config was set correctly
        call_args = mock_pipeline_class.call_args
        assert call_args[1]["config"]["delay"] == 5.0
        assert call_args[1]["config"]["base_url"] == "https://custom.com"

