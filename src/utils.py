"""
Utility functions for error handling, retry logic, and validation
"""

import time
import logging
import functools
from typing import Callable, Any, Optional, Type, Tuple
from datetime import datetime


logger = logging.getLogger(__name__)


def retry_on_exception(
    max_attempts: int = 3,
    delay: float = 2.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Decorator to retry function on exception with exponential backoff

    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch
        on_retry: Optional callback function called on each retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}",
                            exc_info=True
                        )
                        raise

                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. "
                        f"Retrying in {current_delay:.1f}s..."
                    )

                    if on_retry:
                        try:
                            on_retry(attempt, e)
                        except Exception as callback_error:
                            logger.error(f"Retry callback error: {callback_error}")

                    time.sleep(current_delay)
                    current_delay *= backoff

            # Should never reach here, but just in case
            raise last_exception

        return wrapper
    return decorator


def validate_config(config: dict) -> dict:
    """
    Validate and sanitize configuration with defaults

    Args:
        config: Configuration dictionary

    Returns:
        Validated and sanitized config

    Raises:
        ValueError: If critical config is missing or invalid
    """
    validated = config.copy()

    # Mode validation
    mode = validated.get('mode', 'selenium')
    if mode not in ['api', 'selenium']:
        logger.warning(f"Invalid mode '{mode}', defaulting to 'selenium'")
        validated['mode'] = 'selenium'

    # Monitored accounts
    if 'monitored_accounts' not in validated or not validated['monitored_accounts']:
        raise ValueError("monitored_accounts is required and cannot be empty")

    if not isinstance(validated['monitored_accounts'], list):
        raise ValueError("monitored_accounts must be a list")

    # Bot settings
    if 'bot' not in validated:
        validated['bot'] = {}

    bot_defaults = {
        'check_interval': 5,
        'personality': 'haber_duyurucu',
        'max_tweets_per_run': 10,
        'tweets_to_post_per_run': 1,
        'min_tweet_length': 50,
        'max_tweet_length': 280
    }

    for key, default_value in bot_defaults.items():
        if key not in validated['bot']:
            validated['bot'][key] = default_value
            logger.info(f"Using default bot.{key}: {default_value}")

    # Validate numeric values
    numeric_fields = ['check_interval', 'max_tweets_per_run', 'tweets_to_post_per_run',
                     'min_tweet_length', 'max_tweet_length']

    for field in numeric_fields:
        value = validated['bot'].get(field)
        if value is not None and (not isinstance(value, (int, float)) or value <= 0):
            logger.warning(f"Invalid bot.{field}: {value}, using default")
            validated['bot'][field] = bot_defaults[field]

    # AI settings
    if 'ai' not in validated:
        validated['ai'] = {}

    ai_defaults = {
        'provider': 'groq',
        'model': 'llama-3.1-70b-versatile',
        'temperature': 0.7,
        'max_tokens': 280
    }

    for key, default_value in ai_defaults.items():
        if key not in validated['ai']:
            validated['ai'][key] = default_value
            logger.info(f"Using default ai.{key}: {default_value}")

    # Validate temperature range
    temp = validated['ai']['temperature']
    if not isinstance(temp, (int, float)) or temp < 0.0 or temp > 2.0:
        logger.warning(f"Invalid temperature {temp}, using 0.7")
        validated['ai']['temperature'] = 0.7

    # Duplicate detection
    if 'duplicate_detection' not in validated:
        validated['duplicate_detection'] = {}

    dup_defaults = {
        'enabled': True,
        'similarity_threshold': 0.85,
        'check_last_days': 7
    }

    for key, default_value in dup_defaults.items():
        if key not in validated['duplicate_detection']:
            validated['duplicate_detection'][key] = default_value

    # Database
    if 'database' not in validated:
        validated['database'] = {'path': 'data/bot.db'}

    # Selenium
    if 'selenium' not in validated:
        validated['selenium'] = {}

    selenium_defaults = {
        'headless': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'window_size': '1920,1080',
        'timeout': 30,
        'cookie_file': 'data/twitter_cookies.json',
        'page_load_timeout': 60,
        'implicit_wait': 10
    }

    for key, default_value in selenium_defaults.items():
        if key not in validated['selenium']:
            validated['selenium'][key] = default_value

    # Human behavior
    if 'human_behavior' not in validated:
        validated['human_behavior'] = {}

    if 'random_timing' not in validated['human_behavior']:
        validated['human_behavior']['random_timing'] = {
            'enabled': True,
            'min_extra_minutes': 5,
            'max_extra_minutes': 20
        }

    hb_defaults = {
        'working_hours_start': 7,
        'working_hours_end': 1,
        'random_skip_chance': 0.05
    }

    for key, default_value in hb_defaults.items():
        if key not in validated['human_behavior']:
            validated['human_behavior'][key] = default_value

    # Images
    if 'images' not in validated:
        validated['images'] = {'enabled': True}

    return validated


def safe_file_operation(operation: Callable, *args, max_retries: int = 3, **kwargs) -> Any:
    """
    Safely perform file operations with retry logic

    Args:
        operation: File operation function
        max_retries: Maximum number of retries
        *args, **kwargs: Arguments to pass to operation

    Returns:
        Result of operation
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            return operation(*args, **kwargs)
        except (IOError, OSError, PermissionError) as e:
            last_error = e
            if attempt < max_retries - 1:
                logger.warning(f"File operation failed (attempt {attempt + 1}): {e}")
                time.sleep(0.5 * (attempt + 1))
            else:
                logger.error(f"File operation failed after {max_retries} attempts: {e}")

    raise last_error


def sanitize_text(text: str, max_length: int = 280) -> str:
    """
    Sanitize text for safe processing

    Args:
        text: Input text
        max_length: Maximum length

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove null bytes and control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')

    # Normalize whitespace
    text = ' '.join(text.split())

    # Truncate if needed
    if len(text) > max_length:
        text = text[:max_length - 3] + "..."

    return text.strip()


def get_timestamp() -> str:
    """Get current timestamp in standardized format"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def check_disk_space(path: str = '.', min_mb: int = 100) -> bool:
    """
    Check if sufficient disk space is available

    Args:
        path: Path to check
        min_mb: Minimum required space in MB

    Returns:
        True if sufficient space available
    """
    import shutil

    try:
        stat = shutil.disk_usage(path)
        free_mb = stat.free / (1024 * 1024)

        if free_mb < min_mb:
            logger.warning(f"Low disk space: {free_mb:.1f} MB free (minimum: {min_mb} MB)")
            return False

        return True
    except Exception as e:
        logger.error(f"Error checking disk space: {e}")
        return True  # Assume ok if we can't check


def cleanup_old_files(directory: str, days: int = 7, pattern: str = "*") -> int:
    """
    Clean up old files in directory

    Args:
        directory: Directory to clean
        days: Delete files older than this many days
        pattern: File pattern to match

    Returns:
        Number of files deleted
    """
    import os
    import glob
    from pathlib import Path

    if not os.path.exists(directory):
        return 0

    count = 0
    cutoff_time = time.time() - (days * 86400)

    try:
        for file_path in glob.glob(os.path.join(directory, pattern)):
            if os.path.isfile(file_path):
                if os.path.getmtime(file_path) < cutoff_time:
                    try:
                        os.remove(file_path)
                        count += 1
                        logger.debug(f"Deleted old file: {file_path}")
                    except Exception as e:
                        logger.warning(f"Could not delete {file_path}: {e}")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

    if count > 0:
        logger.info(f"Cleaned up {count} old files from {directory}")

    return count
