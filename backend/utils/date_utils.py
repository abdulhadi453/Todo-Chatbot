"""
Date/time manipulation utilities.
These utilities provide consistent date and time operations across the application.
"""

from datetime import datetime, date, timedelta
from typing import Optional, Union
import pytz
from zoneinfo import ZoneInfo


class DateUtils:
    """
    Utility class for date and time manipulation operations.
    Provides consistent formatting, calculation, and validation of date/time values.
    """

    @staticmethod
    def get_current_utc_datetime() -> datetime:
        """
        Get the current UTC datetime.

        Returns:
            Current datetime in UTC timezone
        """
        return datetime.now(pytz.UTC)

    @staticmethod
    def get_current_local_datetime(timezone_str: str = 'UTC') -> datetime:
        """
        Get the current local datetime in the specified timezone.

        Args:
            timezone_str: Timezone string (e.g., 'America/New_York', 'Europe/London', 'UTC')

        Returns:
            Current datetime in the specified timezone
        """
        tz = ZoneInfo(timezone_str)
        return datetime.now(tz)

    @staticmethod
    def convert_timezone(dt: datetime, from_tz: str, to_tz: str) -> datetime:
        """
        Convert a datetime from one timezone to another.

        Args:
            dt: Datetime to convert
            from_tz: Source timezone string
            to_tz: Target timezone string

        Returns:
            Converted datetime in the target timezone
        """
        source_tz = ZoneInfo(from_tz)
        target_tz = ZoneInfo(to_tz)

        # If datetime is naive (no timezone info), assume it's in the source timezone
        if dt.tzinfo is None:
            dt = source_tz.localize(dt)

        # Convert to target timezone
        return dt.astimezone(target_tz)

    @staticmethod
    def parse_datetime(datetime_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
        """
        Parse a datetime string into a datetime object.

        Args:
            datetime_str: Date string to parse
            format_str: Format string for parsing

        Returns:
            Parsed datetime object
        """
        return datetime.strptime(datetime_str, format_str)

    @staticmethod
    def parse_iso_datetime(iso_str: str) -> datetime:
        """
        Parse an ISO 8601 formatted datetime string.

        Args:
            iso_str: ISO 8601 formatted datetime string

        Returns:
            Parsed datetime object
        """
        return datetime.fromisoformat(iso_str.replace('Z', '+00:00'))

    @staticmethod
    def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Format a datetime object as a string.

        Args:
            dt: Datetime object to format
            format_str: Format string for output

        Returns:
            Formatted datetime string
        """
        return dt.strftime(format_str)

    @staticmethod
    def format_iso_datetime(dt: datetime) -> str:
        """
        Format a datetime object as an ISO 8601 string.

        Args:
            dt: Datetime object to format

        Returns:
            ISO 8601 formatted datetime string
        """
        return dt.isoformat()

    @staticmethod
    def add_days(dt: datetime, days: int) -> datetime:
        """
        Add days to a datetime.

        Args:
            dt: Original datetime
            days: Number of days to add (negative to subtract)

        Returns:
            New datetime with days added
        """
        return dt + timedelta(days=days)

    @staticmethod
    def add_hours(dt: datetime, hours: int) -> datetime:
        """
        Add hours to a datetime.

        Args:
            dt: Original datetime
            hours: Number of hours to add (negative to subtract)

        Returns:
            New datetime with hours added
        """
        return dt + timedelta(hours=hours)

    @staticmethod
    def add_minutes(dt: datetime, minutes: int) -> datetime:
        """
        Add minutes to a datetime.

        Args:
            dt: Original datetime
            minutes: Number of minutes to add (negative to subtract)

        Returns:
            New datetime with minutes added
        """
        return dt + timedelta(minutes=minutes)

    @staticmethod
    def add_seconds(dt: datetime, seconds: int) -> datetime:
        """
        Add seconds to a datetime.

        Args:
            dt: Original datetime
            seconds: Number of seconds to add (negative to subtract)

        Returns:
            New datetime with seconds added
        """
        return dt + timedelta(seconds=seconds)

    @staticmethod
    def get_start_of_day(dt: datetime) -> datetime:
        """
        Get the start of the day (00:00:00) for a given datetime.

        Args:
            dt: Input datetime

        Returns:
            Datetime at the start of the same day
        """
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def get_end_of_day(dt: datetime) -> datetime:
        """
        Get the end of the day (23:59:59) for a given datetime.

        Args:
            dt: Input datetime

        Returns:
            Datetime at the end of the same day
        """
        return dt.replace(hour=23, minute=59, second=59, microsecond=999999)

    @staticmethod
    def get_start_of_month(dt: datetime) -> datetime:
        """
        Get the start of the month (first day, 00:00:00) for a given datetime.

        Args:
            dt: Input datetime

        Returns:
            Datetime at the start of the same month
        """
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def get_end_of_month(dt: datetime) -> datetime:
        """
        Get the end of the month (last day, 23:59:59) for a given datetime.

        Args:
            dt: Input datetime

        Returns:
            Datetime at the end of the same month
        """
        # Calculate the first day of the next month
        next_month = dt.replace(day=28) + timedelta(days=4)
        # Subtract the number of days that carry over to get the last day of current month
        last_day = next_month - timedelta(days=next_month.day)
        return last_day.replace(hour=23, minute=59, second=59, microsecond=999999)

    @staticmethod
    def calculate_age(birth_date: Union[date, datetime]) -> int:
        """
        Calculate age in years from birth date.

        Args:
            birth_date: Birth date (date or datetime object)

        Returns:
            Age in years
        """
        if isinstance(birth_date, datetime):
            birth_date = birth_date.date()

        today = date.today()
        age = today.year - birth_date.year
        # Adjust if birthday hasn't occurred this year yet
        if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
            age -= 1

        return age

    @staticmethod
    def days_between(start_date: Union[date, datetime], end_date: Union[date, datetime]) -> int:
        """
        Calculate the number of days between two dates.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Number of days between the dates
        """
        if isinstance(start_date, datetime):
            start_date = start_date.date()
        if isinstance(end_date, datetime):
            end_date = end_date.date()

        return (end_date - start_date).days

    @staticmethod
    def seconds_between(start_dt: datetime, end_dt: datetime) -> float:
        """
        Calculate the number of seconds between two datetimes.

        Args:
            start_dt: Start datetime
            end_dt: End datetime

        Returns:
            Number of seconds between the datetimes
        """
        return (end_dt - start_dt).total_seconds()

    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        Format a duration in seconds into a human-readable format.

        Args:
            seconds: Duration in seconds

        Returns:
            Formatted duration string
        """
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if days > 0:
            return f"{days}d {hours}h {minutes}m {secs}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

    @staticmethod
    def is_weekend(dt: datetime) -> bool:
        """
        Check if a datetime falls on a weekend.

        Args:
            dt: Datetime to check

        Returns:
            True if datetime is on a weekend, False otherwise
        """
        return dt.weekday() >= 5  # Saturday is 5, Sunday is 6

    @staticmethod
    def is_business_day(dt: datetime) -> bool:
        """
        Check if a datetime falls on a business day (Monday-Friday).

        Args:
            dt: Datetime to check

        Returns:
            True if datetime is a business day, False otherwise
        """
        return dt.weekday() < 5  # Monday to Friday

    @staticmethod
    def get_next_business_day(dt: datetime) -> datetime:
        """
        Get the next business day after the given datetime.

        Args:
            dt: Starting datetime

        Returns:
            Next business day datetime
        """
        next_day = dt + timedelta(days=1)
        while not DateUtils.is_business_day(next_day):
            next_day += timedelta(days=1)
        return next_day

    @staticmethod
    def get_previous_business_day(dt: datetime) -> datetime:
        """
        Get the previous business day before the given datetime.

        Args:
            dt: Starting datetime

        Returns:
            Previous business day datetime
        """
        prev_day = dt - timedelta(days=1)
        while not DateUtils.is_business_day(prev_day):
            prev_day -= timedelta(days=1)
        return prev_day

    @staticmethod
    def format_relative_time(dt: datetime) -> str:
        """
        Format a datetime as a relative time string (e.g., "2 hours ago", "in 3 days").

        Args:
            dt: Datetime to format

        Returns:
            Relative time string
        """
        now = DateUtils.get_current_utc_datetime()
        diff = dt - now

        if diff.total_seconds() < 0:
            # Past time
            diff = abs(diff.total_seconds())
            if diff < 60:
                return "just now"
            elif diff < 3600:
                mins = int(diff / 60)
                return f"{mins} minute{'s' if mins != 1 else ''} ago"
            elif diff < 86400:
                hours = int(diff / 3600)
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
            else:
                days = int(diff / 86400)
                return f"{days} day{'s' if days != 1 else ''} ago"
        else:
            # Future time
            diff = diff.total_seconds()
            if diff < 60:
                return "in a moment"
            elif diff < 3600:
                mins = int(diff / 60)
                return f"in {mins} minute{'s' if mins != 1 else ''}"
            elif diff < 86400:
                hours = int(diff / 3600)
                return f"in {hours} hour{'s' if hours != 1 else ''}"
            else:
                days = int(diff / 86400)
                return f"in {days} day{'s' if days != 1 else ''}"

    @staticmethod
    def validate_date_range(start_date: Union[date, datetime], end_date: Union[date, datetime]) -> bool:
        """
        Validate that end_date is after or equal to start_date.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            True if date range is valid, False otherwise
        """
        if isinstance(start_date, datetime):
            start_date = start_date.date()
        if isinstance(end_date, datetime):
            end_date = end_date.date()

        return start_date <= end_date

    @staticmethod
    def get_quarter(dt: datetime) -> int:
        """
        Get the quarter (1-4) for a given datetime.

        Args:
            dt: Input datetime

        Returns:
            Quarter number (1-4)
        """
        return (dt.month - 1) // 3 + 1

    @staticmethod
    def get_quarter_start_date(year: int, quarter: int) -> date:
        """
        Get the start date of a specific quarter.

        Args:
            year: Year
            quarter: Quarter (1-4)

        Returns:
            Start date of the quarter
        """
        if not 1 <= quarter <= 4:
            raise ValueError("Quarter must be between 1 and 4")

        start_month = (quarter - 1) * 3 + 1
        return date(year, start_month, 1)

    @staticmethod
    def get_quarter_end_date(year: int, quarter: int) -> date:
        """
        Get the end date of a specific quarter.

        Args:
            year: Year
            quarter: Quarter (1-4)

        Returns:
            End date of the quarter
        """
        if not 1 <= quarter <= 4:
            raise ValueError("Quarter must be between 1 and 4")

        end_month = quarter * 3
        # Handle December separately
        if end_month > 12:
            end_month = 12

        # Days in month for end date
        if end_month in [1, 3, 5, 7, 8, 10, 12]:
            day = 31
        elif end_month in [4, 6, 9, 11]:
            day = 30
        else:  # February
            day = 29 if DateUtils.is_leap_year(year) else 28

        return date(year, end_month, day)

    @staticmethod
    def is_leap_year(year: int) -> bool:
        """
        Check if a year is a leap year.

        Args:
            year: Year to check

        Returns:
            True if leap year, False otherwise
        """
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    @staticmethod
    def get_days_in_month(year: int, month: int) -> int:
        """
        Get the number of days in a specific month and year.

        Args:
            year: Year
            month: Month (1-12)

        Returns:
            Number of days in the month
        """
        if month in [1, 3, 5, 7, 8, 10, 12]:
            return 31
        elif month in [4, 6, 9, 11]:
            return 30
        elif month == 2:
            return 29 if DateUtils.is_leap_year(year) else 28
        else:
            raise ValueError("Month must be between 1 and 12")