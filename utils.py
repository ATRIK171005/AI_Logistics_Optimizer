"""
utils.py
--------
Enterprise Architectural Utility Module for AI-Based Logistics Network Optimizer.

This module enforces production-quality Python engineering practices:
1. Custom Exception Hierarchy (Domain-specific error handling for OR and ML).
2. Centralized Structured Logging (PEP 282 compliant, console + file sinks).
3. DataFrame Schema Validation & Type Checking.
"""

import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd


# =====================================================================
# 1. CUSTOM EXCEPTION HIERARCHY
# =====================================================================
class LogisticsBaseException(Exception):
    """Base exception class for all AI Logistics Optimizer operations."""
    pass


class DataValidationError(LogisticsBaseException):
    """Raised when uploaded or loaded CSV schema fails validation constraints."""
    def __init__(self, message: str, missing_columns: Optional[List[str]] = None):
        super().__init__(message)
        self.missing_columns = missing_columns or []


class OptimizationFeasibilityError(LogisticsBaseException):
    """Raised when the Linear Programming solver encounters an infeasible or unbounded state."""
    def __init__(self, message: str, solver_status: str):
        super().__init__(message)
        self.solver_status = solver_status


class DatabaseExecutionError(LogisticsBaseException):
    """Raised when SQLite transactional execution encounters a persistence failure."""
    pass


# =====================================================================
# 2. CENTRALIZED ENTERPRISE LOGGER SETUP
# =====================================================================
class LogisticsLogger:
    """
    Singleton-patterned structured logger for tracking OR-Tools optimization steps,
    SQL queries, and machine learning pipeline metrics.
    """
    _instance: Optional[logging.Logger] = None

    @classmethod
    def get_logger(cls, name: str = "MaerskAI_Logistics") -> logging.Logger:
        if cls._instance is not None:
            return cls._instance

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers if re-initialized
        if not logger.handlers:
            formatter = logging.Formatter(
                fmt="[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

            # Console Handler (Standard Output)
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

            # File Handler (Persistent System Log)
            log_dir = Path(__file__).parent / "database"
            log_dir.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_dir / "system.log", encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        cls._instance = logger
        return logger


# Initialize global default logger
logger = LogisticsLogger.get_logger()


# =====================================================================
# 3. SCHEMA VALIDATION UTILITIES
# =====================================================================
def validate_schema(df: pd.DataFrame, required_columns: List[str], dataset_name: str) -> bool:
    """
    Validates that a DataFrame strictly conforms to required domain schemas.

    Args:
        df: The pandas DataFrame to validate.
        required_columns: Exact list of column headers required.
        dataset_name: Human-readable name of the dataset for logging/errors.

    Returns:
        bool: True if validation succeeds.

    Raises:
        DataValidationError: If columns are missing or DataFrame is empty.
    """
    if df is None or df.empty:
        err_msg = f"Dataset '{dataset_name}' is empty or uninitialized."
        logger.error(err_msg)
        raise DataValidationError(err_msg)

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        err_msg = f"Schema violation in '{dataset_name}'. Missing required columns: {missing}"
        logger.error(err_msg)
        raise DataValidationError(err_msg, missing_columns=missing)

    logger.debug(f"Schema validation passed for dataset '{dataset_name}' ({len(df)} records).")
    return True
